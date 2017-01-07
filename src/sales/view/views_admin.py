# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from ..models import Manager
from ..models import Shop
from ..models import Promotion
from ..models import Store
from ..models import Sale
from ..util.option import dict
from ..util.option import lib_path

import urllib
import urllib2
import sys
import json

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def admin_login(request):
    if request.method == 'GET':
        return render(request, 'admin/myLogin.html', {
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
            if user.admin == 0:
                return HttpResponse(content='抱歉，你没有权限登录', status=status)
            request.session['admin_id'] = username
            return HttpResponse(content='success', status=status)
        else:
            return HttpResponse(content='账号或密码错误！', status=status)


@csrf_exempt
def admin_power_manage(request):
    if request.method == 'GET':
        if not request.session.__contains__('admin_id'):
            return redirect('/sales/admin/login')
        job_number = ""
        para = request.GET
        if para.__contains__('job_number'):
            job_number = para.__getitem__('job_number')
        flag = 1
        if job_number == "":
            return render(request, 'admin/power_manage.html', {
                'lib_path': lib_path
            })
        try:
            user = Manager.objects.get(id=job_number)
        except:
            flag = 0
            user = {}
        return render(request, 'admin/power_manage.html', {
            'job_number': job_number,
            'flag': flag,
            'user': user,
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        job_number = para.__getitem__('job_number')
        temp = {}
        for index in para:
            if index != 'job_number':
                value = para.__getitem__(index)
                if value == 'true':
                    value = 1
                else:
                    value = 0
                temp[index] = value
        Manager.objects.update_or_create(id=job_number, defaults=temp)
        return HttpResponse('success')


@csrf_exempt
def admin_manager_list(request):
    if request.method == 'GET':
        if not request.session.__contains__('admin_id'):
            return redirect('/sales/admin/login')
        managers = Manager.objects.exclude(region='')
        return render(request, 'admin/manager_list.html', {
            'managers': managers,
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        print para
        job_number = para.__getitem__('job_number')
        name = para.__getitem__('name')
        area = para.__getitem__('area')
        region = para.__getitem__('region')
        is_leader = para.__getitem__('is_leader')
        if is_leader == 'true':
            is_leader = 1
        else:
            is_leader = 0
        try:
            manager = Manager.objects.get(id=job_number)
        except:
            return HttpResponse('工号不存在！')

        if manager.region != '':
            return HttpResponse('该销售经理已存在，若想修改信息请点击修改')

        manager.name = name
        manager.area = area
        manager.region = region
        manager.is_leader = is_leader
        manager.save()
        return HttpResponse('success')


@csrf_exempt
def admin_modify_manager(request):
    if request.method == 'GET':
        if not request.session.__contains__('admin_id'):
            return redirect('/sales/admin/login')
        managers = Manager.objects.exclude(region='')
        return render(request, 'admin/manager_list.html', {
            'managers': managers,
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        print para
        job_number = para.__getitem__('job_number')
        name = para.__getitem__('name')
        area = para.__getitem__('area')
        region = para.__getitem__('region')
        is_leader = para.__getitem__('is_leader')
        if is_leader == 'true':
            is_leader = 1
        else:
            is_leader = 0
        Manager.objects.filter(id=job_number).update(name=name,area=area,region=region,is_leader=is_leader)
        return HttpResponse('success')


@csrf_exempt
def admin_promotion(request):
    if request.method == 'GET':
        if not request.session.__contains__('admin_id'):
            return redirect('/sales/admin/login')
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
        if sort == 'province':
            stores = Shop.objects.filter(created_time__gt='2016-11-05').order_by(sort, 'city', 'location')
        else:
            stores = Shop.objects.filter(created_time__gt='2016-11-05').order_by(sort)
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
            sales_count = Sale.objects.filter(store_id=store_id, name='Insta360 Nano').count()
            store['sales_count'] = sales_count
        promotions = Promotion.objects.all()
        for promotion in promotions:
            promotion.id = str(promotion.id)
        data = {
            'total': total,
            'current_page': page,
            'page_total': page_total,
            'sort': sort
        }
        return render(request, 'admin/promotion.html', {
            'promotions':promotions,
            'stores': stores,
            'data': data,
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        name= para.__getitem__('name')
        start_time = para.__getitem__('start_time')
        end_time = para.__getitem__('end_time')
        benchmark = para.__getitem__('benchmark')
        benchmark1 = para.__getitem__('benchmark1')
        benchmark2 = para.__getitem__('benchmark2')
        bonus = para.__getitem__('bonus')
        bonus1 = para.__getitem__('bonus1')
        bonus2 = para.__getitem__('bonus2')
        if benchmark > benchmark1 or benchmark1 > benchmark2:
            return HttpResponse('各级梯度必须由小到大')
        if start_time > end_time:
            return HttpResponse('结束日期必须大于开始日期')

        old_promotion_set = Promotion.objects.filter(
            name=name,
            start_time=start_time,
            end_time=end_time,
            benchmark=benchmark,
            benchmark1=benchmark1,
            benchmark2=benchmark2,
            bonus=bonus,
            bonus1=bonus1,
            bonus2=bonus2
        )

        if not old_promotion_set.exists():
            try:
                Promotion.objects.create(
                    start_time=start_time,
                    end_time=end_time,
                    benchmark=benchmark,
                    benchmark1=benchmark1,
                    benchmark2=benchmark2,
                    bonus=bonus,
                    bonus1=bonus1,
                    bonus2=bonus2
                )
            except:
                return HttpResponse('添加失败')
        return HttpResponse('success')

@csrf_exempt
def admin_apply(request):
    if request.method == 'POST':
        para = request.POST
        for item in para:
            try:
                store_id= str(item)
                promotion_id = para.__getitem__(store_id)
                Shop.objects.filter(id=store_id).update(promotion=promotion_id)
            except:
                continue
        return HttpResponse('success')
