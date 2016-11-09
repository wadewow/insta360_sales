# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password, check_password
from ..models import Clerk
from ..models import Shop
from ..util.util import getOpenid
from ..util.wx_option import option
from ..util.option import lib_path

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def clerk_register(request):
    if request.method == 'GET':
        return render(request, 'clerk/register.html', {
            'lib_path': lib_path
        })

    if request.method == 'POST':

        try:
            para = request.POST
            name =  para.__getitem__('name')
            password = para.__getitem__('password')
            phone = para.__getitem__('phone')
            code = para.__getitem__('code')
            wx_code = para.__getitem__('wx_code')


            try:
                store = Shop.objects.get(code=code)
            except:
                return HttpResponse('代码错误，请联系商家！')

            openid = ''
            if wx_code != '':
                openid = getOpenid(wx_code)

            clerk_info = {
                'store_id': store.id,
                'name': name,
                'password': make_password(password),
                'phone': phone,
                'pwd': password,
                'openid': openid
            }
            result = Clerk.objects.get_or_create(phone=phone,
                                                 defaults=clerk_info)
            if result[1]:
                clerk = result[0]
                request.session['clerk_id'] = clerk.id
                return HttpResponse('success')
            else:
                return HttpResponse('该手机号已经被注册！')
        except:
            return HttpResponse('error')


@csrf_exempt
def clerk_register_wx(request):
    redirect_uri = 'http://' + option['domain'] + '/sales/clerk/register'
    url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + option['appid'] + '&redirect_uri=' + redirect_uri + '&response_type=code&scope=snsapi_base&#wechat_redirect'
    return redirect(url)

@csrf_exempt
def clerk_login_wx(request):
    redirect_uri = 'http://' + option['domain'] + '/sales/clerk/login'
    url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + option['appid'] + '&redirect_uri=' + redirect_uri + '&response_type=code&scope=snsapi_base&#wechat_redirect'
    return redirect(url)

@csrf_exempt
def clerk_login(request):
    if request.method == 'POST':
        para = request.POST
        try:
            phone = para.__getitem__('phone')
            password = para.__getitem__('password')
            wx_code = para.__getitem__('wx_code')
            try:
                result = Clerk.objects.get(phone=phone)
                is_valid = check_password(password, result.password)
                if is_valid:
                    id = result.id
                    request.session['clerk_id'] = id
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
        if request.session.__contains__('clerk_id'):
            return redirect('/sales/clerk/info')
        else:
            return render(request, 'clerk/login.html', {
                'lib_path': lib_path
            })


@csrf_exempt
def clerk_info(request):
    if request.method == 'POST':
        return HttpResponse('Do nothing')
    elif request.method == 'GET':
        try:
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login_wx')
            else:
                id = request.session['clerk_id']
                result = Clerk.objects.get(id=id)
                try:
                    store = Shop.objects.get(id=result.store_id)
                except:
                    return render(request, 'clerk/info.html', {
                        'clerk_info': {
                            'store': '',
                            'name': result.name,
                            'phone': result.phone,
                            'code': ''
                        },
                        'lib_path': lib_path
                    })
                return render(request, 'clerk/info.html', {
                    'clerk_info': {
                        'store': store.name,
                        'name': result.name,
                        'phone': result.phone,
                        'code': store.code
                    },
                    'lib_path': lib_path
                })
        except:
            return redirect('/sales/clerk/login_wx')



@csrf_exempt
def clerk_modify(request):
    if request.method == 'POST':
        para = request.POST
        try:
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login_wx')
            else:
                id = request.session['clerk_id']
                code = para.__getitem__('code')
                name = para.__getitem__('name')
                phone = para.__getitem__('phone')
                try:
                    store = Shop.objects.get(code=code)
                except:
                    return HttpResponse('代码错误，请联系商家！')
                try:
                    result = Clerk.objects.filter(id=id).update(
                        store_id=store.id,
                        name=name,
                        phone=phone
                    )
                except:
                    return HttpResponse('fail')
                if result == 0:
                    return HttpResponse('fail')
                else:
                    return HttpResponse('success')
        except:
            return HttpResponse('error')
    elif request.method == 'GET':
        try:
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login_wx')
            else:
                id = request.session['clerk_id']
                result = Clerk.objects.get(id=id)
                try:
                    store = Shop.objects.get(id=result.store_id)
                except:
                    return render(request, 'clerk/modify.html', {
                        'clerk_info': {
                            'code': '',
                            'name': result.name,
                            'phone': result.phone
                        },
                        'lib_path': lib_path
                    })
                return render(request, 'clerk/modify.html', {
                    'clerk_info': {
                        'code': store.code,
                        'name': result.name,
                        'phone': result.phone
                    },
                    'lib_path': lib_path
                })
        except:
            return redirect('/sales/clerk/login_wx')




@csrf_exempt
def clerk_reset(request):
    if request.method == 'GET':
        return render(request, 'clerk/reset.html', {
            'lib_path': lib_path
        })

    if request.method == 'POST':
        para = request.POST
        try:

            password = para.__getitem__('password')
            phone = para.__getitem__('phone')
            try:
                result = Clerk.objects.filter(phone=phone).update(
                    password=make_password(password),
                    pwd=password
                )
            except:
                return HttpResponse('fail')
            if result == 0:
                return HttpResponse('不存在该账号')
            else:
                return HttpResponse('success')
        except:
            return HttpResponse('error')

