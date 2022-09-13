#I hereby certify that this program is solely the result of my own work and is in 
#compliance with the Academic Integrity policy of the course syllabus and the 
#academic integrity policy of the CS department.

from BitHash import *
import random
import pytest


class CuckooHash():

    def __init__(self, size):
        if size == 0: size = 1
        self.__arrays = [ [None] * size, [None] * size ]  # two equally sized HashArrays
        self.__numItems = 0                               # keep track of how many items were inserted


    #method that actually inserts the (k,d) and takes care of collisions, 
    #returns any tuples that were displaced in the insert process
    def __insert(self, k, d, a="start"):
        if a == "start": a = self.__arrays

        #put (k,d) where it belongs in thr first HashArray and save whatever used to be there
        hashed = BitHash(k, 1) % len(a[0])
        temp = a[0][hashed] 
        a[0][hashed] = (k, d)

        #if temp contians a tuple, a collision occured
        if temp: 
            tries = 0

            #loop 16 times or until temp is empty
            while temp and tries < 16:
                tries += 1
                #find where temp belongs in the current hashArrays
                hashed = BitHash(temp[0], tries%2+1) % len(a[tries%2])
                #switch whatever is already there with temp
                temp, a[tries%2][hashed] = a[tries%2][hashed], temp

        return temp

    #wrapper insert method, returns True if insert was successful, False otherwise
    def insert(self, k, d):
        #syntactic sugar
        a = self.__arrays

        #if Cuckoo is too full, grow the underlying hashArrays
        if self.__numItems > len(self.__arrays[0]): self.__grow()

        #find where k belongs in each hashArray
        hash1 = BitHash(k, 1) % len(a[0])
        hash2 = BitHash(k, 2) % len(a[1])

        #if k is already in either hashArray, its already been inserted, return False
        if (a[0][hash1] and a[0][hash1][0] == k) or (a[1][hash2] and a[1][hash2][0] == k): return False

        #pass (k,d) to the helper insert method 
        temp = self.__insert(k, d)

        #if temp contians a tuple, we hit an infinite loop 
        if temp: 
            self.__rehash()                      #rehash and grow the underlying hashArray
            self.__insert(temp[0], temp[1])      #pass temp to the helper insert method

        #by now, insert has been successful, increment numItems
        self.__numItems += 1                    
        return True


    #grows the underlying arrays
    def __grow(self):
        #create a new 2d list, where each hashArray is twice the size
        a = [ [None] * len(self.__arrays[0]) * 2,  [None] * len(self.__arrays[1]) * 2 ]

        #for each original HashArray
        for i in range(len(self.__arrays)):
            #for each position in the HashArray
            for j in self.__arrays[i]: 
                #if there is a tuple at that positsion
                if j: 
                    #insert that tuple into the new 2d list
                    self.__insert(j[0], j[1], a)

        self.__arrays = a


    #changes the hash functions and grows the underlying arrays 
    def __rehash(self):
        ResetBitHash()   #change the seed of the hash functions
        self.__grow()    #grow the underlying hashArrays


    #returns k's data if in the Cuckoo, None otherwise
    def find(self, k):
        #look for k in the first HashArray
        hash1 = BitHash(k, 1)%len(self.__arrays[0])
        if self.__arrays[0][hash1] and self.__arrays[0][hash1][0] == k: 
            return self.__arrays[0][hash1][1]

        #look for k in the second HashArray
        hash2 = BitHash(k, 2)%len(self.__arrays[1])
        if self.__arrays[1][hash2] and self.__arrays[1][hash2][0] == k: 
            return self.__arrays[1][hash2][1]
        
        #k is not in the CuckooHash
        return None


    #deletes k and its data and returns it as a tuple, returns None if not found
    def delete(self, k):
        #look for k in the first HashArray and delete it if found and return the deleted tuple
        hash1 = BitHash(k, 1)%len(self.__arrays[0])
        if self.__arrays[0][hash1] and self.__arrays[0][hash1][0] == k:
            temp = self.__arrays[0][hash1]
            self.__arrays[0][hash1] = None
            self.__numItems -=1
            return temp 

        #look for k in the second HashArray and delete it if found and return the deleted tuple
        hash2 = BitHash(k, 2)%len(self.__arrays[1])
        if self.__arrays[1][hash2] and self.__arrays[1][hash2][0] == k:
             temp = self.__arrays[1][hash2]
             self.__arrays[1][hash2] = None
             self.__numItems -=1
             return temp

        #k is not in the CuckooHash and does not need to be deleted
        return None


    #utility method the retuens all the (key, data) pairs in the Cuckoo, for testing
    def allTuples(self):
        a = []
        for i in self.__arrays:
            for j in i:
                if j: a += [j]
        return a 



