# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from ..models import Store

from ..models import Shop

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def store_filter(request):
    if request.method == 'POST':
        return HttpResponse('Do nothing')
    elif request.method == 'GET':
        para = request.GET
        keyword = para.get('keyword', '')
        store_list = Shop.objects.all()
        if keyword == '':
            return render(request, 'promotion/store_filter.html', {
                'store_list': store_list
            })
        type = para.get('type', 'store')
        if type == 'store':
                store_list = store_list.filter(name__contains=keyword)
        else:
            shopkeeper_list = Store.objects.filter(name__contains=keyword)
            id_list = []
            for shookeeper in shopkeeper_list:
                id_list.append(shookeeper.id)
            print id_list
            store_list = store_list.filter(business_id__in=id_list)

        return render(request, 'promotion/store_filter.html', {
            'store_list': store_list
        })
