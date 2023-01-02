from utils import hashg
import json
from number import getRandomRange


class Tallier:

    def __init__(self, BB):
        self.BB = BB

    """
        Methods for the initialization phase
    """

    def generate_key(self):
        """
            Generate a fresh elgamal key.
        """

        pk = -1
        sk = -1

        # TO COMPLETE
        G = self.BB.get_group()
        sk = G.random_exp()
        pk = pow(G.g, sk, G.p)
        ###
        self.sk = sk
        self.pk = pk

    def generate_key_correctness_proof(self, pk, sk):
        """
            Generate a Schnorr zero-knowlege proof of knowledge of the secret key sk associated 
            to the public key pk.
        """

        # TO COMPLETE
        G = self.BB.get_group()
        r = G.random_exp()
        commit = pow(G.g, r, G.p)
        ##

        challenge = hashg(json.dumps({"pk": pk, "commit": commit}), G.q)

        # TO COMPLETE
        response = (r + challenge * sk) % G.q
        #####
        return {
            "commit": commit,
            "response": response
        }

    def publish_key(self):
        """
            Publish the public key on the bulletin board.
        """
        proof = self.generate_key_correctness_proof(self.pk, self.sk)
        self.BB.append_tallier_key(self.pk, proof)

    """
        Methods for the tallying phase
    """

    def generate_tally_correctness_proof(self, c1, df):
        """
            Generate a Chaum-Pedersen proof that the decryption factor associated to the
            encryption of the tally c1 is correct.
            That is, prove that you know a secret key sk such that <g>^sk = <pk> and 
            <c1>^sk = <df>
        """
        G = self.BB.get_group()

        # TO COMPLETE
        g1 = G.g
        g2 = c1
        r = G.random_exp()
        commit = (pow(g1, r, G.p), pow(g2, r, G.p))  # Est-ce que le commit peut-il être fait comme ça ?

        challenge = hashg(json.dumps({"pk": self.pk, "decryption_factor": df, "commit": commit}), G.q)

        response = (r + challenge * self.sk) % G.q

        ######
        return {
            "commit": commit,
            "response": response
        }

    def compute_decryption_factors(self):
        """
            Compute the partial result of the election associated to the tallier's keys.
            Output a list of n_choices decryption factors and a list of n_choices Chaum-
            Pedersen proofs.
        """
        G = self.BB.get_group()

        tally_encryptions = self.BB.compute_tally_encryptions()
        decryption_factors = []
        proofs = []

        # TO COMPLETE
        for i, encryption in enumerate(tally_encryptions):
            decryption_factors.append(pow(encryption["c1"], self.sk, G.p))  # Df is c1^x
            proofs.append(self.generate_tally_correctness_proof(encryption["c1"], decryption_factors[i]))
        ###

        self.BB.append_decryption_factor(self.pk, decryption_factors, proofs)
