import math
from itertools import product

PROBABILITY_TABLE = {
    1: {0: 0.41, 1: 0.59}, 2: {1: 0.67, 2: 0.33}, 3: {1: 0.39, 2: 0.52, 3: 0.10},
    4: {1: 0.11, 2: 0.59, 3: 0.31}, 5: {2: 0.43, 3: 0.57}, 6: {2: 0.28, 3: 0.72},
}

def get_full_distribution(total_affixes):
    if total_affixes == 0: return {0: 1.0}
    dist = PROBABILITY_TABLE.get(total_affixes, {})
    prob_sum = sum(dist.values())
    if prob_sum < 1.0: dist[0] = round(1.0 - prob_sum, 2)
    return dist

def get_outcome_distribution(total_p, total_s):
    if total_p == 1 and total_s == 1:
        return {(1, 1): 0.33, (1, 0): 0.33, (0, 1): 0.33, (0,0): 0.01}
    p_dist = get_full_distribution(total_p)
    s_dist = get_full_distribution(total_s)
    combined_dist = {}
    for p, p_chance in p_dist.items():
        for s, s_chance in s_dist.items():
            combined_dist[(p, s)] = p_chance * s_chance
    return combined_dist

def nCr(n, r):
    if r < 0 or r > n: return 0
    return math.factorial(n) // math.factorial(r) // math.factorial(n - r)

class CostMapGenerator:
    def __init__(self):
        self.cost_map = {}
        self.build_cost_map()

    def get_cost(self, p, s):
        return self.cost_map.get((p, s), (float('inf'), "N/A"))

    def build_cost_map(self):
        self.cost_map[(0, 0)] = (0, "Start with a normal item.")
        self.cost_map[(1, 0)] = (1, "Start with a 1-prefix magic item.")
        self.cost_map[(0, 1)] = (1, "Start with a 1-suffix magic item.")
        for p in range(4):
            for s in range(4):
                if (p, s) in self.cost_map: continue
                self.compute_best_standard_combination_for(p, s)

    def compute_best_standard_combination_for(self, p_target, s_target):
        if (p_target, s_target) in self.cost_map: return
        best_cost, best_path = float('inf'), "No path found"
        for p1 in range(p_target + 1):
            for s1 in range(s_target + 1):
                if p1 > p_target - p1 or (p1 == p_target - p1 and s1 > s_target - s1): continue
                p2, s2 = p_target - p1, s_target - s1
                cost1, path1 = self.get_cost(p1, s1)
                cost2, path2 = self.get_cost(p2, s2)
                if cost1 == float('inf') or cost2 == float('inf'): continue
                total_p, total_s = p1 + p2, s1 + s2
                if total_p > 6 or total_s > 6 or (total_p==0 and total_s==0): continue

                full_dist = get_outcome_distribution(total_p, total_s)
                prob_mod_selection = (1 / nCr(total_p, p_target) if nCr(total_p,p_target)>0 else 1) * (1 / nCr(total_s, s_target) if nCr(total_s,s_target)>0 else 1)
                p_succ = full_dist.get((p_target, s_target), 0) * prob_mod_selection
                if p_succ == 0: continue

                p_recycle1 = full_dist.get((p1, s1), 0)
                p_recycle2 = full_dist.get((p2, s2), 0)

                if (p1,s1) == (p2,s2):
                    expected_cost = (cost1 * (2 - 2 * p_recycle1)) / p_succ if p_succ > 0 else float('inf')
                else:
                    expected_cost = (cost1 * (1 - p_recycle1) + cost2 * (1 - p_recycle2)) / p_succ if p_succ > 0 else float('inf')

                if expected_cost < best_cost:
                    best_cost = expected_cost
                    path1_indented = "   " + path1.replace("\n", "\n   ")
                    path2_indented = "   " + path2.replace("\n", "\n   ")
                    best_path = (f"To make this item, combine a ({p1}p/{s1}s) and a ({p2}p/{s2}s) item.\n"
                                 f"  - Path for the ({p1}p/{s1}s) item:\n{path1_indented}\n"
                                 f"  - Path for the ({p2}p/{s2}s) item:\n{path2_indented}")

        self.cost_map[(p_target, s_target)] = (best_cost, best_path)

def calculate_recombination_outcomes(desired_p, desired_s):
    cost_gen = CostMapGenerator()
    plans = []

    # --- Strategy 1: Find Cheapest Standard Path from Planner ---
    cost, path = cost_gen.get_cost(desired_p, desired_s)
    if cost != float('inf') and cost > 0:
        plans.append({"name": f"Standard Plan for {desired_p}p/{desired_s}s", "base_item_cost": cost, "exclusive_cost": 0, "explanation": path})

    # --- Strategy 2 & 3: Advanced strategies for 3 prefixes ---
    if desired_p == 3:
        # Doubled Mod
        cost2p, path2p = cost_gen.get_cost(2, desired_s)
        if cost2p != float('inf'):
            p_succ = 0.31
            total_cost = (cost2p * 2) / p_succ
            explanation = f"1. Create two {2}p/{desired_s}s items, sharing one prefix.\n   (Est. ingredient cost: {cost2p*2:.1f} base items).\n   - Path for one ingredient:\n     {path2p.replace(chr(10), chr(10)+'     ')}\n2. Combine them. Final step success chance is {p_succ:.0%}."
            plans.append({"name": f"Doubled Prefix Strategy for 3p/{desired_s}s", "base_item_cost": total_cost, "exclusive_cost": 0, "explanation": explanation})

        # Exclusive Mods
        cost1p, path1p = cost_gen.get_cost(1, desired_s)
        if cost2p != float('inf') and cost1p != float('inf'):
            p_succ = 0.36
            step_cost_e = 3
            total_cost = (cost2p + cost1p) / p_succ
            explanation = (f"1. Create a {2}p/{desired_s}s item (Est. cost: {cost2p:.1f} base items).\n   - Path:\n     {path2p.replace(chr(10), chr(10)+'     ')}\n"
                           f"2. Create a {1}p/{desired_s}s item (Est. cost: {cost1p:.1f} base items).\n   - Path:\n     {path1p.replace(chr(10), chr(10)+'     ')}\n"
                           f"3. Add {step_cost_e} exclusive mods and combine. Final step success chance is {p_succ:.0%}.")
            plans.append({"name": f"Exclusive Mod Strategy for 3p/{desired_s}s", "base_item_cost": total_cost, "exclusive_cost": step_cost_e, "explanation": explanation})

    unique_plans = {plan['name']: plan for plan in plans}
    sorted_plans = sorted(unique_plans.values(), key=lambda x: x['base_item_cost'])
    return sorted_plans[:5]
