"""
LELEC2770 : Privacy Enhancing Technologies

El Gamal encryption library
"""

from random import randint # Insecure randomness, better to use from "secrets" on python >= 3.6
from number import getPrime, isPrime
import math
from tqdm import tqdm

def dLog(p, g, g_m):
    """Compute the discrete log of g_m with basis g, modulo p"""
    #Baby-step giant-step algorithm 
    #See https://en.wikipedia.org/wiki/Baby-step_giant-step

    N = math.ceil(math.sqrt(p - 1))  # phi(p) is p-1 if p is prime
    # Store hashmap of g^{1...m} (mod p). Baby step.
    tbl = {pow(g, i, p): i for i in range(N)}

    # Precompute via Fermat's Little Theorem
    c = pow(g, N * (p - 2), p)

    # Search for an equivalence in the table. Giant step.
    for j in range(N):
        y = (g_m * pow(c, j, p)) % p
        if y in tbl:
            return j * N + tbl[y]

def inverse(x, p):
    """
    @returns x^-1 in Z*_p
    """
    #Compute the inverse thanks to extended euclidean algorithm
    A = x
    M = p
    m0 = M
    y = 0
    z = 1
 
    if (M == 1):
        return 0
 
    while (A > 1):
        # q is quotient
        q = A // M
 
        t = M
 
        # m is remainder now, process
        # same as Euclid's algo
        M = A % M
        A = t
        t = y
 
        # Update z and y
        y = z - q * y
        z = t
 
    # Make x positive
    if (z < 0):
        z = z + m0
 
    
    assert (z * x) % p == 1
    return z

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

QNbits=20 # @student: Is that enough ?
def gen_group(qnbits=QNbits):
    # FYI:
    # p has to be a safe prime (that is p=2*q+1 where q is prime)
    # See https://en.wikipedia.org/wiki/Safe_and_Sophie_Germain_primes
    p = 4
    while not isPrime(p):
        q = getPrime(QNbits)
        p = 2 * q + 1
    g = random_generator(p, q)
    return ElgamalGroup(p, g)

def gen_elgamal_keypair(G):
    """
        :param G: an ElgamalGroup
        @returns (x, y) with x an ElgamalSecretKey and y an ElgamalPublicKey.
    """
    sk = G.random_exp()
    x = ElgamalSecretKey(G,sk)
    y = x.pk()
    return x,y


class ElgamalGroup:
    """A group in which DDH is difficult.

    For mathematicians: the group of non-zero quadratic residues modulo p,
    where p is an odd prime such that p = 2*q+1 where q is prime.
    (The order of the group is q.)
    """
    def __init__(self, p=None, g=None):
        self.p = p
        self.g = g
        self.q = (p-1)//2
        assert self._is_correct()

    def __eq__(self, other):
        """Makes group1 == group2 work."""
        return self.p == other.p and self.q == other.q and self.g == other.g

    def __hash__(self):
        """Needed to use groups as keys of dict objects."""
        return hash((self.p, self.q, self.g))

    def __contains__(self, elem):
        """Is elem in the group ? can be use by writing 'elem in group'"""
        return 1 <= elem < self.p and pow(elem, self.q, self.p) == 1

    def __repr__(self):
        """Pretty-printing for debug."""
        return "{}(p={}, q={}, g={})".format(type(self), self.p, self.q, self.g)

    def _is_correct(self):
        """Are the parameters representing a group of prime order of quadratic
        residues modulo an odd prime ?"""
        return (
            self.p != 2 and
            isPrime(self.p) and
            isPrime(self.q) and
            self.g in self and
            self.q*2+1 == self.p and
            self.g != 1
            )

    def random_exp(self):
        """Take uniformly at random an integer in {0,...,q-1} and return it.

        Therefore, pow(self.g, self.random_exp(), self.p) is a random element
        of the group.
        """
        return randint(0, self.q-1)


class ElgamalPublicKey:
    """El Gamal public key"""

    def __init__(self, G, y):
        """G is an ElgamalGroup and y is an element of that group."""
        self.G = G
        self.y = y

    def __eq__(self, other):
        """Makes pk1 == pk2 work."""
        return self.G == other.G and self.y == other.y

    def __hash__(self):
        """Needed to use public keys as keys of dict objects."""
        return hash((self.G, self.y))

    def __repr__(self):
        """Pretty-printing for debug."""
        return "{}(y={}, G={})".format(type(self),self.y,self.G)

    def encrypt(self, m):
        """Encrypt a message.

        :param m: plaintext
        :type m: int
        :return: ElGamalCiphertext
        """
        r = self.G.random_exp()
        c1 = pow(self.G.g,r,self.G.p)
        c2 = pow(self.G.g,m)*pow(self.y,r)%self.G.p
        return ElgamalCiphertext(self.G, c1, c2)


