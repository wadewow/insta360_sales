# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password, check_password
from ..models import Clerk
from ..models import Shop
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def clerk_register(request):
    if request.method == 'GET':
        return render(request, 'clerk/register.html', {})

    if request.method == 'POST':

        try:
            para = request.POST
            name =  para.__getitem__('name')
            password = para.__getitem__('password')
            phone = para.__getitem__('phone')
            code = para.__getitem__('code')

            try:
                store = Shop.objects.get(code=code)
            except:
                return HttpResponse('代码错误，请联系商家！')

            clerk_info = {
                'store_id': store.id,
                'name': name,
                'password': make_password(password),
                'phone': phone,
                'pwd': password
            }
            result = Clerk.objects.get_or_create(phone=phone,
                                                 defaults=clerk_info)
            print result
            if result[1]:
                clerk = result[0]
                request.session['clerk_id'] = clerk.id
                return HttpResponse('success')
            else:
                return HttpResponse('该手机号已经被注册！')
        except:
            return render(request, 'clerk/register.html', {})


@csrf_exempt
def clerk_login(request):
    if request.method == 'POST':
        para = request.POST
        try:
            phone = para.__getitem__('phone')
            password = para.__getitem__('password')
            try:
                result = Clerk.objects.get(phone=phone)
                is_valid = check_password(password, result.password)
                if is_valid:
                    id = result.id
                    request.session['clerk_id'] = id
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
            return render(request, 'clerk/login.html', {})


@csrf_exempt
def clerk_info(request):
    if request.method == 'POST':
        return HttpResponse('Do nothing')
    elif request.method == 'GET':
        try:
            print request.session.keys()
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login')
            else:
                id = request.session.__getitem__('clerk_id')
                result = Clerk.objects.get(id=id)
                store = Shop.objects.get(id=result.store_id)
                return render(request, 'clerk/info.html', {
                    'clerk_info': {
                        'store': store.name,
                        'name': result.name,
                        'phone': result.phone,
                        'code': store.code
                    }
                })
        except:
            return render(request, 'clerk/login.html', {})



@csrf_exempt
def clerk_modify(request):
    if request.method == 'POST':
        para = request.POST
        try:
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login')
            else:
                id = request.session.__getitem__('clerk_id')
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
                return redirect('/sales/clerk/login')
            else:
                id = request.session.__getitem__('clerk_id')
                result = Clerk.objects.get(id=id)
                store = Shop.objects.get(id=result.store_id)
                return render(request, 'clerk/modify.html', {
                    'clerk_info': {
                        'code': store.code,
                        'name': result.name,
                        'phone': result.phone
                    }
                })
        except:
            return HttpResponse('error')




@csrf_exempt
def clerk_reset(request):
    if request.method == 'GET':
        return render(request, 'clerk/reset.html', {})

    if request.method == 'POST':
        para = request.POST
        try:

            password = para.__getitem__('password')
            phone = para.__getitem__('phone')
            try:
                result = Clerk.objects.filter(phone=phone).update(password=make_password(password))
            except:
                return HttpResponse('fail')
            if result == 0:
                return HttpResponse('不存在该账号')
            else:
                return HttpResponse('success')
        except:
            return HttpResponse('error')

