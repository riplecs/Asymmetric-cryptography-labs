# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 18:40:44 2021

@author: RIPLECS
"""


from laba1 import generate_state, lfsr, L20
from laba2 import conv, Miller_Rabin_test
import requests as r
import random
import gmpy2
import math



BITS = 2**10


def GenerateKeyPair():
    p = conv(lfsr(generate_state(20), L20, 20, BITS))
    while (p - 3)%4 != 0 or not Miller_Rabin_test(p):
        p = conv(lfsr(generate_state(20), L20, 20, BITS))
    q = conv(lfsr(generate_state(20), L20, 20, BITS))
    while (q - 3)%4 != 0 or not Miller_Rabin_test(q):
        q = conv(lfsr(generate_state(20), L20, 20, BITS))
    n = gmpy2.mul(p, q)
    b = random.randint(1, n - 1)
    return p, q, b, n
    

def ExtGCD(a, b):
    r1, r2 = a, b
    s1, s2 = 1, 0
    t1, t2 = 0, 1
    while r2 != 0:
        q = r1//r2
        r1, r2 = r2, r1 - q*r2
        s1, s2 = s2, s1 - q*s2
        t1, t2 = t2, t1 - q*t2
    return s1, t1    


def square_root(y, p, q, n):
    s1 = gmpy2.powmod(y, (p + 1)//4, p)
    s2 = gmpy2.powmod(y, (q + 1)//4, q)
    u, v = ExtGCD(p, q)
    return ((u*p*s2 + v*q*s1)%n, (u*p*s2 - v*q*s1)%n, 
         (-u*p*s2 + v*q*s1)%n, (-u*p*s2 - v*q*s1)%n)
    
    
def GenerateMessage(n):
    m = conv(lfsr(generate_state(20), L20, 20, BITS + BITS/2))
    l = math.ceil(len(bin(n)[2:])/8)
    inv2 = gmpy2.invert(2, n)
    while m <= gmpy2.isqrt(n) or len(bin(m))//8 > l - 10:
        m = conv(lfsr(generate_state(20), L20, 20, BITS + BITS/2))
    return m, l, inv2
    

def Format(m, l):
    r = random.getrandbits(64)
    return 255*(1 << (8*(l - 2))) + m*(1 << 64) +  r
    

def  Iverson_bracket(x, b, n):
    return 1 if gmpy2.jacobi(x + b*inv2, n) == 1 else 0


def Encrypt(m, l, b, n):
    x = Format(m, l)
    y = x*(x + b)%n
    c1 = int(((x + b*inv2)%n)%2)
    c2 = Iverson_bracket(x, b, n)
    return y, c1, c2


def Decrypt(y, c1, c2, b, p, q, n):
    for sq in square_root((y + (b*inv2)**2)%n, p, q, n):
        x = (-b*inv2 + sq)%n
        if int(((x + b*inv2)%n)%2) == c1:
            if Iverson_bracket(x, b, n) == c2:
                x =  bin(x)[10:-64]
                while x[0] == '0':
                    x = x[1:]
                return int(x, 2)

    
def Sign(m, l, p, q, n):
    x = Format(m, l)
    while gmpy2.jacobi(x, p) != 1 or gmpy2.jacobi(x, q) != 1:
        x = Format(m, l)
    s = random.choice(square_root(x, p, q, n))
    return s


def Verify(m, s, n):
    x = bin(s**2%n)[10:-64]
    while x[0] == '0':
        x = x[1:]
    return  int(x, 2) == m
    

def ProofProtocol():
        session = r.session()
        n = int(session.get('http://asymcryptwebservice.appspot.com/znp/'
                            'serverKey').json()['modulus'], 16)
        it = 0
        while True:
            it += 1
            t = random.randint(1, n - 1)
            y = t**2%n
            z = int(session.get('http://asymcryptwebservice.appspot.com/znp/'
                           f'challenge?y={hex(y)[2:]}').json()['root'], 16)
            if t != abs(z):
                gcd = gmpy2.gcd(z + t, n)
                if gcd != 1 and gcd != n:
                    session.close()
                    return it, int(gcd), int(gmpy2.div(n, gcd)), n


if __name__ == '__main__':
    s = r.session()
    my_p, my_q, my_b, my_n = GenerateKeyPair() 
    message, length, inv2 = GenerateMessage(my_n)
    print('\n_______Приклад обміну повідомленнями в схемі Рабіна______\n')
    print('\nНехай сайт надсилатиме нам зашифроване повідомлення.')
    site_key = s.get('http://asymcryptwebservice.appspot.com/rabin/serverKey?'
                  f'keySize={2*BITS}').json()
    print('\nОбмінюємся відкритими ключами із сайтом...')
    print('Наш відкритий ключ: ')
    print('n = ', my_n)
    print('b = ', my_b)
    print('\nВідкритий ключ cайту:')
    site_n = int(site_key["modulus"], 16)
    site_b = int(site_key["b"], 16)
    print(f'site_n = {site_n}')
    print(f'site_b = {site_b}')
    ctext = s.get('http://asymcryptwebservice.appspot.com/rabin/encrypt?'
              f'modulus={hex(my_n)[2:]}&b={hex(my_b)[2:]}&'
              f'message={hex(message)[2:]}')
    cipherText = int(ctext.json()['cipherText'], 16)
    parity = int(ctext.json()['parity'])
    jacobiSymbol = int(ctext.json()['jacobiSymbol'])
    print('\nСайт, використовуючи наш відкритий ключ, шифрує '
          'деяке повідомлення і надсилає його нам:', cipherText)
    print('\nРозшифровуємо його за допомогою свого секретного ключа...')
    dec  = Decrypt(cipherText, parity, jacobiSymbol, my_b, my_p, my_q, my_n)
    if dec == message:
        print('\nМи успішно розшифрував повідомлення:', dec)
    else:
        print('\nЩось пішло не так!')
    new_message, site_length, inv2 = GenerateMessage(site_n)
    print(f'\nЗгенеруємо нове повідомлення {new_message}, щоб зашифрувати '
          'і надіслати його сайту:')
    new_cipherText, c1, c2 = Encrypt(new_message, site_length, site_b, site_n)
    print('\nТепер надішлемо сайту наше зашифроване повідомлення: ', 
          new_cipherText)
    new_dec = s.get('http://asymcryptwebservice.appspot.com/rabin/'
                           f'decrypt?cipherText={hex(new_cipherText)[2:]}&'
                           f'expectedType=BYTES&parity={c1}&jacobiSymbol={c2}')
    new_dec  = int((new_dec.json())['message'], 16)
    if new_dec == new_message:
        print('\nCайт успішно розшифрував повідомлення:', new_dec)
    else:
        print('\nЩось пішло не так!')
    print('\n_______Розглянемо тепер приклад обміну повідомленням із цифровим' 
          ' підписом______\n')
    print('\nПідпишимо повідомлення M та надішлемо його разом із підписом'
          ' сайту:')
    signedMess = Sign(message, length, my_p, my_q, my_n)
    print('\nЦП: ', signedMess)
    check = s.get('http://asymcryptwebservice.appspot.com/rabin/verify?'
                  f'message={hex(message)[2:]}&type=BYTES&signature='
                  f'{hex(signedMess)[2:]}&modulus={hex(my_n)[2:]}').json()
    print('\nСайт перевіряє правильність цифрового підпису...')
    if check['verified']:
        print('\nВерифікація пройшла успішно!')
    else:
        print('\nЦифровий підпис невірний!')
    print('\nТепер отримаємо на перевірку підпис від сайту: ')
    new_sign = s.get('http://asymcryptwebservice.appspot.com/rabin/sign?'
                        f'message={hex(message)[2:]}&type=BYTES').json()
    new_signedMess = int(new_sign['signature'], 16)
    print(new_signedMess)
    print('\nПеревіряємо правильність цифрового підпису...')
    if Verify(message, new_signedMess, site_n):
        print('\nВерифікація пройшла успішно!')
    else:
        print('\nЦифровий підпис невірний!')
    print('\n_______Атака на протокол доведення із нульовим розголошенням'
          '_______')
    s.close()
    i, new_p, new_q, new_n = ProofProtocol()
    print(f'З {i}ї спроби знайдено розклад модуля n = {new_n} на множники:')
    print('p = ', new_p)
    print('q = ', new_q)
    print('Перевірка: n - p*q = ',new_n - new_q*new_p)
