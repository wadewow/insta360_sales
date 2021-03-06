# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.db.models.aggregates import Count
from django.forms.models import model_to_dict
from ..models import Manager
from ..models import Shop
from ..models import Store
from ..models import Sale
from ..models import Clerk
from ..models import SerialToInter
from ..util.option import dict
from ..util.option import lib_path
from ..util.option import mode

import datetime
import json
import urllib
import sys
import csv
import codecs
import collections
import urllib2
import re

reload(sys)
sys.setdefaultencoding('utf-8')

@csrf_exempt
def bi_login(request):
    if request.method == 'GET':
        return render(request, 'bi/login.html', {
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
        data = res_data.read()
        if status == 200:
            try:
                name = json.loads(data)['name']
                if name != '':
                    Manager.objects.filter(id=username).update(name=name)
            except:
                pass
            result = Manager.objects.get_or_create(id=username)
            user = result[0]
            if user.bi == 0:
                return HttpResponse(content='抱歉，你没有权限登录', status=status)
            request.session['bi_id'] = username
            return HttpResponse(content='success', status=status)
        else:
            return HttpResponse(content='账号或密码错误！', status=status)

@csrf_exempt
def bi_stores(request):
    if request.method == 'GET':
        if not request.session.__contains__('bi_id'):
            return redirect('/sales/bi/login')
        para = request.GET
        page = 1
        if para.__contains__('page'):
            try:
                page = int(para.__getitem__('page'))
            except:
                page = 1
        if page < 1:
            page = 1
        size = 40
        sort = '-created_time'
        if para.__contains__('sort'):
            sort = para.__getitem__('sort')

        stores = Shop.objects.filter(created_time__gt='2016-11-05')
        key = ''
        if para.__contains__('key') and para.__getitem__('key') != '':
            key = para.__getitem__('key')
            stores = Shop.objects.filter(created_time__gt='2016-11-05',code=key)
            if not stores.exists():
                stores = Shop.objects.filter(created_time__gt='2016-11-05',name__icontains=key)

        if sort == 'province':
            stores = stores.order_by(sort, 'city', 'location')
        else:
            stores = stores.order_by(sort)
        total = stores.count()
        page_total = total / size + (1 if (total % size) > 0 else 0)
        if page_total <=0:
            page_total = 1
        if page > page_total:
            page = page_total
        start = size * (page -1)
        end = start + size
        if end > total:
            end = total
        if total == 0:
            stores = {}
        else:
            stores = stores[start: end]
            stores = stores.values()
        url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getAgentNumberInfo'
        req = urllib2.Request(url=url)
        try:
            res_data = urllib2.urlopen(req)
        except:
            res_data = '["默认"]'
        data = res_data.read()
        try:
            agent_list = json.loads(data)
        except:
            agent_list = [{'custom_number':'默认'}]
        agent_dict = {}
        for agent in agent_list:
            agent_dict[agent['custom_number']] = agent['company']

        for store in stores:
            new_option = {}
            option = json.loads(store['option'])
            for index, item in enumerate(option):
                n = dict[item]
                new_option[n] = option[item]
            store['option'] = new_option
            photo_join = store['photo']
            photos = photo_join.split(':')
            store['photo'] = photos
            business_id = store['business_id']
            manager_id = store['manager']
            store['agent'] = agent_dict[store['agent']]
            try:
                shopkeeper = Store.objects.get(id=business_id)
                store['business_id'] = shopkeeper
            except:
                pass
            try:
                manager = Manager.objects.get(id=manager_id)
                store['manager'] = manager
            except:
                pass
            store_id = store['id']
            sales = Sale.objects.filter(store_id=store_id, name='Insta360 Nano')
            today = timezone.localtime(timezone.now()).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            created_time = store['created_time']
            one_week = today - datetime.timedelta(days=7)
            two_week = today - datetime.timedelta(days=14)
            three_week = today - datetime.timedelta(days=21)

            if created_time >= two_week:
                state = '试营业'
            else:
                one_week_sales = sales.filter(created_time__gt=one_week).count()
                if one_week_sales > 0:
                    state = '正常'
                else:
                    two_week_sales = sales.filter(created_time__gt=two_week).count()
                    if two_week_sales > 0:
                        state = '预警'
                    else:
                        three_week_sales = sales.filter(created_time__gt=three_week).count()
                        if three_week_sales > 0:
                            state = '问题'
                        else:
                            state = '放弃'
            sales_count = sales.count()
            store['sales_count'] = sales_count
            store['state'] = state
            valid_count = sales.filter(valid=1).count()
            store['valid_count'] = valid_count
        data = {
            'total': total,
            'current_page': page,
            'page_total': page_total,
            'sort': sort,
            'key': key,
        }
        return render(request, 'bi/stores.html', {
            'stores': stores,
            'data': data,
            'lib_path': lib_path,
            'mode': mode
        })


@csrf_exempt
def bi_managers(request):
    if request.method == 'GET':
        if not request.session.__contains__('bi_id'):
            return redirect('/sales/bi/login')
        para = request.GET
        managers = Manager.objects.exclude(region='')
        if para.__contains__('sort'):
            sort = para.__getitem__('sort')
            managers = managers.order_by(sort)

        managers = managers.values()
        for manager in managers:
            manager_id = manager['id']
            stores = Shop.objects.filter(manager=manager_id, created_time__gt='2016-11-05')
            store_count = stores.count()
            bonus = stores.aggregate(bonus=Sum('bonus'))
            bonus = bonus['bonus']
            if bonus == None:
                bonus = 0
            machine_count = stores.exclude(machine_serial='').count()
            store_sales = Sale.objects.filter(manager=manager_id).count()
            today = timezone.localtime(timezone.now()).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            one_week = today - datetime.timedelta(days=7)
            two_week = today - datetime.timedelta(days=14)
            three_week = today - datetime.timedelta(days=21)
            trial = 0
            normal= 0
            warn = 0
            problem = 0
            abandon = 0
            for store in stores:
                store_id = store.id
                sales = Sale.objects.filter(store_id=store_id, name='Insta360 Nano')
                created_time = store.created_time
                if created_time >= two_week:
                    trial += 1
                else:
                    one_week_sales = sales.filter(created_time__gt=one_week).count()
                    if one_week_sales > 0:
                        normal += 1
                    else:
                        two_week_sales = sales.filter(created_time__gt=two_week).count()
                        if two_week_sales > 0:
                            warn += 1
                        else:
                            three_week_sales = sales.filter(created_time__gt=three_week).count()
                            if three_week_sales > 0:
                                problem += 1
                            else:
                                abandon += 1

            manager['store_count'] = store_count
            manager['store_sales'] = store_sales
            manager['machine_count'] = machine_count
            manager['trial'] = trial
            manager['bonus'] = bonus
            manager['normal'] = normal
            manager['warn'] = warn
            manager['problem'] = problem
            manager['abandon'] = abandon
        if para.__contains__('i_sort'):
            i_sort = para.__getitem__('i_sort')
            managers = list(managers)
            managers.sort(key=lambda manager: manager[i_sort], reverse=True)
        return render(request, 'bi/managers.html', {
            'managers': managers,
            'lib_path': lib_path,
            'mode': mode
        })


@csrf_exempt
def bi_sales(request):
    if request.method == 'GET':
        if not request.session.__contains__('bi_id'):
            return redirect('/sales/bi/login')
        para = request.GET
        page = 1
        if para.__contains__('page'):
            try:
                page = int(para.__getitem__('page'))
            except:
                page = 1
        if page < 1:
            page = 1
        sort = '-created_time'
        if para.__contains__('sort'):
            sort = para.__getitem__('sort')
        size = 40
        now = timezone.now()
        deadline = now - datetime.timedelta(hours=12)
        deadline1 = now - datetime.timedelta(hours=168)
        sales = Sale.objects.filter(name='Insta360 Nano').exclude(
            valid=0,
            active=0,
            delay=0,
            created_time__lt=deadline).exclude(
            valid=0,
            active=0,
            delay=1,
            created_time__lt=deadline1)
        if sort == '-active':
            sales = sales.order_by(sort, '-active_time')
        else:
            sales = sales.order_by(sort)
        total = sales.count()
        page_total = total / size + (1 if (total % size) > 0 else 0)
        if page_total <=0:
            page_total = 1
        if page > page_total:
            page = page_total
        start = size * (page -1)
        end = start + size
        if end > total:
            end = total
        if total == 0:
            sales = {}
        else:
            sales = sales[start: end]
            sales = sales.values()

        for sale in sales:
            # sale['show'] = 1
            business_id = sale['business_id']
            store_id = sale['store_id']
            clerk_id = sale['clerk_id']
            try:
                shopkeeper = Store.objects.get(id=business_id)
                sale['business'] = shopkeeper
            except:
                pass
            try:
                store = Shop.objects.get(id=store_id)
                manager_id = store.manager
                manager = Manager.objects.get(id=manager_id)
                store.manager = manager
                sale['store']= store
            except:
                pass
            try:
                clerk = Clerk.objects.get(id=clerk_id)
                sale['clerk'] = clerk
            except:
                pass
            valid = sale['valid']
            active = sale['active']
            if valid == 1:
                created_time = sale['created_time']
                device_code = sale['device_code']
                if device_code == '':
                    num = 1
                else:
                    num = Sale.objects.filter(
                        device_code=device_code,
                        clerk_id=clerk_id,
                        name='Insta360 Nano',
                        created_time__lte=created_time
                    ).count()
                if num > 1:
                    state = '重复激活'
                else:
                    state = '生效'
            else:
                if active == 1:
                    state = '超时'
                else:
                    state = '等待激活'
            sale['state'] = state

        data = {
            'total': total,
            'current_page': page,
            'page_total': page_total,
            'sort': sort
        }
        return render(request, 'bi/sales.html', {
            'sales': sales,
            'data': data,
            'lib_path': lib_path,
            'mode': mode
        })

@csrf_exempt
def bi_trend(request):
    if request.method == 'GET':
        if not request.session.__contains__('bi_id'):
            return redirect('/sales/bi/login')
        return render(request, 'bi/trend.html', {
            'lib_path': lib_path,
            'mode': mode
        })


@csrf_exempt
def bi_store_trend(request):
    if request.method == 'GET':
        para = request.GET
        today = (timezone.localtime(timezone.now()) + datetime.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
        begin = today.replace(year=2016,month=11,day=5)

        if para.__contains__('start_time'):
            try:
                start_time = datetime.datetime.strptime(para.__getitem__('start_time'), '%Y-%m-%d')
                if start_time.date() < begin.date() :
                    start_time = begin
            except:
                start_time = begin
        else:
            start_time = begin
        if para.__contains__('end_time'):
            try:
                end_time = datetime.datetime.strptime(para.__getitem__('end_time'), '%Y-%m-%d')
                end_time = end_time + datetime.timedelta(days=1)
                if end_time.date() > today.date() :
                    end_time = today
            except:
                end_time = today
        else:
            end_time = today
        result = collections.OrderedDict()
        delta = (end_time.date() - start_time.date()).days
        for i in range(delta):
            end = (start_time + datetime.timedelta(days=(i+1)))
            start = end - datetime.timedelta(days=1)
            stores = Shop.objects.filter(created_time__range=(begin,end))
            store_count = stores.count()
            machine_count = stores.exclude(machine_serial='').count()
            nano_count = Sale.objects.filter(active=1, name='Insta360 Nano', active_time__range=(start, end)).count()
            temp = {
                'store': store_count,
                'nano': nano_count,
                'machine': machine_count
            }
            result[start.strftime('%m-%d')] = temp
        return JsonResponse(result, safe=False)

@csrf_exempt
def bi_map(request):
    if request.method == 'GET':
        if not request.session.__contains__('bi_id'):
            return redirect('/sales/bi/login')
        return render(request, 'bi/map.html', {
            'lib_path': lib_path,
            'mode': mode
        })


@csrf_exempt
def bi_sales_map(request):
    if request.method == 'GET':
        para = request.GET
        today = (timezone.localtime(timezone.now()) + datetime.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
        begin = today.replace(year=2016,month=11,day=5)

        if para.__contains__('start_time'):
            try:
                start_time = datetime.datetime.strptime(para.__getitem__('start_time'), '%Y-%m-%d')
                if start_time.date() < begin.date() :
                    start_time = begin
            except:
                start_time = begin
        else:
            start_time = begin
        if para.__contains__('end_time'):
            try:
                end_time = datetime.datetime.strptime(para.__getitem__('end_time'), '%Y-%m-%d')
                end_time = end_time + datetime.timedelta(days=1)
                if end_time.date() > today.date() :
                    end_time = today
            except:
                end_time = today
        else:
            end_time = today

        result = {}
        stores = Shop.objects.filter(created_time__range=(start_time,end_time))
        store_count = stores.values('province').annotate(store_count=Count('id'))
        machine_count = stores.exclude(machine_serial='').values('province').annotate(machine_count=Count('id'))
        sale_count = Sale.objects.filter(created_time__range=(start_time,end_time)).values('province').annotate(sale_count=Count('id'))
        store_data = []
        for item in store_count:
            name = item['province']
            if '内蒙古' in name or '黑龙江' in name:
                name = name[0:3]
            else:
                name = name[0:2]
            temp = {
                'name': name,
                'value': item['store_count']
            }
            store_data.append(temp)

        machine_data = []
        for item in machine_count:
            name = item['province']
            if '内蒙古' in name or '黑龙江' in name:
                name = name[0:3]
            else:
                name = name[0:2]
            temp = {
                'name': name,
                'value': item['machine_count']
            }
            machine_data.append(temp)

        sale_data = []
        for item in sale_count:
            name = item['province']
            if '内蒙古' in name or '黑龙江' in name:
                name = name[0:3]
            else:
                name = name[0:2]
            temp = {
                'name': name,
                'value': item['sale_count']
            }
            sale_data.append(temp)
        result['store'] = store_data
        result['machine'] = machine_data
        result['sale'] = sale_data
        return JsonResponse(result, safe=False)


@csrf_exempt
def bi_nano_detail(request):
    if request.method == 'GET':
        if not request.session.__contains__('bi_id'):
            return redirect('/sales/bi/login')
        return render(request, 'bi/nano_detail.html', {
            'lib_path': lib_path,
            'mode': mode
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
        return render(request, 'bi/nano_detail.html', {
            'serial_number': serial_number,
            'exist': exist,
            'agent': agent,
            'factory': factory,
            'sale': sale_info,
            'active': active_info,
            'lib_path': lib_path,
            'mode': mode
        })


@csrf_exempt
def bi_batch_active(request):
    if request.method == 'GET':
        if not request.session.__contains__('bi_id'):
            return redirect('/sales/bi/login')
        return render(request, 'bi/batch_active.html', {
            'lib_path': lib_path,
            'mode': mode
        })
    if request.method == 'POST':
        para = request.POST
        if not para.__contains__("serial_numbers"):
            return redirect('sales/bi/batch_active')
        serial_numbers = para.__getitem__("serial_numbers")

        pattern = re.compile('INS.{11}', re.S)
        items = re.findall(pattern, serial_numbers)
        join_serial = ''
        for i in items:
            join_serial += i + ','
        url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getActivateInfos/'
        url1 = 'http://api.internal.insta360.com:8088/insta360_nano/camera/agent/getOutOfFactoryInfo'
        values = {
            'serial_number': join_serial
        }
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data=data)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        res = json.loads(res)
        active_num = 0
        inactive_num = 0
        for index, item in enumerate(res):
            values = {
                'serial_number': item,
            }
            agent = {}
            factory = {}
            try:
                data1 = urllib.urlencode(values)
                req1 = urllib2.Request(url1, data=data1)
                res_data1 = urllib2.urlopen(req1)
                res1 = res_data1.read()
                res1 = json.loads(res1)
                agent = res1['agent']
                factory = res1['factory']
            except:
                pass
            data = res[item]
            active_time = data['first_use_time']
            type = data['type']
            status = data['status']
            if active_time != '0':
                active_num += 1
                res[item]['active'] = '已激活'
                temp = datetime.datetime.utcfromtimestamp(int(active_time))
                temp = temp + datetime.timedelta(hours=8)
                active_time = temp.strftime("%Y-%m-%d %H:%M:%S")
                res[item]['first_use_time'] = active_time
            else:
                inactive_num += 1
                res[item]['active'] = '未激活'
                res[item]['first_use_time'] = ''
            if type == '1':
                res[item]['type'] = '国内货'
            elif type == '2':
                res[item]['type'] = '国际货'
            if status == '1':
                res[item]['status'] = '未绑定云播账号'
            elif status == '2':
                res[item]['status'] = '已绑定云播账号'
            res[item]['agent'] = agent
            res[item]['factory'] = factory
        total_num = inactive_num + active_num
        tip = '共' + str(total_num) + '个' + '序列号，其中' + str(active_num) + '个已激活，' + str(inactive_num) + '个未激活'
        return render(request, 'bi/batch_active.html', {
            'lib_path': lib_path,
            'flag': 1,
            'result': res,
            'tip': tip,
            'mode': mode
        })


@csrf_exempt
def bi_inter_list(request):
    if request.method == 'GET':
        if not request.session.__contains__('bi_id'):
            return redirect('/sales/bi/login')
        para = request.GET

        page = 1
        if para.__contains__('page'):
            try:
                page = int(para.__getitem__('page'))
            except:
                page = 1
        if page < 1:
            page = 1
        size = 40

        sort = ''
        if para.__contains__('sort'):
            sort = para.__getitem__('sort')
        if sort == 'id':
            serials = SerialToInter.objects.all().order_by(sort)
        else:
            serials = SerialToInter.objects.all()
        total = serials.count()
        page_total = total / size + (1 if (total % size) > 0 else 0)
        if page_total <= 0:
            page_total = 1
        if page > page_total:
            page = page_total
        start = size * (page - 1)
        end = start + size
        if end > total:
            end = total
        if total == 0:
            serials = {}
        else:
            serials = serials[start: end]
            serials = serials.values()

        url1 = 'http://api.internal.insta360.com:8088/insta360_nano/camera/agent/getOutOfFactoryInfo'
        url2 = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getActivateInfo/'
        for serial in serials:
            serial_number = serial['id']
            values = {
                'serial_number': serial_number,
            }
            try:
                data = urllib.urlencode(values)
                req = urllib2.Request(url1, data=data)
                res_data = urllib2.urlopen(req)
                res = res_data.read()
                res = json.loads(res)
                serial['agent'] = res['agent']
                serial['factory'] = res['factory']
            except:
                pass
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
            serial['sale'] = sale_info


            try:
                data = urllib.urlencode(values)
                req = urllib2.Request(url2, data=data)
                res_data = urllib2.urlopen(req)
                res = res_data.read()
                res = json.loads(res)
                flag = res['flag']
                if not flag:
                    continue
                active = 0
                active_location = ''
                active_time = res['data']['first_use_time']
                if active_time != '0':
                    active = 1
                    active_location = res['data']['active_location']
                    active_location = active_location.replace(',',' ')
            except:
                active = 0
                active_location = ''
            active_info = {
                'active': active,
                'active_location': active_location
            }

            serial['active_info'] = active_info
        if sort == 'agent':
            serials = list(serials)
            serials.sort(key=lambda serial: serial['factory']['consumer'], reverse=False)
        data = {
            'total': total,
            'current_page': page,
            'page_total': page_total,
            'sort': sort
        }
        return render(request, 'bi/inter_list.html', {
            'serials': serials,
            'data': data,
            'lib_path': lib_path,
            'mode': mode
        })


@csrf_exempt
def bi_export(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response.write(codecs.BOM_UTF8)
    response['Content-Disposition'] = 'attachment; filename="门店列表.csv"'

    writer = csv.writer(response)

    writer.writerow(['门店名称', '门店代码', '商家名称', '商家姓名', '商家手机', '省份', '城市', '详细地址', '门店状态', '累计促销费用', '物料', '样机序列号' ,'展台序列号' , '代理商', '销售经理', '累计总销量', '有效订单数', '创建时间', '创建天数', '网店地址', '备注'])
    stores = Shop.objects.filter(created_time__gt='2016-11-05').values()
    url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getAgentNumberInfo'
    req = urllib2.Request(url=url)
    try:
        res_data = urllib2.urlopen(req)
    except:
        res_data = '["默认"]'
    data = res_data.read()
    try:
        agent_list = json.loads(data)
    except:
        agent_list = [{'custom_number': '默认'}]
    agent_dict = {}
    for agent in agent_list:
        agent_dict[agent['custom_number']] = agent['company']
    for store in stores:
        store_id = store['id']
        new_option = ''
        option = json.loads(store['option'])
        for index, item in enumerate(option):
            if option[item] == 'true':
                new_option += dict[item] + ' '
        store['option'] = new_option
        photo_join = store['photo']
        photos = photo_join.split(':')
        store['photo'] = photos
        business_id = store['business_id']
        manager_id = store['manager']
        store['agent'] = agent_dict[store['agent']]
        try:
            shopkeeper = Store.objects.get(id=business_id)
            store['business'] = shopkeeper
        except:
            pass
        try:
            manager = Manager.objects.get(id=manager_id)
            store['manager'] = manager
        except:
            pass
        sales = Sale.objects.filter(store_id=store_id, name='Insta360 Nano')

        now = timezone.now()
        today = timezone.localtime(now).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        created_time = store['created_time']
        one_week = today - datetime.timedelta(days=7)
        two_week = today - datetime.timedelta(days=14)
        three_week = today - datetime.timedelta(days=21)

        if created_time >= two_week:
            state = '试营业'
        else:
            one_week_sales = sales.filter(created_time__gt=one_week).count()
            if one_week_sales > 0:
                state = '正常'
            else:
                two_week_sales = sales.filter(created_time__gt=two_week).count()
                if two_week_sales > 0:
                    state = '预警'
                else:
                    three_week_sales = sales.filter(created_time__gt=three_week).count()
                    if three_week_sales > 0:
                        state = '问题'
                    else:
                        state = '放弃'

        sales_count = sales.count()
        valid_count = sales.filter(valid=1).count()
        created_time += datetime.timedelta(hours=8)
        created_date = created_time.strftime('%Y-%m-%d %H:%M:%S')
        now = timezone.now()
        delta = (now - created_time).days + 1
        if len(store['online']) < 10:
            store['online'] = ''
        writer.writerow([store['name'],
                         store['code'],
                         store['business'].store,
                         store['business'].name,
                         store['business'].phone,
                         store['province'],
                         store['city'],
                         store['location'],
                         state,
                         store['bonus'],
                         store['option'],
                         store['machine_serial'],
                         store['exhibition'],
                         store['agent'],
                         store['manager'].name + '('+ store['manager'].area +')',
                         sales_count,
                         valid_count,
                         created_date,
                         delta,
                         store['online'],
                         store['remark']
                         ]
                        )
    return response


@csrf_exempt
def bi_export_sales(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response.write(codecs.BOM_UTF8)
    response['Content-Disposition'] = 'attachment; filename="销售情况列表.csv"'

    writer = csv.writer(response)
    writer.writerow(['门店名称', '商家名称', '省份', '店员姓名', '店员手机', '序列号', '售出时间', '激活状态', '激活时间', '激活机器码', '订单状态', '红包奖励（元）', '销售经理'])

    now = timezone.now()
    deadline = now - datetime.timedelta(hours=12)
    deadline1 = now - datetime.timedelta(hours=168)
    sales = Sale.objects.filter(name='Insta360 Nano').exclude(
        valid=0,
        active=0,
        delay=0,
        created_time__lt=deadline).exclude(
        valid=0,
        active=0,
        delay=1,
        created_time__lt=deadline1).order_by('-created_time').values()

    for sale in sales:
        business_id = sale['business_id']
        store_id = sale['store_id']
        clerk_id = sale['clerk_id']
        try:
            shopkeeper = Store.objects.get(id=business_id)
            sale['business'] = shopkeeper
        except:
            pass
        try:
            store = Shop.objects.get(id=store_id)
            manager_id = store.manager
            manager = Manager.objects.get(id=manager_id)
            store.manager = manager
            sale['store'] = store
        except:
            pass
        try:
            clerk = Clerk.objects.get(id=clerk_id)
            sale['clerk'] = clerk
        except:
            pass
        valid = sale['valid']
        active = sale['active']
        if valid == 1:
            created_time = sale['created_time']
            device_code = sale['device_code']
            if device_code == '':
                num = 1
            else:
                num = Sale.objects.filter(
                    device_code=device_code,
                    clerk_id=clerk_id,
                    name='Insta360 Nano',
                    created_time__lte=created_time
                ).count()
            if num > 1:
                state = '重复激活'
            else:
                state = '生效'
        else:
            if active == 1:
                state = '超时'
            else:
                state = '等待激活'
        sale['state'] = state
        created_time = sale['created_time']
        created_time += datetime.timedelta(hours=8)
        created_date = created_time.strftime('%Y-%m-%d %H:%M:%S')
        active = sale['active']
        if active == 1:
            active_state = '已激活'
            active_time = sale['active_time']
            active_time += datetime.timedelta(hours=8)
            active_date = created_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            active_state = '未激活'
            active_date = ''

        writer.writerow([sale['store'].name,
                         sale['business'].store,
                         sale['province'],
                         sale['clerk'].name,
                         sale['clerk'].phone,
                         sale['serial_number'],
                         created_date,
                         active_state,
                         active_date,
                         sale['device_code'],
                         state,
                         sale['base'],
                         sale['store'].manager.name + '('+ sale['store'].manager.area +')',
                         ]
                        )
    return response