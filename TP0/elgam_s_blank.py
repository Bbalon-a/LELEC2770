from random import randint # Insecure randomness, better to use from "secrets" on python >= 3.6
from number import getPrime, isPrime

NBITS = 64

def gen_pq():
    # FYI:
    # p has to be a safe prime (that is p=2*q+1 where q is prime)
    # See https://en.wikipedia.org/wiki/Safe_and_Sophie_Germain_primes
    p = 4
    while not isPrime(p):
        q = getPrime(NBITS)
        p = 2 * q + 1
    return p, q

def random_generator(p, q):
    """
    Take uniformly at random a generator of the group.
    Since the group is cyclic and of prime order,
    any (non-unitary) element is a generator.
    """
    # FYI:
    # The group is the group of quadratic residues modulo p, that is,
    # the group of squares in Z*_p, or
    # the set of x in Z such that there exists a y such that x = y^2 mod p
    g_prime = randint(2, p - 1) # Take any (non-unity) element of Z*_p
    g = pow(g_prime, 2, p)  # Squaring it gives generator of the group
    assert pow(g, q, p) == 1
    return g

def dLog(p, g, g_m):
    """
        @returns Compute the discrete log of g_m with basis g, modulo p

        Make the simplest, most inefficient algorithm :-)

        (you're welcome to make an efficient one tho)
    """
    pass


def inverse(x, p):
    """
    @returns x^-1 in Z*_p
    """
    pass

def gen_elgamal_keypair(g, p, q):
    """
        @returns x, y with x the private key and y the public key
    """
    pass

def elgamal_encrypt(g, p, q, m, y):
    """
        @returns ciphertext c = (c1, c2)
    """
    pass

def elgamal_decrypt(g, p, q, x, c1, c2):
    """
        @returns the decrypted message m
    """
    pass


if __name__ == "__main__":
    p, q = gen_pq()
    g = random_generator(p, q)
    x, y = gen_elgamal_keypair(g, p, q)
    c1, c2 = elgamal_encrypt(g, p, q, 42, y)
    c3, c4 = elgamal_encrypt(g, p, q, 10, y)
    assert 42 == elgamal_decrypt(g, p, q, x, c1, c2)
    # Wow, elgmal is additively homomorphic! Could you also write the maths on
    # paper?
    c5, c6 = c1 * c3 % p, c2 * c4 % p
    assert 52 == elgamal_decrypt(g, p, q, x, c5, c6)
    print("OK!")

