import math
from itertools import product

PROBABILITY_TABLE = {
    (1,1): { (1,1): 0.33, (1,0): 0.33, (0,1): 0.33 },
    1: {1: 1.0}, 2: {1: 0.67, 2: 0.33}, 3: {1: 0.39, 2: 0.52, 3: 0.10},
    4: {1: 0.11, 2: 0.59, 3: 0.31}, 5: {2: 0.43, 3: 0.57}, 6: {2: 0.28, 3: 0.72},
}

def get_outcome_distribution(total_p, total_s):
    if total_p == 1 and total_s == 1:
        return PROBABILITY_TABLE[(1,1)]
    total_affixes = total_p or total_s
    if total_affixes > 6: total_affixes = 6
    dist = PROBABILITY_TABLE.get(total_affixes, {})
    if total_p > 0:
        return {(p, 0): chance for p, chance in dist.items()}
    else:
        return {(0, s): chance for s, chance in dist.items()}

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
        self.cost_map[(1, 0)] = (0, "Start with a 1-prefix magic item.")
        self.cost_map[(0, 1)] = (0, "Start with a 1-suffix magic item.")
        for p in range(4):
            for s in range(4):
                if (p, s) in self.cost_map: continue
                self.compute_best_standard_combination_for(p, s)

    def compute_best_standard_combination_for(self, p_target, s_target):
        if (p_target, s_target) in self.cost_map: return
        best_r_cost, best_path = float('inf'), "No path found"
        for p1 in range(p_target + 1):
            for s1 in range(s_target + 1):
                if p1 > p_target - p1 or (p1 == p_target - p1 and s1 > s_target - s1): continue
                p2, s2 = p_target - p1, s_target - s1
                cost1_r, path1 = self.get_cost(p1, s1)
                cost2_r, path2 = self.get_cost(p2, s2)
                if cost1_r == float('inf') or cost2_r == float('inf'): continue
                total_p, total_s = p1 + p2, s1 + s2
                if total_p > 6 or total_s > 6 or (total_p==0 and total_s==0): continue
                p_success = 0
                if total_p == 1 and total_s == 1:
                    if p_target == 1 and s_target == 1: p_success = 0.33
                else:
                    p_dist = get_outcome_distribution(total_p, 0)
                    s_dist = get_outcome_distribution(0, total_s)
                    prob_p_num = p_dist.get((p_target, 0), 0) if p_target > 0 else (1 - sum(p_dist.values()))
                    prob_s_num = s_dist.get((0, s_target), 0) if s_target > 0 else (1 - sum(s_dist.values()))
                    prob_num_affixes = prob_p_num * prob_s_num
                    ways_p = nCr(total_p, p_target)
                    ways_s = nCr(total_s, s_target)
                    prob_mod_selection = (1 / ways_p if ways_p > 0 else 1) * (1 / ways_s if ways_s > 0 else 1)
                    p_success = prob_num_affixes * prob_mod_selection
                if p_success > 0:
                    step_cost_r = 1 / p_success
                    total_r = cost1_r + cost2_r + step_cost_r
                    if total_r < best_r_cost:
                        best_r_cost = total_r
                        path1_indented = "   " + path1.replace("\n", "\n   ")
                        path2_indented = "   " + path2.replace("\n", "\n   ")
                        best_path = (f"Combine ({p1}p/{s1}s) and ({p2}p/{s2}s) (Step Cost: {step_cost_r:.1f} attempts).\n"
                                     f"  - To get the ({p1}p/{s1}s) item:\n{path1_indented}\n"
                                     f"  - To get the ({p2}p/{s2}s) item:\n{path2_indented}")
        self.cost_map[(p_target, s_target)] = (best_r_cost, best_path)

def calculate_recombination_outcomes(desired_p, desired_s):
    """The Strategy Presenter."""
    cost_gen = CostMapGenerator()
    plans = []

    # --- Strategy 1: Find Cheapest Standard Path from Planner ---
    cost_r, path = cost_gen.get_cost(desired_p, desired_s)
    if cost_r != float('inf') and cost_r > 0:
        plans.append({"name": f"Standard Plan for {desired_p}p/{desired_s}s", "cost": cost_r, "exclusive_cost": 0, "explanation": path})

    # --- Strategy 2: Doubled Modifier (for 3 prefixes) ---
    if desired_p == 3:
        cost2p_r, path2p = cost_gen.get_cost(2, desired_s)
        if cost2p_r != float('inf'):
            p_success = 0.31
            step_cost_r = 1 / p_success
            total_r = cost2p_r * 2 + step_cost_r
            explanation = f"1. Create two {2}p/{desired_s}s items, sharing one prefix (Total ingredient cost: {cost2p_r*2:.1f} attempts).\n   - Path for one item:\n     {path2p.replace(chr(10), chr(10)+'     ')}\n2. Combine them. (Final Step Cost: {step_cost_r:.1f} attempts)"
            plans.append({"name": f"Doubled Prefix Strategy for {desired_p}p/{desired_s}s", "cost": total_r, "exclusive_cost": 0, "explanation": explanation})

    # --- Strategy 3: Exclusive Mods (for 3 prefixes) ---
    if desired_p == 3:
        cost2p_r, path2p = cost_gen.get_cost(2, desired_s)
        cost1p_r, path1p = cost_gen.get_cost(1, desired_s)
        if cost2p_r != float('inf') and cost1p_r != float('inf'):
            p_success = 0.36
            step_cost_r = 1 / p_success
            step_cost_e = 3
            total_r = cost2p_r + cost1p_r + step_cost_r
            explanation = (f"1. Create a {2}p/{desired_s}s item (Cost: {cost2p_r:.1f} attempts).\n   - Path:\n     {path2p.replace(chr(10), chr(10)+'     ')}\n"
                           f"2. Create a {1}p/{desired_s}s item (Cost: {cost1p_r:.1f} attempts).\n   - Path:\n     {path1p.replace(chr(10), chr(10)+'     ')}\n"
                           f"3. Add {step_cost_e} exclusive mods and combine. (Final Step Cost: {step_cost_r:.1f} attempts)")
            plans.append({"name": f"Exclusive Mod Strategy for {desired_p}p/{desired_s}s", "cost": total_r, "exclusive_cost": step_cost_e, "explanation": explanation})

    unique_plans = {plan['name']: plan for plan in plans}
    sorted_plans = sorted(unique_plans.values(), key=lambda x: x['cost'])
    return sorted_plans[:5]
