# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from ..models import Manager
from ..models import Shop
from ..models import Store
from ..models import Sale
from ..models import Clerk
from ..util.option import dict
from ..util.option import lib_path

import datetime
import json
import sys
import collections
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')

@csrf_exempt
def bi_login(request):
    if request.method == 'GET':
        return render(request, 'bi/login.html', {
            'lib_path': lib_path
        })

@csrf_exempt
def bi_stores(request):
    if request.method == 'GET':
        # if not request.session.__contains__('manager_id'):
        #     return redirect('/sales/bi/login')
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
        stores = Shop.objects.filter(created_time__gt='2016-11-05').order_by('-created_time')
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
        stores = stores[start: end]

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

        stores = stores.values()
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
        data = {
            'total': total,
            'current_page': page,
            'page_total': page_total

        }
        return render(request, 'bi/stores.html', {
            'stores': stores,
            'data': data,
            'lib_path': lib_path
        })



@csrf_exempt
def bi_sales(request):
    if request.method == 'GET':
        # if not request.session.__contains__('manager_id'):
        #     return redirect('/sales/bi/login')
        para = request.GET
        page = 1
        if para.__contains__('page'):
            try:
                page = int(para.__getitem__('page'))
            except:
                page = 1
        if page < 1:
            page = 1
        size = 20
        now = timezone.now()
        deadline = now - datetime.timedelta(hours=12)
        sales = Sale.objects.filter(created_time__gt='2016-11-05', name='Insta360 Nano').exclude(valid=0, active=0, created_time__lt=deadline).order_by('-created_time')
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
                state = '生效'
            else:
                if active == 1:
                    state = '超时'
                else:
                    # now = timezone.now()
                    # created_time = sale['created_time']
                    # deadline = created_time + datetime.timedelta(hours=12)
                    # if now >= deadline:
                    #     state = '作废'
                    #     sale['show'] = 0
                    # else:
                    state = '等待激活'
            sale['state'] = state

        data = {
            'total': total,
            'current_page': page,
            'page_total': page_total
        }
        return render(request, 'bi/sales.html', {
            'sales': sales,
            'data': data,
            'lib_path': lib_path
        })

@csrf_exempt
def bi_trend(request):
    if request.method == 'GET':
        return render(request, 'bi/trend.html', {
            'lib_path': lib_path
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
            except:
                end_time = today
        else:
            end_time = today
        result = collections.OrderedDict()

        for i in range((end_time.date() - start_time.date()).days):

            end = (start_time + datetime.timedelta(days=(i+1)))
            start = (end - datetime.timedelta(days=1))
            # print end
            store_count = Shop.objects.filter(created_time__range=(begin,end)).count()
            nano_count = Sale.objects.filter(active=1, name='Insta360 Nano', active_time__range=(start, end)).count()
            temp = {
                'store': store_count,
                'nano': nano_count
            }
            result[start.strftime('%m-%d')] = temp
        return JsonResponse(result, safe=False)