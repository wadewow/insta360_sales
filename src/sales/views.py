# coding=utf-8


from models import Token


from view.views_shopkeeper import *
from view.views_store import *
from view.views_clerk import *
from view.views_sale import *
from view.views_manager import *
from view.views_account import *
from view.views_service import *
from view.views_agent import *
from view.views_wx import *
from view.views_util import *
from view.views_bi import *
from .util.wx_option import option
from .util.option import lib_path
from django.utils import timezone

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
            'appId': option['appid'],
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'signature': signature,
            'jsApiList': ['scanQRCode','closeWindow']
        }
        return JsonResponse(config, safe=False)


@csrf_exempt
def upload_pic(request):
    if request.method == 'POST':
        para = request.POST
        files = request.FILES
        print files
        print para
    

@csrf_exempt
def import_manager(request):
    if request.method == 'GET':
        for i in range(0,200):
            temp = str(i)
            n = len(temp)
            for i in range(0,4-n):
                temp = '0' + temp
            Manager.objects.update_or_create(id=temp)

        return HttpResponse('finish')
    # return render(request, 'test/test.html', {
        # 'lib_path': lib_path})


@csrf_exempt
def import_exhibition(request):
    if request.method == 'GET':
        csvfile = file('sales/exhibition.csv', 'rb')
        reader = csv.reader(csvfile)
        for line in reader:
            print line
            Exhibition.objects.update_or_create(id=line[0])
        csvfile.close()
        return HttpResponse("finish")

@csrf_exempt
def import_sale_nano(request):
    if request.method == 'GET':
        csvfile = file('sales/sale_nano.csv', 'rb')
        reader = csv.reader(csvfile)
        for line in reader:
            print line
            SaleNano.objects.update_or_create(id=line[1],name=line[0])
        csvfile.close()
        return HttpResponse('finished')

@csrf_exempt
def query_ex(request):
    if request.method == 'GET':
        para = request.GET
        if not para.__contains__('serial_number'):
            return HttpResponse('Missing serial_number')
        serial_number = para.__getitem__('serial_number')
        try:
            Exhibition.objects.get(id=serial_number)
        except:
            return HttpResponse('Exhibition does not exists')
        return HttpResponse('Exhibition exists')

@csrf_exempt
def set_offset(request):
    if request.method == 'GET':
        stores = Shop.objects.all()
        for store in stores:
            machine_serial = store.machine_serial
            if machine_serial != '':
                url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/camera/setOffsetBySerial'
                values = {
                    'serial_number': machine_serial,
                    'offset': ''
                }
                try:
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url, data=data)
                    res_data = urllib2.urlopen(req)
                    res = res_data.read()
                    res = json.loads(res)
                    if res['flag'] == 0:
                        print machine_serial
                except:
                    print 'setOffsetBySerial error'
        return HttpResponse('finish')

@csrf_exempt
def set_active(request):
    if request.method == 'GET':
        para = request.GET
        if not para.__contains__('serial_number'):
            return HttpResponse('Missing parameter serial_number')
        serial_number = para.__getitem__('serial_number')
        try:
            sale = Sale.objects.get(serial_number=serial_number)
        except:
            return HttpResponse('No information for this serial number')
        now = timezone.now()
        sale.active = 1
        sale.active_time = now
        created_time = sale.created_time
        active_time = now
        base = sale.base
        clerk_id = sale.clerk_id
        deadline = created_time + datetime.timedelta(hours=12)
        if active_time < deadline:
            device_code = sale.device_code
            if device_code == '':
                num = 1
            else:
                num = Sale.objects.filter(device_code=device_code, clerk_id=clerk_id, name='Insta360 Nano').count()
            if num < 2:
                if base == 0:
                    base = round(random.uniform(1, 10), 2)
                    if base > 3:
                        base = round((base * random.uniform(0.1, 1)), 2)
                    if base > 5.5:
                        base = round((base * random.uniform(0.2, 1)), 2)
                    if base < 1:
                        base = base * 2
                    sale.base = base
                    sale.valid = 1
                    try:
                        account = Clerk.objects.get(id=clerk_id)
                    except:
                        return HttpResponse("No clerk information")
                    if sale.name != '测试商品':
                        account.balance += base
                    account.base += base
                    account.save()
        sale.save()
        return HttpResponse('Succeed')

@csrf_exempt
def QR_code(request):
    return render(request, 'clerk/QR_code.html', {
        'lib_path': lib_path
    })

@csrf_exempt
def test(request):
    return render(request, 'test.html', {
        'lib_path': lib_path
    })

@csrf_exempt
def test1(request):
    return HttpResponse('fffff')



