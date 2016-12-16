# coding=utf-8

from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils import timezone
from django.forms.models import model_to_dict

from ..util.option import lib_path
from ..models import CashRecord
from ..models import SerialToInter
from ..models import Manager
from ..models import Shop
from ..models import Store
from ..models import Sale

import urllib
import urllib2
import datetime
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
            # result = Manager.objects.get_or_create(id=username)
            # user = result[0]
            # if user.service == 0:
            if False:
                return HttpResponse(content='抱歉，你没有权限登录', status=status)
            request.session['service_id'] = username
            return HttpResponse(content='success', status=status)
        else:
            return HttpResponse(content='账号或密码错误！', status=status)

@csrf_exempt
def cash_query(request):
    if request.method == 'GET':
        if not request.session.__contains__('service_id'):
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
        if not request.session.__contains__('service_id'):
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
def service_cloud_query(request):
    if request.method == 'GET':
        if not request.session.__contains__('service_id'):
            return redirect('/sales/service/login')
        return render(request, 'service/unbind_cloud.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        words = para.get('words','')
        url = 'http://statistics.internal.insta360.com/api/cloud/getCloudUserInfo'
        values = {
            'words': words,
        }
        try:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            res = json.loads(res)
            flag = res['flag']
            record = res['info']
            timestamp = record['register_time'][:-3]
            temp = datetime.datetime.utcfromtimestamp(int(timestamp))
            register_time = temp + datetime.timedelta(hours=8)
            record['register_time'] = register_time
            if not flag:
                return render(request, 'service/unbind_cloud.html', {
                    'exsit': 0,
                    'lib_path': lib_path
                })
        except:
            return render(request, 'service/unbind_cloud.html', {
                'exsit': 0,
                'lib_path': lib_path
            })

        return render(request, 'service/unbind_cloud.html', {
            'exsit': 1,
            'record': record,
            'lib_path': lib_path
        })


@csrf_exempt
def service_unbind_cloud(request):
    if request.method == 'GET':
        if not request.session.__contains__('service_id'):
            return redirect('/sales/service/login')
        return render(request, 'service/unbind_cloud.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        print para
        if not para.__contains__('serial_number'):
            return render(request, 'service/unbind_cloud.html', {
                'lib_path': lib_path
            })
        serial_number = para.__getitem__('serial_number')
        url = 'http://statistics.internal.insta360.com/api/cloud/unbundlingAccount'
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


@csrf_exempt
def service_cloud_home(request):
    if request.method == 'GET':
        if not request.session.__contains__('service_id'):
            return redirect('/sales/service/login')
        url = 'http://statistics.internal.insta360.com/api/cloud/getHomePageInfo'
        try:
            req = urllib2.Request(url)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            records = json.loads(res)
        except:
            return render(request, 'service/cloud_home.html', {
                'lib_path': lib_path
            })

        return render(request, 'service/cloud_home.html', {
            'records': records,
            'lib_path': lib_path
        })

    if request.method == 'POST':
        data = request.body
        url = 'http://statistics.internal.insta360.com/api/cloud/setHomePage'
        try:
            req = urllib2.Request(url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            res = json.loads(res)
            print res
            flag = res['flag']
            if flag:
                return HttpResponse('保存成功')
            else:
                info = res['info']
                information = '\n'
                for i in info:
                    information += i + '\n'
                return HttpResponse('保存失败,以下网址有误' + information)
        except:
            return HttpResponse('保存失败')


@csrf_exempt
def service_nano_detail(request):
    if request.method == 'GET':
        if not request.session.__contains__('service_id'):
            return redirect('/sales/service/login')
        return render(request, 'service/nano_detail.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        serial_number = para.__getitem__('serial_number')
        url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/agent/getOutOfFactoryInfo'
        values = {
            'serial_number': serial_number,
        }
        exist = 0
        agent = {}
        factory = {}
        try:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            res = json.loads(res)
            agent = res['agent']
            factory = res['factory']
            if len(agent) == 0:
                agent['flag'] = 0
            else:
                agent['flag'] = 1
            if len(factory) == 0:
                factory['flag'] = 0
            else:
                factory['flag'] = 1
            if agent['flag'] == 1 or factory['flag'] == 1:
                exist = 1
        except:
            pass
        url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getActivateInfo/'
        try:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data=data)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            active_info = json.loads(res)
            if active_info['flag']:
                exist = 1
            active_time = active_info['data']['first_use_time']
            if active_time == '0':
                active_info['exist'] = 0
            else:
                active_info['exist'] = 1
                temp = datetime.datetime.utcfromtimestamp(int(active_time))
                temp = temp + datetime.timedelta(hours=8)
                active_info['data']['first_use_time'] = temp.strftime("%Y-%m-%d %H:%M:%S")
        except:
            active_info = {}
        try:
            sale = Sale.objects.get(serial_number=serial_number, name="Insta360 Nano")
            store_id = sale.store_id
            manager_id = sale.manager
            business_id = sale.business_id
            try:
                store = Shop.objects.get(id=store_id)
            except:
                store = {}
            try:
                manager = Manager.objects.get(id=manager_id)
            except:
                manager = {}
            try:
                business = Store.objects.get(id=business_id)
            except:
                business = {}
            sale_info = model_to_dict(sale)
            sale_info['store'] = store
            sale_info['manager'] = manager
            sale_info['business'] = business
            sale_info['flag'] = 1
        except:
            sale_info = {
                'flag': 0
            }
        return render(request, 'service/nano_detail.html', {
            'serial_number': serial_number,
            'exist': exist,
            'agent': agent,
            'factory': factory,
            'sale': sale_info,
            'active': active_info,
            'lib_path': lib_path
        })
