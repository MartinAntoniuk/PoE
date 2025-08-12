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
        # Exclusive Mod Strategy
        explanation_exclusive = (
            "Strategy: Exclusive Mod Crafting for 3 Prefixes\n\n"
            "This is the most reliable method. It uses crafted mods to force the outcome.\n\n"
            "**Step 1: Create Item A (2 desired prefixes)**\n"
            "   - Combine two magic items with prefixes {A} and {B}. 33% chance for a 2-prefix item {A, B}. Expected attempts: ~3.\n\n"
            "**Step 2: Get Item B (1 desired prefix)**\n"
            "   - A magic item with prefix {C}.\n\n"
            "**Step 3: Prepare for Final Combine**\n"
            "   - On Item A (2p): Add an exclusive crafted prefix.\n"
            "   - On Item B (1p): Add 'Multimod' + two exclusive crafted prefixes.\n"
            "   - Add an exclusive suffix (e.g., Aspect) to one item.\n\n"
            "**Step 4: The Final Combination**\n"
            "   - Combine Item A (now 3p) and Item B (now 3p/1s+).\n"
            "   - Total prefix pool is 6 -> 72% chance of 3 prefixes.\n"
            "   - The exclusive suffix trick gives a 50% chance to guarantee your 3 prefixes.\n"
            "   - Final success chance: 0.5 * 0.72 = 36%."
        )
        options.append({"chance": 0.36, "explanation": explanation_exclusive, "name": "3-Prefix Exclusive Mod Craft"})

        # Doubled Modifier Strategy
        explanation_doubled = (
            "Strategy: Doubled Modifier Crafting for 3 Prefixes\n\n"
            "This method avoids exclusive mods by 'doubling up' on a common prefix.\n\n"
            "**Step 1: Create Item A (prefixes A, B)**\n"
            "   - Combine a magic item with prefix {A} and another with prefix {B}.\n"
            "   - 33% chance for a 2-prefix item {A, B}. Expected attempts: ~3.\n\n"
            "**Step 2: Create Item B (prefixes B, C)**\n"
            "   - Combine a magic item with prefix {B} and another with prefix {C}.\n"
            "   - 33% chance for a 2-prefix item {B, C}. Expected attempts: ~3.\n\n"
            "**Step 3: The Final Combination**\n"
            "   - Combine Item A {A, B} and Item B {B, C}.\n"
            "   - Total prefix pool is 4: {A, B, B, C}.\n"
            "   - Chance of a 3-prefix result: 31%.\n"
            "   - Chance of selecting {A, B, C} from the pool is 50%.\n"
            "   - Final success chance: 0.31 * 0.50 = 15.5%."
        )
        options.append({"chance": 0.155, "explanation": explanation_doubled, "name": "3-Prefix Doubled Modifier Craft"})

        # 2p + 1p Strategy
        explanation_2p1p = (
            "Strategy: 2-Prefix + 1-Prefix Combine\n\n"
            "A simpler, but less effective, method than doubling modifiers.\n\n"
            "**Step 1: Create Item A (prefixes A, B)**\n"
            "   - Combine a magic item with prefix {A} and another with prefix {B}.\n"
            "   - 33% chance for a 2-prefix item {A, B}. Expected attempts: ~3.\n\n"
            "**Step 2: Get Item B (prefix C)**\n"
            "   - Get a magic item with only prefix {C}.\n\n"
            "**Step 3: The Final Combination**\n"
            "   - Combine Item A {A, B} and Item B {C}.\n"
            "   - Total prefix pool is 3: {A, B, C}.\n"
            "   - Chance of a 3-prefix result: 10%.\n"
            "   - If you get 3 prefixes, they are guaranteed to be {A, B, C}."
        )
        options.append({"chance": 0.10, "explanation": explanation_2p1p, "name": "3-Prefix 2p+1p Craft"})

        # Naive Strategy for comparison
        explanation_simple = (
            "Strategy: Simple 3p+3p Combine (Low Success)\n\n"
            "**Step 1: Create two 3-prefix items.** (Very difficult).\n"
            "**Step 2: Combine them.**\n"
            "   - Total prefix pool is 6 -> 72% chance of 3 prefixes.\n"
            "   - Chance of selecting the correct 3 from 6 is 1/nCr(6,3) = 5%.\n"
            "   - Total chance: 0.72 * 0.05 = 3.6%."
        )
        options.append({"chance": 0.036, "explanation": explanation_simple, "name": "3-Prefix Naive Combine"})


    # --- Strategy for 2 Prefixes ---
    if desired_prefixes <= 2 <= max_prefixes:
        explanation = (
            "Strategy: Simple Combine for 2 Prefixes\n\n"
            "**Step 1: Get two 1-prefix items.**\n"
            "   - Get two magic items, each with one of your desired prefixes.\n\n"
            "**Step 2: Combine them.**\n"
            "   - Combine the two 1p/0s items. Total prefix pool is 2.\n"
            "   - This gives a 33% chance of a 2-prefix result, which are guaranteed to be the ones you want."
        )
        options.append({"chance": 0.33, "explanation": explanation, "name": "2-Prefix Simple Combine"})

    # --- Strategy for 1 Prefix ---
    if desired_prefixes <= 1 <= max_prefixes:
        explanation = (
            "Strategy: Use a 1-Prefix Item (No Recombinator Needed)\n\n"
            "Use Alteration Orbs on a magic item until you hit the prefix you want."
        )
        options.append({"chance": 0.99, "explanation": explanation, "name": "1-Prefix Alteration Spam"})

    # Filter out duplicate strategies and sort
    unique_options = {opt['name']: opt for opt in options}
    sorted_options = sorted(unique_options.values(), key=lambda x: x['chance'], reverse=True)

    return sorted_options[:5]


def calculate_recombination_outcomes(desired_prefixes, max_prefixes, desired_suffixes, max_suffixes):
    return find_best_crafting_options(desired_prefixes, max_prefixes, desired_suffixes, max_suffixes)
