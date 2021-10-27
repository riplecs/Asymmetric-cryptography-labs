# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 18:13:52 2021

@author: RIPLECS
"""

from laba1 import generate_state
from laba1 import lfsr
from laba1 import L20
import requests as r
import random
import gmpy2



PRIMES = [2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37, 41, 43]
BITS = 256
COMPOSITE_NUMS = []


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
        x = random.randint(2, p)
        if gmpy2.gcd(x, p) > 1:
            return False
        x = gmpy2.powmod(x, d, p)
        if x == 1 or gmpy2.sub(x, p) == -1:
            continue
        for l in range(1, s):
            x = gmpy2.powmod(x, 2, p)
            if gmpy2.sub(x, p) == -1:
                break
            elif x == 1:
                return False
            else:
                continue
        return False
    return True


def conv(lst):
    return int(''.join([str(i) for i in lst]), 2)    
    

def choice_big_prime(n0, n1, b):
    p = None
    while p == None:
        x = conv(lfsr(generate_state(20), L20, 20, b))
        while x < n0 or x > n1:
            x = conv(lfsr(generate_state(20), L20, 20, b))
        m0 = x if gmpy2.f_mod(x, 2) == 1 else x + 1
        for i in range(gmpy2.f_div(gmpy2.sub(n1, m0), 2) + 1):
            num = m0 + 2*i
            if Miller_Rabin_test(num):
                p = num
                break
            COMPOSITE_NUMS.append(num)
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


def Decrypt(cypher_message, d, public_key):
    return gmpy2.powmod(cypher_message, d, public_key[1])


def Sign(message, d, public_key):
    return (message, Decrypt(message, d, my_public_key))


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
    
    

if __name__=='__main__':
    p1 = choice_big_prime(2**(BITS - 1), 2**BITS - 1, BITS)
    q1 = choice_big_prime(2**(BITS - 1), 2**BITS - 1, BITS)
    while q1 == p1:
        q1 = choice_big_prime(2**(BITS - 1), 2**BITS - 1, BITS)
    p2 = choice_big_prime(p1, 2**BITS - 1, BITS)
    q2 = choice_big_prime(q1, 2**BITS - 1, BITS)
    while p2 == q2:
        q2 = choice_big_prime(2**(BITS - 1), 2**BITS - 1, BITS)
    d1, A_public_key = GenerateKeyPair(p1, q1)
    d2, B_public_key = GenerateKeyPair(p2, q2)
    M = conv(lfsr(generate_state(20), L20, 20, BITS))
    while M >= B_public_key[1] or M >= A_public_key[1]:
        M = conv(lfsr(generate_state(20), L20, 20, BITS))
    print('\n_______Приклади обміну повідомленнями в схемі RSA_______\n')
    print('Випадкове повідомлення:', M)
    print('\nВідкритий ключ юзера А:')
    print(f'(e1, n1) = ({A_public_key[0]}, {A_public_key[1]})')
    print('\nВідкритий ключ юзера В:')
    print(f'(e2, n2) = ({B_public_key[0]}, {B_public_key[1]})')
    C = Encrypt(M, B_public_key)
    print('\nЮзер А зашифровує повідомлення, використовуючи '
          'відкритий ключ юзера В:', C, 'і надсилає йому.')
    print('\nЮзер В розшифровує повідомлення, використовуючи  '
          'cвій секретний ключ: ', Decrypt(C, d2, B_public_key))
    print('\n* Тепер обміняємось повідомленням із сайтом.')
    print('\nНехай сайт надсилатиме юзеру А зашифроване повідомлення.')
    S_key = r.get('http://asymcryptwebservice.appspot.com/rsa/serverKey?'
                  f'keySize={2*BITS}').json()
    print('\nЮзер А обмінюється відкритими ключами із сайтом...')
    print('\nВідкритий ключ cайту:')
    print(f'(e_s, n_s) = ({int(S_key["publicExponent"], 16)},' 
          f'{int(S_key["modulus"], 16)})')
    E = hex(A_public_key[0])[2:]
    N = hex(A_public_key[1])[2:]
    C = r.get('http://asymcryptwebservice.appspot.com/rsa/encrypt?modulus='
              f"{N}&publicExponent={E}"
              f'&message={hex(M)[2:]}&type=BYTES')
    CipherText = int(C.json()['cipherText'], 16)
    print('\nСайт, використовуючи відкритий ключ юзера А, шифрує '
          'деяке повідомлення і надсилає його юзеру А:', CipherText)
    print('\nЮзер А розшифровує його за допомогою свого секретного ключа...')
    Dec = Decrypt(CipherText, d1, A_public_key)
    if Dec == M:
        print('\nЮзер А успішно розшифрував повідомлення:', Dec)
    else:
        print('\nЩось пішло не так!')
    print('\n_______Розглянемо тепер приклад обміну повідомлення із цифровим підписом_______')
    print('\nЮзер А бере свої вікриті та закриті ключі, повідомлення, '
          'робить цифровий підпис і надсилає його юзеру B:')
    signed_mess = Sign(M, d1, A_public_key)
    print('\nЦП: ', int(signed_mess[1]))
    print('\nЮзер В перевіряє правильність цифрового підпису...')
    if Verify(signed_mess, A_public_key):
        print('\nВерифікація пройшла успішно!')
    else:
        print('\nЦифровий підпис невірний!')
    print('\n* Cпробуємо тепер надіслати його сайту.')
    check = r.get('http://asymcryptwebservice.appspot.com/rsa/verify?message='
                  f'{hex(M)[2:]}&type=BYTES&signature={hex(signed_mess[1])[2:]}'
                  f'&modulus={N}&publicExponent={E}').json()
    print('\nСайт перевіряє правильність цифрового підпису...')
    if check['verified']:
        print('\nВерифікація пройшла успішно!')
    else:
        print('\nЦифровий підпис невірний!')
    print('\n_______Приклад роботи протоколу конфіденційного розсилання ключів_______')
    k = conv(lfsr(generate_state(20), L20, 20, BITS))
    while k >= A_public_key[1]:
        k = conv(lfsr(generate_state(20), L20, 20, BITS))
    print('\nЮзеру А треба конфіденційно передати юзеру В значення k:', k)
    print('\nПеревірка, чи n2 < n1...')
    if B_public_key[1] < A_public_key[1]:
        while B_public_key[1] < A_public_key[1]:
            d1, A_public_key = GenerateKeyPair(p1, q1)
        print('\nНовий відкритий ключ юзера А:')
        print(f'(e1, n1) = ({A_public_key[0]}, {A_public_key[1]})')
    else:
        print('\nКлючі юзера А не змінилися.')
    print('\nЮзер А формує повідомлення і надсилає його юзеру В: ')
    K1, S1 = SendKey(k, d1, A_public_key, B_public_key)
    print((int(K1), int(S1)))
    if ReceiveKey(d2, K1, S1, B_public_key, A_public_key):
        print('\nЮзер В отримав повідомлення, знайшов k і перевірив підпис,'
              ' все добре.')
    else:
        print('Щось пішло не так!')
    print('\n' + 100*'_')
    print('\nЗначення p і q для юзерів А та В: ')
    print('p1 = ', p1, '\nq1 = ', q1, 
          '\np2 = ', p2, '\nq2 = ', q2)
    print('\n\nДеякі числа, що не пройшли перевірку на простоту: ')
    for i in range(0, len(COMPOSITE_NUMS), 15):
        print(COMPOSITE_NUMS[i])
    #########################################################################
    site_n = int('9AAB3D2F5F7AF077F6C0D373050BE298B43585DF605DA3028583EA7E0269F'
                 'ABD601210C1B95B6B26E9F67497ADF3AAF707EDAB51BEB06E3526495B46C3FEE267', 16)
    site_e = int('10001', 16)
    while site_n < A_public_key[1]:
        d1, A_public_key = GenerateKeyPair(p1, q1)
    print('\nПублічний ключ юзера А в hex: ')
    print(hex(A_public_key[0])[2:], hex(A_public_key[1])[2:])
    print('\nСгенеруємо випадкове k: ')    
    k = conv(lfsr(generate_state(20), L20, 20, BITS))
    while k >= site_n or k >= A_public_key[1]:
        k = conv(lfsr(generate_state(20), L20, 20, BITS))
    print('k = ', hex(k)[2:])
    print('\nCформуємо повідомлення (k1, S1), використовуючи відкритий'
          ' ключ сайту: ')
    K1, S1 = SendKey(k, d1, A_public_key, (site_e, site_n))
    print('k1 = ', hex(K1)[2:], 's1 = ', hex(S1)[2:])
    print(f'http://asymcryptwebservice.appspot.com/rsa/receiveKey?key={hex(K1)[2:]}'
          f'&signature={hex(S1)[2:]}&modulus={hex(A_public_key[1])[2:]}'
          f'&publicExponent={hex(A_public_key[0])[2:]}')
 
    

