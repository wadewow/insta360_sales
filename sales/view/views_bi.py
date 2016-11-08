# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from PIL import Image
from ..models import Manager
from ..models import Shop
from ..models import Store
from ..models import Sale
from ..models import Clerk
from ..util.option import dict
from ..util.option import lib_path

import datetime
import json
import os
import sys
import urllib
import urllib2
import time

reload(sys)
sys.setdefaultencoding('utf-8')

@csrf_exempt
def bi_stores(request):
    if request.method == 'GET':
        para = request.GET
        page = 1
        if para.__contains__('page'):
            try:
                page = int(para.__getitem__('page'))
            except:
                page = 1
        if page < 1:
            page = 1
        size = 10
        stores = Shop.objects.filter(created_time__gt='2016-11-05').order_by('-created_time')
        total = stores.count()
        page_total = total / size + (1 if (total % size) > 0 else 0)
        if page > page_total:
            page = page_total
        start = size * (page -1)
        end = start + size
        if end > total:
            end = total
        stores = stores[start: end]

        for store in stores:
            new_option = {}
            option = json.loads(store.option)
            for index, item in enumerate(option):
                n = dict[item]
                new_option[n] = option[item]
            store.option = new_option
            photo_join = store.photo
            photos = photo_join.split(':')
            store.photo = photos
            business_id = store.business_id
            manager_id = store.manager
            try:
                shopkeeper = Store.objects.get(id=business_id)
                store.business_id = shopkeeper
            except:
                pass
            try:
                manager = Manager.objects.get(id=manager_id)
                store.manager = manager
            except:
                pass
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
        sales = Sale.objects.filter(created_time__gt='2016-11-05', name='Insta360 Nano').order_by('-created_time')
        total = sales.count()
        page_total = total / size + (1 if (total % size) > 0 else 0)
        if page > page_total:
            page = page_total
        start = size * (page -1)
        end = start + size
        if end > total:
            end = total
        sales = sales[start: end]
        sales = sales.values()
        for sale in sales:
            sale['show'] = 1
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
                    now = timezone.now()
                    created_time = sale['created_time']
                    deadline = created_time + datetime.timedelta(hours=12)
                    if now >= deadline:
                        state = '作废'
                        sale['show'] = 0
                    else:
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
