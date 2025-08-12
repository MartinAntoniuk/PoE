import math

PROBABILITY_TABLE = {
    1: {0: 0.41, 1: 0.59, 2: 0.0, 3: 0.0},
    2: {0: 0.0, 1: 0.67, 2: 0.33, 3: 0.0},
    3: {0: 0.0, 1: 0.39, 2: 0.52, 3: 0.10},
    4: {0: 0.0, 1: 0.11, 2: 0.59, 3: 0.31},
    5: {0: 0.0, 1: 0.0, 2: 0.43, 3: 0.57},
    6: {0: 0.0, 1: 0.0, 2: 0.28, 3: 0.72},
}

def get_outcome_distribution(total_affixes):
    if total_affixes > 6: total_affixes = 6
    return PROBABILITY_TABLE.get(total_affixes, {0:0, 1:0, 2:0, 3:0})

def get_expected_attempts(p_success):
    if p_success == 0: return float('inf')
    return 1 / p_success

def calculate_recombination_outcomes(desired_prefixes, max_prefixes, desired_suffixes, max_suffixes):
    """
    This function finds the best crafting plans to achieve the desired outcome.
    A plan is a series of steps, where each step is a recombination.
    The cost of a plan is measured in the expected number of recombinations.
    """
    plans = []

    # --- Plans for 3 Prefixes ---
    if desired_prefixes <= 3 <= max_prefixes:
        # --- Plan 1: Exclusive Mod Strategy ---
        # Step 1: Make a 2p item {A, B}
        p_step1 = get_outcome_distribution(2).get(2, 0) # 0.33
        attempts_step1 = get_expected_attempts(p_step1)
        step1_desc = f"1. Create Item A (2 prefixes {{A, B}}):\n   - Combine a magic item {{A}} and a magic item {{B}}.\n   - Success Chance: {p_step1:.0%}. Expected Attempts: {attempts_step1:.1f}"

        # Step 2: Final Combine
        # Pool of 6p -> 72% for 3p result. 50% chance to force via exclusive suffix.
        p_step2 = 0.72 * 0.5
        attempts_step2 = get_expected_attempts(p_step2)
        step2_desc = f"2. Final Combination:\n   - Prepare Item A with an exclusive prefix, and a 1-prefix item {{C}} with multimod + exclusive prefixes.\n   - Combine them. Success Chance: {p_step2:.1%}. Expected Attempts: {attempts_step2:.1f}"

        total_attempts_exclusive = attempts_step1 + attempts_step2
        explanation_exclusive = f"{step1_desc}\n\n{step2_desc}\n\nTotal Expected Attempts: ~{total_attempts_exclusive:.1f}"
        plans.append({
            "name": "3-Prefix Exclusive Mod Craft",
            "chance": p_step2, # Chance of the final step
            "cost": total_attempts_exclusive,
            "explanation": explanation_exclusive
        })

        # --- Plan 2: Doubled Modifier Strategy ---
        # Step 1: Make item {A, B} (same as above)
        # Step 2: Make item {B, C}
        p_step2_doubled = get_outcome_distribution(2).get(2, 0) # 0.33
        attempts_step2_doubled = get_expected_attempts(p_step2_doubled)
        step2_desc_doubled = f"2. Create Item B (2 prefixes {{B, C}}):\n   - Combine a magic item {{B}} and a magic item {{C}}.\n   - Success Chance: {p_step2_doubled:.0%}. Expected Attempts: {attempts_step2_doubled:.1f}"

        # Step 3: Final Combine
        # Pool of 4p {A,B,B,C}. 31% for 3p. 100% chance of correct mods (as per user feedback).
        p_step3_doubled = get_outcome_distribution(4).get(3, 0) # 0.31
        attempts_step3_doubled = get_expected_attempts(p_step3_doubled)
        step3_desc_doubled = f"3. Final Combination:\n   - Combine item {{A, B}} and item {{B, C}}.\n   - Success Chance: {p_step3_doubled:.1%}. Expected Attempts: {attempts_step3_doubled:.1f}"

        total_attempts_doubled = attempts_step1 + attempts_step2_doubled + attempts_step3_doubled
        explanation_doubled = f"{step1_desc}\n\n{step2_desc_doubled}\n\n{step3_desc_doubled}\n\nTotal Expected Attempts: ~{total_attempts_doubled:.1f}"
        plans.append({
            "name": "3-Prefix Doubled Modifier Craft",
            "chance": p_step3_doubled,
            "cost": total_attempts_doubled,
            "explanation": explanation_doubled
        })

        # --- Plan 3: 2p + 1p Strategy ---
        # Step 1: Make item {A, B} (same as above)
        # Step 2: Final combine
        p_step2_2p1p = get_outcome_distribution(3).get(3, 0) # 0.10
        attempts_step2_2p1p = get_expected_attempts(p_step2_2p1p)
        step2_desc_2p1p = f"2. Final Combination:\n   - Combine item {{A, B}} and a magic item {{C}}.\n   - Success Chance: {p_step2_2p1p:.1%}. Expected Attempts: {attempts_step2_2p1p:.1f}"

        total_attempts_2p1p = attempts_step1 + attempts_step2_2p1p
        explanation_2p1p = f"{step1_desc}\n\n{step2_desc_2p1p}\n\nTotal Expected Attempts: ~{total_attempts_2p1p:.1f}"
        plans.append({
            "name": "3-Prefix 2p+1p Craft",
            "chance": p_step2_2p1p,
            "cost": total_attempts_2p1p,
            "explanation": explanation_2p1p
        })

    # Sort plans by their total cost (expected attempts)
    sorted_plans = sorted(plans, key=lambda x: x['cost'])

    # Rename 'chance' to 'final_step_chance' for clarity in the output
    for plan in sorted_plans:
        plan['final_step_chance'] = plan.pop('chance')

    return sorted_plans[:5]
