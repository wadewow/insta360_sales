# coding=utf-8


from models import Token


from view.views_shopkeeper import *
from view.views_store import *
from view.views_clerk import *
from view.views_sale import *
from view.views_manager import *
from view.views_account import *

import json
import sys
import time
import datetime
import csv
import hashlib
import urllib
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')

@csrf_exempt
def index(request):
    return render(request, 'index/index.html', {
        'title': 'Index - Insta360 ',
        'msg': 'Sales.Internal For Insta360.',
        'detail': 'PYTHON / SALES.'
    })


@csrf_exempt
def logout(request):
    if request.method == 'POST':
        para = request.POST
        try:
            type = para.__getitem__('type')
            if type == "shopkeeper":
                request.session.__delitem__("shopkeeper_id")
            elif type == "clerk":
                request.session.__delitem__("clerk_id")
        except:
            return HttpResponse('logout')
        return HttpResponse('logout')
    elif request.method == 'GET':
        return HttpResponse('logout')


@csrf_exempt
def weixin(request):
    if request.method == 'GET':
        para = request.GET
        # signature = para.__getitem__('signature')
        # timestamp = para.__getitem__('timestamp')
        # nonce = para.__getitem__('nonce')
        echostr = para.__getitem__('echostr')
        return HttpResponse(echostr)
    if request.method == 'POST':
        para = request.POST
        now = timezone.now()
        before = (now - datetime.timedelta(seconds=7100))
        result = Token.objects.filter(type=0,created_time__gte=before).order_by('-created_time').first()
        if result != None:
            access_token = result.token
        else:
            url = "https://api.weixin.qq.com/cgi-bin/token"
            values = {
                'grant_type' : 'client_credential',
                'appid': 'wx9c9c45a70bb3da47',
                'secret': '3e8850494ea778835940955f02d71047'
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

        result = Token.objects.filter(type=1, created_time__gte=before).order_by('-created_time').first()
        if result != None:
            jsapi_ticket = result.token
        else:
            url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket"
            values = {
                'type': 'jsapi',
                'access_token': access_token
            }
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            print res
            res = json.loads(res)
            jsapi_ticket = res['ticket']
            temp = {
                'token': jsapi_ticket
            }
            Token.objects.update_or_create(type=1, defaults=temp)

        noncestr = 'insta360'
        timestamp = str(int(time.time()))
        url = para.__getitem__('url')

        signature = 'jsapi_ticket='+jsapi_ticket+'&noncestr='+noncestr+'&timestamp='+timestamp+'&url='+url
        signature = hashlib.sha1(signature).hexdigest()
        config = {
            'appId': 'wx9c9c45a70bb3da47',
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'signature': signature,
            'jsApiList': ['scanQRCode','closeWindow']
        }
        return JsonResponse(config, safe=False)



@csrf_exempt
def test(request):
    if request.method == 'GET':

        #
        # for i in range(0,200):
        #     temp = str(i)
        #     n = len(temp)
        #     for i in range(0,4-n):
        #         temp = '0' + temp
        #     Manager.objects.create(id=temp)

        return HttpResponse('finish')
    # return render(request, 'test/test.html', {})
