from number import getPrime, isPrime 
from random import randint

class Group:
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

    return p, g


def dLog(p, g, g_m):
    """Compute the discrete log of g_m with basis g, modulo p"""
    gg = 1
    for i in range(0, 2 ** 20):
        if gg == g_m:
            return i
        gg = (gg*g)%p

def inverse(x, p):
    """
    @returns x^-1 in Z*_p
    """

    res = pow(x, p-2, p)
    assert (res * x) % p == 1
    return res


