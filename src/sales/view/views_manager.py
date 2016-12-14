# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.hashers import make_password

from ..models import Manager
from ..models import Shop
from ..models import Clerk
from ..models import Exhibition
from ..models import Store
from ..models import Sale
from ..util.util import getCode
from ..util.option import dict
from ..util.option import lib_path

import json
import sys
import urllib
import urllib2
import codecs
import datetime
import csv

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def manager_login(request):
    if request.method == 'GET':
        return render(request, 'manager/login.html', {
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

        url = 'http://account.arashivision.com/user/getUserToken'
        values = {
            'jobnumber': username,
            'password': password
        }
        data = urllib.urlencode(values)
        req = urllib2.Request(url=url, data=data)
        try:
            res_data = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print e.code
            print e.reason
            return HttpResponse(content='账号或密码错误！')
        status = res_data.code
        data = res_data.read()
        print status
        print data
        if status == 200:
            request.session['manager_id'] = username
            return HttpResponse(content='success', status=status)
        else:
            return HttpResponse(content='账号或密码错误！', status=status)


@csrf_exempt
def manager_login_pc(request):
    if request.method == 'GET':
        return render(request, 'manager/login_pc.html', {
            'lib_path': lib_path
        })


@csrf_exempt
def manager_list(request):
    if request.method == 'GET':
        if not request.session.__contains__('manager_id'):
            return redirect('/sales/manager/login')
        else:
            manager_id = request.session['manager_id']

            try:
                manager = Manager.objects.get(id=manager_id)
                is_leader = manager.is_leader
                if is_leader == 1:
                    region = manager.region
                    manager_list = Manager.objects.filter(region=region).values('id')
                    stores = Shop.objects.filter(manager__in=manager_list)
                else:
                    stores = Shop.objects.filter(manager=manager_id)
            except:
                stores = Shop.objects.filter(manager=manager_id)

            store_list = stores.values()
            for store in store_list:
                new_option = {}
                option = json.loads(store['option'])
                for index, item in enumerate(option):
                    n = dict[item]
                    new_option[n] = option[item]
                store['option'] = new_option
                store_id = store['id']
                sales_count = Sale.objects.filter(store_id=store_id, name='Insta360 Nano').count()
                store['sales_count'] = sales_count
                t_manager_id = store['manager']
                try:
                    manager = Manager.objects.get(id=t_manager_id)
                    store['manager'] = manager
                except:
                    pass
            return render(request, 'manager/list.html', {
                'store_list': store_list,
                'lib_path': lib_path
            })


@csrf_exempt
def manager_create(request):
    if request.method == 'GET':
        if not request.session.__contains__('manager_id'):
            return redirect('/sales/manager/login')

        url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getAgentNumberInfo'
        req = urllib2.Request(url=url)
        try:
            res_data = urllib2.urlopen(req)
        except:
            res_data = '["默认"]'
        data = res_data.read()
        try:
            agent_list = json.loads(data)
        except:
            agent_list = []
        option = dict
        return render(request, 'manager/create.html', {
            "options": option,
            "agent_list": agent_list,
            'lib_path': lib_path
        })
    if request.method == 'POST':
        try:
            if not request.session.__contains__('manager_id'):
                return redirect('/sales/manager/login')
            else:
                manager = request.session['manager_id']
                para = request.POST
                business_store = para.__getitem__('business_store')
                business_name = para.__getitem__('business_name')
                business_phone = para.__getitem__('business_phone')
                business_password = business_phone[-6:]

                try:
                    Store.objects.get(store=business_store)
                    is_used = True
                except ObjectDoesNotExist:
                    is_used = False
                except MultipleObjectsReturned:
                    is_used = True
                if is_used:
                    return HttpResponse("该商家公司名称已被使用！")

                business_info = {
                    'store': business_store,
                    'name': business_name,
                    'password': make_password(business_password),
                    'phone': business_phone,
                    'pwd': business_password
                }
                result = Store.objects.get_or_create(phone=business_phone,
                                                     defaults=business_info)
                if result[1]:
                    business = result[0]
                else:
                    return HttpResponse('该手机号已经被注册！')
                temp = para.__getitem__("store_city")
                try:
                    temps = temp.split("/")
                    store_province = temps[0]
                    store_city = temps[1]
                except:
                    store_province = temp
                    store_city = ''
                store_name = para.__getitem__("store_name")
                store_online = para.__getitem__("store_online")
                store_location = para.__getitem__("store_location")
                store_exhibition = para.__getitem__("store_exhibition")
                store_machine_serial = para.__getitem__("store_machine_serial")
                store_remark = para.__getitem__("store_remark")
                store_agent = para.__getitem__("store_agent")
                try:
                    res = Exhibition.objects.get(id=store_exhibition)
                except:
                    return HttpResponse('展台序列号无效')

                n = len(manager)
                for i in range(0,4-n):
                    manager = '0' + manager
                try:
                    Manager.objects.get(id=manager)
                except:
                    return HttpResponse('销售经理编号无效！')

                try:
                    Shop.objects.get(machine_serial=store_machine_serial)
                    return HttpResponse('该样机已被使用！')
                except MultipleObjectsReturned:
                    return HttpResponse('该样机已被使用！')
                except ObjectDoesNotExist:
                    pass

                option = {}
                for index, item in enumerate(dict):
                    if para.__contains__(item):
                        value = para.__getitem__(item)
                        option[item] = value

                code = getCode(6)
                while True:
                    try:
                        Shop.objects.get(code=code)
                        code = getCode(6)
                    except ObjectDoesNotExist:
                        break
                    except MultipleObjectsReturned:
                        code = getCode(6)

                try:
                    photo_num = int(para.__getitem__("photo_num"))
                except:
                    photo_num = 1

                path_join = ''
                for i in range(0, photo_num):
                    if (not request.FILES.__contains__("photo" + str(i))) or para.__contains__('removephoto' + str(i)):
                        continue
                    file = request.FILES.__getitem__("photo"+str(i))
                    path = 'sales/static/store/' + file.name
                    path = default_storage.save(path, file)

                    path_join += path[5:] + ':'
                if len(path_join) > 0:
                    path_join = path_join[:-1]


                res.active = 1
                res.save()
                store = Shop.objects.create(
                    business_id=business.id,
                    name=store_name,
                    online=store_online,
                    province=store_province,
                    city=store_city,
                    location=store_location,
                    photo=path_join,
                    code=code,
                    exhibition=store_exhibition,
                    option=json.dumps(option),
                    machine_serial=store_machine_serial,
                    remark = store_remark,
                    agent=store_agent,
                    manager=manager
                )

                if store_machine_serial != '':
                    url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/camera/setOffsetBySerial'
                    values = {
                        'serial_number': store_machine_serial,
                        'offset': 0
                    }
                    try:
                        data = urllib.urlencode(values)
                        req = urllib2.Request(url, data=data)
                        res_data = urllib2.urlopen(req)
                        res = res_data.read()
                        res = json.loads(res)
                        print res
                    except:
                        print 'setOffsetBySerial error'

                clerk_name = para.__getitem__('clerk_name')
                clerk_phone = para.__getitem__('clerk_phone')
                clerk_password = clerk_phone[-6:]

                clerk_info = {
                    'store_id': store.id,
                    'name': clerk_name,
                    'password': make_password(clerk_password),
                    'phone': clerk_phone,
                    'pwd': clerk_password,
                }
                result = Clerk.objects.get_or_create(phone=clerk_phone,
                                                     defaults=clerk_info)
                if not result[1]:
                    return HttpResponse('该手机号已经被注册！')
                return HttpResponse('success')
        except:
            return HttpResponse('创建失败')


@csrf_exempt
def manager_modify_store(request):
    if request.method == 'POST':
        try:
            if not request.session.__contains__('manager_id'):
                return redirect('/sales/manager/login')
            else:
                para = request.POST
                store_id = para.__getitem__("store_id")
                temp = para.__getitem__("city")
                try:
                    temps = temp.split("/")
                    province = temps[0]
                    city = temps[1]
                except:
                    province = temp
                    city = ''
                name = para.__getitem__("name")
                online = para.__getitem__("online")
                location = para.__getitem__("location")
                exhibition = para.__getitem__("exhibition")
                machine_serial = para.__getitem__("machine_serial")
                remark = para.__getitem__('remark')
                reason = para.__getitem__('reason')
                # agent = para.__getitem__("agent")
                manager = para.__getitem__("manager")
                try:
                    res = Exhibition.objects.get(id=exhibition)
                except:
                    return HttpResponse('序列号无效')

                n = len(manager)
                for i in range(0,4-n):
                    manager = '0' + manager
                try:
                    Manager.objects.get(id=manager)
                except:
                    return HttpResponse('销售经理编号无效！')

                # url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getActivateInfo/'
                # values = {
                #     'serial_number': machine_serial
                # }
                # data = urllib.urlencode(values)
                # req = urllib2.Request(url, data=data)
                # res_data = urllib2.urlopen(req)
                # res_data = res_data.read()
                # res_data = json.loads(res_data)
                # flag = res_data['flag']
                # if not flag:
                #     return HttpResponse("样机序列号无效！")


                try:
                    Shop.objects.exclude(id=store_id).get(machine_serial=machine_serial)
                    return HttpResponse('该样机已被使用！')
                except MultipleObjectsReturned:
                    return HttpResponse('该样机已被使用！')
                except ObjectDoesNotExist:
                    pass


                option = {}
                for index, item in enumerate(dict):
                    if para.__contains__(item):
                        value = para.__getitem__(item)
                        option[item] = value

                try:
                    photo_num = int(para.__getitem__("photo_num"))
                except:
                    photo_num = 1
                path_join = ''
                for i in range(0, photo_num):
                    if (not request.FILES.__contains__("photo" + str(i))) or para.__contains__('removephoto' + str(i)):
                        continue
                    file = request.FILES.__getitem__("photo" + str(i))

                    # timestamp = str(int(time.time()))

                    path = 'sales/static/store/' + file.name
                    path = default_storage.save(path, file)

                    # if os.path.isfile(path):
                    #     sImg = Image.open(path)
                    #     w, h = sImg.size
                    #     dImg = sImg.resize((w / 4, h / 4), Image.ANTIALIAS)
                    #     dImg.save(path)
                    #     print path
                    path_join += path[5:] + ':'
                if len(path_join) > 0:
                    path_join = path_join[:-1]

                res.active = 1
                res.save()
                try:
                    store = Shop.objects.filter(id=store_id)
                    s = store.first()
                    old_machine_serial = s.machine_serial
                except:
                    return HttpResponse('该门店不存在')
                if len(path_join) > 0:
                    try:
                        res = store.update(
                            name=name,
                            online=online,
                            province=province,
                            city=city,
                            location=location,
                            exhibition=exhibition,
                            photo=path_join,
                            option=json.dumps(option),
                            machine_serial=machine_serial,
                            remark=remark,
                            reason=reason,
                            # agent=agent,
                            manager=manager
                        )
                    except:
                        return HttpResponse('修改失败')
                else:
                    try:
                        res = store.update(
                            name=name,
                            online=online,
                            province=province,
                            city=city,
                            location=location,
                            exhibition=exhibition,
                            option=json.dumps(option),
                            machine_serial=machine_serial,
                            remark=remark,
                            reason=reason,
                            # agent=agent,
                            manager=manager
                        )
                    except:
                        return HttpResponse('修改失败')
                if res == 0:
                    return HttpResponse('该门店不存在')
                else:
                    shopkeeper_id = Shop.objects.get(id=store_id).business_id
                    result = {
                        'result': 'success',
                        'shopkeeper_id': shopkeeper_id
                    }
                    if old_machine_serial != machine_serial:
                        if old_machine_serial != '':
                            url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/camera/setOffsetBySerial'
                            values = {
                                'serial_number': old_machine_serial,
                                'offset': 1
                            }
                            try:
                                data = urllib.urlencode(values)
                                req = urllib2.Request(url, data=data)
                                res_data = urllib2.urlopen(req)
                                res = res_data.read()
                                res = json.loads(res)
                                print res
                            except:
                                print 'setOffsetBySerial error'

                        if machine_serial != '':
                            url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/camera/setOffsetBySerial'
                            values = {
                                'serial_number': machine_serial,
                                'offset': 0
                            }
                            try:
                                data = urllib.urlencode(values)
                                req = urllib2.Request(url, data=data)
                                res_data = urllib2.urlopen(req)
                                res = res_data.read()
                                res = json.loads(res)
                                print res
                            except:
                                print 'setOffsetBySerial error'
                    return JsonResponse(result, safe=False)
        except:
            return HttpResponse('error')
    elif request.method == 'GET':
        try:
            para = request.GET
            if not request.session.__contains__('manager_id'):
                return redirect('/sales/manager/login')
            elif not para.__contains__('store_id'):
                return redirect('/sales/manager/list')
            else:
                manager_id = request.session['manager_id']
                url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getAgentNumberInfo'
                req = urllib2.Request(url=url)
                try:
                    res_data = urllib2.urlopen(req)
                except:
                    res_data = '["默认"]'
                data = res_data.read()
                agent_list = json.loads(data)
                store_id = para.__getitem__('store_id')
                result = Shop.objects.get(id=store_id)
                if str(manager_id) != str(result.manager):
                    return redirect('/sales/manager/list')
                option = json.loads(result.option)
                print option
                return render(request, 'manager/modify_store.html', {
                    'store_info': {
                        'name': result.name,
                        'province': result.province,
                        'city': result.city,
                        'location': result.location,
                        'online': result.online,
                        'id': result.id,
                        'shopkeeper_id': result.business_id,
                        'exhibition': result.exhibition,
                        'remark': result.remark,
                        'option': option,
                        'machine_serial': result.machine_serial,
                        'agent': result.agent,
                        'manager': result.manager,
                        'reason': result.reason
                    },
                    "options": dict,
                    "agent_list": agent_list,
                    'lib_path': lib_path
                })
        except:
            return redirect('/sales/manager/login')


@csrf_exempt
def manager_stores(request):
    if request.method == 'GET':
        if not request.session.__contains__('manager_id'):
            return redirect('/sales/manager/login_pc')
        manager_id = request.session['manager_id']
        try:
            manager = Manager.objects.get(id=manager_id)
            is_leader = manager.is_leader
            if is_leader == 1:
                region = manager.region
                manager_list = Manager.objects.filter(region=region).values('id')
                stores = Shop.objects.filter(manager__in=manager_list)
            else:
                stores = Shop.objects.filter(manager=manager_id)
        except:
            stores = Shop.objects.filter(manager=manager_id)

        para = request.GET
        page = 1
        if para.__contains__('page'):
            try:
                page = int(para.__getitem__('page'))
            except:
                page = 1
        if page < 1:
            page = 1
        size = 40
        sort = '-created_time'
        if para.__contains__('sort'):
            sort = para.__getitem__('sort')
        if sort == 'province':
            stores = stores.order_by(sort, 'city', 'location')
        else:
            stores = stores.order_by(sort)
        total = stores.count()
        page_total = total / size + (1 if (total % size) > 0 else 0)
        if page_total <= 0:
            page_total = 1
        if page > page_total:
            page = page_total
        start = size * (page - 1)
        end = start + size
        if end > total:
            end = total
        if total == 0:
            stores = {}
        else:
            stores = stores[start: end]
            stores = stores.values()

        url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getAgentNumberInfo'
        req = urllib2.Request(url=url)
        try:
            res_data = urllib2.urlopen(req)
        except:
            res_data = '["默认"]'
        data = res_data.read()
        try:
            agent_list = json.loads(data)
        except:
            agent_list = [{'custom_number':'默认'}]
        agent_dict = {}
        for agent in agent_list:
            agent_dict[agent['custom_number']] = agent['company']
        for store in stores:
            new_option = {}
            option = json.loads(store['option'])
            for index, item in enumerate(option):
                n = dict[item]
                new_option[n] = option[item]
            store['option'] = new_option
            photo_join = store['photo']
            photos = photo_join.split(':')
            store['photo'] = photos
            business_id = store['business_id']
            manager_id = store['manager']
            store['agent'] = agent_dict[store['agent']]
            try:
                shopkeeper = Store.objects.get(id=business_id)
                store['business_id'] = shopkeeper
            except:
                pass
            try:
                manager = Manager.objects.get(id=manager_id)
                store['manager'] = manager
            except:
                pass
            store_id = store['id']
            sales = Sale.objects.filter(store_id=store_id, name='Insta360 Nano')
            sales_count = sales.count()
            store['sales_count'] = sales_count
            valid_count = sales.filter(valid=1).count()
            store['valid_count'] = valid_count
        data = {
            'total': total,
            'current_page': page,
            'page_total': page_total,
            'sort': sort
        }
        return render(request, 'manager/stores.html', {
            'stores': stores,
            'data': data,
            'lib_path': lib_path
        })


@csrf_exempt
def manager_sales(request):
    if request.method == 'GET':
        if not request.session.__contains__('manager_id'):
            return redirect('/sales/manager/login_pc')
        manager_id = str(request.session['manager_id'])
        try:
            manager = Manager.objects.get(id=manager_id)
            is_leader = manager.is_leader
            if is_leader == 1:
                region = manager.region
                manager_list = Manager.objects.filter(region=region).values('id')
                sales = Sale.objects.filter(name='Insta360 Nano', manager__in=manager_list)
            else:
                sales = Sale.objects.filter(name='Insta360 Nano', manager=manager_id)
        except:
            sales = Sale.objects.filter(name='Insta360 Nano', manager=manager_id)
        para = request.GET
        page = 1
        if para.__contains__('page'):
            try:
                page = int(para.__getitem__('page'))
            except:
                page = 1
        if page < 1:
            page = 1
        sort = '-created_time'
        if para.__contains__('sort'):
            sort = para.__getitem__('sort')
        size = 40

        if sort == '-active':
            sales = sales.order_by(sort, '-active_time')
        else:
            sales = sales.order_by(sort)

        total = sales.count()
        page_total = total / size + (1 if (total % size) > 0 else 0)
        if page_total <=0:
            page_total = 1
        if page > page_total:
            page = page_total
        start = size * (page -1)
        end = start + size
        if end > total:
            end = total
        if total == 0:
            sales = {}
        else:
            sales = sales[start: end]
            sales = sales.values()
        for sale in sales:
            business_id = sale['business_id']
            store_id = sale['store_id']
            clerk_id = sale['clerk_id']
            try:
                shopkeeper = Store.objects.get(id=business_id)
                sale['business'] = shopkeeper
            except:
                pass
            try:
                store = Shop.objects.get(id=store_id)
                manager_id = store.manager
                manager = Manager.objects.get(id=manager_id)
                store.manager = manager
                sale['store']= store
            except:
                pass
            try:
                clerk = Clerk.objects.get(id=clerk_id)
                sale['clerk'] = clerk
            except:
                pass
            valid = sale['valid']
            active = sale['active']
            if valid == 1:
                created_time = sale['created_time']
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
                    state = '重复激活'
                else:
                    state = '生效'
            else:
                if active == 1:
                    state = '超时'
                else:
                    # now = timezone.now()
                    # created_time = sale['created_time']
                    # deadline = created_time + datetime.timedelta(hours=12)
                    # if now >= deadline:
                    #     state = '作废'
                    #     sale['show'] = 0
                    # else:
                    state = '等待激活'
            sale['state'] = state

        data = {
            'total': total,
            'current_page': page,
            'page_total': page_total,
            'sort': sort
        }
        return render(request, 'manager/sales.html', {
            'sales': sales,
            'data': data,
            'lib_path': lib_path
        })


@csrf_exempt
def manager_delay(request):
    if request.method == 'GET':
        if not request.session.__contains__('manager_id'):
            return redirect('/sales/manager/login_pc')
        return render(request, 'manager/delay.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        serial_number = para.get('serial_number','')
        res = Sale.objects.filter(serial_number=serial_number).update(delay = 1)
        if res == 0:
            result = '没有该序列号的销售记录'
        else:
            result = '已延长激活时间至一周'
        return HttpResponse(result)


@csrf_exempt
def manager_delay_m(request):
    if request.method == 'GET':
        if not request.session.__contains__('manager_id'):
            return redirect('/sales/manager/login')
        return render(request, 'manager/delay_m.html', {
            'lib_path': lib_path
        })


@csrf_exempt
def manager_export(request):
    if not request.session.__contains__('manager_id'):
        return redirect('/sales/manager/login_pc')
    manager_id = request.session['manager_id']
    response = HttpResponse(content_type='text/csv')
    response.write(codecs.BOM_UTF8)
    response['Content-Disposition'] = 'attachment; filename="销售经理门店列表.csv"'

    writer = csv.writer(response)
    writer.writerow(['门店名称', '门店代码', '商家名称', '商家姓名', '商家手机', '省份', '城市', '详细地址', '配置', '样机序列号' ,'展台序列号' , '代理商', '销售经理', '累计总销量', '有效订单数', '创建时间', '创建天数', '网店地址', '备注'])

    try:
        manager = Manager.objects.get(id=manager_id)
        is_leader = manager.is_leader
        if is_leader == 1:
            region = manager.region
            manager_list = Manager.objects.filter(region=region).values('id')
            stores = Shop.objects.filter(manager__in=manager_list)
        else:
            stores = Shop.objects.filter( manager=manager_id)
    except:
        stores = Shop.objects.filter(manager=manager_id)

    stores = stores.values()
    url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getAgentNumberInfo'
    req = urllib2.Request(url=url)
    try:
        res_data = urllib2.urlopen(req)
    except:
        res_data = '["默认"]'
    data = res_data.read()
    try:
        agent_list = json.loads(data)
    except:
        agent_list = [{'custom_number': '默认'}]
    agent_dict = {}
    for agent in agent_list:
        agent_dict[agent['custom_number']] = agent['company']
    for store in stores:
        store_id = store['id']
        new_option = ''
        option = json.loads(store['option'])
        for index, item in enumerate(option):
            if option[item] == 'true':
                new_option += dict[item] + ' '
        store['option'] = new_option
        photo_join = store['photo']
        photos = photo_join.split(':')
        store['photo'] = photos
        business_id = store['business_id']
        manager_id = store['manager']
        store['agent'] = agent_dict[store['agent']]
        try:
            shopkeeper = Store.objects.get(id=business_id)
            store['business'] = shopkeeper
        except:
            pass
        try:
            manager = Manager.objects.get(id=manager_id)
            store['manager'] = manager
        except:
            pass
        sales = Sale.objects.filter(store_id=store_id, name='Insta360 Nano')
        created_time = store['created_time']

        sales_count = sales.count()
        valid_count = sales.filter(valid=1).count()
        created_time += datetime.timedelta(hours=8)
        created_date = created_time.strftime('%Y-%m-%d %H:%M:%S')
        now = timezone.now()
        delta = (now - created_time).days + 1
        if len(store['online']) < 10:
            store['online'] = ''
        writer.writerow([store['name'],
                         store['code'],
                         store['business'].store,
                         store['business'].name,
                         store['business'].phone,
                         store['province'],
                         store['city'],
                         store['location'],
                         store['option'],
                         store['machine_serial'],
                         store['exhibition'],
                         store['agent'],
                         store['manager'].name + '('+ store['manager'].area +')',
                         sales_count,
                         valid_count,
                         created_date,
                         delta,
                         store['online'],
                         store['remark']
                         ])
    return response


@csrf_exempt
def manager_export_sales(request):
    if not request.session.__contains__('manager_id'):
        return redirect('/sales/manager/login_pc')
    manager_id = request.session['manager_id']
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response.write(codecs.BOM_UTF8)
    response['Content-Disposition'] = 'attachment; filename="销售情况列表.csv"'

    writer = csv.writer(response)
    writer.writerow(['门店名称', '商家名称', '省份', '店员姓名', '店员手机', '序列号', '售出时间', '激活状态', '激活时间', '激活机器码', '订单状态', '红包奖励（元）', '销售经理'])

    try:
        manager = Manager.objects.get(id=manager_id)
        is_leader = manager.is_leader
        if is_leader == 1:
            region = manager.region
            manager_list = Manager.objects.filter(region=region).values('id')
            sales = Sale.objects.filter(name='Insta360 Nano', manager__in=manager_list)
        else:
            sales = Sale.objects.filter(name='Insta360 Nano', manager=manager_id)
    except:
        sales = Sale.objects.filter(name='Insta360 Nano', manager=manager_id)

    sales = sales.order_by('-created_time').values()

    for sale in sales:
        business_id = sale['business_id']
        store_id = sale['store_id']
        clerk_id = sale['clerk_id']
        try:
            shopkeeper = Store.objects.get(id=business_id)
            sale['business'] = shopkeeper
        except:
            pass
        try:
            store = Shop.objects.get(id=store_id)
            manager_id = store.manager
            manager = Manager.objects.get(id=manager_id)
            store.manager = manager
            sale['store'] = store
        except:
            pass
        try:
            clerk = Clerk.objects.get(id=clerk_id)
            sale['clerk'] = clerk
        except:
            pass
        valid = sale['valid']
        active = sale['active']
        if valid == 1:
            created_time = sale['created_time']
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
                state = '重复激活'
            else:
                state = '生效'
        else:
            if active == 1:
                state = '超时'
            else:
                # now = timezone.now()
                # created_time = sale['created_time']
                # deadline = created_time + datetime.timedelta(hours=12)
                # if now >= deadline:
                #     state = '作废'
                #     sale['show'] = 0
                # else:
                state = '等待激活'
        sale['state'] = state
        created_time = sale['created_time']
        created_time += datetime.timedelta(hours=8)
        created_date = created_time.strftime('%Y-%m-%d %H:%M:%S')
        active = sale['active']
        if active == 1:
            active_state = '已激活'
            active_time = sale['active_time']
            active_time += datetime.timedelta(hours=8)
            active_date = created_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            active_state = '未激活'
            active_date = ''

        writer.writerow([sale['store'].name,
                         sale['business'].store,
                         sale['province'],
                         sale['clerk'].name,
                         sale['clerk'].phone,
                         sale['serial_number'],
                         created_date,
                         active_state,
                         active_date,
                         sale['device_code'],
                         state,
                         sale['base'],
                         sale['store'].manager.name + '('+ sale['store'].manager.area +')',
                         ]
                        )
    return response