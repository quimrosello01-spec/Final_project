from __future__ import annotations

from typing import Dict, List
import pandas as pd

from .place import Place
from .host import Host

class City:
    def __init__(self, size: int, area_rates: dict[int, tuple[float,float]]):
        self.size = size
        self.area_rates = area_rates
        self.step = 0

        # Grid-related structures
        self.grid_size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.positions = {}

        self.place: Dict[int, Place] = {}
        self.hosts: Dict[int, Host] = {}

    def initialize(self) -> None:
        index = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.grid[r][c] = index
                self.positions[index] = (r, c)
                index += 1
        num_place = self.size * self.size

        for place_id in range(num_place):
            host_id = place_id
            place = Place(place_id=place_id, host_id=host_id, city=self)
            self.place[place_id]=place

        # Initialize place area, rate, neighbours, prices
        for place in self.place.values():
             place.setup()

        for place in self.place.values():
            host_id = place.host_id
            host = Host(host_id=host_id, place=place, city=self)
            self.hosts[host_id] = host
        
    def approve_bids(self, bids: List[dict]) -> List[dict]:
        if not bids:
            return []
        df = pd.DataFrame(bids)
        df = df.sort_values("spread", ascending=False)

        approved = []
        used_buyers = set()
        used_places = set()

        for _, row in df.iterrows():
            place_id = int(row["place_id"])
            buyer_id = int(row["buyer_id"])

            if buyer_id in used_buyers or place_id in used_places:
                continue

            approved.append(row.to_dict())
            used_buyers.add(buyer_id)
            used_places.add(place_id)

        return approved
    
    def execute_transactions(self, transactions: List[dict]) -> None:
        for tx in transactions:
            place_id = int(tx["place_id"])
            buyer_id = int(tx["buyer_id"])
            seller_id = int(tx["seller_id"])
            bid_price = float(tx["bid_price"])

            place = self.place[place_id]
            buyer = self.hosts[buyer_id]
            seller = self.hosts[seller_id]

            buyer.profits -= bid_price
            seller.profits += bid_price

            if place_id in seller.assets:
                seller.assets.remove(place_id)
            buyer.assets.add(place_id)

            place.host_id = buyer.host_id
            place.price[self.step] = bid_price

    def clear_market(self) -> List[dict]:
        all_bids: List[dict] = []

        for host in self.hosts.values():
            host_bids = host.make_bids()
            all_bids.extend(host_bids)
        
        if not all_bids:
            return []
        
        approved = self.approve_bids(all_bids)
        if approved:
            self.execute_transactions(approved)
        return approved
    
    def iterate(self) -> List[dict]:
        self.step += 1

        for place in self.place.values():
            place.update_occupancy()
        
        for host in self.hosts.values():
            host.update_profits()
        
        transactions = self.clear_market()
        return transactions

    def compute_wealths(self):
        wealths = {}
        for host in self.hosts.values():
            asset_value = 0
            for pid in host.assets:
                p = self.place[pid]
                last_price = p.price[max(p.price.keys())]
                asset_value += last_price

            wealths[host.host_id] = host.profits + asset_value

        return wealths