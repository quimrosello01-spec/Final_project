import matplotlib.pyplot as plt
import os
from src.final_project.city import City


# Adjustable area nightly rate ranges
area_rates = {
    0: (100, 200),
    1: (50, 250),
    2: (250, 350),
    3: (150, 450)
}


# -------------------------------------------------------
# GINI COEFFICIENT
# -------------------------------------------------------
def compute_gini(values):
    """Compute the Gini coefficient from a list of wealth values."""
    if len(values) == 0:
        return 0

    sorted_vals = sorted(values)
    n = len(values)
    cumulative = 0
    weighted_sum = 0

    for i, val in enumerate(sorted_vals, 1):
        cumulative += val
        weighted_sum += i * val

    numerator = 2 * weighted_sum
    denominator = n * cumulative

    gini = (numerator / denominator) - (n + 1) / n
    return max(0, min(gini, 1))


# -------------------------------------------------------
# RUN SIMULATION — logs Gini over time
# -------------------------------------------------------
def run_simulation(modify_rules=False):
    city = City(size=10, area_rates=area_rates)
    city.initialize()

    # -----------------------------------------
    # RULE MODIFICATION (Bidding strategy)
    # -----------------------------------------
    if modify_rules:

        for host in city.hosts.values():

            original_make_bids = host.make_bids  # ← keep original for reference

            def modified_bids(self):
                bids = original_make_bids()
                for b in bids:

                    # ORIGINAL RULE (kept for reference)
                    # b["bid_price"] = self.profits

                    # MODIFIED RULE
                    b["bid_price"] = 0.7 * self.profits

                return bids

            host.make_bids = modified_bids.__get__(host, host.__class__)

    # -----------------------------------------
    # Simulation loop: track Gini
    # -----------------------------------------
    steps = 180  # 15 years = 180 months
    gini_history = []

    for _ in range(steps):
        city.iterate()

        wealths = city.compute_wealths()
        values = list(wealths.values())

        gini_val = compute_gini(values)
        gini_history.append(gini_val)

    return gini_history


# -------------------------------------------------------
# GRAPH 1: Wealth distribution (unchanged)
# -------------------------------------------------------
def graph1(city):
    wealths = city.compute_wealths()

    ids = sorted(wealths, key=lambda x: wealths[x])
    values = [wealths[i] for i in ids]
    areas = [city.hosts[i].area for i in ids]
    colors = ["C" + str(a) for a in areas]

    plt.figure(figsize=(12, 6))
    plt.bar(range(len(ids)), values, color=colors)
    plt.xlabel("Host (sorted by wealth)")
    plt.ylabel("Wealth")
    plt.title("Host Wealth After 15 Years")

    # Legend
    import matplotlib.patches as mpatches
    patches = [
        mpatches.Patch(color="C0", label="Area 0"),
        mpatches.Patch(color="C1", label="Area 1"),
        mpatches.Patch(color="C2", label="Area 2"),
        mpatches.Patch(color="C3", label="Area 3")
    ]
    plt.legend(handles=patches, title="Area of Origin")

    os.makedirs("reports", exist_ok=True)
    plt.savefig("reports/graph1.png")
    plt.close()


# -------------------------------------------------------
# GRAPH 2: Gini over time
# -------------------------------------------------------
def graph2(gini_history, filename, label):
    plt.figure(figsize=(12, 6))
    plt.plot(gini_history, label=label)

    plt.xlabel("Month")
    plt.ylabel("Gini Coefficient")
    plt.title(f"Inequality (Gini) Over Time — {label}")
    plt.legend()

    os.makedirs("reports", exist_ok=True)
    plt.savefig(f"reports/{filename}")
    plt.close()


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
def main():

    # Run original rules
    gini_v0 = run_simulation(modify_rules=False)

    # Run modified rules
    gini_v1 = run_simulation(modify_rules=True)

    # Save the graphs
    graph2(gini_v0, "graph2_v0.png", "Original Rules")
    graph2(gini_v1, "graph2_v1.png", "Modified Rules")

    print("Graphs saved in /reports")


if __name__ == "__main__":
    main()
