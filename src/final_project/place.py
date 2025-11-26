import random 
class Place:
    def __init__(self, place_id, host_id, city):
        self.place_id = place_id
        self.host_id = host_id
        self.city = city

        # Attributes initialized later
        self.neighbours = []
        self.area = None
        self.rate = None
        self.price = {}
        self.occupancy = 0
    
    def setup(self):
        # determine are based on city grid position
        # assuming city has attributes: grid_size and positions mapping place_id --> (row, col)
        row, col = self.city.positions[self.place_id]
        mid_row = self.city.grid_size // 2
        mid_col = self.city.grid_size // 2
        
        if row < mid_row and col < mid_col:
            self.area = 0 #bottom_left
        elif row < mid_row and col >= mid_col:
            self.area = 1 #bottom_right
        elif row >= mid_row and col < mid_col:
            self.area = 2 #top_left
        else:
            self.area = 3 #top_right
        
        # Assign nightly rate based on area
        rate_range = self.city.area_rates[self.area]
        self.rate = random.uniform(rate_range[0], rate_range[1])

        # Intialized price history
        self.price = {0: 900*self.rate}

        # Compute neighbours (adjacent cells)
        self.neighbours = self._find_neighbours(row, col)

    def _find_neighbours(self, row, col):
        neighbours = []
        for r in range(row-1, row+2):
            for c in range(col-1,col+2):
                if (r,c)!=(row, col) and 0<=r < self.city.grid_size and 0<=c < self.city.grid_size:
                    
                    # find place_id for this position
                    pid = self.city.grid[r][c]
                    if pid is not None:
                        neighbours.append(pid)
        return neighbours
    
    def update_occupancy(self):
        # Compute mean rate for the area:
        area_rates = [p.rate for p in self.city.place.values() if p.area == self.area]
        mean_rate = sum(area_rates)/len(area_rates)

        if self.rate > mean_rate:
            self.occupancy = random.randint(5,15)
        else:
            self.occupancy = random.randint(10,20)