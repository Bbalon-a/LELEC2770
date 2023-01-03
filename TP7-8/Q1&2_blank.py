import os
import numpy as np

directory = os.path.dirname(os.path.realpath(__file__))

chols, ages = np.loadtxt(directory +'/diabetes1.csv', dtype=int, delimiter=',', skiprows=1, unpack=True, usecols=(0,2,))
locs, genders = np.loadtxt(directory +'/diabetes1.csv', dtype=str, delimiter=',', skiprows=1, unpack=True, usecols=(1, 3,))

assert(len(chols) == len(ages) == len(locs) == len(genders))

def k_anon(chols, ages, locs, genders):
    pass

### 

def distance(x, xprime, normalizer):
    return abs((x-xprime)/float(normalizer))

