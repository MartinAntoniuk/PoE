import math
from itertools import product

PROBABILITY_TABLE = {
    1: {1: 1.0}, 2: {1: 0.67, 2: 0.33}, 3: {1: 0.39, 2: 0.52, 3: 0.10},
    4: {1: 0.11, 2: 0.59, 3: 0.31}, 5: {2: 0.43, 3: 0.57}, 6: {2: 0.28, 3: 0.72},
}

def get_outcome_distribution(total_affixes):
    if total_affixes > 6: total_affixes = 6
    return PROBABILITY_TABLE.get(total_affixes, {})

def nCr(n, r):
    if r < 0 or r > n: return 0
    return math.factorial(n) // math.factorial(r) // math.factorial(n - r)

class CostMapGenerator:
    """Generates a cost map for creating standard items via simple recombinations."""
    def __init__(self):
        self.cost_map = {}
        self.build_cost_map()

    def get_cost(self, p, s):
        return self.cost_map.get((p, s), (float('inf'), "N/A"))

    def build_cost_map(self):
        self.cost_map[(0, 0)] = (0, "Start with a normal item.")
        self.cost_map[(1, 0)] = (0, "Start with a 1-prefix magic item.")
        self.cost_map[(0, 1)] = (0, "Start with a 1-suffix magic item.")
        self.cost_map[(1, 1)] = (0.25, "Use a Regal Orb on a 1-affix item.")

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

                p_dist = get_outcome_distribution(total_p)
                s_dist = get_outcome_distribution(total_s)
                prob_num_affixes = p_dist.get(p_target, 0) * (s_dist.get(s_target, 0) if s_target > 0 else (1 if total_s == 0 else 0))

                ways_p = nCr(total_p, p_target)
                ways_s = nCr(total_s, s_target)
                prob_mod_selection = (1 / ways_p if ways_p > 0 else 0) * (1 / ways_s if ways_s > 0 else 1)
                p_success = prob_num_affixes * prob_mod_selection

                if p_success > 0:
                    step_cost_r = 1 / p_success
                    total_r = cost1_r + cost2_r + step_cost_r
                    if total_r < best_r_cost:
                        best_r_cost = total_r
                        best_path = f"To make a {p_target}p/{s_target}s item:\n  1. Make a {p1}p/{s1}s item. Path:\n     {path1.replace(chr(10), chr(10)+'     ')}\n  2. Make a {p2}p/{s2}s item. Path:\n     {path2.replace(chr(10), chr(10)+'     ')}\n  3. Combine them. (Step Cost: {step_cost_r:.1f} attempts)"

        self.cost_map[(p_target, s_target)] = (best_r_cost, best_path)

def calculate_recombination_outcomes(desired_p, max_p, desired_s, max_s):
    """The Strategy Presenter."""
    cost_gen = CostMapGenerator()
    plans = []

    # For now, we only generate plans for the exact desired outcome.
    p_goal, s_goal = desired_p, desired_s

    # --- Strategy 1: Simple Combinations ---
    for p1 in range(p_goal + 1):
        for s1 in range(s_goal + 1):
            if p1 > p_goal - p1 or (p1 == p_goal - p1 and s1 > s_goal - s1): continue
            p2, s2 = p_goal - p1, s_goal - s1

            cost1_r, path1 = cost_gen.get_cost(p1, s1)
            cost2_r, path2 = cost_gen.get_cost(p2, s2)
            if cost1_r == float('inf') or cost2_r == float('inf'): continue

            total_p, total_s = p1 + p2, s1 + s2
            if total_p > 6 or total_s > 6 or (total_p==0 and total_s==0): continue

            prob_num = get_outcome_distribution(total_p).get(p_goal, 0) * (get_outcome_distribution(total_s).get(s_goal, 0) if s_goal > 0 else 1)
            prob_mod = (1/nCr(total_p, p_goal) if nCr(total_p,p_goal)>0 else 0) * (1/nCr(total_s,s_goal) if nCr(total_s,s_goal)>0 else 1)
            p_success = prob_num * prob_mod
            if p_success > 0:
                step_cost_r = 1 / p_success
                total_r = cost1_r + cost2_r + step_cost_r
                explanation = f"1. Create a {p1}p/{s1}s item (Cost: {cost1_r:.1f} attempts).\n   - How: {path1}\n2. Create a {p2}p/{s2}s item (Cost: {cost2_r:.1f} attempts).\n   - How: {path2}\n3. Combine them. (Final Step Cost: {step_cost_r:.1f} attempts)"
                plans.append({"name": f"Standard Combine: ({p1}p/{s1}s) + ({p2}p/{s2}s)", "cost": total_r, "exclusive_cost": 0, "explanation": explanation})

    # --- Strategy 2: Doubled Modifier ---
    if p_goal == 3:
        cost2p_r, path2p = cost_gen.get_cost(2, s_goal)
        if cost2p_r != float('inf'):
            p_success = 0.31 # 31% chance for 3p from 4p pool, 100% mod selection
            step_cost_r = 1 / p_success
            total_r = cost2p_r * 2 + step_cost_r
            explanation = f"1. Create two {2}p/{s_goal}s items, sharing one prefix (Cost: {cost2p_r*2:.1f} attempts total).\n   - How to make one: {path2p}\n2. Combine them. (Final Step Cost: {step_cost_r:.1f} attempts)"
            plans.append({"name": "Doubled Prefix Strategy", "cost": total_r, "exclusive_cost": 0, "explanation": explanation})

    # --- Strategy 3: Exclusive Mods ---
    if p_goal == 3:
        cost2p_r, path2p = cost_gen.get_cost(2, s_goal)
        cost1p_r, path1p = cost_gen.get_cost(1, s_goal)
        if cost2p_r != float('inf') and cost1p_r != float('inf'):
            p_success = 0.36
            step_cost_r = 1 / p_success
            step_cost_e = 3
            total_r = cost2p_r + cost1p_r + step_cost_r
            explanation = f"1. Create a {2}p/{s_goal}s item (Cost: {cost2p_r:.1f} attempts).\n   - How: {path2p}\n2. Create a {1}p/{s_goal}s item (Cost: {cost1p_r:.1f} attempts).\n   - How: {path1p}\n3. Add {step_cost_e} exclusive mods and combine. (Final Step Cost: {step_cost_r:.1f} attempts)"
            plans.append({"name": "Exclusive Mod Strategy", "cost": total_r, "exclusive_cost": step_cost_e, "explanation": explanation})

    # Sort and filter
    unique_plans = {plan['name']: plan for plan in plans}
    sorted_plans = sorted(unique_plans.values(), key=lambda x: x['cost'])
    return sorted_plans[:5]
