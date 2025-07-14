# Advanced example demonstrating differences between JR, PJR, and EJR

from pjr_ejr import check_jr, check_pjr, check_ejr, find_committees_satisfying_criterion

def analyze_example_1():
    """
    Example 1: A case where JR and PJR are satisfied but EJR might not be.
    """
    print("=== EXAMPLE 1: Demonstrating JR vs PJR vs EJR ===")
    
    # 9 voters, committee size 3 (quota = 3)
    approvals = {
        'v1': {'a', 'b'},      # Group 1: likes a,b
        'v2': {'a', 'b'},
        'v3': {'a', 'b'},
        'v4': {'c', 'd'},      # Group 2: likes c,d  
        'v5': {'c', 'd'},
        'v6': {'c', 'd'},
        'v7': {'e', 'f'},      # Group 3: likes e,f
        'v8': {'e', 'f'},
        'v9': {'e', 'f'},
    }
    
    committee_size = 3
    num_voters = len(approvals)
    quota = num_voters / committee_size
    
    print(f"Voters: {num_voters}, Committee size: {committee_size}, Quota: {quota}")
    print("\nVoter groups:")
    print("  Group 1 (v1-v3): approve {a, b}")
    print("  Group 2 (v4-v6): approve {c, d}")  
    print("  Group 3 (v7-v9): approve {e, f}")
    
    # Test different committees
    test_committees = [
        {'a', 'c', 'e'},  # One from each group
        {'a', 'b', 'c'},  # Two from group 1, one from group 2
        {'a', 'c', 'f'},  # Mixed representatives
    ]
    
    print(f"\nTesting committees:")
    for i, committee in enumerate(test_committees, 1):
        print(f"\nCommittee {i}: {sorted(committee)}")
        jr = check_jr(approvals, committee, num_voters, committee_size)
        pjr = check_pjr(approvals, committee, num_voters, committee_size)
        ejr = check_ejr(approvals, committee, num_voters, committee_size)
        print(f"  JR: {jr}, PJR: {pjr}, EJR: {ejr}")


def analyze_example_2():
    """
    Example 2: A case designed to show when PJR is more restrictive than JR.
    """
    print("\n\n=== EXAMPLE 2: PJR more restrictive than JR ===")
    
    # 8 voters, committee size 4 (quota = 2)
    approvals = {
        'v1': {'a', 'b'},      # 2 voters like a,b
        'v2': {'a', 'b'},
        'v3': {'a', 'c'},      # 2 voters like a,c  
        'v4': {'a', 'c'},
        'v5': {'d'},           # 4 voters like only d
        'v6': {'d'},
        'v7': {'d'},
        'v8': {'d'},
    }
    
    committee_size = 4
    num_voters = len(approvals)
    quota = num_voters / committee_size
    
    print(f"Voters: {num_voters}, Committee size: {committee_size}, Quota: {quota}")
    print("\nVoter preferences:")
    for voter, approved in approvals.items():
        print(f"  {voter}: {sorted(approved)}")
    
    # Key insight: 
    # - 'a' is approved by 4 voters (v1-v4), so they deserve 2 representatives
    # - 'd' is approved by 4 voters (v5-v8), so they deserve 2 representatives
    
    test_committees = [
        {'a', 'b', 'c', 'd'},  # Should satisfy PJR: a,b for first group, c for overlap, d for last group
        {'a', 'd', 'e', 'f'},  # Might satisfy JR but not PJR
    ]
    
    print(f"\nTesting committees:")
    for i, committee in enumerate(test_committees, 1):
        print(f"\nCommittee {i}: {sorted(committee)}")
        jr = check_jr(approvals, committee, num_voters, committee_size)
        pjr = check_pjr(approvals, committee, num_voters, committee_size)
        ejr = check_ejr(approvals, committee, num_voters, committee_size)
        print(f"  JR: {jr}, PJR: {pjr}, EJR: {ejr}")
        
        if jr and not pjr:
            print("  --> This shows JR being less restrictive than PJR!")


def find_and_compare_all_criteria():
    """
    Find all committees satisfying each criterion for a specific example.
    """
    print("\n\n=== EXAMPLE 3: Complete comparison ===")
    
    approvals = {
        'v1': {'a', 'b'},
        'v2': {'a', 'c'}, 
        'v3': {'b', 'c'},
        'v4': {'d', 'e'},
        'v5': {'d', 'f'},
        'v6': {'e', 'f'},
    }
    
    committee_size = 3
    
    print("Approvals:")
    for voter, approved in approvals.items():
        print(f"  {voter}: {sorted(approved)}")
    
    print(f"\nCommittee size: {committee_size}")
    print(f"Quota: {len(approvals)/committee_size:.2f}")
    
    for criterion in ["jr", "pjr", "ejr"]:
        committees = find_committees_satisfying_criterion(approvals, committee_size, criterion)
        print(f"\n{criterion.upper()} committees ({len(committees)} total):")
        for committee in committees:
            print(f"  {sorted(committee)}")


if __name__ == "__main__":
    analyze_example_1()
    analyze_example_2() 
    find_and_compare_all_criteria() 