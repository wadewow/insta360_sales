# coding=utf-8

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.files.storage import default_storage
from ..util.option import lib_path
from ..models import Exhibition
from ..models import SerialToInter
from ..models import Manager

import urllib2
import urllib
import json
import sys
import xlrd
from datetime import datetime
from xlrd import xldate_as_tuple
reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def util_login(request):
    if request.method == 'GET':
        return render(request, 'util/login.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        if para.__contains__('username'):
            username = para.__getitem__('username')
        else:
            return HttpResponse("Missing parameter: username")
        if para.__contains__('password'):
            password = para.__getitem__('password')
        else:
            return HttpResponse("Missing parameter: password")
        url = 'http://account.arashivision.com/user/getUserToken'
        values = {
            'jobnumber': username,
            'password': password
        }
        data = urllib.urlencode(values)
        req = urllib2.Request(url=url, data=data)
        try:
            res_data = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print e.code
            print e.reason
            return HttpResponse(content='账号或密码错误！')
        status = res_data.code
        if status == 200:
            result = Manager.objects.get_or_create(id=username)
            user = result[0]
            if user.util == 0:
                return HttpResponse(content='抱歉，你没有权限登录', status=status)
            request.session['util_id'] = username
            return HttpResponse(content='success', status=status)
        else:
            return HttpResponse(content='账号或密码错误！', status=status)

@csrf_exempt
def util_import_exhibition(request):
    if request.method == 'GET':
        if not request.session.__contains__('util_id'):
            return redirect('/sales/util/login')
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
        if not request.session.__contains__('util_id'):
            return redirect('/sales/util/login')
        return render(request, 'util/import_nano.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        # para = request.POST
        # if not para.__contains__("join"):
        #     return render(request, 'util/import_nano.html', {
        #         'lib_path': lib_path
        #     })
        # print request.FILES
        file = request.FILES.__getitem__('file')
        path = 'sales/static/store/' + file.name
        path = default_storage.save(path, file)
        url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/agent/addSellOutData'
        try:
            book = xlrd.open_workbook(path)
            default_storage.delete(path)
            table = book.sheets()[0]
            rows = table.nrows
            join = ''
            count = 0
            nums = 0
            for i in range(3, rows):
                data = table.row_values(i)
                length = len(data)
                if length < 8:
                    continue
                try:
                    temp = "('" + str(datetime(*xldate_as_tuple(data[0],0)))[:-9] + "','" + str(data[1]) + "','" + str(data[2]) + "','" + str(
                        data[3]) + "','" + str(data[4]) + "','" + str(data[5]) + "','" + str(data[6]) + "','" + str(datetime(*xldate_as_tuple(data[7],0)))[:-9] + "'),"
                except:
                    continue
                join += temp
                count += 1

                if count % 1000 == 0:
                    if len(join) > 3:
                        join = join[:-1]
                    values = {
                        'sql_str': join
                    }
                    join = ''
                    try:
                        data = urllib.urlencode(values)
                        req = urllib2.Request(url, data=data)
                        res_data = urllib2.urlopen(req)
                        res = res_data.read()
                        print res
                        res = json.loads(res)
                        flag = res['flag']
                        if flag:
                            nums += int(res['nums'])
                    except:
                        pass
            if len(join) > 3:
                join = join[:-1]
            # print join
            values = {
                'sql_str': join
            }
            try:
                data = urllib.urlencode(values)
                req = urllib2.Request(url, data=data)
                res_data = urllib2.urlopen(req)
                res = res_data.read()
                print res
                res = json.loads(res)
                flag = res['flag']
                if flag:
                    nums += int(res['nums'])
            except:
                pass
            added = 2 * count - nums
            result =  '新增' + str(added) + '条记录'
            return HttpResponse(result)
        except:
            return HttpResponse('文件格式错误')



        # join = para.__getitem__("join")
        # count = int(para.__getitem__("count"))
        # join = join[:-1]

        # print join
        # url = 'http://112.124.47.228:9002/camera/agent/addSellOutData'
        # values = {
        #     'sql_str': join
        # }
        # try:
        #     data = urllib.urlencode(values)
        #     req = urllib2.Request(url, data=data)
        #     print 'asd'
        #     res_data = urllib2.urlopen(req)
        #     print 'qwe'
        #     res = res_data.read()
        #     print res
        #     res = json.loads(res)
        #     flag = res['flag']
        #     if flag:
        #         nums = res['nums']
        #         added = 2 * count - int(nums)
        #         return HttpResponse('成功添加' + str(added) + '条记录')
        #     else:
        #         return HttpResponse('格式错误')
        # except:
        #     print 'network error'
        # return HttpResponse('网络错误')


@csrf_exempt
def util_convert_type(request):
    if request.method == 'GET':
        if not request.session.__contains__('util_id'):
            return redirect('/sales/util/login')
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