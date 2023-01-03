#!/usr/bin/env python

from __future__ import print_function
from random import randint
from sys import argv, stdout

from fastecdsa.curve import P256
from fastecdsa.point import Point
from tqdm import tqdm
from mathutil import p256_mod_sqrt, mod_inv

def take30bytes(x):
    return x & (2**(8*30)-1)

class DualEC():
    def __init__(self, seed, P, Q):
        self.seed = seed
        self.P = P
        self.Q = Q

    def genbits(self):
        """Returns a pseudo-random integer of 30 bytes"""
        t = self.seed
        s = (t * self.P).x
        self.seed = s
        r = (s * self.Q).x
        return take30bytes(r)  # return 30 bytes


def backdoor_sanity_check(P, Q, d):
    # Verify that we have the backdoor (i.e P == d*Q)
    assert(d * Q == P)


def find_point_on_p256(x):
    """If x is such that there exists a point (x, y) on the curve P256, then
    return that point. Otherwise, return None."""
    # equation: y^2 = x^3-ax+b
    y2 = (x * x * x) - (3 * x) + P256.b
    y2 = y2 % P256.p
    y = p256_mod_sqrt(y2)
    if y2 == (y * y) % P256.p:
        return Point(x, y, curve=P256)
    else:
        return None


def gen_backdoor():
    """Generate backdored Dual EC parameters P = d*Q."""
    P = P256.G  # dual EC says set P to P256 base point
    d = randint(2, P256.q)  # pick a number that is in the field P256 is over
    # TO COMPLETE: set Q
    # You may find the function mod_inv (from file mathutil.py) useful; P256.q
    # is the (prime) number of points in the curve.
    
    #The backdoor implemented if P = dQ then Q is chosen as:  Q = P d^-1
    Q = P * mod_inv(d,P256.q)
    # /TO COMPLETE

    backdoor_sanity_check(P, Q, d)

    print('P = ({:x}, {:x})'.format(P.x, P.y))
    print('Q = ({:x}, {:x})'.format(Q.x, Q.y))
    print('d = {:x}'.format(d))

    return P, Q, d

def take26bytes(next_output):
    return next_output & 2**(8*26)-1

def take4MSBytes(next_output):
    return next_output >> (8*26)

def gen_prediction(observed1, observed2, P, Q, d):
    """Given a 34 bytes observation of the output of the backdored (P, Q, d)
    dual EC generator, predict the next 26 bytes of output.
    """
    
    for high_bits in tqdm(range(2**16)):
        # Set the 16 most significant bits to the guess value
        guess = (high_bits << (8 * 30)) | observed1
        # TO COMPLETE
        # You may find the following functions to be useful:
        # find_point_on_p256, take26bytes, take4MSBytes
        
        #observed1 = r1' where r1 = 16bits|r1' with r1' 30 bytes long
        #r1 = x(s1 Q) --> R1 = s1 Q
        R1 = find_point_on_p256(guess)
        if R1 is not None:
            #If a point is found one the curve, one has to check if it works or not with the observed2 value
            #r2' = observed2|26bytes with r2' being 30 bytes long

            #S2 = x(s1 P)= x(R1 Q^-1 P) = x(R1 d) as the backdoor set P = dQ
            S2_guess = (R1 * d).x
            #R2 = S2 Q --> r2 = x(S2 Q)
            #r2 is 32bytes long with r2 = 2bytes|r2' = 2bytes|observed2|26bytes 
            if(take4MSBytes(take30bytes((S2_guess*Q).x)) == observed2):
                #Then the 4 most significant bytes are the same and it is the good point 
                #We only return the 26 first bytes of r2 for the verification
                return take26bytes((S2_guess*Q).x)
        # /TO COMPLETE

    raise ValueError("Invalid obseved bytes wrt Q and d")


def main():
    P, Q, d = gen_backdoor()
    # seed is some random value
    seed = randint(1, 2**30)
    dualec = DualEC(seed, P, Q)
    bits1 = dualec.genbits()
    bits2 = dualec.genbits()

    # We observe 34 bytes of output of the PRG
    # first: the 30 bytes from the first PRG computation
    observed1 = bits1
    # second: 4 bytes from the second PRG computation
    observed2 = (bits2 >> (26 * 8))
    print('Observed 34 bytes:\n({:x}, {:x})'.format(observed1, observed2))

    # We have to predict the other 26 bytes from the second PRG computation
    predicted = gen_prediction(observed1, observed2, P, Q, d)
    print('Predicted 26 bytes:\n{:x}'.format(predicted))

    # The actual other 26 bytes from the second PRG computation
    actual = bits2 & (2**(8 * 26) - 1)
    print('Actual 26 bytes:\n{:x}'.format(actual))

    print('Actual matches prediction:', actual == predicted)


if __name__ == '__main__':
    main()
