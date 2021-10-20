# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 18:13:52 2021

@author: RIPLECS
"""

from laba1 import generate_state
from laba1 import lfsr
from laba1 import L20
import random
import gmpy2
import time


PRIMES = [2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37, 41, 43]
BITS = 32


def decomposition(n):
    numbers = []
    while gmpy2.f_mod(n, 2) == 0:
        numbers.append(2)
        n = gmpy2.div(n, 2)
    if n > 1:
        numbers.append(int(n))
    return numbers.count(2), numbers[-1]


def trial_division(n):
    for num in PRIMES:
        if gmpy2.f_mod(n, num) == 0:
            return False
    return True
            
    
def Miller_Rabin_test(p, k = 1000):
    if not trial_division(p):
        return False
    s, d = decomposition(p-1)
    for it in range(k):
        triger = None
        x = random.randint(2, p)
        if gmpy2.gcd(x, p) > 1:
            return False
        x = gmpy2.powmod(x, d, p)
        if x == 1 or gmpy2.sub(x, p) == -1:
            continue
        for r in range(1, s):
            x = gmpy2.powmod(x, 2, p)
            if gmpy2.sub(x, p) == -1:
                triger = True
                break
            elif x == 1:
                return False
            else:
                continue
        if triger:
            continue
        return False
    return True


def conv(lst):
    return int(''.join([str(i) for i in lst]), 2)    
    

def choice_big_prime(n0, n1, b):
    p = None
    while p == None:
        x = conv(lfsr(generate_state(20), L20, 20, b))
        while x < n0:
            x = conv(lfsr(generate_state(20), L20, 20, b))
        m0 = x if gmpy2.f_mod(x, 2) == 1 else x + 1
        for i in range(gmpy2.f_div(gmpy2.sub(n1, m0), 2) + 1):
            if Miller_Rabin_test(m0 + 2*i):
                p = m0 + 2*i
                break
    return p


def GenerateKeyPair(p, q):
    n = gmpy2.mul(p, q)
    oiler = gmpy2.mul(p - 1, q - 1)
    e = random.randint(2, oiler - 1)
    while gmpy2.gcd(e, oiler) > 1:
        e = random.randint(2, oiler - 1)
    d = gmpy2.invert(e, oiler)
    return d, (e, n)


def Encrypt(message, public_key):
    return gmpy2.powmod(message, public_key[0], public_key[1])


def Sign(message, d, public_key):
    return (message, Encrypt(message, d, public_key[1]))
 
    
def Decrypt(cypher_message, d, public_key):
    return gmpy2.powmod(cypher_message, d, public_key[1])


def Verify(sign, public_key):
    return Encrypt(sign[1], public_key) == sign[0]

    
def SendKey(k, d, my_public_key, public_key):
    k1 = Encrypt(k, public_key)
    s = Decrypt(k, d, my_public_key)
    s1 = Encrypt(s, public_key)
    return (k1, s1)
    
    
def ReceiveKey(d1, k1, s1, my_public_key, public_key):
    k = Decrypt(k1, d1, my_public_key)
    s = Decrypt(s1, d1, my_public_key)
    return k == Encrypt(s, public_key)
    
