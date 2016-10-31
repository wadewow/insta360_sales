# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password, check_password

from ..models import Store

from ..models import Sale
from ..models import Shop
from ..models import Clerk

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def shopkeeper_register(request):
    if request.method == 'GET':
        return render(request, 'shopkeeper/register.html', {})

    if request.method == 'POST':
        para = request.POST
        try:
            store = para.__getitem__('store')
            name =  para.__getitem__('name')
            password = para.__getitem__('password')
            phone = para.__getitem__('phone')
            store_info = {
                'store': store,
                'name': name,
                'password': make_password(password),
                'phone': phone,
            }
            result = Store.objects.get_or_create(phone=phone,
                                                 defaults=store_info)
            if result[1]:
                shopkeeper= result[0]
                request.session['shopkeeper_id'] = shopkeeper.id
                return HttpResponse('success')
            else:
                return HttpResponse('该手机号已经被注册！')
        except:
            return HttpResponse('error')


@csrf_exempt
def shopkeeper_login(request):
    if request.method == 'POST':
        para = request.POST
        try:
            phone = para.__getitem__('phone')
            password = para.__getitem__('password')
            try:
                result = Store.objects.get(phone=phone)
                is_valid = check_password(password, result.password)
                if is_valid:
                    id = result.id
                    request.session['shopkeeper_id'] = id
                    return HttpResponse('success')
                else:
                    return HttpResponse('密码错误！')
            except ObjectDoesNotExist:
                return HttpResponse('该用户不存在！')
        except:
            return HttpResponse('error')
    elif request.method == 'GET':
        if request.session.__contains__('shopkeeper_id'):
            return redirect('/sales/shopkeeper/info')
        else:
            return render(request, 'shopkeeper/login.html', {})


@csrf_exempt
def shopkeeper_info(request):
    if request.method == 'POST':
        return HttpResponse('Do nothing')
    elif request.method == 'GET':
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login')
            else:
                id = request.session.__getitem__('shopkeeper_id')
                result = Store.objects.get(id=id)
                return render(request, 'shopkeeper/info.html', {
                    'store_info': {
                        'store': result.store,
                        'name': result.name,
                        'phone': result.phone,
                    }
                })
        except:
            return render(request, 'shopkeeper/login.html', {})



@csrf_exempt
def shopkeeper_modify(request):
    if request.method == 'POST':
        para = request.POST
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login')
            else:
                id = request.session.__getitem__('shopkeeper_id')
                store = para.__getitem__('store')
                name = para.__getitem__('name')
                phone = para.__getitem__('phone')

                try:
                    result = Store.objects.filter(id=id).update(
                        store=store,
                        name=name,
                        phone=phone,
                    )
                except:
                    return HttpResponse('该手机号已被绑定！')
                if result == 0:
                    return HttpResponse('fail')
                else:
                    return HttpResponse('success')
        except:
            return HttpResponse('error')
    elif request.method == 'GET':
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login')
            else:
                id = request.session.__getitem__('shopkeeper_id')
                result = Store.objects.get(id=id)
                return render(request, 'shopkeeper/modify.html', {
                    'store_info': {
                        'store': result.store,
                        'name': result.name,
                        'phone': result.phone,
                    }
                })
        except:
            return HttpResponse('error')


@csrf_exempt
def shopkeeper_reset(request):
    if request.method == 'GET':
        return render(request, 'shopkeeper/reset.html', {})

    if request.method == 'POST':
        para = request.POST
        try:

            password = para.__getitem__('password')
            phone = para.__getitem__('phone')
            try:
                result = Store.objects.filter(phone=phone).update(password=make_password(password))
            except:
                return HttpResponse('fail')
            if result == 0:
                return HttpResponse('不存在该账号')
            else:
                return HttpResponse('success')
        except:
            return HttpResponse('error')



@csrf_exempt
def shopkeeper_sales(request):
    if request.method == 'GET':
        if not request.session.__contains__('shopkeeper_id'):
            return redirect('/sales/shopkeeper/login')
        else:
            shopkeeper_id = request.session.get('shopkeeper_id')
            sales = Sale.objects.filter(business_id=shopkeeper_id).order_by("-created_time").values()

            for sale in sales:
                clerk_id = sale['clerk_id']
                store_id = sale['store_id']
                clerk = Clerk.objects.get(id=clerk_id)
                store = Shop.objects.get(id=store_id)
                clerk_name = clerk.name
                clerk_phone = clerk.phone
                store_name = store.name
                store_code = store.code
                sale['clerk_name'] = clerk_name
                sale['clerk_phone'] = clerk_phone
                sale['store_name'] = store_name
                sale['store_code'] = store_code

            return render(request, 'shopkeeper/sales.html', {
                'sale_list': sales
            })