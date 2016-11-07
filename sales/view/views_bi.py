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
        stores = Shop.objects.all()
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
            try:
                shopkeeper = Store.objects.get(id=business_id)
                store.business_id = shopkeeper
            except:
                pass

        return render(request, 'bi/stores.html', {
            'stores': stores
        })
