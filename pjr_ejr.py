# PJR and EJR Implementation
# Proportional Justified Representation and Extended Justified Representation

import itertools
from typing import Dict, List, Set, Tuple

def check_jr(approvals: Dict[str, Set[str]], committee: Set[str], num_voters: int, committee_size: int) -> bool:
    """
    Check if a committee satisfies Justified Representation (JR).
    
    Args:
        approvals: Dict mapping voter_id -> set of approved candidates
        committee: Set of selected candidates
        num_voters: Total number of voters
        committee_size: Size of the committee
    
    Returns:
        True if JR is satisfied, False otherwise
    """
    quota = num_voters / committee_size
    
    # Find all cohesive groups
    candidates = set()
    for voter_approvals in approvals.values():
        candidates.update(voter_approvals)
    
    for candidate in candidates:
        # Find voters who approve this candidate
        supporters = set()
        for voter, voter_approvals in approvals.items():
            if candidate in voter_approvals:
                supporters.add(voter)
        
        # If this candidate has enough supporters to form a cohesive group
        if len(supporters) >= quota:
            # Check if any of their approved candidates are in the committee
            group_approvals = set()
            for voter in supporters:
                group_approvals.update(approvals[voter])
            
            if not (group_approvals & committee):
                return False  # This cohesive group has no representation
    
    return True


def check_pjr(approvals: Dict[str, Set[str]], committee: Set[str], num_voters: int, committee_size: int) -> bool:
    """
    Check if a committee satisfies Proportional Justified Representation (PJR).
    
    PJR requires that every group of i*quota voters gets at least i representatives.
    """
    quota = num_voters / committee_size
    
    # Find all possible cohesive groups
    candidates = set()
    for voter_approvals in approvals.values():
        candidates.update(voter_approvals)
    
    # Check all possible subsets of voters to find cohesive groups
    voters = list(approvals.keys())
    
    for i in range(1, committee_size + 1):
        min_group_size = i * quota
        
        # Find cohesive groups of size at least min_group_size
        for candidate in candidates:
            supporters = []
            for voter in voters:
                if candidate in approvals[voter]:
                    supporters.append(voter)
            
            if len(supporters) >= min_group_size:
                # This is a cohesive group that deserves i representatives
                # Find the union of all their approvals
                group_approvals = set()
                for voter in supporters:
                    group_approvals.update(approvals[voter])
                
                # Count how many of their approved candidates are in committee
                representation_count = len(group_approvals & committee)
                
                if representation_count < i:
                    return False
    
    return True


def check_ejr(approvals: Dict[str, Set[str]], committee: Set[str], num_voters: int, committee_size: int) -> bool:
    """
    Check if a committee satisfies Extended Justified Representation (EJR).
    """
    quota = num_voters / committee_size
    voters = list(approvals.keys())
    
    # For each possible number of deserved representatives
    for i in range(1, committee_size + 1):
        # Check all possible groups of voters
        for group_size in range(int(i * quota), num_voters + 1):
            for voter_group in itertools.combinations(voters, group_size):
                # Check if this group can be partitioned into i cohesive subgroups
                if can_partition_into_cohesive_subgroups(voter_group, approvals, i, quota):
                    # Find common approvals of this group
                    group_approvals = set()
                    for voter in voter_group:
                        if not group_approvals:
                            group_approvals = approvals[voter].copy()
                        else:
                            group_approvals &= approvals[voter]
                    
                    # If they have common approvals, check representation
                    if group_approvals:
                        representation_count = len(group_approvals & committee)
                        if representation_count < i:
                            return False
    
    return True


def can_partition_into_cohesive_subgroups(voters: Tuple[str], approvals: Dict[str, Set[str]], 
                                        num_subgroups: int, quota: float) -> bool:
    """
    Helper function to check if voters can be partitioned into cohesive subgroups.
    
    A cohesive subgroup is a set of voters who all approve at least one common candidate.
    We need to partition the voters into num_subgroups disjoint subgroups, each of size >= quota.
    """
    if len(voters) < num_subgroups * quota:
        return False
    
    min_subgroup_size = int(quota)
    voters_list = list(voters)
    
    # Try to find a valid partition using backtracking
    return _find_partition_recursive(voters_list, approvals, num_subgroups, min_subgroup_size, [], 0)


