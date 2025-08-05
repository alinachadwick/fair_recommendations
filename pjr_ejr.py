from itertools import combinations
from typing import List, Set, Tuple, Dict
from collections import defaultdict

def precompute_voter_groups(voters: List[Set[int]], n: int, k: int) -> Dict[Tuple[int, int], List[Tuple]]:
    """
    Precompute relevant voter groups and their common candidates.
    
    Returns:
        Dictionary mapping (ell, group_size) to list of (voter_indices, common_candidates)
    """
    voter_groups = defaultdict(list)
    
    for ell in range(1, k + 1):
        quota = (ell * n) // k
        
        for group_size in range(quota, n + 1):
            for voter_indices in combinations(range(n), group_size):
                # Find common candidates
                common_candidates = set.intersection(*[voters[i] for i in voter_indices])
                
                # Only store groups that have at least ell common candidates
                if len(common_candidates) >= ell:
                    voter_groups[(ell, group_size)].append((voter_indices, common_candidates))
    
    return voter_groups

def check_pjr_optimized(committee: Set[int], voter_groups: Dict[Tuple[int, int], List[Tuple]], n: int, k: int) -> bool:
    """
    Check if a committee satisfies PJR using precomputed voter groups.
    """
    for ell in range(1, k + 1):
        quota = (ell * n) // k
        for group_size in range(quota, n + 1):
            key = (ell, group_size)
            if key in voter_groups:
                for voter_indices, common_candidates in voter_groups[key]:
                    # Check if committee contains at least ell of the common candidates
                    if len(common_candidates.intersection(committee)) < ell:
                        return False
    return True

def find_pjr_committees_optimized(voters: List[Set[int]], k: int, candidates: Set[int] = None) -> List[Set[int]]:
    """
    Optimized version of PJR committee finding.
    """
    # Extract all candidates if not provided
    if candidates is None:
        candidates = set()
        for voter_prefs in voters:
            candidates.update(voter_prefs)
    
    n = len(voters)
    
    # Optimization 1: Precompute voter groups and their common candidates
    voter_groups = precompute_voter_groups(voters, n, k)
    
    # Optimization 2: Early termination - if no valid groups exist, all committees are PJR
    if not any(voter_groups.values()):
        return [set(committee) for committee in combinations(candidates, k)]
    
    # Optimization 3: Candidate filtering - only consider candidates that appear in voter preferences
    relevant_candidates = set()
    for voter_prefs in voters:
        relevant_candidates.update(voter_prefs)
    candidates = candidates.intersection(relevant_candidates)
    
    pjr_committees = []
    
    # Try all possible committees
    for committee in combinations(candidates, k):
        committee_set = set(committee)
        if check_pjr_optimized(committee_set, voter_groups, n, k):
            pjr_committees.append(committee_set)
    
    return pjr_committees

def find_pjr_committees_with_pruning(voters: List[Set[int]], k: int, candidates: Set[int] = None) -> List[Set[int]]:
    """
    Version with additional pruning strategies.
    """
    if candidates is None:
        candidates = set()
        for voter_prefs in voters:
            candidates.update(voter_prefs)
    
    n = len(voters)
    
    # Calculate candidate support (how many voters approve each candidate)
    candidate_support = defaultdict(int)
    for voter_prefs in voters:
        for candidate in voter_prefs:
            candidate_support[candidate] += 1
    
    # Sort candidates by support (heuristic: popular candidates more likely to be in PJR committees)
    sorted_candidates = sorted(candidates, key=lambda c: candidate_support[c], reverse=True)
    
    # Precompute critical voter groups
    critical_groups = []
    for ell in range(1, k + 1):
        quota = (ell * n) // k
        
        # Find minimal voter groups that could violate PJR
        for group_size in range(quota, min(quota + k, n + 1)):  # Limit search space
            for voter_indices in combinations(range(n), group_size):
                common_candidates = set.intersection(*[voters[i] for i in voter_indices])
                if len(common_candidates) >= ell:
                    critical_groups.append((ell, voter_indices, common_candidates))
    
    pjr_committees = []
    
    # Generate committees with pruning
    def is_valid_partial(partial_committee: Set[int], remaining_slots: int) -> bool:
        """Check if a partial committee can possibly lead to a PJR committee."""
        for ell, voter_indices, common_candidates in critical_groups:
            current_intersection = len(common_candidates.intersection(partial_committee))
            remaining_candidates = common_candidates - partial_committee
            
            # If we can't possibly get enough representatives even with remaining slots
            if current_intersection + min(remaining_slots, len(remaining_candidates)) < ell:
                return False
        return True
    
    # Build committees incrementally with pruning
    def build_committee(current: Set[int], remaining: List[int], needed: int):
        if needed == 0:
            if check_pjr_from_critical_groups(current):
                pjr_committees.append(current.copy())
            return
        
        if not remaining or not is_valid_partial(current, needed):
            return
        
        # Try including the next candidate
        candidate = remaining[0]
        current.add(candidate)
        build_committee(current, remaining[1:], needed - 1)
        current.remove(candidate)
        
        # Try excluding the next candidate
        build_committee(current, remaining[1:], needed)
    
    def check_pjr_from_critical_groups(committee: Set[int]) -> bool:
        """Check PJR using only critical groups."""
        for ell, voter_indices, common_candidates in critical_groups:
            if len(common_candidates.intersection(committee)) < ell:
                return False
        return True
    
    build_committee(set(), sorted_candidates, k)
    
    return pjr_committees

