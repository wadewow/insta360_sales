# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from ..models import Shop
from ..models import Store
from ..models import Clerk
from ..models import Sale
from ..util.option import lib_path

import json
import sys
import urllib
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def agent_login(request):
    if request.method == 'GET':
        return render(request, 'agent/login.html', {
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

        if True:
            request.session['agent_id'] = username
            return HttpResponse(content='success')
        else:
            return HttpResponse(content='账号或密码错误！')


@csrf_exempt
def agent_list(request):
    if request.method == 'GET':
        if not request.session.__contains__('agent_id'):
            return redirect('/sales/agent/login')
        else:
            agent_id = request.session['agent_id']
            store_list = Shop.objects.filter(agent=agent_id).values()
            for store in store_list:
                business_id = store['business_id']
                try:
                    business = Store.objects.get(id=business_id)
                except:
                    business = {}
                store['business'] = business
                # store_id = store['id']
                # sales_count = Sale.objects.filter(store_id=store_id, name='Insta360 Nano').count()
                # store['sales_count'] = sales_count
            return render(request, 'agent/list.html', {
                'store_list': store_list,
                'lib_path': lib_path
            })


@csrf_exempt
def agent_sales(request):
    if request.method == 'GET':
        if not request.session.__contains__('agent_id'):
            return redirect('/sales/agent/login')
        para = request.GET
        if not para.__contains__('store_id'):
            return redirect('/sales/agent/list')
        agent_id = request.session['agent_id']
        store_id = para.__getitem__('store_id')
        sale_list = Sale.objects.filter(store_id=store_id, name="Insta360 Nano").order_by('-created_time').values()
        serial_numbers = ''
        for sale in sale_list:
            clerk_id = sale['clerk_id']
            try:
                clerk = Clerk.objects.get(id=clerk_id)
            except:
                clerk = {}
            sale['clerk'] = clerk
            serial_number = sale['serial_number']
            serial_numbers = serial_numbers + serial_number + ','
        url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/agent/getagentbyserialnumber'
        values = {
            'serial_numbers': serial_numbers
        }
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data=data)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        res = json.loads(res)
        for sale in sale_list:
            sale['illegal'] = 0
            serial_number = sale['serial_number']
            try:
                agent = res[serial_number]
                agent_number = agent['custom_number']
                print agent_number
                print agent_id
                print agent_number == agent_id
                if agent != agent_id:
                    sale['illegal'] = 1
                sale['agent'] = agent

            except:
                pass

        return render(request, 'agent/sales.html', {
            'sale_list': sale_list,
            'lib_path': lib_path
        })