def _find_partition_recursive(remaining_voters: List[str], approvals: Dict[str, Set[str]], 
                            subgroups_needed: int, min_size: int, 
                            current_partition: List[List[str]], start_idx: int) -> bool:
    """
    Recursive helper to find a valid partition using backtracking.
    
    Args:
        remaining_voters: List of voters not yet assigned to subgroups
        approvals: Voter approval mappings
        subgroups_needed: Number of subgroups still needed
        min_size: Minimum size for each subgroup
        current_partition: Current partial partition being built
        start_idx: Starting index for generating combinations (to avoid duplicates)
    """
    # Base case: if we've found all needed subgroups
    if subgroups_needed == 0:
        return len(remaining_voters) == 0  # All voters should be assigned
    
    # If not enough voters left to form remaining subgroups
    if len(remaining_voters) < subgroups_needed * min_size:
        return False
    
    # Try different subgroup sizes (from min_size up to what's reasonable)
    max_reasonable_size = len(remaining_voters) - (subgroups_needed - 1) * min_size
    
    # Generate all possible subgroups of valid size
    for size in range(min_size, max_reasonable_size + 1):
        # Try all combinations of 'size' voters from remaining_voters
        for subgroup in itertools.combinations(remaining_voters, size):
            # Check if this subgroup is cohesive (has common approvals)
            if _is_cohesive_subgroup(subgroup, approvals):
                # Create new remaining voters list without this subgroup
                new_remaining = [v for v in remaining_voters if v not in subgroup]
                
                # Recursively try to partition the remaining voters
                new_partition = current_partition + [list(subgroup)]
                if _find_partition_recursive(new_remaining, approvals, subgroups_needed - 1, 
                                           min_size, new_partition, 0):
                    return True
    
    return False


def _is_cohesive_subgroup(voters: Tuple[str], approvals: Dict[str, Set[str]]) -> bool:
    """
    Check if a group of voters is cohesive (they have at least one commonly approved candidate).
    """
    if not voters:
        return False
    
    # Find intersection of all voters' approvals
    common_approvals = approvals[voters[0]].copy()
    for voter in voters[1:]:
        common_approvals &= approvals[voter]
    
    return len(common_approvals) > 0


def find_committees_satisfying_criterion(approvals: Dict[str, Set[str]], committee_size: int, 
                                       criterion: str = "jr") -> List[Set[str]]:
    """
    Find all committees of given size that satisfy the specified criterion.
    
    Args:
        approvals: Dict mapping voter_id -> set of approved candidates
        committee_size: Size of committee to select
        criterion: "jr", "pjr", or "ejr"
    
    Returns:
        List of committees (sets of candidates) satisfying the criterion
    """
    # Get all candidates
    candidates = set()
    for voter_approvals in approvals.values():
        candidates.update(voter_approvals)
    
    num_voters = len(approvals)
    valid_committees = []
    
    # Check all possible committees
    for committee in itertools.combinations(candidates, committee_size):
        committee_set = set(committee)
        
        if criterion == "jr":
            if check_jr(approvals, committee_set, num_voters, committee_size):
                valid_committees.append(committee_set)
        elif criterion == "pjr":
            if check_pjr(approvals, committee_set, num_voters, committee_size):
                valid_committees.append(committee_set)
        elif criterion == "ejr":
            if check_ejr(approvals, committee_set, num_voters, committee_size):
                valid_committees.append(committee_set)
    
    return valid_committees


def generate_example_approvals() -> Dict[str, Set[str]]:
    """Generate an example approval voting scenario."""
    return {
        'v1': {'a', 'b', 'c'},
        'v2': {'a', 'b', 'd'},
        'v3': {'a', 'c', 'd'},
        'v4': {'b', 'c', 'e'},
        'v5': {'d', 'e', 'f'},
        'v6': {'d', 'e', 'f'},
    }


def main():
    """Example usage of the PJR and EJR implementations."""
    print("=== PJR and EJR Implementation ===\n")
    
    # Generate example data
    approvals = generate_example_approvals()
    committee_size = 3
    
    print("Voter Approvals:")
    for voter, approved in approvals.items():
        print(f"  {voter}: {sorted(approved)}")
    print(f"\nCommittee size: {committee_size}")
    print(f"Number of voters: {len(approvals)}")
    print(f"Quota (n/k): {len(approvals)/committee_size:.2f}")
    
    # Find committees satisfying each criterion
    print("\n" + "="*50)
    
    for criterion in ["jr", "pjr", "ejr"]:
        print(f"\nCommittees satisfying {criterion.upper()}:")
        committees = find_committees_satisfying_criterion(approvals, committee_size, criterion)
        
        if committees:
            for i, committee in enumerate(committees, 1):
                print(f"  {i}. {sorted(committee)}")
        else:
            print("  None found!")
    
    # Test a specific committee
    print("\n" + "="*50)
    test_committee = {'a', 'b', 'd'}
    print(f"\nTesting committee {sorted(test_committee)}:")
    
    jr_result = check_jr(approvals, test_committee, len(approvals), committee_size)
    pjr_result = check_pjr(approvals, test_committee, len(approvals), committee_size)
    ejr_result = check_ejr(approvals, test_committee, len(approvals), committee_size)
    
    print(f"  JR satisfied: {jr_result}")
    print(f"  PJR satisfied: {pjr_result}")
    print(f"  EJR satisfied: {ejr_result}")


if __name__ == "__main__":
    main() 