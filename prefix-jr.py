# Alina Chadwick
# Prefix-JR (im)possibility simulations

import random

# input: preferences = {u1: [a1, a2, a3], u2: [a6, a7, a1], ...}
# output: ranking over alternatives that satisfies Prefix-JR if it exists

def get_approval_sets(preferences, k):
    approval_sets = {} # key = user, value = list of approved alternatives
    for user in preferences:
        ranking = preferences[user]
        approval_set = ranking[:k] # maybe make this a set maybe just treat it like a set
        approval_sets[user] = approval_set
    return approval_sets


def find_cohesive_groups(preferences, k):
    cohesive_groups = [] # list of cohesive sets
    approval_sets = get_approval_sets(preferences, k)
    n = len(approval_sets)
    min_size_needed = n / k
    num_approvals_dict = {}
    alternatives = set()
    for user in approval_sets:
        approved = approval_sets[user]
        for alt in approved:
            if alt not in alternatives:
                alternatives.add(alt)
            if alt not in num_approvals_dict:
                num_approvals_dict[alt] = [user]
            else:
                num_approvals_dict[alt].append(user)

    for alt in num_approvals_dict:
        approvals = num_approvals_dict[alt]
        if len(approvals) >= min_size_needed:
            approvals_set = set(approvals)
            cohesive_groups.append(approvals_set)
    
    return cohesive_groups, alternatives, approval_sets


def satisfies_jr(preferences, k):
    alts_to_explore = set()
    cohesive_groups, alternatives, approval_sets = find_cohesive_groups(preferences, k)
    # base case:
    if len(cohesive_groups) == 0:
        # randomly select alternative to go in that spot
        for alt in alternatives:
            alts_to_explore.add(alt)
        return alts_to_explore
    else:
        for group in cohesive_groups:
            for user in group:
                approvals = approval_sets[user]
                for approval in approvals:
                    alts_to_explore.add(approval)
    return alts_to_explore
        

def branch_all(partial_ranking, remaining_alts, preferences):
    k = len(partial_ranking) + 1

    if not remaining_alts:
        return [partial_ranking]  # base case: full ranking found

    valid_alts = satisfies_jr(preferences, k)
    valid_alts = valid_alts.intersection(remaining_alts)

    all_rankings = []
    for alt in valid_alts:
        next_partial = partial_ranking + [alt]
        next_remaining = remaining_alts - {alt}
        results = branch_all(next_partial, next_remaining, preferences)
        all_rankings.extend(results)
    
    return all_rankings

def find_all_prefix_jr_rankings(preferences):
    all_alts = set(alt for ranking in preferences.values() for alt in ranking)
    return branch_all([], all_alts, preferences)

preferences = {
    'u1': ['a1', 'a2', 'a3', 'a4', 'a5'],
    'u2': ['a1', 'a2', 'a4', 'a5', 'a3'],
    'u3': ['a1', 'a2', 'a5', 'a3', 'a4'],
    'u4': ['a3', 'a4', 'a5', 'a1', 'a2'],
    'u5': ['a3', 'a4', 'a5', 'a2', 'a1'],
}

ranking = find_all_prefix_jr_rankings(preferences)
print("Prefix-JR rankings found:", ranking)
    
# def generate_random_preferences(num_voters, num_alternatives, seed=None):
#     if seed is not None:
#         random.seed(seed)
    
#     alternatives = [f'a{i}' for i in range(1, num_alternatives + 1)]
#     preferences = {}
    
#     for voter in range(1, num_voters + 1):
#         prefs = alternatives[:]
#         random.shuffle(prefs)
#         preferences[f'u{voter}'] = prefs
    
#     return preferences

# prefs = generate_random_preferences(num_voters=10, num_alternatives=5, seed=42)
# for voter, ranking in prefs.items():
#     print(f"{voter}: {ranking}")

# # Try finding a Prefix-JR ranking
# ranking = find_prefix_jr_ranking(prefs)
# print("Prefix-JR Ranking:", ranking if ranking else "None exists!")
