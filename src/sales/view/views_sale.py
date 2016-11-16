# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from ..util.option import lib_path

from ..models import Clerk
from ..models import Sale
from ..models import Shop
from ..models import SaleNano

import random
import json
import sys
import time
import datetime
import urllib
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def sale_scan(request):
    if request.method == 'GET':
        if not request.session.__contains__('clerk_id'):
            return redirect('/sales/clerk/login_wx')
        else:
            return render(request, 'sale/scan.html', {
                'lib_path': lib_path
            })

    if request.method == 'POST':
        try:
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login_wx')
            else:
                para = request.POST
                serial_number = para.__getitem__('serial')
                test = True

                #############################
                try:
                    SaleNano.objects.get(id=serial_number)
                except ObjectDoesNotExist:
                    test = False
                clerk_id = request.session['clerk_id']
                clerk = Clerk.objects.get(id=clerk_id)
                try:
                    shop = Shop.objects.get(id=clerk.store_id)
                except:
                    return redirect('/sales/clerk/info')
                if test:
                    now = timezone.now()
                    active = 1
                    active_time = now
                    name = '测试商品'
                    sale_info = {
                        'active_time': active_time,
                        'store_id': clerk.store_id,
                        'clerk_id': clerk_id,
                        'name': name,
                        'active': active,
                        'serial_number': serial_number,
                        'business_id': shop.business_id,
                        'created_time': now,
                        'manager': shop.manager
                    }
                    Sale.objects.update_or_create(serial_number=serial_number, name=name, defaults=sale_info)
                    return HttpResponse('success')
                #######################################


                try:
                    Shop.objects.get(machine_serial=serial_number)
                    is_machine_serial = True
                except ObjectDoesNotExist:
                    is_machine_serial = False
                except MultipleObjectsReturned:
                    is_machine_serial = True

                if is_machine_serial:
                    return HttpResponse("样机序列号无法扫描！")




                url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getActivateInfo/'
                values = {
                    'serial_number': serial_number
                }
                data = urllib.urlencode(values)
                req = urllib2.Request(url, data=data)
                res_data = urllib2.urlopen(req)
                res = res_data.read()
                res = json.loads(res)
                flag = res['flag']
                if not flag:
                    return HttpResponse("序列号无效！")
                active_time = res['data']['first_use_time']
                device_code = res['data']['equipment_code']
                now = timezone.now()
                active = 0
                if active_time != '0':
                    # active = 1
                    # temp = time.localtime(int(active_time))
                    # active_time = time.strftime("%Y-%m-%d %H:%M:%S", temp)
                    return HttpResponse("该序列号已被售出！")
                else:
                    active_time = now


                name = 'Insta360 Nano'
                try:
                    sale = Sale.objects.get(serial_number=serial_number, name=name)
                    created_time = sale.created_time
                    deadline = created_time + datetime.timedelta(hours=12)
                    format_created = (created_time + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                    if now < deadline:
                        return HttpResponse('该商品于' + format_created + '被扫描，12小时之内无法再次扫描')
                except:
                    pass
                sale_info = {
                    'active_time': active_time,
                    'store_id': clerk.store_id,
                    'clerk_id': clerk_id,
                    'name': name,
                    'active': active,
                    'serial_number': serial_number,
                    'business_id': shop.business_id,
                    'created_time': now,
                    'device_code': device_code,
                    'manager': shop.manager
                }
                try:
                    temp = Sale.objects.get(serial_number=serial_number, name=name)
                    s_id = temp.store_id
                    t_shop = Shop.objects.get(id=s_id)
                    t_shop.sales_count = t_shop.sales_count - 1
                    t_shop.save()
                except:
                    pass
                Sale.objects.update_or_create(serial_number=serial_number, name=name, defaults=sale_info)
                shop.sales_count = shop.sales_count + 1
                shop.save()
                return HttpResponse('success')
        except:
            return HttpResponse('扫描失败！')

@csrf_exempt
def sale_sales(request):
    if request.method == 'POST':
        return HttpResponse('Do nothing')
    if request.method == 'GET':
        try:
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login_wx')
            else:
                clerk_id = request.session['clerk_id']
                Clerk.objects.get(id=clerk_id)
                sales = Sale.objects.filter(clerk_id=clerk_id, name='Insta360 Nano', active=0).values()
    ######################################
                serial_numbers = ''
                for sale in sales:
                    serial_number = sale['serial_number']
                    serial_numbers = serial_numbers + serial_number + ','
                url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getActivateInfos/'
                values = {
                    'serial_number': serial_numbers
                }
                data = urllib.urlencode(values)
                req = urllib2.Request(url, data=data)
                res_data = urllib2.urlopen(req)
                res = res_data.read()
                res = json.loads(res)
                for index, item in enumerate(res):
                    data = res[item]
                    active_time = data['first_use_time']
                    active = 0
                    if active_time != '0':
                      active = 1

                      temp = datetime.datetime.utcfromtimestamp(int(active_time))
                      temp = temp + datetime.timedelta(hours=8)
                      active_time = temp.strftime("%Y-%m-%d %H:%M:%S")

                      # temp = time.localtime(int(active_time)) #################
                      # active_time = time.strftime("%Y-%m-%d %H:%M:%S", temp)
                    else:
                      active_time = timezone.now()
                    sale_info = {
                      'active_time': active_time,
                      'active': active,
                    }
                    Sale.objects.update_or_create(serial_number=item, name='Insta360 Nano',defaults=sale_info)

                now = timezone.now()
                sales = Sale.objects.filter(clerk_id=clerk_id).order_by("-created_time").values()

    #########################################


                for sale in sales:
                    active = sale['active']
                    created_time = sale['created_time']
                    active_time =sale['active_time']
                    deadline = created_time + datetime.timedelta(hours=12)
                    base = sale['base']
                    cash = 0
                    show_time = ''
                    invalid = 0
                    if active==0:
                        if now >= deadline:
                            hint = '未在12小时内激活，不可提现'
                            invalid = 1
                        else:
                            show_time = deadline
                            hint = '之前激活可提现'

                    else:
                        show_time = active_time
                        # print created_time
                        # print deadline
                        # print active_time
                        if active_time >= deadline:
                            hint = '激活，不可提现'
                            invalid = 1
                        else:
                            device_code = sale['device_code']
                            if device_code == '':
                                num = 1
                            else:
                                num = Sale.objects.filter(device_code=device_code,clerk_id=clerk_id,name='Insta360 Nano').count()
                            if num > 1:
                                show_time = ''
                                hint = '被重复手机激活，不可提现'
                            else:
                                hint = '激活，可提现'

                                cash = 1
                                if base == 0:
                                    base = round(random.uniform(1, 10), 2)
                                    if base > 3:
                                        base = round((base * random.uniform(0.1, 1)), 2)
                                    if base > 5.5:
                                        base = round((base * random.uniform(0.2, 1)), 2)
                                    if base < 1:
                                        base = base * 2
                                    temp = {
                                        'base': base
                                    }
                                    Sale.objects.update_or_create(id=sale['id'], defaults=temp)
                                    try:
                                        account = Clerk.objects.get(id=clerk_id)
                                    except:
                                        return HttpResponse("请重新注册")
                                    if sale['name'] != '测试商品':
                                        account.balance += base
                                    account.base += base
                                    account.save()
                                    Sale.objects.filter(id=sale['id']).update(valid=1)
                    sale['hint'] = hint
                    sale['cash'] = cash
                    sale['base'] = base
                    sale['show_time'] = show_time
                    sale['invalid'] = invalid

                return render(request, 'sale/sales.html', {
                    'sale_list': sales,
                    'lib_path': lib_path
                })
        except:
            return redirect('/sales/clerk/login_wx')

#
# @csrf_exempt
# def sale_cash(request):
#     if request.method == 'GET':
#         if not request.session.__contains__('clerk_id'):
#             return redirect('/sales/clerk/login_wx')
#         else:
#             return render(request, 'sale/scan.html', {
# 'lib_path': lib_path})
#
#     if request.method == 'POST':
#         try:
#             if not request.session.__contains__('clerk_id'):
#                 return redirect('/sales/clerk/login_wx')
#             else:
#                 para = request.POST
#                 sale_id = para.__getitem__('sale_id')
#                 Sale.objects.filter(id=sale_id).update(cashed=1)
#                 return HttpResponse("success")
#         except:
#             return  HttpResponse("error")


@csrf_exempt
def sale_guide(request):
    if request.method == 'POST':
        try:
            para = request.POST
            print para
            if not para.__contains__('location'):
                return HttpResponse("Missing parameter: location")
            elif not para.__contains__('serial_number'):
                return HttpResponse("Missing parameter: serail_number")
            else:
# # ######################
#                 timestamp = int(time.time())
#                 temp = time.localtime(int(timestamp))
#                 active_time = time.strftime("%Y-%m-%d %H:%M:%S", temp)
#                 print active_time
##########################
                result = {
                }
                result['status'] = 0
                location = para.__getitem__('location')
                serial_number = para.__getitem__('serial_number')

                print 'location:' + location
                print 'serial_number:' + serial_number

                shop = Shop.objects.filter(machine_serial=serial_number).order_by('-created_time').first()
                if shop != None:
                    store_name = shop.name
                    store_location = shop.province + ' ' + shop.city + ' ' + shop.location
                    info = {}
                    info['name'] = store_name
                    info['location'] = store_location
                    result['status'] = 1

                    website = shop.online
                    if ('jd.com' in website or 'weixin.crossmart' in website):
                        result['status'] = 1
                        info['type'] = 'jd'
                        info['website'] = website
                        result['data'] = info
                    elif len(website) > 10:
                        result['status'] = 1
                        info['type'] = 'taobao'
                        info['website'] = website
                        result['data'] = info
                    else:
                        result['status'] = 2
                        result['data'] = info
                    return JsonResponse(data=result, safe=False)

                sale = Sale.objects.filter(serial_number=serial_number).order_by('-created_time').first()
                if sale == None:
                    result['message'] = 'No nano information'
                    return JsonResponse(data=result,safe=False)
                else:
                    store_id = sale.store_id
                    try:
                        shop = Shop.objects.get(id=store_id)
                    except:
                        result['message'] = 'No store information'
                        return JsonResponse(data=result, safe=False)
                    province = shop.province

                    serial = SaleNano.objects.filter(id=serial_number).count()
                    if False:
                    # if (not location in province) and serial == 0:
                        result['message'] = 'Location mismatching'
                        print result['message']
                        return JsonResponse(data=result, safe=False)
                    else:
                        qualified = False
######################################
                        try:
                            activated_time = para.__getitem__('activated_time')
                        except:
                            activated_time = '0'
                        if activated_time != '0':
                            sale.active = 1
                            temp = time.localtime(int(activated_time))
                            sale.active_time = time.strftime("%Y-%m-%d %H:%M:%S", temp)
                            sale.save()

######################################
                        if serial == 0:
                            active = sale.active
                            created_time = sale.created_time
                            active_time = sale.active_time

                            deadline = created_time + datetime.timedelta(hours=12)
                            deadline = (deadline + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

                            clerk_id = sale.clerk_id
                            device_code = sale.device_code
                            if device_code == '':
                                num = 1
                            else:
                                num = Sale.objects.filter(device_code=device_code, clerk_id=clerk_id,name='Insta360 Nano').count()

                            print active_time
                            print deadline

                            if active == 1 and active_time < deadline and num < 2:
                                qualified = True
                        else:
                            qualified = True


                        #  #######################################
                        if not qualified:
                            result['message'] = 'Not qualified'
                            return JsonResponse(data=result, safe=False)
                        else:
                            store_name = shop.name
                            store_location = shop.province + ' ' + shop.city + ' ' + shop.location
                            info = {}
                            info['name'] = store_name
                            info['location'] = store_location
                            result['status'] = 1

                            website = shop.online
                            if ('jd.com' in website or 'weixin.crossmart' in website):
                                result['status'] = 1
                                info['type'] = 'jd'
                                info['website'] = website
                                result['data'] = info
                            elif len(website) > 10:
                                result['status'] = 1
                                info['type'] = 'taobao'
                                info['website'] = website
                                result['data'] = info
                            else:
                                result['status'] = 2
                                result['data'] = info
                            return JsonResponse(data=result, safe=False)

        except:
            return HttpResponse("Something unknown wrong")


@csrf_exempt
def sale_test(request):
    if request.method == 'GET':
        if not request.session.__contains__('clerk_id'):
            return redirect('/sales/clerk/login_wx')
        else:
            return render(request, 'sale/scan.html', {
                'lib_path': lib_path
            })

    if request.method == 'POST':
        try:
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login_wx')
            else:
                para = request.POST

                serial_number = para.__getitem__('serial')
                try:
                    SaleNano.objects.get(id=serial_number)
                except:
                    return HttpResponse('非测试序列号不可扫描')

                now = timezone.now()
                active = 1
                active_time = now
                clerk_id = request.session['clerk_id']
                clerk = Clerk.objects.get(id=clerk_id)
                try:
                    shop = Shop.objects.get(id=clerk.store_id)
                except:
                    return redirect('/sales/clerk/info')
                name = '测试商品'
                sale_info = {
                    'active_time': active_time,
                    'store_id': clerk.store_id,
                    'clerk_id': clerk_id,
                    'name': name,
                    'active': active,
                    'serial_number': serial_number,
                    'business_id': shop.business_id,
                    'created_time': now
                }
                Sale.objects.update_or_create(serial_number=serial_number, name=name, defaults=sale_info)
                return HttpResponse('success')
        except:
            return HttpResponse('扫描失败！')