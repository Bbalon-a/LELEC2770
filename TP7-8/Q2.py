import os
import numpy as np


directory = os.path.dirname(os.path.realpath(__file__))
###############

# Question 2

###############
#Basket has is the csv file with 11 columns and 1000 entries (11,1000) 100 rows by ID
#11 columns for Milk, Meat, Apple, Bread, Pizza, Beer, Banana, Fish, Sugar, CornFlakes, ID
basket = np.loadtxt(directory +'/databases/basket.csv', dtype=int, delimiter=',', skiprows=1, unpack=True)

#Question 2 (a)
#List of the proba of each user (the 11th column of basket contains which user bought it)
proba_user = np.array([len(np.where(basket[10]==i)[0])/len(basket[10])for i in range(0,11)])
HU = 0
for proba in proba_user[1:]:
    HU -= proba * np.log2(proba)
print("---------------------------")
print("Q2 (a)")
print("---------------------------")
print(f"The Shannon entropy of the set of users H[U] = {round(HU,2)} bits")

#Question 2 (b)
#For only one classe it is simple, you only have to parse the data
def HI(proba_users,product,basket,HU):
    HI = HU
    for userID, prob in enumerate(proba_users):
        idx_user = np.where(basket[10]==userID)[0]
        if len(idx_user)!=0 :
            idx_product1 = np.where(basket[product]==1)[0]
            idx_product0 = np.where(basket[product]==0)[0]
            nb1 = len(np.intersect1d(idx_user,idx_product1))
            nb0 = len(idx_user)-nb1

            prob_0_knowing_u = nb0/len(idx_user) if nb0!=0 else 1 
            prob_1_knowing_u = nb1/len(idx_user) if nb1!=0 else 1

            prob_u_knowing_0 = nb0/len(idx_product0) if nb0 !=0 else 1 
            prob_u_knowing_1 = nb1/len(idx_product1) if nb1 !=0 else 1 
            HI += prob * (prob_0_knowing_u * np.log2(prob_u_knowing_0) + prob_1_knowing_u * np.log2(prob_u_knowing_1))
    return HI 

        
print("---------------------------")
print("Q2 (b)")
print("---------------------------")
print(f"The HI for milk is = {abs(round(HI(proba_user,0,basket,HU),5))} bits")
print("As HI =0, there is no information leaked by the database. It is normal as everyone as bought milk")
print("And because the list contains the same number of basket per ID")
print()
product = ["Meat","Apple","Bread","Pizza","Beer","Banana","Fish","Sugar","Corn Flakes"]
for i in range(1,10):
    print(f"The HI for {product[i-1]} is = {abs(round(HI(proba_user,i,basket,HU),5))} bits")

print("The maximal HI is with Pizza")


def int_to_list(int):
    a= [0]*10
    count = 0
    while int !=0:
        if int % 2:  #If odd
            a[count] =1
        count+=1
        int = int>>1
    return a

#For more classes, it is also simple but just to do this on all classes
def HI_all(proba_users,basket,HU):
    HI = HU 
    basket_matrix = basket.T[:,:-1] #Matrix of size (1000,10) representing the product
    products_bought = np.unique(basket_matrix,axis=0) #Stores the list of products bought without repetition
    for userID, prob in enumerate(proba_users):
        sum_product = 0
        idx_user = np.where(basket[10]==userID)[0]
        if len(idx_user!=0):
            #We only look at what is in the table
            for i in range(len(products_bought)):
                idx_product = np.where((basket_matrix== products_bought[i]).all(axis=1))[0]
                nb = len(np.intersect1d(idx_user,idx_product)) #Number of times the list of products has been bought by userID
                prob_O_knowing_u = nb/len(idx_user) if nb!=0 else 1 
                prob_u_knowing_O = nb/len(idx_product) if nb !=0 else 1 
                sum_product+=prob_O_knowing_u * np.log2(prob_u_knowing_O)
        HI+= prob*sum_product
    return HI
                
print(f"With the use of all classes the HI = {round(HI_all(proba_user,basket,HU),5)} bits")

print("---------------------------")
print("Q2 (c)")
print("---------------------------")
basket_test = np.loadtxt(directory +'/databases/basket_test.csv', dtype=int, delimiter=',', skiprows=1, unpack=True)
ID_true = np.loadtxt(directory +'/databases/user_test.csv', dtype=int, delimiter=',', skiprows=1, unpack=True)

def identification(proba_users,basket,basket_test):
    #We only do P[u|o_test] = - P[u] P[o_test|u] log(P[u|o_test])
    #Where the probabilities (P[u],P[o_test|u],log(P[u|o_test])) are computed on the database basket.csv

    basket_test = basket_test.T #Matrix of size (100,10) representing the product of the test basket
    basket_matrix = basket.T[:,:-1] #Matrix of size (1000,10) representing the product of the basket
    proba_matrix = np.zeros((len(basket_test),len(proba_users)-1),dtype=np.float64) #Store the probabilities that the ligne in basket_test belongs to user i
    for testID,products_test in enumerate(basket_test):
        for userID, prob in enumerate(proba_users):
            idx_user = np.where(basket[10]==userID)[0]
            if len(idx_user!=0):
                idx_product = np.where((basket_matrix== products_test).all(axis=1))[0]
                nb = len(np.intersect1d(idx_user,idx_product)) #Number of times the item in test has been bought by userID
                prob_O_knowing_u = nb/len(idx_user) if nb!=0 else 1 
                prob_u_knowing_O = nb/len(idx_product) if nb !=0 else 1 
                proba_matrix[testID][userID-1] = -prob* prob_O_knowing_u * np.log2(prob_u_knowing_O)

    ID_estimate = np.argmax(proba_matrix,axis=1)+1 #We only keep the maximal probability of each row because it is the most probable user
    return ID_estimate

ID_estim= identification(proba_user,basket,basket_test)
percentageTrue = sum(ID_estim==ID_true)/len(ID_true)
print("For the testing database basket_test.csv ")
print(f"The number of poeple well identified is {round(percentageTrue*100,2)} %")