#fake CuckooHash, implemented as a dictionary, for testing 
class FakeCuckoo():

    def __init__(self):
        self.__dict = {}

    def insert(self, k, d):
        if k in self.__dict: return False
        self.__dict[k] = d
        return True

    def find(self, k): 
        if k in self.__dict: return self.__dict[k]
        return None

    def delete(self, k):
        if k in self.__dict: return k, self.__dict.pop(k)
        return None

    def allTuples(self):
        return self.__dict.items()




#######################################
###############  TESTS  ###############
#######################################

#choose a random size for the CuckooHash tests
size = random.randint(1000, 100000)


#make sure insert works properly (everything inserted is actually there)
def test_insert():
    #create a list of (key, data) pairs 
    a = []
    for i in range(size):
        a += [(i, random.random())]

    #create a CuckooHash and insert all of the key, data pairs from a into it
    c = CuckooHash(size)
    for i in a: 
        c.insert(i[0], i[1])

    #make sure that a and the CuckooHash contian the same tuples
    assert c.allTuples().sort() == a.sort()


#make sure every value inserted in the Cuckoo can be found
def test_find():
    #create a list of (key, data) pairs
    a = []
    for i in range(size):
        a += [(i, random.random())]

    #create a CuckooHash and insert all of the key, data pairs from a into it
    c = CuckooHash(size)
    for i in a: 
        c.insert(i[0], i[1])
    
    #make sure each tuple in a can be found in the CuckooHash
    for i in a: 
        assert c.find(i[0]) == i[1]


#make sure delete actually removes the (key, data) from the CuckooHash
def test__delete():
    #create a list of (key, data) pairs
    a = []
    for i in range(size):
        a += [(i, random.random())]

    #create a CuckooHash and insert all of the key, data pairs from a into it
    c = CuckooHash(size)
    for i in a: 
        c.insert(i[0], i[1])

    #delete everything in a from the CuckooHash
    for i in a:
        c.delete(i[0])

    #make sure nothing from a can be found in the CuckooHash
    for i in a: 
        assert not c.find(i[0])

    #make sure no key, data pairs are left in the CuckooHash
    assert len(c.allTuples()) == 0


#assert that nothing can be found or deleted in an empty Cuchoo
def test_emptyCuckoo():

    c = CuckooHash(size)

    for i in range(size):
        assert not c.find(random.random())
        assert not c.delete(random.random())

#test CuckooHashes of differnt sizes that only have one element in them
def test_oneCuckoo():
    a = CuckooHash(1)
    b = CuckooHash(10)
    c = CuckooHash(100)
    d = CuckooHash(1000)
    e = CuckooHash(10000)
    f = FakeCuckoo()

    val = 1234

    for i in [a, b, c, d, e, f]:
        assert i.insert(val, str(val)) 

    for i in [a, b, c, d, e, f]:
        assert i.find(val) == str(val)
        assert not i.find(5678)

    for i in [a, b, c, d, e, f]:
        assert i.delete(val) == (val, str(val))
        assert len(i.allTuples()) == 0


#test a normal CuckooHash (size 1000)   
def test_normalTest():

    c = CuckooHash(1000)
    f = FakeCuckoo()

    for i in range(1000):
        c.insert(str(i), str(i))
        f.insert(str(i), str(i))

    for i in range(1000):
        assert c.delete(str(i)) == f.delete(str(i))


#test CuckooHash when it will have to grow to accomodate its inserts
def test_growCuckoo():
    
    c = CuckooHash(1)
    
    for i in range(100):
        c.insert(i, random.random())

    for i in range(100):
        assert c.find(i)


#test insert when the same key is inserted twice
def test_insertDuplicates():

    c = CuckooHash(size)
    
    for i in range(size):
        c.insert(i, str(i))
        assert not c.insert(i, str(i))


#test CuckooHash when the keys are strings
def test_stringCuckoo():

    c = CuckooHash(size)
    f = FakeCuckoo()

    for i in range(size):
        assert c.insert(str(i), i) == f.insert(str(i), i)

    for i in range(size):
        assert c.find(str(i)) == f.find(str(i))

    for i in range(size):
        assert c.delete(str(i)) == f.delete(str(i))


#torture test
def test_torture():

    c = CuckooHash(size)
    f = FakeCuckoo()
    a = [c.insert, c.find, c.delete]
    arr = [f.insert, f.find, f.delete]

    for i in range(size):
        #choose a random CuckooHash method
        method = random.randint(0, 2)
        key = random.random()

        #if its insert, create data and try to insert
        if method == 0: 
            data = random.random()
            assert a[method](key, data) == arr[method](key, data)
        
        #otherwise, a key is enough to try to find or delete
        else:
            assert a[method](key) == arr[method](key)




pytest.main(["-v", "-s", "CuckooHash.py"])  