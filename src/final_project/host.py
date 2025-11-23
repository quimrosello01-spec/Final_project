class Host:
    def __init__(self, host_id, place, city, profits=0):
        self.host_id = host_id
        self.city = city
        self.profits = profits
        self.area = place.area
        self.assets = {place.place_id}

    def update_profits(self):
        for pid in self.assets:
            place = self.city.places[pid]
            self.profits += place.rate * place.occupancy

    def make_bids(self):
        opportunities = set()

        for pid in self.assets:
            place = self.city.places[pid]
            for neigh in place.neighbours:
                if neigh not in self.assets:
                    opportunities.add(neigh)

        bids = []

        for pid in opportunities:
            place = self.city.places[pid]
            latest_step = max(place.price.keys())
            ask_price = place.price[latest_step]

            if self.profits >= ask_price:
                bid = {
                    "place_id": pid,
                    "seller_id": place.host_id,
                    "buyer_id": self.host_id,
                    "spread": self.profits - ask_price,
                    "bid_price": self.profits
                }
                bids.append(bid)

        return bids

