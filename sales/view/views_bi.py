# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from PIL import Image
from ..models import Manager
from ..models import Shop
from ..models import Store
from ..util.option import dict
from ..util.option import lib_path

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
        stores = Shop.objects.filter(created_time__gt='2016-11-04 23:00').order_by('-created_time')
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
        size = 10
        stores = Shop.objects.filter(created_time__gt='2016-11-04 23:00').order_by('-created_time')
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
