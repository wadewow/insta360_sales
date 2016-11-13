# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.hashers import make_password, check_password
from ..util.wx_option import option
from ..util.util import getOpenid
from ..util.option import lib_path
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
        return render(request, 'shopkeeper/register.html', {
            'lib_path': lib_path
        })

    if request.method == 'POST':
        para = request.POST
        try:
            store = para.__getitem__('store')
            name =  para.__getitem__('name')
            password = para.__getitem__('password')
            phone = para.__getitem__('phone')
            wx_code = para.__getitem__('wx_code')
            openid = ''
            if wx_code != '':
                openid = getOpenid(wx_code)

            # stores = Store.objects.all().values_list("store", flat=True).distinct()
            # if store in stores:
            #     return HttpResponse('该商家公司名称已被使用！')
            try:
                Store.objects.get(store=store)
                is_used = True
            except ObjectDoesNotExist:
                is_used = False
            except MultipleObjectsReturned:
                is_used = True
            if is_used:
                return HttpResponse("该商家公司名称已被使用！")


            store_info = {
                'store': store,
                'name': name,
                'password': make_password(password),
                'phone': phone,
                'pwd': password,
                'openid': openid
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
def shopkeeper_register_wx(request):
    redirect_uri = 'http://' + option['domain'] + '/sales/shopkeeper/register'
    url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + option['appid'] + '&redirect_uri=' + redirect_uri + '&response_type=code&scope=snsapi_base&#wechat_redirect'
    return redirect(url)

@csrf_exempt
def shopkeeper_login_wx(request):
    redirect_uri = 'http://' + option['domain'] + '/sales/shopkeeper/login'
    url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + option['appid'] + '&redirect_uri=' + redirect_uri + '&response_type=code&scope=snsapi_base&#wechat_redirect'
    return redirect(url)


@csrf_exempt
def shopkeeper_login(request):
    if request.method == 'POST':
        para = request.POST
        try:
            phone = para.__getitem__('phone')
            password = para.__getitem__('password')
            wx_code = para.__getitem__('wx_code')
            try:
                try:
                    result = Store.objects.get(phone=phone)
                except ObjectDoesNotExist:
                    result = Store.objects.get(store=phone)
                is_valid = check_password(password, result.password)
                if is_valid:
                    id = result.id
                    request.session['shopkeeper_id'] = id
                    if wx_code != '':
                        openid = getOpenid(wx_code)
                        if openid != '':
                            result.openid = openid
                            result.save()
                    return HttpResponse('success')
                else:
                    return HttpResponse('密码错误！')
            except ObjectDoesNotExist:
                return HttpResponse('该用户不存在！')
        except:
            return HttpResponse('error')
    elif request.method == 'GET':
        if request.session.__contains__('shopkeeper_id'):
            shopkeeper_id = request.session['shopkeeper_id']
            try:
                Store.objects.get(id=shopkeeper_id)
            except:
                return render(request, 'shopkeeper/login.html', {
                    'lib_path': lib_path
                })
            return redirect('/sales/shopkeeper/info')
        else:
            return render(request, 'shopkeeper/login.html', {
                'lib_path': lib_path
            })


@csrf_exempt
def shopkeeper_info(request):
    if request.method == 'POST':
        return HttpResponse('Do nothing')
    elif request.method == 'GET':
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login_wx')
            else:
                id = request.session['shopkeeper_id']
                result = Store.objects.get(id=id)
                return render(request, 'shopkeeper/info.html', {
                    'store_info': {
                        'store': result.store,
                        'name': result.name,
                        'phone': result.phone,
                    },
                    'lib_path': lib_path
                })
        except:
            return render(request, 'shopkeeper/login.html', {
                'lib_path': lib_path
            })



@csrf_exempt
def shopkeeper_modify(request):
    if request.method == 'POST':
        para = request.POST
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login_wx')
            else:
                id = request.session['shopkeeper_id']
                store = para.__getitem__('store')
                name = para.__getitem__('name')
                phone = para.__getitem__('phone')

                # stores = Store.objects.exclude(id=id).values_list("store", flat=True).distinct()
                # if store in stores:
                #     return HttpResponse('该商家公司名称已被使用！')
                try:
                    Store.objects.exclude(id=id).get(store=store)
                    is_used = True
                except ObjectDoesNotExist:
                    is_used = False
                except MultipleObjectsReturned:
                    is_used = True

                if is_used:
                    return HttpResponse("该商家公司名称已被使用！")


                try:
                    result = Store.objects.filter(id=id).update(
                        store=store,
                        name=name,
                        phone=phone,
                    )
                except:
                    return HttpResponse('该手机号已被绑定！')
                if result == 0:
                    return HttpResponse('账号不存在，请重新注册')
                else:
                    return HttpResponse('success')
        except:
            return HttpResponse('error')
    elif request.method == 'GET':
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login_wx')
            else:
                id = request.session['shopkeeper_id']
                result = Store.objects.get(id=id)
                return render(request, 'shopkeeper/modify.html', {
                    'store_info': {
                        'store': result.store,
                        'name': result.name,
                        'phone': result.phone,
                    },
                    'lib_path': lib_path
                })
        except:
            return redirect('/sales/shopkeeper/login_wx')


@csrf_exempt
def shopkeeper_reset(request):
    if request.method == 'GET':
        return render(request, 'shopkeeper/reset.html', {
            'lib_path': lib_path
        })

    if request.method == 'POST':
        para = request.POST
        try:

            password = para.__getitem__('password')
            phone = para.__getitem__('phone')
            try:
                result = Store.objects.filter(phone=phone).update(
                    password=make_password(password),
                    pwd=password
                )
            except:
                return HttpResponse('重置失败')
            if result == 0:
                return HttpResponse('不存在该账号')
            else:
                return HttpResponse('success')
        except:
            return HttpResponse('重置失败')



@csrf_exempt
def shopkeeper_sales(request):
    if request.method == 'GET':
        if not request.session.__contains__('shopkeeper_id'):
            return redirect('/sales/shopkeeper/login_wx')
        else:
            shopkeeper_id = request.session['shopkeeper_id']
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
                'sale_list': sales,
                'lib_path': lib_path
            })