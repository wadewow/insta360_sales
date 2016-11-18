# coding=utf-8

from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils import timezone

from ..util.option import lib_path
from ..models import CashRecord
from ..models import SerialToInter

import urllib
import urllib2
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

@csrf_exempt
def service_login(request):
    if request.method == 'GET':
        return render(request, 'service/login.html', {
            'lib_path': lib_path
        })


@csrf_exempt
def cash_query(request):
    if request.method == 'GET':
        if not request.session.__contains__('manager_id'):
            return redirect('/sales/service/login')
        return render(request, 'service/cash_query.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        code = para.get('code','')
        try:
            record = CashRecord.objects.get(code=code)
        except ObjectDoesNotExist:
            return render(request, 'service/cash_query.html', {
                'exsit': 0,
                'lib_path': lib_path
            })
        return render(request, 'service/cash_query.html', {
            'exsit': 1,
            'record': record,
            'lib_path': lib_path
        })


@csrf_exempt
def service_cash(request):
    if request.method == 'GET':
        return redirect('/sales/cash_query')
    if request.method == 'POST':
        para = request.POST
        id = para.get('id', '')
        wechat = para.get('wechat','')
        if id == '':
            return redirect('/sales/cash_query')
        try:
            record = CashRecord.objects.get(id=id)
        except ObjectDoesNotExist:
            return render(request, 'service/cash_query.html', {
                'exsit': 0,
                'lib_path': lib_path
            })
        record.wechat = wechat
        record.save()

        return render(request, 'service/cash_query.html', {
            'exsit': 1,
            'record': record,
            'lib_path': lib_path
        })


@csrf_exempt
def service_serial_to_inter(request):
    if request.method == 'GET':
        if not request.session.__contains__('manager_id'):
            return redirect('/sales/service/login')
        return render(request, 'service/serial_to_inter.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        if not para.__contains__('serial_number'):
            return render(request, 'service/serial_to_inter.html', {
                'lib_path': lib_path
            })
        serial_number = para.__getitem__('serial_number')
        # serial_number = serial_number.strip()
        url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/camera/setNanoedition'
        values = {
            'serial_number': serial_number,
            'type': 2
        }
        try:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            res = json.loads(res)
            print res
            flag = res['flag']
            if flag == 1:
                result = '成功设置为国际货'
                now = timezone.now()
                temp = {
                    'update_time': now
                }
                SerialToInter.objects.update_or_create(id=serial_number, defaults=temp)
            else:
                data = res['data']
                if data == 'deal fail':
                    result = '该序列号已经是国际货'
                else:
                    result = '序列号不存在'
            return HttpResponse(result)
        except:
            return HttpResponse('网络错误')


@csrf_exempt
def service_unbind_cloud(request):
    if request.method == 'GET':
        if not request.session.__contains__('manager_id'):
            return redirect('/sales/service/login')
        return render(request, 'service/unbind_cloud.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        if not para.__contains__('serial_number'):
            return render(request, 'service/unbind_cloud.html', {
                'lib_path': lib_path
            })
        serial_number = para.__getitem__('serial_number')
        url = 'http://api.internal.insta360.com/admin/cloud/unbundlingAccount'
        values = {
            'serial_number': serial_number,
        }
        try:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            res = json.loads(res)
            print res
            flag = res['flag']
            if flag == True:
                result = '解绑成功'
            else:
                result = '该序列号没有绑定云播账号'
            return HttpResponse(result)
        except:
            return HttpResponse('网络错误')