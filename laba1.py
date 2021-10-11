# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 14:50:27 2021

@author: RIPLECS
"""

from collections import Counter
from bitstring import BitArray
import numpy as np
import random 
import gmpy2
import time

alphas = [0.01, 0.05, 0.1]
quantiles = {0.01: 2.326347874, 0.05: 1.644853627, 0.1: 1.281551566}

L20 = [0, 11, 15, 17]
L89 = [37, 88]
#Bluma-Mikala
A = int('5B88C41246790891C095E2878880342E88C79974303BD0400B090FE38A688356', 16)
Q = int('675215CC3E227D3216C056CFA8F8822BB486F788641E85E0DE77097E1DB049F1', 16)
P = int('CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3', 16)
#BBS
p = int('D5BBB96D30086EC484EBA3D7F9CAEB07', 16)
q = int('425D2B9BFDB25B9CF6C416CC6E37B59C1F', 16)
#Lehmer
A = 2**16 + 1
M = 2**32
C = 119


def python_generator(k):
    return random.getrandbits(k)


def generate_state(k):
    result = []
    for i in range(k):
        result.append(random.choice([0, 1]))
    if result == k*[0]:
        result = generate_state(k)
    return result
 
    
def convert_to_int(vec):
    return int(''.join(map(str, vec)), 2)


def LehmerLow(a, m ,c):
    x0 = python_generator(32)
    res = []
    for i in range(2**18):
        x1 = (a*x0 + c)%m
        b = bin(x1)[2:]
        res.append(('0'*(32 - len(b)) + b)[-8:])
        x0 = x1
    return [int(i, 2) for i in res]


def LehmerHigh(a, m, c):
    x0 = python_generator(32)
    res = []
    for i in range(2**18):
        x1 = (a*x0 + c)%m
        b = bin(x1)[2:]
        res.append(('0'*(32 - len(b)) + b)[:8])
        x0 = x1
    return [int(i, 2) for i in res]


def lfsr(state, taps, n, lim = 2**21):
    res = []
    state0 = state
    it = 0
    while True:
        it += 1
        res += [state[0]]
        state = state[1:] + [sum(state[i] for i in taps)%2]
        if state == state0 or it == lim:
            return res[:2**21]


def Geffe():
    res=[]
    x0 = generate_state(11)
    y0 = generate_state(9)
    s0 = generate_state(10)
    x=lfsr(x0, [0, 2], 11)
    y=lfsr(y0, [0, 1, 3, 4], 9)
    s=lfsr(s0, [0, 3], 10)
    for i in range(len(y)):
        res=res+[x[i] if s[i]==1 else y[i]]
    return res


def librarian(file):
    text = open(file, 'r')
    res = ''.join(text)
    text.close()
    return BitArray(res.encode('utf-8')).bin[:2**21]


def Wolfram():
    r0 = generate_state(32)
    res = []
    for i in range(2**21):
        res.append(r0[-1])
        f = r0[1:] + r0[:1]
        s = r0[-1:] + r0[:-1]
        sf = [0 if s[i]==r0[i]==0 else 1 for i in range(32)]
        r = [(sf[i]+f[i])%2 for i in range(32)]
        r0 = r
    return res

  
def Blum_Mikal(a, q, p):
    x = []
    T0 = random.randint(0, p-1)
    for i in range(2**21):
        T1 = gmpy2.powmod(a, T0, p)
        x.append(1 if T1 < (p-1)/2 else 0)
        T0 = T1
    return x


def Blim_Mikal_bytes(a, q, p):
    x = []
    T0 = random.randint(0, p-1)
    b = gmpy2.div((p-1), 256)
    for i in range(2**18):
        T1 = gmpy2.powmod(a, T0, p)
        k = 0
        while gmpy2.mul(k, b) >= T1 or gmpy2.mul(k + 1, b) < T1:
            k+=1
        k = bin(k)[2:]
        x.append('0'*(8 - len(k)) + k)
        T0 = T1
    return [int(i, 2) for i in x]

      
def BBS(p, q):
    n = p*q
    r0 = random.randint(2, n)
    x = []
    for i in range(2**21):
        r1 = (r0**2)%n
        x.append(r1%2)
        r0 = r1
    return x


def BBS_bytes(p, q):
    n = p*q
    r0 = random.randint(2, n)
    x = []
    for i in range(2**18):
        r1 = (r0**2)%n
        b = bin(r1%256)[2:]
        x.append('0'*(8 - len(b))+b)
        r0 = r1
    return [int(i, 2) for i in x]


def check_hypothesis(hi, l):
    print('   χ2 = ', hi)
    for alpha in alphas:
        hi2_alpha = np.sqrt(2*l)*quantiles[alpha] + l
        if hi <= hi2_alpha:
            print(f'   Test passed with α = {alpha}, χ2_(1-α) = {hi2_alpha}')
        else:
            print(f'   Test failed with α = {alpha}, χ2_(1-α) = {hi2_alpha}')



def equiprobability_test(nums, l = 255):
    n = len(nums)/256
    vi = []
    for j in range(256):
        vi.append(nums.count(j))
    hi2 = sum(((vi[i] - n)**2)/n for i in range(256))
    check_hypothesis(hi2, l)

            
  
def independence_test(nums, l = 65025):
    n = int(len(nums)/2)
    pairs = [(nums[2*i], nums[2*i - 1]) for i in range(n)]
    v = np.zeros((256, 256))
    unique_pairs = Counter(pairs)
    for pair in unique_pairs:
        v[pair[0]][pair[1]] = unique_pairs[pair]
    vi = [sum(v[i][j] for j in range(256)) for i in range(256)]
    alpha = [sum(v[i][j] for i in range(256)) for j in range(256)]
    hi2 = 0
    for i in range(256):
        for j in range(256):
            if vi[i]*alpha[j]!=0:
                hi2 += ((v[i][j]**2)/(vi[i]*alpha[j]))
    hi2 = n*(hi2 - 1)
    check_hypothesis(hi2, l)
            
            
def homogeneity_test(nums, r = 16):
    m_ = int(len(nums)/r)
    n = m_*r 
    l = 255*(r - 1)
    strings = []
    for i in range(0, len(nums), m_):
        strings.append(nums[i: i + m_])
    v = np.zeros((256, r))
    for i in range(256):
        for j in range(r):
            v[i][j] = strings[j].count(i)
    vi = [sum(v[i][j] for j in range(r)) for i in range(256)]
    alpha = m_
    hi2 = 0
    for i in range(256):
        for j in range(r):
            if vi[i] != 0 :
                hi2 += (v[i][j]**2)/(vi[i]*alpha)
    hi2 = n*(hi2 - 1)
    check_hypothesis(hi2, l)
    

def group_to_bytes(vect):
    if len(vect)%8!=0:
        vect = '0'*(8 - len(vect)%8) + vect
    result = []
    for i in range(0, len(vect), 8):
        result.append(int(vect[i:i+8], 2))
    return result


def conv(lst):
    return group_to_bytes(''.join([str(i) for i in lst]))


def main():
    start_time = time.time()
    
    geffe = Geffe()
    while len(geffe) < 2**21:
        geffe += Geffe()
    
    gens = {'DEFAULT GENERATOR' : group_to_bytes(bin(python_generator(2**21))[2:]), 
            'LEHMER LOW' : LehmerLow(A_L, M_L, C_L),
            'LEHMER HIGH' : LehmerHigh(A_L, M_L, C_L),
            'L20' : conv(lfsr(generate_state(20), L20, 20)),
            'L89' : conv(lfsr(generate_state(89), L89, 89)),
            'GEFFE' : conv(geffe),
            'LIBRARIAN' : group_to_bytes(librarian('voina-i-mir.txt')),
            'WOLFRAM' :  conv(Wolfram()), 
            'BlUMA-MIKALA' : conv(Blum_Mikal(A, Q, P)),
            'BYTES BlUMA-MIKALA' : Blum_Mikal_bytes(A, Q, P),
            'BBS' : conv(BBS(p, q)),
            'BYTES BBS' : BBS_bytes(p, q)
            }

    print('Generation time: %s seconds ' % (time.time() - start_time))
    start_time = time.time()

    for gen in gens:
        print(f'\n           {gen}\n')
        print('1. Equiprobability test: ')
        equiprobability_test(gens[gen])
        print('2. Independence test: ')
        independence_test(gens[gen])
        print('3. Homogeneity test: ')
        homogeneity_test(gens[gen])

    print('Testing time: %s seconds ' % (time.time() - start_time))

if __name__ == '__main__':
    main()
