# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 14:50:27 2021

@author: RIPLECS
"""

import random 
from bitstring import BitArray
import sys


L20 = [0, 11, 15, 17]
L89 = [37, 88]
p = int('D5BBB96D30086EC484EBA3D7F9CAEB07', 16)
q = int('425D2B9BFDB25B9CF6C416CC6E37B59C1F', 16)
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
    for i in range(4):
        x1 = (a*x0 + c)%m
        res.append(bin(x1)[2:][-8:])
        x0 = x1
    return res


def LehmerHigh(a, m, c):
    x0 = python_generator(32)
    res = []
    for i in range(4):
        x1 = (a*x0 + c)%m
        res.append(bin(x1)[2:][:8])
        x0 = x1
    return res


def lfsr(state, taps, n):
    res=[]
    state0=state
    it=0
    while True:
        it+=1
        res+=[state[0]]
        state=state[1:]+[sum(state[i] for i in taps)%2]
        if state==state0 or it==2**21:
            break
    return res[:32]


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
    return BitArray(res.encode('utf-8')).bin[:32]


def rotate(v, n):
    return v[-n:] + v[:-n]


def Wolfram():
    r0 = generate_state(32)
    res = []
    for i in range(32):
        res.append(r0[-1])
        f = rotate(r0, -1)
        s = rotate(r0, 1)
        sf = [0 if s[i]==r0[i]==0 else 1 for i in range(32)]
        r = [(sf[i]+f[i])%2 for i in range(32)]
        r0 = r
    return res

  
def Blum_Mikal(a, q):
    p = 2*q + 1
    x = []
    T0 = random.randint(0, p-1)
    for i in range(32):
        T1 = (a**T0)%p
        x.append(1 if T1 < (p-1)/2 else 0)
        T0 = T1
    return x
#A = int('5B88C41246790891C095E2878880342E88C79974303BD0400B090FE38A688356', 16)
#Q = int('675215CC3E227D3216C056CFA8F8822BB486F788641E85E0DE77097E1DB049F1', 16)
A = int('5B83', 16)
Q = int('61D1', 16)

      
def BBS(p, q):
    n = p*q
    r0 = random.randint(2, n)
    x = []
    for i in range(32):
        r1 = (r0**2)%n
        x.append(r1%2)
        r0 = r1
    return x


def BBS_bytes(p, q):
    n = p*q
    r0 = random.randint(2, n)
    x = []
    for i in range(4):
        r1 = (r0**2)%n
        b = bin(r1%256)[2:]
        x.append('0'*(8 - len(b))+b)
        r0 = r1
    return x


print('1) Вбудований генератор: ', python_generator(32))
#print('2) Генератор LehmerLow: ', convert_to_int(LehmerLow(A, M, C)))
#print('3) Генератор LehmerHigh: ', convert_to_int(LehmerHigh(A, M, C)))
#print('4) Генератор L20: ', convert_to_int(lfsr(generate_state(20), L20, 20)))
#print('5) Генератор L89: ', convert_to_int(lfsr(generate_state(89), L89, 89)))
#print('6) Генератор Джиффі: ', convert_to_int(Geffe()))
#print('7) Генератор "Бібліотекар": ', convert_to_int(librarian('катерина.txt')))
print('8) Генератор Вольфрама: ', convert_to_int(Wolfram()))
print('9) Генератор Блюма-Мікалі: ', convert_to_int(Blum_Mikal(A, Q)))
#print('11) Генератор BBS: ', convert_to_int(BBS(p, q)))
#print('12) Байтовий генератор BBS: ', convert_to_int(BBS_bytes(p, q)))


