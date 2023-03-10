import json
import hashlib

import elgamal
from vote_dproof import verify_ballot, generate_ballot

def _hashg(json_obj, q):
    """Hash a JSON object to a integer modulo q.

    :param json_obj: JSON object encoded into a str.

    Procedure:
    * map the object to json in binary canonical form (see
    <https://pypi.org/project/canonicaljson/>)
    * hash it with SHA256
    * interpret the byte string as a big-endian integer
    * reduce it mod q
    """
    return int.from_bytes(
            hashlib.sha256(canonicaljson.dumps(json.loads(json_obj))).digest(),
            byteorder='big'
            ) % q


"""
    ELECTION INITIALIZATION
"""
def combine_keys(G, partial_keys):
    """
    Given the partial keys of the trustees, combine them to obtain the key of the election.
    """
    # QUESTION 5.1
    assert [key[1].G == G for key in partial_keys]    
    assert [key[1] == key[0].pk() for key in partial_keys]

    pk = ... # TO COMPLETE

    return elgamal.ElgamalPublicKey(G, pk)

def prove_key_correctness(elgamal_key):
    """
    Given an elgamal key, return a valid proof of knowledge of the secret key.
    To do so, use the _hashg method.
    """
    # QUESTION 5.3
    pk = ... # TO COMPLETE
    commit = ... # TO COMPLETE
    response = ... # TO COMPLETE

    return {"pk": pk,
            "commit": commit,
            "response": response}

def validate_key_correctness(key):
    """
    Given a proof of knowledge of the secret key of an elgamal key,
    verify that the proof is correct.
    """
    # QUESTION 5.2
    pk = key["pk"] 
    commit = key["commit"] 
    response = key["response"]
    
    # Verify the proof

    return False

def generate_empty_bb(p, g, pk):
    return {"group": {"p": p, "g": g}, "pk": pk, "ballots": []}

def generate_election(n_trustees, p = None, g = None):
    if p == None or g == None:
        G = elgamal.gen_group()
        p = G.p
        g = G.g
    else:
        G = elgamal.ElGamalGroup(p, g)
    partial_keys = [elgamal.gen_elgamal_keypair(G) for i in range(n_trustees)]
   
    pk = combine_keys(G, partial_keys)
    
    bb = generate_empty_bb(p, g, pk.y)
    
    #bb["tallier_keys"] = [prove_key_correctness(key) for key in partial_keys]
    return bb, partial_keys

"""
    VOTING PHASE
"""

def cast_vote(bb, vote):
    """
    Given the bulletin board bb of an election and a 0-1 vote, update 
    the bulletin board with a valid ballot of the vote.
    """
    # QUESTION 4.3
    assert vote in (0, 1)
        
    ballot = ... # TO COMPLETE 
    bb["ballots"].append(ballot)

"""
    COMPUTATION OF THE DECRYPTION FACTORS  
"""

def compute_tally_encryption(bb):
    """ 
    Given the bulletin board bb of an election, return a valid encryption
    of the result of the election.
    """
    # QUESTION 4.1 
    encrypted_tally = ... # TO COMPLETE
  
    return encrypted_tally

def compute_decryption_factor_without_proof(tally_encryption, partial_key):
    """
    Given an encryption of the tally and the partial key of a trustee,
    compute the corresponding decryption factor.
    """
    # QUESTION 5.1

    df = ... # TO COMPLETE

    return df


def compute_decryption_factor_with_proof(tally_encryption, partial_key):
    """
    Given an encryption of the tally and the partial key of a trustee,
    compute the corresponding decryption factor and the corresponding proof of 
    correct computation.
    To do so, use the _hashg method.
    """
    # QUESTION 5.3    

    pk = ... # TO COMPLETE
    c1 = ... # TO COMPLETE
    df = ... # TO COMPLETE
    commit = ... # TO COMPLETE
    response = ... # TO COMPLETE
    
    return {"pk": pk,
            "c1": c1,
            "decryption_factor": df,
            "commit": commit,
            "response": response
            }

def validate_decryption_factor_proof(decryption_factor):
    """
    Given a proof of correctness of a decryption factor,
    verify that the proof is correct.
    """
    # QUESTION 5.2

    pk = decryption_factor["pk"]
    c1 = decryption_factor["c1"]
    df = decryption_factor["decryption_factor"]
    commit = decryption_factor["commit"]
    response = decryption_factor["response"]

    # Verify the proof
    return False


def compute_all_decryption_factors(bb, partial_keys):
    tally_encryption = compute_tally_encryption(bb)
    decryption_factors = [compute_decryption_factor_with_proof(tally_encryption, key)
                            for key in partial_keys]
    
    bb["decryption_factors"] = decryption_factors 

"""
    COMPUTE THE FINAL RESULT OF THE ELECTION
"""

def combine_decryption_factors(bb):
    """
    Given the bulletin board bb of an election with the decryption factors,
    comptue the final result.
    """
    # QUESTION 5.2
    
    res = ... # TO COMPLETE
    return res

def tally(bb):
    """
    Given the bulletin board bb of an election with the decryption factors,
    validate the correctness of the bulletin board and compute the final result.
    Return None if one of the trustees has cheated.
    """
    # QUESTION 5.2
    
    # Verify the proofs and compute the result

    return None

# QUESTION 4.1: Read the bulletin board and compute an encryption of the tally. 
#               Ask the decryption oracle for the result of the election.
# QUESTION 4.2: What is the vote of the first ballot? 
with open("bb.json", "r") as fd:
    bb = json.loads(fd.readline())


# QUESTION 5.2: Read the bulletin board with the decryption factors and verify 
#               the result of the election.
with open("bb_proof.json", "r") as fd:
    bb = json.loads(fd.readline())
