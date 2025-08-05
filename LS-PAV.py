
voters = ["a1", "a2", "a3"]
candidates = [1, 2, 3, 4, 5, 6]

a1 = [5,6,3,2]
a2 = [4,3,5,2]
a3 = [3,4,2,1]

preferences = {}
preferences["a1"] = a1
preferences["a2"] = a2
preferences["a3"] = a3

#calculate the PAV score of a committee
def calculate_PAV_score(committee, preferences):
    voter_to_representation = {}
    voter_to_score = {}
    total_score = 0
    for voter in preferences:
        voter_to_representation[voter] = 0
        voter_to_score[voter] = 0
    

    for voter in preferences:
        for candidate in committee:
            if candidate in preferences[voter]:
                voter_to_representation[voter] += 1
                voter_to_score[voter] += 1/voter_to_representation[voter]
    
    for voter in voter_to_score:
        total_score += voter_to_score[voter]

    # print(voter_to_score)
    
    return total_score

#return true if the first committee is better than the second committee by at least epsilon
def profitable_deviation(committee_1, committee_2, preferences, epsilon):
    score_1 = calculate_PAV_score(committee_1, preferences)
    score_2 = calculate_PAV_score(committee_2, preferences)
    if score_2 - score_1 >= epsilon:
        return True
    else:
        return False
    
# print(profitable_deviation([4,3,2], [1,5,6], preferences, 0))

def find_better_commitee(initial_commitee, preferences, candidates, epsilon):

    current_elected_candidate = set()
    remaining_candidates = []
    for candidate in initial_commitee:
        current_elected_candidate.add(candidate)
    
    for candidate in candidates:
        if candidate not in current_elected_candidate:
            remaining_candidates.append(candidate)
    
    for i in range(len(initial_commitee)):
        for j in range(len(remaining_candidates)):
            alternative_commitee = initial_commitee.copy()
            alternative_commitee[i] = remaining_candidates[j]
            if profitable_deviation(initial_commitee, alternative_commitee, preferences, epsilon):
                print("Initial commitee: ", initial_commitee, " with score of: ", calculate_PAV_score(initial_commitee, preferences))
                print("Alternative commitee: ", alternative_commitee, " with score of: ", calculate_PAV_score(alternative_commitee, preferences))
                return alternative_commitee
    
    return initial_commitee
    
# print(find_better_commitee([2,6,1], preferences, candidates, 0.5))
    

def LS_PAV(candidates, preferences, committee_size):
    initial_commitee = []
    for i in range(committee_size):
        initial_commitee.append(candidates[i])

    while profitable_deviation(initial_commitee, find_better_commitee(initial_commitee, preferences, candidates, 0), preferences, 0.3):
        initial_commitee = find_better_commitee(initial_commitee, preferences, candidates, 0)

    return initial_commitee

print(LS_PAV(candidates, preferences, 3))
   
        
    


