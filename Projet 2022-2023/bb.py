from group import gen_group, Group, inverse, dLog
from utils import hashg
import json


def load_bb_json(bb_json):
    n_choices = bb_json["n_choices"]
    n_selections = bb_json["n_selections"]
    p = bb_json["group"]["p"]
    g = bb_json["group"]["g"]

    BB = BulletinBoard(n_choices, n_selections, p, g)

    BB.phase = bb_json["phase"]
    BB.group = bb_json["group"]
    BB.tallier_keys = bb_json["tallier_keys"]
    BB.ballots = bb_json["ballots"]
    BB.decryption_factors = bb_json["decryption_factors"]

    if BB.phase != "init":
        BB.pk = BB.compute_public_key()
    if BB.phase == "tally":
        BB.tally_encryptions = BB.compute_tally_encryptions()

    return BB


class BulletinBoard:

    def __init__(self, n_choices, n_selections=-1, p=None, g=None):
        if p == None or g == None:
            p, g = gen_group()
        self.G = Group(p, g)

        self.n_choices = n_choices
        self.n_selections = n_selections

        self.phase = "init"
        self.group = {"p": p, "g": g}
        self.tallier_keys = []
        self.ballots = []
        self.decryption_factors = []

    def start_voting_phase(self):
        self.phase = "vote"
        self.pk = self.compute_public_key()

    def start_tally_phase(self):
        self.phase = "tally"
        self.tally_encryptions = self.compute_tally_encryptions()

    def append_tallier_key(self, key, proof):
        """
            Append the partial public key of a tallier and its proof of correctness
            to the bulletin board.
        """
        if self.phase != "init":
            raise RuntimeError("The election is not in the initialization phase.")

        self.tallier_keys.append({"pk": key, "proof": proof})

    def append_ballot(self, vote_encryptions, zero_one_proofs, k_selections_proof=None):
        """
            Append a ballot to the bulletin board.
            If the election does not constraint the number of selections that can be made,
            the k_selections_proof argument should be set to None. 
        """
        if self.phase != "vote":
            raise RuntimeError("The election is not in the voting phase.")

        if k_selections_proof == None and self.n_selections != -1:
            raise RuntimeError("Proof of {} selections missing.".format(self.n_selections))

        ballot = {
            "vote_encryptions": [{"c1": vote_encryption[0],
                                  "c2": vote_encryption[1]}
                                 for vote_encryption in vote_encryptions],
            "zero_one_proofs": zero_one_proofs,
        }

        if self.n_selections != -1:
            ballot["{}_selection_proof".format(self.n_selections)] = k_selections_proof

        self.ballots.append(ballot)

    def append_decryption_factor(self, pk, df, proof):
        """
            Append the decryption factor of a tallier and its proof of correctness
            to the bulletin board.
        """
        if self.phase != "tally":
            raise RuntimeError("The election is not in the tallying phase.")

        self.decryption_factors.append({"pk": pk, "df": df, "proof": proof})

    def compute_public_key(self):
        """ 
            Compute and return the public key of the bulletin board from the partial 
            keys of the talliers.
            The output should be a valid elgamal public key.
            Keys with an invalid proof are discarded.
        """
        if self.phase == "init":
            raise RuntimeError("The election public key cannot be computed yet.")

        if hasattr(self, "pk"):
            return self.pk

        pk = -1

        # TO COMPLETE
        # tallier_keys of the form {"pk": key, "proof": proof}
        G = self.get_group()
        pk = 1  # Unit for the multiplication
        for key in self.tallier_keys:
            if self.verify_key_correctness_proof(key["pk"], key["proof"]):
                pk *= key["pk"]
        pk = pk % G.p
        ##

        return pk

    def compute_tally_encryptions(self):
        """ 
            Compute and return a list of valid encryptions of the tally of the election 
            from the valid ballots in the bulletin board.
            The output is a list of n_choices dictionaries {"c1": <val>, "c2": <val>}
            representing an elgamal ciphertext.
            Ballots with an invalid proof are discarded.
        """
        if self.phase != "tally":
            raise RuntimeError("The encryption of the tally cannot be computed yet.")

        if hasattr(self, "tally_encryptions"):
            return self.tally_encryptions

        # tally_encryptions = [{"c1": -1, "c2": -1} for i in range(self.n_choices)]

        # TO COMPLETE
        tally_encryptions = [{"c1": 1, "c2": 1} for i in range(self.n_choices)]
        G = self.get_group()
        for ballot in self.ballots:
            if self.verify_ballot(ballot):
                for i, vote in enumerate(ballot["vote_encryptions"]):
                    tally_encryptions[i]["c1"] = (tally_encryptions[i]["c1"] * vote["c1"]) % G.p
                    tally_encryptions[i]["c2"] = (tally_encryptions[i]["c2"] * vote["c2"]) % G.p

        ####

        return tally_encryptions

    def verify_key_correctness_proof(self, pk, proof):
        """
            Verify that the proof associated to an elgamal public key is correct.
        """
        G = self.get_group()

        # commit corresponds to a in the slides
        commit = proof["commit"]
        # response corresponds to f in the slides
        response = proof["response"]
        # the correct e that should have been used
        challenge = hashg(json.dumps({"pk": pk, "commit": commit}), G.q)

        # TO COMPLETE
        G = self.get_group()
        return pow(G.g, response, G.p) == (commit * pow(pk, challenge, G.p)) % G.p
        ###

    def verify_disjunctive_proof(self, vote_encryption, proof):
        """
            Verify that the '0 or 1' disjunctive proof for vote_encryption is correct.
        """

        # YOU HAVE NOTHING TO DO HERE :-)
        G = self.get_group()
        c1 = vote_encryption["c1"]
        c2 = vote_encryption["c2"]
        e = hashg(json.dumps({
            "ct": vote_encryption,
            "commit": proof["commit"],
            "pk": self.pk,
        }), G.q)

        if (sum(proof["challenge"]) % G.q != e):
            return False

        for s in range(2):
            f = proof["response"][s]
            (d1, d2) = proof["commit"][s]
            e = proof["challenge"][s]
            if s == 1:
                c2 = (c2 * inverse(G.g, G.p)) % G.p
            if (pow(G.g, f, G.p) != (d1 * pow(c1, e, G.p)) % G.p or
                    pow(self.pk, f, G.p) != (d2 * pow(c2, e, G.p)) % G.p):
                return False

        return True

    def verify_k_selection_proof(self, vote_encryptions, proof):
        """
            Verify that the proof that the ciphertexts in vote_encryptions encrypt exactly
            n_selections times "1" is correct.
        """

        G = self.get_group()

        # TO COMPLETE
        c1 = 1  # unit for multiplication
        c2 = 1  # unit for multiplication

        for index, vote_encryption in enumerate(vote_encryptions):
            c1 = (c1 * vote_encryption['c1']) % G.p
            c2 = (c2 * vote_encryption['c2']) % G.p
        ###

        # We want to verify that the voter knows the r such that c1 = g^r and (c2/g^k) = h^r

        commit = proof["commit"]
        response = proof["response"]
        challenge = hashg(json.dumps({"ciphertext": (c1, c2), "commit": commit}), G.q)

        # We make the variables correspond to those in the slides

        a1 = commit[0]
        a2 = commit[1]
        f = response
        e = challenge

        g1 = G.g
        g2 = self.compute_public_key()

        h1 = c1
        h2 = c2 * inverse(pow(G.g, self.get_n_selections(), G.p), G.p) % G.p

        # TO COMPLETE
        cond1 = (pow(g1, f, G.p) == (a1 * pow(h1, e, G.p)) % G.p)
        cond2 = (pow(g2, f, G.p) == (a2 * pow(h2, e, G.p)) % G.p)
        ###

        return cond1 and cond2

    def verify_tally_correctness_proof(self, partial_pk, c1, df, proof):
        """
            Verify that the proof of correctness of the decryption factor is correct. 
        """

        commit = proof["commit"]
        response = proof["response"]
        challenge = hashg(json.dumps({"pk": partial_pk, "decryption_factor": df, "commit": commit}), self.G.q)

        # TO COMPLETE
        G = self.get_group()
        a1 = commit[0]
        a2 = commit[1]
        f = response
        e = challenge
        h1 = partial_pk  # pk = g^x and h1 = g1^x with g1 = g
        h2 = df  # h2 = g2^x and g2 = c1 as df = c1^x = h2

        trueC1 = pow(G.g, f, G.p) == (a1 * pow(h1, e, G.p)) % G.p
        trueC2 = pow(c1, f, G.p) == (a2 * pow(h2, e, G.p)) % G.p
        return trueC1 and trueC2

        ###

    def verify_ballot(self, ballot):
        """
            Verify that a ballot has a correct structure and valid proofs.
        """
        # TO COMPLETE

        # if self.n_selections != -1
        # ballot = { "vote_encryptions": [{"c1": vote_encryption[0], "c2": vote_encryption[1]}, {"c1": vote_encryption[0], "c2": vote_encryption[1]} ,...]
        #           ,"zero_one_proofs": zero_one_proofs (list)} 
        # Otherwise ballot has a additional argument "{k_selections_proof}_selection_proof" : k_selections_proof"

        # Verify structure
        if self.n_selections == -1 and len(ballot) == 3:
            print("Ballot as not k_selections_proof_selection_proof set to None")
            return False
        if self.n_selections == -1 and len(ballot) != 2:
            print("Ballot is simple but have more or less than 2 elements")
            return False
        elif self.n_selections != -1 and len(ballot) != 3:
            # TODO verify if it is always 3 -> is there still a test to be added here ?
            print("Ballot is complex but have more or less than 3 elements")
            return False

        # Verify validity
        if self.n_selections != -1:  # Case of complex ballots
            for vote in range(len(ballot["zero_one_proofs"])):
                vote_encrypt = ballot["vote_encryptions"][vote]
                proof = ballot["zero_one_proofs"][vote]
                if not self.verify_disjunctive_proof(vote_encrypt, proof):
                    print("ballot not valid")
                    return False
            # verify k_selection
            if not self.verify_k_selection_proof(ballot["vote_encryptions"],
                                                 ballot["{}_selection_proof".format(self.n_selections)]):
                print("False returned")
                return False
        else:
            for vote in range(len(ballot["zero_one_proofs"])):
                vote_encrypt = ballot["vote_encryptions"][vote]
                proof = ballot["zero_one_proofs"][vote]
                if not self.verify_disjunctive_proof(vote_encrypt, proof):
                    print("ballot not valid")
                    return False
        ###

        return True

    def tally(self):
        """
            Compute the final result of the election.
            The result is a list of integers representing the number of votes of each option.
            Ignore the talliers that provided a fake public key in the initialization phase.
            Ignore invalid ballots and if a decryption factor is invalid, abort the election 
            and return -1.
        """

        result = [0] * self.n_choices
        ######
        # TO COMPLETE
        G = self.get_group()
        # We track the taillier with a valid key
        valid_taillers = [0] * len(self.tallier_keys)
        for i, key in enumerate(self.tallier_keys):
            if self.verify_key_correctness_proof(key["pk"], key["proof"]):
                valid_taillers[i] = 1
                # print(f"True init key for tallier {i}")
            else:
                print(f"Fake init key for tallier {i}")

        # We track the ballots with a valid proof
        valid_ballots = [0] * len(self.ballots)
        for i, ballot in enumerate(self.ballots):
            if self.verify_ballot(ballot):
                # print(f"Ballot {i} valid")
                valid_ballots[i] = 1

        # Verify decryption factor
        for tally, df_list in enumerate(self.decryption_factors):
            # Skip the tallier with invalid key pair
            if valid_taillers[tally] == 1:
                pk_tally = df_list["pk"]
                for vote, df in enumerate(df_list["df"]):
                    # Verify tally df correctness
                    if not self.verify_tally_correctness_proof(pk_tally, self.tally_encryptions[vote]["c1"], df,
                                                               df_list["proof"][vote]):
                        print("Invalid description factor")
                        return -1

        for i, encrypt in enumerate(self.tally_encryptions):
            c1 = encrypt["c1"]
            c2 = encrypt["c2"]
            for tally, df_list in enumerate(self.decryption_factors):
                if valid_taillers[tally] == 1:
                    c2 = c2 * inverse(df_list["df"][i], G.p)
            c2 = c2 % G.p
            result[i] = dLog(G.p, G.g, c2)

        ###

        return result

    def get_group(self):
        return self.G

    def get_n_choices(self):
        return self.n_choices

    def get_n_selections(self):
        return self.n_selections

    def get_dict(self):
        return {
            "phase": self.phase,
            "group": self.group,
            "n_choices": self.n_choices,
            "n_selections": self.n_selections,
            "tallier_keys": self.tallier_keys,
            "ballots": self.ballots,
            "decryption_factors": self.decryption_factors
        }

    def publish(self):
        """
            Return a json representation of the bulletin board.
        """

        return json.dumps(self.get_dict())
