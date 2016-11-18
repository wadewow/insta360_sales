# coding=utf-8

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from ..util.option import lib_path
from ..models import Exhibition
from ..models import SerialToInter

import urllib2
import urllib
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def util_login(request):
    if request.method == 'GET':
        return render(request, 'util/login.html', {
            'lib_path': lib_path
        })


@csrf_exempt
def util_import_exhibition(request):
    if request.method == 'GET':
        return render(request, 'util/import_exhibition.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        if not para.__contains__("exhibitions"):
            return redirect('sales/util/import_exhibition')
        exhibitions = para.__getitem__("exhibitions")
        # print exhibitions
        temps = exhibitions.split('\n')
        added = []
        for temp in temps:
            temp = str(temp)
            temp = temp.strip()
            length = len(temp)
            if not temp.startswith('INA'):
                continue
            if length < 13 and length >15:
                continue
            res = Exhibition.objects.update_or_create(id=temp)
            if res[1]:
                added.append(temp)
                print temp

        count = len(added)
        return render(request, 'util/import_exhibition.html', {
            'lib_path': lib_path,
            'added': added,
            'count': count,
            'flag': 1
        })


@csrf_exempt
def util_import_nano(request):
    if request.method == 'GET':
        return render(request, 'util/import_nano.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        if not para.__contains__("join"):
            return render(request, 'util/import_nano.html', {
                'lib_path': lib_path
            })
        join = para.__getitem__("join")
        count = int(para.__getitem__("count"))
        join = join[:-1]

        # print join
        url = 'http://112.124.47.228:9002/camera/agent/addSellOutData'
        values = {
            'sql_str': join
        }
        try:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data)
            print 'asd'
            res_data = urllib2.urlopen(req)
            print 'qwe'
            res = res_data.read()
            print res
            res = json.loads(res)
            print res
            flag = res['flag']
            if flag:
                nums = res['nums']
                added = 2 * count - int(nums)
                return HttpResponse('成功添加' + str(added) + '条记录')
            else:
                return HttpResponse('格式错误')
        except:
            print 'network error'
        return HttpResponse('网络错误')


@csrf_exempt
def util_convert_type(request):
    if request.method == 'GET':
        return render(request, 'util/convert_type.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        print para
        if (not para.__contains__("serial_numbers")) or (not para.__contains__("type")):
            return render(request, 'util/convert_type.html', {
                'lib_path': lib_path
            })
        serial_numbers = para.__getitem__("serial_numbers")
        type = para.__getitem__("type")
        if type == 'abroad':
            type = 2
        else:
            type = 1
        temps = serial_numbers.split('\n')
        added = []
        for temp in temps:
            temp = str(temp)
            temp = temp.strip()
            if not temp.startswith('INS'):
                continue

            url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/camera/setNanoedition'
            values = {
                'serial_number': temp,
                'type': type
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
                    added.append(temp)
                    if type == 2:
                        now = timezone.now()
                        temp = {
                            'update_time': now
                        }
                        SerialToInter.objects.update_or_create(id=temp, defaults=temp)
            except:
                print 'network error'

        count = len(added)
        return render(request, 'util/convert_type.html', {
            'lib_path': lib_path,
            'added': added,
            'count': count,
            'flag': 1
        })