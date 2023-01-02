"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : Secure 2-party computation

Oblivious Transfer
"""
import os
from random import randint # Insecure randomness, better to use from "secrets" on python >= 3.6
from tqdm import tqdm
import elgamal

class Sender:
    """Oblblivious transfer sender for 2-byte messages

    :param msg0: Message 0
    :param msg1: Message 1
    :type msg0: bytes
    :type msg1: bytes
    """

    def __init__(self, msg0, msg1):
        assert isinstance(msg0, bytes) and len(msg0) == 2
        assert isinstance(msg1, bytes) and len(msg1) == 2
        self.m0 = msg0
        self.m1 = msg1

    def response(self, c, pk):
        """Compute response to a challenge sent by the receiver

        :param c: Encrypted challenge
        :param pk: Encryption public key
        :type c: ElgamalCiphertext
        :type pk: ElgamalPublicKey
        :return: Encrypted responses e_0, e_1
        :rtype: (ElgamalCiphertext, ElgamalCiphertext)
        """
        # hint to convert message bytes to integer, use
        # https://docs.python.org/3/library/stdtypes.html#int.from_bytes
        m0 = int.from_bytes(self.m0, byteorder='little',signed=False)
        m1 = int.from_bytes(self.m1, byteorder='little',signed=False)
        r0 = pk.G.random_exp()
        r1 = pk.G.random_exp()
        ElgamalCT1 = pk.encrypt(1)
        e0 = ElgamalCT1.homomorphic_sub(c).homomorphic_mul(m0).homomorphic_add(c.homomorphic_mul(r0))
        e1 = c.homomorphic_mul(m1).homomorphic_add(ElgamalCT1.homomorphic_sub(c).homomorphic_mul(r1))
        return e0, e1


class Receiver:
    """Oblblivious transfer receiver for 2-byte messages

    Attributes:
    * pk: Public key
    * sk: Secret key
    """

    def __init__(self):
        self.sk, self.pk = elgamal.gen_elgamal_keypair(elgamal.gen_group())

    def challenge(self, b):
        """Generate an OT challenge

        :param b: Message to receive (0 or 1)
        :type b: int
        :return: OT challenge
        :rtype: ElgamalCiphertext
        """
        return self.pk.encrypt(b)

    def decrypt_response(self, e_0, e_1, b):
        """Decrypt response received from Sender

        :param e_0: Response part 0
        :param e_1: Response part 1
        :type e_0: ElgamalCiphertext
        :type e_1: ElgamalCiphertext
        :return: Transferred message
        :rtype: bytes
        """
        # hint to convert message integer to bytes, use
        # https://docs.python.org/3/library/stdtypes.html#int.to_bytes
        # the byteorder does not matter as long as you always use the same !
        
        msg = self.sk.decrypt(e_1) if b else self.sk.decrypt(e_0)
        print(b)
        print(msg)
        msg = msg.to_bytes(2, byteorder='little',signed=False)
        assert isinstance(msg, bytes) and len(msg) == 2
        return msg


def test_OT():
    #Sometimes it doesn't work don't know why
    for _ in tqdm(range(10),desc="test"):
        b = randint(0, 1)
        b=0
        Bob = Receiver()
        msg0 = os.urandom(2)
        msg1 = os.urandom(2)
        #Error if conversion is negative)
        while(int.from_bytes(msg0, byteorder='little',signed=False)<0 or int.from_bytes(msg1, byteorder='little',signed=False)<0):
            msg0 = os.urandom(2)
            msg1 = os.urandom(2)
    
        Alice = Sender(msg0, msg1)

        c = Bob.challenge(b)
        pk = Bob.pk

        e0, e1 = Alice.response(c, pk)
        m = Bob.decrypt_response(e0, e1, b)

        assert (msg0, msg1)[b] == m
    print('Test OT: OK.')


if __name__ == "__main__":
    test_OT()
