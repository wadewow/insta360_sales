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
