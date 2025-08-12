import math
from itertools import product

PROBABILITY_TABLE = {
    1: {0: 0.41, 1: 0.59}, 2: {1: 0.67, 2: 0.33}, 3: {1: 0.39, 2: 0.52, 3: 0.10},
    4: {1: 0.11, 2: 0.59, 3: 0.31}, 5: {2: 0.43, 3: 0.57}, 6: {2: 0.28, 3: 0.72},
}

def get_outcome_distribution(total_affixes):
    if total_affixes > 6: total_affixes = 6
    return PROBABILITY_TABLE.get(total_affixes, {})

def nCr_exact(n, r):
    if r < 0 or r > n: return 0
    return math.factorial(n) // math.factorial(r) // math.factorial(n - r)

class CraftingPlanner:
    def __init__(self):
        # cost_map stores: {(p, s): (recomb_cost, exclusive_cost, explanation_path)}
        self.cost_map = {}
        self.build_cost_map()

    def get_cost(self, p, s):
        return self.cost_map.get((p, s), (float('inf'), float('inf'), "N/A"))

    def build_cost_map(self):
        self.cost_map[(0, 0)] = (0, 0, "Start with a normal item.")
        self.cost_map[(1, 0)] = (0, 0, "Start with a 1-prefix magic item.")
        self.cost_map[(0, 1)] = (0, 0, "Start with a 1-suffix magic item.")
        self.cost_map[(1, 1)] = (0.25, 0, "Use a Regal Orb on a 1-affix item.")

        for p in range(4):
            for s in range(4):
                if (p, s) in self.cost_map: continue
                self.compute_best_combination_for(p, s)

    def compute_best_combination_for(self, p_target, s_target):
        # This is the core of the dynamic planner.
        # It finds the cheapest way to make a (p_target, s_target) item.
        if (p_target, s_target) in self.cost_map: return

        best_r_cost, best_e_cost, best_path = float('inf'), float('inf'), "No path found"

        # Strategy 1: Simple Combination
        for p1 in range(p_target + 1):
            for s1 in range(s_target + 1):
                if p1 > p_target - p1 or (p1 == p_target - p1 and s1 > s_target - s1): continue
                p2, s2 = p_target - p1, s_target - s1
                cost1_r, cost1_e, path1 = self.get_cost(p1, s1)
                cost2_r, cost2_e, path2 = self.get_cost(p2, s2)
                if cost1_r == float('inf') or cost2_r == float('inf'): continue

                total_p, total_s = p1 + p2, s1 + s2
                if total_p > 6 or total_s > 6 or (total_p==0 and total_s==0): continue

                p_dist = get_outcome_distribution(total_p)
                s_dist = get_outcome_distribution(total_s)

                # Simplified success - assumes if numbers are right, mods are right.
                # This is a limitation, but a full mod-aware simulation is too complex.
                prob_p = p_dist.get(p_target, 0)
                prob_s = s_dist.get(s_target, 0) if s_target > 0 else (1 if total_s == 0 else (1 - sum(s_dist.values())))
                p_success = prob_p * prob_s if p_target > 0 and s_target > 0 else (prob_p or prob_s)

                if p_success > 0:
                    step_cost_r = 1 / p_success
                    total_r, total_e = cost1_r + cost2_r + step_cost_r, cost1_e + cost2_e
                    if total_r < best_r_cost:
                        best_r_cost, best_e_cost = total_r, total_e
                        best_path = f"Combine a {p1}p/{s1}s item and a {p2}p/{s2}s item ({step_cost_r:.1f} attempts)."

        # Strategy 2: Doubled Modifier (for 3-prefix items)
        if p_target == 3 and s_target == 0:
            cost2p_r, cost2p_e, _ = self.get_cost(2, 0)
            if cost2p_r != float('inf'):
                p_success = 0.31 # From our previous analysis
                step_cost_r = 1 / p_success
                total_r = cost2p_r * 2 + step_cost_r # Need two 2p items
                total_e = cost2p_e * 2
                if total_r < best_r_cost:
                    best_r_cost, best_e_cost = total_r, total_e
                    best_path = f"Create two 2p items and combine them (doubling one prefix). Step cost: {step_cost_r:.1f} attempts."

        self.cost_map[(p_target, s_target)] = (best_r_cost, best_e_cost, best_path)

    def find_top_plans(self, desired_p, max_p, desired_s, max_s):
        plans = []
        # This function now needs to be much smarter. It should check the final step,
        # including special strategies like exclusive mods.
        for p_target in range(desired_p, max_p + 1):
            for s_target in range(desired_s, max_s + 1):
                if p_target == 0 and s_target == 0: continue

                # Path 1: The pre-calculated cheapest path from the cost map
                cost_r, cost_e, path = self.get_cost(p_target, s_target)
                if cost_r != float('inf'):
                    plans.append({
                        "name": f"Standard Plan for {p_target}p/{s_target}s",
                        "cost": cost_r, "exclusive_cost": cost_e,
                        "explanation": f"The cheapest standard way to build a {p_target}p/{s_target}s item.\nFull Path:\n{path}"
                    })

                # Path 2: Exclusive Mod strategy (for 3 prefixes)
                if p_target == 3:
                    cost2p_r, cost2p_e, _ = self.get_cost(2, 0)
                    cost1p_r, cost1p_e, _ = self.get_cost(1, 0)
                    if cost2p_r != float('inf'):
                        p_success = 0.36 # 72% * 50%
                        step_cost_r = 1 / p_success
                        step_cost_e = 3 # 1 on 2p item, 2 on 1p item

                        total_r = cost2p_r + cost1p_r + step_cost_r
                        total_e = cost2p_e + cost1p_e + step_cost_e

                        plans.append({
                            "name": f"Exclusive Mod Plan for 3p",
                            "cost": total_r, "exclusive_cost": total_e,
                            "explanation": f"Use exclusive mods on a 2p and 1p item to force the outcome. (Final step cost: {step_cost_r:.1f} recombs, {step_cost_e} exclusives)."
                        })

        # De-duplicate and sort plans
        unique_plans = {}
        for plan in plans:
            if plan['name'] not in unique_plans or plan['cost'] < unique_plans[plan['name']]['cost']:
                unique_plans[plan['name']] = plan

        sorted_plans = sorted(unique_plans.values(), key=lambda x: x['cost'])
        return sorted_plans[:5]

def calculate_recombination_outcomes(desired_prefixes, max_prefixes, desired_suffixes, max_suffixes):
    planner = CraftingPlanner()
    return planner.find_top_plans(desired_prefixes, max_prefixes, desired_suffixes, max_suffixes)
