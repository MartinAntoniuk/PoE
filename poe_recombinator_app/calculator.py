import math
from itertools import product

# Table 1 from the Reddit post: Conditional final affix number distributions.
# Format: {total_affixes: {final_mods: chance}}
PROBABILITY_TABLE = {
    1: {0: 0.41, 1: 0.59, 2: 0.0, 3: 0.0},
    2: {0: 0.0, 1: 0.67, 2: 0.33, 3: 0.0},
    3: {0: 0.0, 1: 0.39, 2: 0.52, 3: 0.10},
    4: {0: 0.0, 1: 0.11, 2: 0.59, 3: 0.31},
    5: {0: 0.0, 1: 0.0, 2: 0.43, 3: 0.57},
    6: {0: 0.0, 1: 0.0, 2: 0.28, 3: 0.72},
}

def get_outcome_distribution(total_affixes):
    """
    Returns the probability distribution for the number of final affixes
    given the total number of affixes in the pool.
    """
    if total_affixes > 6:
        total_affixes = 6 # The table caps at 6
    return PROBABILITY_TABLE.get(total_affixes, {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0})

def nCr_exact(n, r):
    """
    Exact combination formula to avoid floating point issues.
    """
    if r < 0 or r > n:
        return 0
    return math.factorial(n) // math.factorial(r) // math.factorial(n - r)


def find_best_crafting_options(desired_prefixes, max_suffixes):
    """
    Finds the top 5 best crafting options.
    """
    options = []

    # Strategy 1: The "Exclusive Mod Shenanigans" strategy. This is almost always the best.
    if desired_prefixes == 3:
        total_p_shenanigans = 6
        prob_p_dist = get_outcome_distribution(total_p_shenanigans)
        chance_3p = prob_p_dist.get(3, 0.0)
        final_chance = 0.5 * chance_3p

        options.append({
            "chance": final_chance,
            "explanation": (
                f"Strategy: Exclusive Mod Shenanigans for 3 Prefixes (Highest Success Chance)\n\n"
                "This is the most effective but also most complex strategy. It involves using crafted 'exclusive' mods to guarantee the outcome.\n\n"
                "**How to do it:**\n"
                "1. **Item A (2 Prefixes):** Get an item with two of your desired prefixes. Craft a 'named' exclusive prefix.\n"
                "2. **Item B (1 Prefix):** Get an item with your third desired prefix. Craft 'Can have multiple crafted modifiers' and then two more 'named' exclusive prefixes.\n"
                "3. **Suffixes:** On both items, have the suffixes you want, but also add an exclusive suffix to one of them (e.g., an Aspect craft).\n\n"
                "**Why it works:**\n"
                "This creates a large pool of prefixes (3 desired + 3 exclusive = 6 total), which gives a ~72% chance to result in an item with 3 prefixes. By having an exclusive suffix, there's a 50% chance the recombinator processes suffixes first. If it picks the exclusive suffix, all other exclusive mods are removed from the pool. This leaves only your 3 desired prefixes, which are then guaranteed.\n\n"
                f"Calculation: 0.5 (chance to process suffixes first) * {chance_3p:.2%} (chance for 3 prefixes from 6 total) = {final_chance:.2%}"
            )
        })

    if desired_prefixes == 2:
        # For 2 prefixes, we can aim for a pool of 4 or 5 total prefixes.
        # Let's use 5 total prefixes: 2 desired, 3 exclusive.
        total_p_shenanigans = 5
        prob_p_dist = get_outcome_distribution(total_p_shenanigans)
        chance_2p = prob_p_dist.get(2, 0.0)
        # We also need to account for the chance of getting 3 prefixes, which would be a failure.
        # In the shenanigans setup, if we get 3 prefixes, one of them must be one of our desired ones,
        # so it's not a total failure, but let's stick to the main goal.

        final_chance = 0.5 * chance_2p

        options.append({
            "chance": final_chance,
            "explanation": (
                f"Strategy: Exclusive Mod Shenanigans for 2 Prefixes\n\n"
                "This strategy uses exclusive mods to improve the odds of getting your two desired prefixes.\n\n"
                "**How to do it:**\n"
                "1. **Item A (1 Prefix):** Get an item with one of your desired prefixes. Craft a 'named' exclusive prefix.\n"
                "2. **Item B (1 Prefix):** Get an item with your other desired prefix. Craft 'Can have multiple crafted modifiers' and then two more 'named' exclusive prefixes.\n"
                "3. **Suffixes:** Add an exclusive suffix to one of the items.\n\n"
                "**Why it works:**\n"
                "This creates a pool of 5 prefixes (2 desired + 3 exclusive). This gives a {chance_2p:.2%} chance of a 2-prefix outcome. The exclusive suffix trick gives a 50% chance to force the outcome to only consider your desired prefixes.\n\n"
                f"Calculation: 0.5 * {chance_2p:.2%} = {final_chance:.2%}"
            )
        })


    # Strategy 2: Simpler, non-exclusive mod strategies.
    for p1, s1, p2, s2 in product(range(1, 4), range(0, 4), range(1, 4), range(0, 4)):
        if p1 + p2 > 6 or s1 + s2 > 6:
            continue

        # We need to have the desired prefixes on the input items.
        if p1 + p2 < desired_prefixes:
            continue

        total_p = p1 + p2
        total_s = s1 + s2

        p_dist = get_outcome_distribution(total_p)
        s_dist = get_outcome_distribution(total_s)

        prob_p = p_dist.get(desired_prefixes, 0.0)
        prob_s = sum(s_dist.get(s, 0.0) for s in range(max_suffixes + 1))

        mod_selection_chance = nCr_exact(p1, p1) * nCr_exact(p2, desired_prefixes - p1) / nCr_exact(total_p, desired_prefixes) if total_p >= desired_prefixes and p1 <= desired_prefixes else 0

        final_prob = prob_p * prob_s * mod_selection_chance

        if final_prob > 0.001: # Filter out very low probability options
            options.append({
                "chance": final_prob,
                "explanation": (
                    f"Strategy: Simple Combination\n\n"
                    f"Item 1: {p1} prefixes, {s1} suffixes\n"
                    f"Item 2: {p2} prefixes, {s2} suffixes\n\n"
                    f"This assumes you have your {desired_prefixes} desired prefixes distributed between the two items.\n"
                    f"Total prefixes in pool: {total_p}. Total suffixes: {total_s}\n"
                    f"Chance to get {desired_prefixes} prefixes: {prob_p:.2%}\n"
                    f"Chance to get <= {max_suffixes} suffixes: {prob_s:.2%}\n"
                    f"Chance to select the correct prefixes (heuristic): {mod_selection_chance:.2%}\n\n"
                    "This is a more straightforward approach but generally has a lower chance of success because it relies on luck to pick the correct modifiers from the pool."
                )
            })

    # Sort options by chance and return the top 5
    sorted_options = sorted(options, key=lambda x: x['chance'], reverse=True)
    return sorted_options[:5]


def calculate_recombination_outcomes(desired_prefixes, max_suffixes):
    """
    This function now calls the new find_best_crafting_options function.
    """
    return find_best_crafting_options(desired_prefixes, max_suffixes)
