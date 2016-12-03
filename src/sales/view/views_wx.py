# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from ..models import Token
from ..util.wx_option import option

import json
import sys
import time
import datetime
import urllib
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def wx_mass_message(request):
    if request.method == 'POST':
        # para = request.POST
        now = timezone.now()
        before = (now - datetime.timedelta(seconds=7100))
        result = Token.objects.filter(type=0,created_time__gte=before).order_by('-created_time').first()
        if result != None:
            access_token = result.token
        else:
            url = "https://api.weixin.qq.com/cgi-bin/token"
            values = {
                'grant_type' : 'client_credential',
                'appid': option['appid'],
                'secret': option['secret']
            }
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            print res
            res = json.loads(res)
            access_token = res['access_token']
            temp = {
                'token' : access_token
            }
            Token.objects.update_or_create(type=0,defaults=temp)

        url = "https://api.weixin.qq.com/cgi-bin/message/mass/send?access_token=" + access_token
        openId_list = []
        openId_list.append("o5zHkvhEpIZdmDlYHA7E0vwdx4w4")
        openId_list.append("o5zHkvuVF-Y9DR4fuR-ck7a5-pi0")
        values = {
            "touser": openId_list,
            "msgtype": "text",
            "text": {
                "content": "insta360 mass message test"
            }
        }
        data = json.dumps(values)
        req = urllib2.Request(url, data=data)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        res = json.loads(res)
        print res
        return JsonResponse(res, safe=False)
