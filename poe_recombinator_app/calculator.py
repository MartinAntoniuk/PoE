import math
from itertools import product

# Probability table remains the same
PROBABILITY_TABLE = {
    1: {0: 0.41, 1: 0.59, 2: 0.0, 3: 0.0},
    2: {0: 0.0, 1: 0.67, 2: 0.33, 3: 0.0},
    3: {0: 0.0, 1: 0.39, 2: 0.52, 3: 0.10},
    4: {0: 0.0, 1: 0.11, 2: 0.59, 3: 0.31},
    5: {0: 0.0, 1: 0.0, 2: 0.43, 3: 0.57},
    6: {0: 0.0, 1: 0.0, 2: 0.28, 3: 0.72},
}

def get_outcome_distribution(total_affixes):
    if total_affixes > 6:
        total_affixes = 6
    return PROBABILITY_TABLE.get(total_affixes, {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0})

def nCr_exact(n, r):
    if r < 0 or r > n: return 0
    return math.factorial(n) // math.factorial(r) // math.factorial(n - r)

def find_best_crafting_options(desired_prefixes, max_prefixes, desired_suffixes, max_suffixes):
    options = []

    # --- Strategy for 3 Prefixes ---
    if desired_prefixes <= 3 <= max_prefixes:
        explanation = (
            "Strategy: Exclusive Mod Crafting for 3 Prefixes\n\n"
            "This is the most reliable method to create a 3-prefix item.\n\n"
            "**Step 1: Create Item A (2 desired prefixes)**\n"
            "   - Combine two magic items, one with each of your first two desired prefixes.\n"
            "   - This has a 33% chance to result in a 2-prefix item. Expected attempts: ~3.\n\n"
            "**Step 2: Get Item B (1 desired prefix)**\n"
            "   - This is a magic item with your third desired prefix.\n\n"
            "**Step 3: Prepare for Final Combine**\n"
            "   - On Item A (2p): Add an exclusive crafted prefix (e.g., 'Chosen').\n"
            "   - On Item B (1p): Add 'Multimod', then two exclusive crafted prefixes.\n"
            "   - Add an exclusive suffix (e.g., Aspect) to one item for control.\n\n"
            "**Step 4: The Final Combination**\n"
            "   - Combine Item A (now 3p) and Item B (now 3p/1s+).\n"
            "   - Total prefix pool is 6, giving a 72% chance of a 3-prefix result.\n"
            "   - The exclusive suffix gives a 50% chance to force the outcome, guaranteeing your 3 desired prefixes.\n"
            "   - Final success chance for this step: 0.5 * 0.72 = 36%."
        )
        options.append({"chance": 0.36, "explanation": explanation, "name": "3-Prefix Exclusive Mod Craft"})

    # --- Strategy for 2 Prefixes ---
    if desired_prefixes <= 2 <= max_prefixes:
        explanation = (
            "Strategy: Simple Combine for 2 Prefixes\n\n"
            "This is the most straightforward way to get a 2-prefix item.\n\n"
            "**Step 1: Get two 1-prefix items.**\n"
            "   - Get two magic items, each with one of your desired prefixes.\n\n"
            "**Step 2: Combine them.**\n"
            "   - Combine the two 1p/0s items.\n"
            "   - The total prefix pool is 2. This gives a 33% chance of a 2-prefix result.\n"
            "   - Since there are only two prefixes in the pool, you are guaranteed to get the ones you want if the 2-prefix result occurs.\n\n"
            "**Suffix Outcome:**\n"
            "   - If you start with 0 suffixes on both items, the resulting item will also have 0 suffixes."
        )
        options.append({"chance": 0.33, "explanation": explanation, "name": "2-Prefix Simple Combine"})

    # --- Strategy for 1 Prefix ---
    if desired_prefixes <= 1 <= max_prefixes:
        explanation = (
            "Strategy: Use a 1-Prefix Item\n\n"
            "To get a 1-prefix item, you don't need to use a recombinator. You can simply:\n\n"
            "1. Use an Orb of Transmutation on a normal (white) item to make it magic.\n"
            "2. If it has a prefix you want, you are done. If it has a suffix, you can use an Orb of Augmentation to add a prefix.\n"
            "3. Use Alteration Orbs until you hit the prefix you want.\n\n"
            "This process has a very high chance of success and is very cheap."
        )
        options.append({"chance": 0.99, "explanation": explanation, "name": "1-Prefix Alteration Spam"})

    # --- Fallback / Comparison Strategy ---
    explanation_simple = (
        "Strategy: Simple 3p+3p Combine (Low Success)\n\n"
        "This is a less effective but simpler method to illustrate the power of exclusive mods.\n\n"
        "**Step 1: Create two 3-prefix items.** (This is very difficult).\n"
        "**Step 2: Combine them.**\n"
        "   - Total prefix pool is 6. Chance of 3 prefixes is 72%.\n"
        "   - Chance of selecting your 3 desired prefixes from the pool of 6 is 1/nCr(6,3) = 5%.\n"
        "   - Total chance: 0.72 * 0.05 = 3.6%."
    )
    if desired_prefixes == 3:
      options.append({"chance": 0.036, "explanation": explanation_simple, "name": "3-Prefix Naive Combine"})

    # Filter out duplicate strategies and sort
    unique_options = {opt['name']: opt for opt in options}
    sorted_options = sorted(unique_options.values(), key=lambda x: x['chance'], reverse=True)

    return sorted_options[:5]


def calculate_recombination_outcomes(desired_prefixes, max_prefixes, desired_suffixes, max_suffixes):
    return find_best_crafting_options(desired_prefixes, max_prefixes, desired_suffixes, max_suffixes)
