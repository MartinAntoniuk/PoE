import math
from itertools import product

PROBABILITY_TABLE = {
    # Special case for 1p/1s combine, from guide: 33% for 1p1s, 33% for 1p, 33% for 1s.
    (1,1): { (1,1): 0.33, (1,0): 0.33, (0,1): 0.33 },
    1: {1: 1.0}, 2: {1: 0.67, 2: 0.33}, 3: {1: 0.39, 2: 0.52, 3: 0.10},
    4: {1: 0.11, 2: 0.59, 3: 0.31}, 5: {2: 0.43, 3: 0.57}, 6: {2: 0.28, 3: 0.72},
}

def get_outcome_distribution(total_p, total_s):
    if total_p == 1 and total_s == 1:
        return PROBABILITY_TABLE[(1,1)]
    # For simplicity, we only model one affix type at a time for the standard table
    total_affixes = total_p or total_s
    if total_affixes > 6: total_affixes = 6
    dist = PROBABILITY_TABLE.get(total_affixes, {})
    # Return distribution in (p,s) format
    if total_p > 0:
        return {(p, 0): chance for p, chance in dist.items()}
    else:
        return {(0, s): chance for s, chance in dist.items()}


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
        # The (1,1) case is now calculated dynamically below

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

                dist = get_outcome_distribution(total_p, total_s)
                p_success = dist.get((p_target, s_target), 0)

                if p_success > 0:
                    step_cost_r = 1 / p_success
                    total_r = cost1_r + cost2_r + step_cost_r
                    if total_r < best_r_cost:
                        best_r_cost = total_r
                        best_path = f"Combine ({p1}p/{s1}s) + ({p2}p/{s2}s). (Step Cost: {step_cost_r:.1f} attempts)"

        self.cost_map[(p_target, s_target)] = (best_r_cost, best_path)

def calculate_recombination_outcomes(desired_p, max_p, desired_s, max_s):
    """The Strategy Presenter."""
    cost_gen = CostMapGenerator()
    plans = []
    p_goal, s_goal = desired_p, desired_s # Focusing on exact goal as requested

    # --- Strategy 1: Find Cheapest Standard Path from Planner ---
    cost_r, path = cost_gen.get_cost(p_goal, s_goal)
    if cost_r != float('inf') and cost_r > 0:
        explanation = f"The dynamic planner found the cheapest standard path is to:\n{path}"
        plans.append({"name": f"Standard Plan for {p_goal}p/{s_goal}s", "cost": cost_r, "exclusive_cost": 0, "explanation": explanation})

    # --- Strategy 2: Doubled Modifier ---
    if p_goal == 3:
        cost2p_r, _ = cost_gen.get_cost(2, s_goal)
        if cost2p_r != float('inf'):
            p_success = 0.31
            step_cost_r = 1 / p_success
            total_r = cost2p_r * 2 + step_cost_r
            explanation = f"1. Create two {2}p/{s_goal}s items, sharing one prefix (Est. cost for both: {cost2p_r*2:.1f} attempts).\n2. Combine them. (Final Step Cost: {step_cost_r:.1f} attempts)"
            plans.append({"name": "Doubled Prefix Strategy", "cost": total_r, "exclusive_cost": 0, "explanation": explanation})

    # --- Strategy 3: Exclusive Mods ---
    if p_goal == 3:
        cost2p_r, _ = cost_gen.get_cost(2, s_goal)
        cost1p_r, _ = cost_gen.get_cost(1, s_goal)
        if cost2p_r != float('inf') and cost1p_r != float('inf'):
            p_success = 0.36
            step_cost_r = 1 / p_success
            step_cost_e = 3
            total_r = cost2p_r + cost1p_r + step_cost_r
            explanation = f"1. Create a {2}p/{s_goal}s item (Est. cost: {cost2p_r:.1f} attempts).\n2. Create a {1}p/{s_goal}s item (Est. cost: {cost1p_r:.1f} attempts).\n3. Add {step_cost_e} exclusive mods and combine. (Final Step Cost: {step_cost_r:.1f} attempts)"
            plans.append({"name": "Exclusive Mod Strategy", "cost": total_r, "exclusive_cost": step_cost_e, "explanation": explanation})

    unique_plans = {plan['name']: plan for plan in plans}
    sorted_plans = sorted(unique_plans.values(), key=lambda x: x['cost'])
    return sorted_plans[:5]
