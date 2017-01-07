# coding=utf-8

from random import Random
import random
import urllib
import urllib2
import json
from wx_option import option

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


def getBaseBonus():
    base = round(random.uniform(1, 10), 2)
    if base > 3:
        base = round((base * random.uniform(0.1, 1)), 2)
    if base > 5.5:
        base = round((base * random.uniform(0.2, 1)), 2)
    if base < 1:
        base = round(random.uniform(1, 2), 2)
    return base


def calBonus(bm, bm1, bm2, bonus, bonus1, bonus2, num):
    total = 0
    if num > bm and num < bm1:
        total += bonus * (num - bm)
    elif num > bm1 and num < bm2:
        total += (bm1 - bm) * bonus + (num - bm1) * bonus1
    elif num > bm2:
        total += (bm1 - bm) * bonus + (bm2 - bm1) * bonus1 + (num - bm2) * bonus2
    return total


def getOpenid(code):
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    values = {
        'appid': option['appid'],
        'secret': option['secret'],
        'code': code,
        'grant_type': 'authorization_code',
    }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data=data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    res = json.loads(res)

    try:
        openid = res['openid']
    except:
        openid = ''
    return openid
