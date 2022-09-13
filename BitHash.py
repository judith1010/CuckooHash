import cityhash 
import random

__rnd = random.Random()   # get a random number generator for this module
__rnd.seed("BitHash random numbers") # set the RNG seed to a known value
__BitHashSeeds = None
__MAX_SEEDS = 1000

# this function causes subsequent calls to BitHash to be based on new random 
# seeds. This is useful in the event that client code needs a new hash 
# function, for example, for Cuckoo Hashing. 
def ResetBitHash():
    global __BitHashSeeds
    if not __BitHashSeeds: __BitHashSeeds = [0] * __MAX_SEEDS
    for i in range(__MAX_SEEDS): 
        __BitHashSeeds[i] = __rnd.getrandbits(64) 
        
ResetBitHash() # set up the seeds in advance of the first BitHash call

# returns a 64-bit hash value using Google's very fast and robust 
# CityHash. You can simulate having having many independent
# hash functions by specifying which hashFuncNum you want.This 
# causes a different seed to be used for each possible hashFuncNum.
def BitHash(s, hashFuncNum = 1):
    return cityhash.CityHash64WithSeed(str(s), __BitHashSeeds[hashFuncNum-1])
   
def __main():
    # use BitHash to get two hash values for each of a bunch of strings
    # and print them out.
    v1 = BitHash("foo");  v2 = BitHash("foo", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("bar");  v2 = BitHash("bar", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("baz");  v2 = BitHash("baz", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("blat"); v2 = BitHash("blat",2);  print(hex(v1), hex(v2))
    
    # now reset BitHash so that it is effectively a new set of hash functions, 
    # and print out the hash values for the same words.
    print("\nresetting BitHash to a new set of hash functions\n")
    ResetBitHash()
    
    v1 = BitHash("foo");  v2 = BitHash("foo", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("bar");  v2 = BitHash("bar", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("baz");  v2 = BitHash("baz", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("blat"); v2 = BitHash("blat",2);  print(hex(v1), hex(v2))

    # now reset BitHash again so that it is effectively yet another set of 
    # hash functiona, and print out the hash values for the same words.
    print("\nresetting BitHash to yet another set of hash functions\n")
    ResetBitHash()
    
    v1 = BitHash("foo");  v2 = BitHash("foo", 3);  print(hex(v1), hex(v2))
    v1 = BitHash("bar");  v2 = BitHash("bar", 3);  print(hex(v1), hex(v2))
    v1 = BitHash("baz");  v2 = BitHash("baz", 3);  print(hex(v1), hex(v2))
    v1 = BitHash("blat"); v2 = BitHash("blat",3);  print(hex(v1), hex(v2))

def __main2():
    numBuckets = int(input("How many buckets? "))
    while True:
        s = input("string to hash? ")
        hashValue = BitHash(s) % numBuckets
        print("Hash value:", hashValue)
        
if __name__ == '__main__':
    __main2()       
                
                       