# Example usage with timing
if __name__ == "__main__":
    import time
    
    # Add the original brute force function for comparison
    def check_pjr(voters: List[Set[int]], committee: Set[int], k: int) -> bool:
        n = len(voters)
        for ell in range(1, k + 1):
            quota = (ell * n) // k
            for group_size in range(quota, n + 1):
                for voter_group in combinations(range(n), group_size):
                    common_candidates = set.intersection(*[voters[i] for i in voter_group])
                    if len(common_candidates) >= ell:
                        if len(common_candidates.intersection(committee)) < ell:
                            return False
        return True
    
    def find_pjr_committees_brute_force(voters: List[Set[int]], k: int, candidates: Set[int] = None) -> List[Set[int]]:
        if candidates is None:
            candidates = set()
            for voter_prefs in voters:
                candidates.update(voter_prefs)
        pjr_committees = []
        for committee in combinations(candidates, k):
            committee_set = set(committee)
            if check_pjr(voters, committee_set, k):
                pjr_committees.append(committee_set)
        return pjr_committees
    
    # Test example
    voters = [
        {0, 5, 2, 6, 1, 7},
        {0, 3, 2, 9, 8 , 10},
        {0, 1, 3, 4, 2, 10},
        {3, 4, 6, 8, 5, 7},
        {3, 2, 5, 1, 0, 4},
        {3, 0, 4, 7, 1, 2}
    ]

    voters_2 = [
        # Group 1: Voters who like candidates 0,1,2 (minority coalition)
        {0, 1, 2},
        {0, 1, 2}, 
        {0, 1, 2},
        {0, 1},    # Partial overlap
        
        # Group 2: Voters who like candidates 3,4,5 (another minority)
        {3, 4, 5},
        {3, 4, 5},
        {3, 4},
        
        # Group 3: Voters who like candidates 6,7,8
        {6, 7, 8},
        {6, 7, 8},
        {6, 7},
        
        # Individual voters with specific preferences
        {9, 10},
        {11, 12},
        {13, 14},
        {15, 16},
        {17, 18, 19}  # Last voter likes high-numbered candidates
    ]

    k = 5
    
    # Time the original version
    start = time.time()
    original_result = find_pjr_committees_brute_force(voters, k)
    original_time = time.time() - start
    
    # Time the optimized version
    start = time.time()
    optimized_result = find_pjr_committees_optimized(voters, k)
    optimized_time = time.time() - start
    
    # Time the pruning version
    start = time.time()
    pruning_result = find_pjr_committees_with_pruning(voters, k)
    pruning_time = time.time() - start
    
    print(f"Original version: {len(original_result)} committees in {original_time:.4f}s")
    print(f"Optimized version: {len(optimized_result)} committees in {optimized_time:.4f}s")
    print(f"Pruning version: {len(pruning_result)} committees in {pruning_time:.4f}s")
    
    if original_time > 0:
        print(f"Speedup: {original_time/optimized_time:.2f}x (optimized), {original_time/pruning_time:.2f}x (pruning)")
    
    # Verify results are the same
    original_sorted = set(map(tuple, map(sorted, original_result)))
    optimized_sorted = set(map(tuple, map(sorted, optimized_result)))
    print(f"\nResults match: {original_sorted == optimized_sorted}")
    
    # Show the committees
    print("\nPJR Committees found:")
    for committee in sorted(optimized_result):
        print(f"  {sorted(committee)}")