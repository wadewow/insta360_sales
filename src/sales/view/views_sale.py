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
                    if shop.code == '':
                        return HttpResponse('您所属的门店已注销')
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
                        'manager': shop.manager,
                        'province': shop.province
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
                now = timezone.now()
                active = 0
                if active_time != '0':
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
                    'manager': shop.manager,
                    'province': shop.province
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
def sale_super_scan(request):
    if request.method == 'GET':
        if not request.session.__contains__('clerk_id'):
            return redirect('/sales/clerk/login')
        else:
            return render(request, 'sale/super_scan.html', {
                'lib_path': lib_path
            })

    if request.method == 'POST':
        try:
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login')
            else:
                para = request.POST
                serial_number = para.__getitem__('serial')
                test = True

                try:
                    SaleNano.objects.get(id=serial_number)
                except ObjectDoesNotExist:
                    test = False
                clerk_id = request.session['clerk_id']
                clerk = Clerk.objects.get(id=clerk_id)
                try:
                    shop = Shop.objects.get(id=clerk.store_id)
                    if shop.code == '':
                        return HttpResponse('您所属的门店已注销')
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
                        'manager': shop.manager,
                        'province': shop.province
                    }
                    Sale.objects.update_or_create(serial_number=serial_number, name=name, defaults=sale_info)
                    return HttpResponse('success')

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
                now = timezone.now()
                active = 0
                active_time = now

                name = 'Insta360 Nano'
                sale_info = {
                    'active_time': active_time,
                    'store_id': clerk.store_id,
                    'clerk_id': clerk_id,
                    'name': name,
                    'active': active,
                    'serial_number': serial_number,
                    'business_id': shop.business_id,
                    'created_time': now,
                    'manager': shop.manager,
                    'province': shop.province
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
def sale_super_record(request):
    if request.method == 'GET':
        para = request.GET
        serial_number = para.__getitem__('serial')
        clerk_phone = para.__getitem__('phone')
        test = True
        try:
            SaleNano.objects.get(id=serial_number)
        except ObjectDoesNotExist:
            test = False
        clerk = Clerk.objects.get(phone=clerk_phone)
        try:
            shop = Shop.objects.get(id=clerk.store_id)
            if shop.code == '':
                return HttpResponse('您所属的门店已注销')
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
                'clerk_id': clerk.id,
                'name': name,
                'active': active,
                'serial_number': serial_number,
                'business_id': shop.business_id,
                'created_time': now,
                'manager': shop.manager,
                'province': shop.province
            }
            Sale.objects.update_or_create(serial_number=serial_number, name=name, defaults=sale_info)
            return HttpResponse('success')
        # try:
        #     Shop.objects.get(machine_serial=serial_number)
        #     is_machine_serial = True
        # except ObjectDoesNotExist:
        #     is_machine_serial = False
        # except MultipleObjectsReturned:
        #     is_machine_serial = True
        #
        # if is_machine_serial:
        #     return HttpResponse("样机序列号无法扫描！")

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
        now = timezone.now()
        active = 0
        active_time = now

        name = 'Insta360 Nano'
        sale_info = {
            'active_time': active_time,
            'store_id': clerk.store_id,
            'clerk_id': clerk.id,
            'name': name,
            'active': active,
            'serial_number': serial_number,
            'business_id': shop.business_id,
            'created_time': now,
            'manager': shop.manager,
            'province': shop.province
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
                    device_code = data['equipment_code']
                    if active_time != '0':
                      active = 1

                      temp = datetime.datetime.utcfromtimestamp(int(active_time))
                      temp = temp + datetime.timedelta(hours=8)
                      active_time = temp.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        continue
                    sale_info = {
                      'active_time': active_time,
                      'active': active,
                      'device_code': device_code
                    }
                    Sale.objects.update_or_create(serial_number=item, name='Insta360 Nano',defaults=sale_info)

                now = timezone.now()
                sales = Sale.objects.filter(clerk_id=clerk_id).order_by("-created_time").values()

    #########################################
                for sale in sales:
                    active = sale['active']
                    created_time = sale['created_time']
                    active_time =sale['active_time']
                    delay = sale['delay']
                    delta = (168 if delay == 1 else 12)
                    deadline = created_time + datetime.timedelta(hours=delta)
                    base = sale['base']
                    cash = 0
                    show_time = ''
                    invalid = 0
                    if active==0:
                        if now >= deadline:
                            hint = '未在' + str(delta) + '小时内激活，不可提现'
                            invalid = 0
                        else:
                            show_time = deadline
                            hint = '之前激活可提现'
                    else:
                        show_time = active_time
                        if active_time >= deadline:
                            hint = '激活，不可提现'
                            invalid = 0
                        else:
                            device_code = sale['device_code']
                            if device_code == '':
                                num = 1
                            else:
                                num = Sale.objects.filter(
                                    device_code=device_code,
                                    clerk_id=clerk_id,
                                    name='Insta360 Nano',
                                    created_time__lte=created_time
                                ).count()
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
                                    Sale.objects.filter(id=sale['id']).update(valid=1, base=base)
                                    try:
                                        account = Clerk.objects.get(id=clerk_id)
                                    except:
                                        return HttpResponse("请重新注册")
                                    if sale['name'] != '测试商品':
                                        account.balance += base
                                    account.base += base
                                    account.save()
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


@csrf_exempt
def sale_guide(request):
    if request.method == 'POST':
        # try:
            para = request.POST
            print para
            if not para.__contains__('location'):
                return HttpResponse("Missing parameter: location")
            elif not para.__contains__('serial_number'):
                return HttpResponse("Missing parameter: serial_number")
            else:
                result = {
                }
                result['status'] = 0
                location = para.__getitem__('location')
                serial_number = para.__getitem__('serial_number')

                shop = Shop.objects.filter(machine_serial=serial_number).order_by('-created_time').first()
                if shop != None and location in shop.province and shop.code != '':
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
                    ######################################
                    try:
                        activated_time = para.__getitem__('activated_time')
                    except:
                        activated_time = '0'
                    if activated_time != '0' and sale.active == 0:
                        sale.active = 1
                        temp = datetime.datetime.utcfromtimestamp(int(activated_time))
                        temp = temp + datetime.timedelta(hours=8)
                        sale.active_time= temp.strftime("%Y-%m-%d %H:%M:%S")
                        sale.save()
                    ######################################
                    store_id = sale.store_id
                    try:
                        shop = Shop.objects.get(id=store_id)
                        if shop.code == '':
                            result['message'] = 'The store has been disabled'
                            return JsonResponse(data=result, safe=False)
                    except:
                        result['message'] = 'No store information'
                        return JsonResponse(data=result, safe=False)
                    province = shop.province

                    serial = SaleNano.objects.filter(id=serial_number).count()
                    if not location in province:
                        result['message'] = 'Location mismatching'
                        return JsonResponse(data=result, safe=False)
                    else:
                        qualified = False
                        if serial == 0:
                            active = sale.active
                            created_time = sale.created_time
                            active_time = sale.active_time
                            delay = sale.delay
                            delta = (168 if delay == 1 else 12)
                            deadline = created_time + datetime.timedelta(hours=delta)
                            clerk_id = sale.clerk_id
                            device_code = sale.device_code
                            if device_code == '':
                                num = 1
                            else:
                                num = Sale.objects.filter(device_code=device_code, clerk_id=clerk_id,name='Insta360 Nano').count()
                            if active == 1 and active_time < deadline and num < 2:
                                qualified = True
                        else:
                            qualified = True

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

        # except:
        #     return HttpResponse("Something unknown wrong")
