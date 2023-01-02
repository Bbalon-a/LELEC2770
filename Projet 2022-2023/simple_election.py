from random import randint, shuffle
import json

from voter import Voter
from bb import BulletinBoard,load_bb_json
from tallier import Tallier

import numpy as np
n_choices = 4
n_selections = 3


loadjson = True
if loadjson:
    complex = True
# INITIALIZATION PHASE
if not loadjson:
    BB = BulletinBoard(n_choices, n_selections)

    n_talliers = 10
    talliers = [Tallier(BB) for i in range(n_talliers)]

    for i in range(n_talliers):
        talliers[i].generate_key()
        talliers[i].publish_key()

    # VOTING PHASE

    BB.start_voting_phase()

    n_voters = 5
    voters = [Voter(BB) for i in range(n_voters)]
    votes_real = [] #Ajout de ma part pour vérifier si tout est bon
    for i in range(n_voters):
        if n_selections != -1:
            votes = [1] * n_selections + [0] * (n_choices - n_selections)
            shuffle(votes)
            votes_real.append(votes)
            ballot = voters[i].generate_complex_ballot(votes)
        else:
            votes = [randint(0, 1) for i in range(n_choices)]
            votes_real.append(votes) #Ajout 
            ballot = voters[i].generate_simple_ballot(votes)

        voters[i].cast_ballot(ballot)

    # TALLYING PHASE 

    BB.start_tally_phase()

    for i in range(n_talliers):
        talliers[i].compute_decryption_factors()

    result = BB.tally()
    print("Result of the election:")
    print(np.sum(np.array(votes_real),axis=0))
    for i in range(n_choices):
        print("  Candidate {} gets {} vote{}.".format(i+1, result[i], "s"[(result[i] == 0):]))

else:
    if complex :
        bulletin = "complex_bb.json"
    else:
        bulletin = "simple_bb.json"
    with open(bulletin, "r") as fd:
        b = json.loads(fd.readline())
    BB = load_bb_json(b)
    print(BB.n_choices)
    print(len(BB.ballots))
    n_talliers = len(BB.tallier_keys)
    print(n_talliers)

    result = BB.tally()
    print(result)
    print("Result of the election:")
    for i in range(BB.n_choices):
        print("  Candidate {} gets {} vote{}.".format(i+1, result[i], "s"[(result[i] == 0):]))

