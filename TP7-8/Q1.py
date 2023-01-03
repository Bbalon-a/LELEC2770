import os
import numpy as np
from collections import Counter

directory = os.path.dirname(os.path.realpath(__file__))
###############

# Question 1

###############
#Loading of the diabete databases
chols, ages = np.loadtxt(directory +'/databases/diabetes1.csv', dtype=int, delimiter=',', skiprows=1, unpack=True, usecols=(0,2,))
locs, genders = np.loadtxt(directory +'/databases/diabetes1.csv', dtype=str, delimiter=',', skiprows=1, unpack=True, usecols=(1, 3,))
height, waist = np.loadtxt(directory +'/databases/diabetes2.csv', dtype=int, delimiter=',', skiprows=1, unpack=True, usecols=(0,2,))
frame = np.loadtxt(directory +'/databases/diabetes2.csv', dtype=str, delimiter=',', skiprows=1, unpack=True, usecols=(1,))

#Verification
assert(len(chols) == len(ages) == len(locs) == len(genders))
assert(len(height)== len(waist)== len(frame))

#Question 1.a

#K-anonymity
def k_anon_diabete1(chols, ages, locs, genders):
    set = [(chols[i],locs[i],ages[i],genders[i]) for i in range(len(chols))]
    counter = Counter(set)
    occurence_list = counter.most_common() #Return list of (attribute, occurence) from most common to less common
    return occurence_list[-1][1],set

def k_anon_diabete2(height,waist,frame):
    set = [(height[i],frame[i],waist[i]) for i in range(len(frame))]
    counter = Counter(set)
    occurence_list = counter.most_common() #Return list of (attribute, occurence) from most common to less common
    return occurence_list[-1][1],set

k_1,set1 = k_anon_diabete1(chols,ages,locs,genders)
k_2,set2 = k_anon_diabete2(height,waist,frame)
print("---------------------------")
print("Q1 (a)")
print("---------------------------")
print(f"The K-anonymity of diabete 1 is K = {k_1}")
print(f"The K-anonymity of diabete 2 is K = {k_2}")

#Question 1.b

#To increase the K-anonymity, one can replace some columns by their mean
def k_anon_max_diabete1(chols,ages,locs,genders):
    #We remove the cholesterols and the ages by replacing it with the mean
    chols_mean = np.array([np.mean(chols)]*len(chols))
    age_mean   = np.array([np.mean(ages)]*len(ages))
    new_set= [(chols_mean[i],locs[i],age_mean[i],genders[i]) for i in range(len(chols_mean))]
    counter = Counter(new_set)
    return counter.most_common()[-1][1],new_set

def k_anon_max_diabete2(height,frame,waist,mean_per_class=True):
    #Frame has 3 possible values, therefore the mean can be done on the
    #all data or for each of the 3 classes (small, medium, large)
    if mean_per_class:
        idx_s = np.where(frame=='small')[0]
        idx_m = np.where(frame=='medium')[0]
        idx_l = np.where(frame=='large')[0]
        height_mean = np.zeros(len(height))
        waist_mean  = np.zeros(len(waist))
        height_mean[idx_s] = np.mean(height[idx_s])
        height_mean[idx_m] = np.mean(height[idx_m])
        height_mean[idx_l] = np.mean(height[idx_l])
        waist_mean[idx_s] = np.mean(waist[idx_s])
        waist_mean[idx_m] = np.mean(waist[idx_m])
        waist_mean[idx_l] = np.mean(waist[idx_l])
    else:
        height_mean = np.array([np.mean(height)]*len(height))
        waist_mean   = np.array([np.mean(waist)]*len(waist))
    new_set = [(height_mean[i],frame[i],waist_mean[i]) for i in range(len(frame))]
    counter = Counter(new_set)
    return counter.most_common()[-1][1],new_set

k_max1, set_max1 = k_anon_max_diabete1(chols,ages,locs,genders)
k_max2, set_max2 = k_anon_max_diabete2(height,frame,waist,mean_per_class=False)
k_max2_true, set_max2_true = k_anon_max_diabete2(height,frame,waist)

print("---------------------------")
print("Q1 (b)")
print("---------------------------")
print(f"K-anonymity max for diabete1.csv is {k_max1}")
print(f"K-anonymity max for diabete2.csv is {k_max2}")
print(f"K-anonymity max for diabete2.csv is {k_max2_true} if mean done per classe")

#Question 1.c
#Compute the distortion between the databases 
def distance_element(x, xprime):
    assert len(x) == len(xprime) 
    
    if len(x) == 3:
        xH, xF, xW = x
        xprimeH, xprimeF, xprimeW = xprime
        d=0
        d+= np.abs(xH-xprimeH)/15
        if(xF =='small' and xprimeF =='large') or (xF =='large' and xprimeF =='small'):
            d+=2
        elif xF == xprimeF:
            d+=0
        else:
            d+=1
        d+= np.abs(xW-xprimeW)/20
    elif len(x) == 4:
        xC, xL, xY, xG = x
        xprimeC, xprimeL, xprimeY, xprimeG = xprime
        d = 0 
        d += np.abs(xC - xprimeC)/100
        d += np.abs(xY - xprimeY)/50
        if( xL != xprimeL):
            d+=1
        if(xG != xprimeG):
            d+=1
    else:
        assert ValueError

    return d


def distance_db(x,xprime):
    d = 0
    for i in range(len(x)):
        d+=distance_element(x[i],xprime[i])
    return d
print("---------------------------")
print("Q1 (c)")
print("---------------------------")
print(f"Distance between set1 and set1 modified = {round(distance_db(set1,set_max1),3)}")
print(f"Distance between set2 and set2 modified = {round(distance_db(set2,set_max2),3)}")
print(f"Distance between set2 and set2 modified = {round(distance_db(set2,set_max2_true),3)} if mean is done per classe")

print("---------------------------")
print("Q1 (d)")
print("---------------------------")
print("The more you want to increase the k-anonymity, the more the data becomes useless in term of statistic.")
print("Bigger distances between the inital set and the modified ones, means less usefull data for a better anonymity.")
print("This is a tradoff between anonymity and utility of databases.")
print()
print("Bonus:")
print("The distance should decrease compared to the ones obtained in (c)")

print("---------------------------")
print("Q1 (e)")
print("---------------------------")
print("The drawback of K-anonymity is if there is only one entry then K =1.")
print("Differential privacy stores the differences between what was written before and after")
