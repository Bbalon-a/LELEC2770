from group import inverse
from utils import hashg

import json


class Voter:
    def __init__(self, BB):
        self.BB = BB

    def generate_disjunctive_proof(self, vote, vote_encryption, randomness_encryption):
        """
            Generate a disjunctive proof that vote_encryption is an encryption of zero or one.
        """

        # YOU HAVE NOTHING TO DO HERE :-)

        assert vote == 0 or vote == 1

        def _sort(x, y):
            return (x, y) if vote == 0 else (y, x)

        G = self.BB.get_group()
        pk = self.BB.compute_public_key()

        # simulated proof
        e_sim = G.random_exp()
        f_sim = G.random_exp()
        s_sim = (vote_encryption[1] * inverse(pow(G.g, 1 - vote, G.p), G.p)) % G.p
        d_sim = (
            (pow(G.g, f_sim, G.p) * inverse(pow(vote_encryption[0], e_sim, G.p), G.p)) % G.p,
            (pow(pk, f_sim, G.p) * inverse(pow(s_sim, e_sim, G.p), G.p)) % G.p,
        )

        # correct proof
        z = G.random_exp()
        d_true = (pow(G.g, z, G.p), pow(pk, z, G.p))
        e = hashg(json.dumps({
            "ct": {"c1": vote_encryption[0], "c2": vote_encryption[1]},
            "commit": _sort(d_true, d_sim),
            "pk": pk,
        }), G.q)
        e_true = (e - e_sim) % G.q
        f_true = (randomness_encryption * e_true + z) % G.q

        return {
            "commit": _sort(d_true, d_sim),
            "challenge": _sort(e_true, e_sim),
            "response": _sort(f_true, f_sim),
        }

    def generate_k_selections_proof(self, k, vote_encryptions, randomness_encryptions):
        """
            Generate a proof that vote_encryptions is a list of ciphertexts that 
            encrypt exactly n_selections time "1".
        """

        G = self.BB.get_group()
        pk = self.BB.compute_public_key()

        c1 = 1  # unit for multiplication
        c2 = 1  # unit for multiplication
        r = 0  # for adding all randomnesses

        for index, vote_encryption in enumerate(vote_encryptions):
            c1 = (c1 * vote_encryption[0]) % G.p
            c2 = (c2 * vote_encryption[1]) % G.p
            r = (r + randomness_encryptions[index]) % G.q

        # We need to prove that we know r such that c1 = g^r and (c2/g^k) = h^r

        w = G.random_exp()
        a1 = pow(G.g, w, G.p)  # g^w
        a2 = pow(pk, w, G.p)  # h^w
        commit = (a1, a2)

        challenge = hashg(json.dumps({"ciphertext": (c1, c2), "commit": commit}), G.q)
        response = (w + challenge * r) % G.q

        return {
            "commit": commit,
            "response": response
        }

    def generate_complex_ballot(self, votes):
        """
            Generate a complex ballot encoding the voting intentions given in 'votes'.
        """

        # YOU HAVE NOTHING TO DO HERE :-)

        if sum(votes) != self.BB.get_n_selections():
            raise ValueError("The vote has not the right number of selections")

        vote_encryptions, zero_one_proofs, randomness_encryptions = self.generate_simple_ballot(votes,
                                                                                                return_randomness=True)

        # Compute k-selections proof 
        k_selections_proof = self.generate_k_selections_proof(self.BB.get_n_selections(), vote_encryptions,
                                                              randomness_encryptions)

        return vote_encryptions, zero_one_proofs, k_selections_proof

    def generate_simple_ballot(self, votes, return_randomness=False):
        """
            Generate a simple ballot encoding the voting intentions given in 'votes'.
            Output:
              - vote_encryptions: a list of elgamal vote ciphertexts associated to the 
                                  public key of the election
              - zero_one_proofs:  a list of disjunctive proofs that the associated
                                  ciphertexts encrypt either zero or one.
              - randomness:       a list of the random exponents used in the elgamal
                                  encryptions of the ciphertexts.
            If the argument 'return_randomness' is False, the output 'randomness' is dropped
        """

        if len(votes) != self.BB.get_n_choices():
            raise ValueError("The vote has not the right number of entries")

        G = self.BB.get_group()
        pk = self.BB.compute_public_key()

        vote_encryptions = []
        randomness = []
        zero_one_proofs = []

        for vote in votes:
            if vote != 0 and vote != 1:
                raise ValueError("One of the vote is not 0 or 1.")

        # TO COMPLETE
        for vote in votes:
            r = G.random_exp()
            c1 = pow(G.g, r, G.p)
            c2 = (pow(G.g, vote, G.p) * pow(pk, r, G.p)) % G.p
            proof = self.generate_disjunctive_proof(vote, (c1, c2), r)
            vote_encryptions.append((c1, c2))
            randomness.append(r)
            zero_one_proofs.append(proof)
        ###

        if return_randomness:
            return vote_encryptions, zero_one_proofs, randomness
        else:
            return vote_encryptions, zero_one_proofs

    def cast_ballot(self, ballot):
        self.BB.append_ballot(*ballot)
