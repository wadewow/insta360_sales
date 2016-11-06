# coding=utf-8

from random import Random

def getCode(n):
    code = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    length = len(chars) - 1
    random = Random()
    for i in range(n):
        code += chars[random.randint(0, length)]
    return code


def getCode1(n):
    code = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(n):
        code += chars[random.randint(0, length)]
    return code


def calBonus(bm, bm1, bm2, bonus, bonus1, bonus2, num):
    total = 0
    if num > bm and num < bm1:
        total += bonus * (num - bm)
    elif num > bm1 and num < bm2:
        total += (bm1 - bm) * bonus + (num - bm1) * bonus1
    elif num > bm2:
        total += (bm1 - bm) * bonus + (bm2 - bm1) * bonus1 + (num - bm2) * bonus2
    return total