class ElgamalSecretKey:
    """El Gamal secret key."""

    def __init__(self, G, x):
        self.G = G
        self.x = x

    def __eq__(self, other):
        return self.G == other.G and self.x == other.x

    def pk(self):
        """Generate the corresponding public key.
        
        :rtype: ElgamalPublicKey
        """
        y = pow(self.G.g,self.x,self.G.p)
        return ElgamalPublicKey(self.G, y)

    def decrypt(self, c):
        """Decrypt ciphertext c.

        :param c: cipertext
        :type c: ElgamalCiphertext
        :returns: plaintext
        :rtype: int
        """
        numL = dLog(self.G.p,self.G.g,c.c2)
        denL = dLog(self.G.p,self.G.g,pow(c.c1,self.x,self.G.p))
        return numL-denL

class ElgamalCiphertext:
    """El Gamal ciphertext.

    Thanks to group homomorphism, operations over plaintexts can be implemented
    in the ciphertext domain.
    For two ciphertexts ca, cb and an integer a,
    * ca+cb corresponds to plaintext addition (hence ciphertext multiplication)
    * a*ca corresponds to plaintext multiplication (hence ciphertext
    exponentiation)
    """
    def __init__(self, G, c1, c2):
        self.G = G
        self.c1 = c1
        self.c2 = c2

    def __eq__(self, other):
        return self.G == other.G and self.c1 == other.c1 and self.c2 == other.c2

    def __repr__(self):
        """Pretty-printing for debug."""
        return "{}(c1={}, c2={})".format(type(self), self.c1, self.c2)

    def homomorphic_add(self, other):
        """Generate a new ciphertext that encrypts the sum of the plaintexts
        corresponding to self and other.
        
        :param other: ElgamalCiphertext
        :rtype: ElgamalCiphertext
        """
        return ElgamalCiphertext(
                self.G,
                (self.c1*other.c1) % self.G.p,
                (self.c2*other.c2) % self.G.p
                )

    def homomorphic_neg(self):
        """Generate a new ciphertext that encrypts the opposite of the
        plaintext encrypted by self.

        :rtype: ElgamalCiphertext
        """
        return ElgamalCiphertext(
                self.G,
                inverse(self.c1,self.G.p),
                inverse(self.c2,self.G.p)
                )

    def homomorphic_sub(self, other):
        """Generate a new ciphertext that encrypts the subtraction of the plaintexts
        corresponding to self and other.
        
        :param other: ElgamalCiphertext
        :rtype: ElgamalCiphertext
        """
        # Hint: you can use the two methods defined above
        return self.homomorphic_add(other.homomorphic_neg())

    def homomorphic_mul(self, alpha):
        """Generate a new ciphertext that encrypts the product of alpha and the plaintext
        corresponding to self.
        
        :param alpha: int
        :rtype: ElgamalCiphertext
        """
        return ElgamalCiphertext(
                self.G,
                pow(self.c1,alpha,self.G.p),
                pow(self.c2,alpha,self.G.p)
                )
        

if __name__ == "__main__":
    # A few simple tests
    Ntests = 10
    pt_nbits = 10
    for _ in tqdm(range(Ntests),desc="DLog Testing"):
        p = getPrime(32)
        g = randint(1, p-1)
        x = randint(1, 2**pt_nbits-1)
        assert dLog(p, g, pow(g, x, p)) == x

    for _ in tqdm(range(Ntests),desc="Inverse Testing"):
        p = getPrime(32)
        x = randint(1, p-1)
        assert (inverse(x, p)*x) % p == 1
    
    for _ in tqdm(range(Ntests),desc="Gen_elgamal_keypair testing"):
        G = gen_group()
        sk, pk = gen_elgamal_keypair(G)
        assert pk == sk.pk()

    for _ in tqdm(range(Ntests),desc="Encrypt/decrypt testing"):
        G = gen_group()
        sk, pk = gen_elgamal_keypair(G)
        m = randint(0, 2**pt_nbits-1)
        assert sk.decrypt(pk.encrypt(m)) == m

    for _ in tqdm(range(Ntests),desc="Homomorphic addition testing"):
        G = gen_group()
        m1 = randint(0, 2**(pt_nbits-1)-1)
        m2 = randint(0, 2**(pt_nbits-1)-1)
        sk, pk = gen_elgamal_keypair(G)
        assert sk.decrypt(pk.encrypt(m1).homomorphic_add(pk.encrypt(m2))) == m1+m2
    
    for _ in tqdm(range(Ntests),desc="Homomorphic subtraction testing"):
        G = gen_group()
        sk, pk = gen_elgamal_keypair(G)
        m1 = randint(0, 2**(pt_nbits-1)-1)
        m2 = randint(0, 2**(pt_nbits-1)-1)
        assert sk.decrypt(pk.encrypt(m1+m2).homomorphic_sub(pk.encrypt(m2))) == m1

    for _ in tqdm(range(Ntests),desc="Homomorphic multiplication testing"):
        G = gen_group()
        sk, pk = gen_elgamal_keypair(G)
        m = randint(0, 2**(pt_nbits//2)-1)
        alpha = randint(0, 2**(pt_nbits//2)-1)
        assert sk.decrypt(pk.encrypt(m).homomorphic_mul(alpha)) == alpha*m
    print('All OK')

