import json
import hashlib

import elgamal
from vote_dproof import verify_ballot, generate_ballot
import canonicaljson
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
    # TO COMPLETE
    sk_elec = sum([key[0].x for key in partial_keys]) % G.p
    pk = 1 
    for key in partial_keys:
        pk = (pk * key[1].y) %G.p
    assert pow(G.g,sk_elec,G.p) == pk
    # TO COMPLETE

    return elgamal.ElgamalPublicKey(G, pk)

def prove_key_correctness(elgamal_key):
    """
    Given an elgamal key, return a valid proof of knowledge of the secret key.
    To do so, use the _hashg method.
    """
    # QUESTION 5.3
    # TO COMPLETE
    pk =  elgamal_key[1].y# TO COMPLETE
    G = elgamal_key[1].G
    r = G.random_exp()
    commit = pow(G.g,r,G.p)# TO COMPLETE
    challenge = _hashg(json.dumps({"pk": pk, "commit": commit}), G.q) 
    response = (r + challenge * elgamal_key[0].x) % G.q# TO COMPLETE
    # TO COMPLETE
    return {"pk": pk,
            "commit": commit,
            "response": response}

def validate_key_correctness(key,G):
    """
    Given a proof of knowledge of the secret key of an elgamal key,
    verify that the proof is correct.
    """
    # QUESTION 5.2
    pk = key["pk"] 
    commit = key["commit"] 
    response = key["response"]
     
    # Verify the proof
    #TO COMPLETE
    challenge = _hashg(json.dumps({"pk": pk, "commit": commit}), G.q)
    return pow(G.g,response,G.p) == (commit * pow(pk,challenge,G.p))%G.p
    #TO COMPLETE

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
    
    bb["tallier_keys"] = [prove_key_correctness(key) for key in partial_keys]
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
    # TO COMPLETE
    p  = bb['group']['p']
    g  = bb['group']['g']
    G  = elgamal.ElgamalGroup(p,g)
    pk = elgamal.ElgamalPublicKey(G,bb['pk'])
    ballot = generate_ballot(pk,vote)
    # TO COMPLETE 
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
    # TO COMPLETE
    p  = bb['group']['p']
    g  = bb['group']['g']
    G  = elgamal.ElgamalGroup(p,g)
    pk = elgamal.ElgamalPublicKey(G,bb['pk'])
    c1 = 1
    c2 =1 
    for ballot in bb["ballots"]:
        if verify_ballot(pk,ballot):
            c1 = (c1 * ballot['ct']['c1']) % p
            c2 = (c2 * ballot['ct']['c2']) % p
    encrypted_tally = (c1,c2)
     # TO COMPLETE
  
    return encrypted_tally

def compute_decryption_factor_without_proof(tally_encryption, partial_key):
    """
    Given an encryption of the tally and the partial key of a trustee,
    compute the corresponding decryption factor.
    """
    # QUESTION 5.1
    # TO COMPLETE
    c1 = tally_encryption[0]
    sk_trustee = partial_key[0].x
    p = partial_key[0].G.p
    df = pow(c1,sk_trustee,p)
    # TO COMPLETE

    return df


def compute_decryption_factor_with_proof(tally_encryption, partial_key):
    """
    Given an encryption of the tally and the partial key of a trustee,
    compute the corresponding decryption factor and the corresponding proof of 
    correct computation.
    To do so, use the _hashg method.
    """
    # QUESTION 5.3    
    # TO COMPLETE
    pk = partial_key[1].y # TO COMPLETE
    c1 = tally_encryption[0] # TO COMPLETE
    G = partial_key[0].G
    sk_tallier = partial_key[0].x
    df = pow(c1,sk_tallier,G.p) # TO COMPLETE
    r = G.random_exp()
    commit = [pow(G.g,r,G.p),pow(c1,r,G.p)] # TO COMPLETE
    challenge = _hashg(json.dumps({"pk": pk, "c1": c1,"decryption_factor":df,"commit": commit}), G.q)
    response = (r+challenge*sk_tallier)%G.q # TO COMPLETE
    # TO COMPLETE
    return {"pk": pk,
            "c1": c1,
            "decryption_factor": df,
            "commit": commit,
            "response": response
            }

def validate_decryption_factor_proof(decryption_factor,G):
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
    #TO COMPLETE
    challenge = _hashg(json.dumps({"pk": pk, "c1": c1,"decryption_factor":df,"commit": commit}), G.q) 
    
    CP_ZKP_0 = pow(G.g,response,G.p) == (commit[0] * pow(pk,challenge,G.p)) % G.p
    CP_ZKP_1 = pow(c1,response,G.p)  == (commit[1] * pow(df,challenge,G.p)) % G.p
    return CP_ZKP_0 and CP_ZKP_1
    #TO COMPLETE

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
    compute the final result.
    """
    # QUESTION 5.2
    # TO COMPLETE
    p  = bb['group']['p']
    g  = bb['group']['g']
    G  = elgamal.ElgamalGroup(p,g)
    pk_elec = 1
    for df in bb["decryption_factors"]:
        if not validate_decryption_factor_proof(df,G):
            return None
        pk_elec = (pk_elec * df["pk"])%G.p
    bb["pk"] = pk_elec
    res = compute_tally_encryption(bb)
    # TO COMPLETE
    return res

def tally(bb):
    """
    Given the bulletin board bb of an election with the decryption factors,
    validate the correctness of the bulletin board and compute the final result.
    Return None if one of the trustees has cheated.
    """
    # QUESTION 5.2
    
    # Verify the proofs and compute the result

    res = combine_decryption_factors(bb)
    

    return res

# QUESTION 4.1: Read the bulletin board and compute an encryption of the tally. 
#               Ask the decryption oracle for the result of the election.
# QUESTION 4.2: What is the vote of the first ballot? 
with open("bb.json", "r") as fd:
    bb = json.loads(fd.readline())
    result = compute_tally_encryption(bb)
    #Question 4.1
    print("The encrypted results are")
    print("{\"c1\": ",result[0], ",\"c2\": ",result[1],"}")
    #Put this result in https://lelec2770. pythonanywhere.com/elections1
    #And you will get 
    #Result = 27

    #Question 4.2
    #One can't give the value of the first ballot to the oracle because he won't give any results 
    #One possibility is to do the sum of all ballots from 2 to 100 and remove 27
    c1bis = 1
    c2bis = 1
    p  = bb['group']['p']
    g  = bb['group']['g']
    G  = elgamal.ElgamalGroup(p,g)
    pk = elgamal.ElgamalPublicKey(G,bb['pk'])
    for ballot in bb["ballots"][1:]:
        if verify_ballot(pk,ballot):
            c1bis = c1bis * ballot['ct']['c1'] % p
            c2bis = c2bis * ballot['ct']['c2'] % p
    print("The encrypted results without the first ballot are")
    print("{\"c1\": ",c1bis, ",\"c2\": ",c2bis,"}")
    #results = 27
    #This gives the same results as before
    #Therefore the first ballot encrypted 0
    

# QUESTION 5.2: Read the bulletin board with the decryption factors and verify 
#               the result of the election.
with open("bb_proof.json", "r") as fd:
    bb = json.loads(fd.readline())
    res = tally(bb)
    print("The encrypted results for bb with proof are")
    print("{\"c1\": ",res[0], ",\"c2\": ",res[1],"}")
    



    
