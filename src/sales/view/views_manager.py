# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from ..models import Manager
from ..models import Shop
from ..models import Exhibition
from ..models import Store
from ..models import Sale
from ..util.option import dict
from ..util.option import lib_path

import json
import sys
import urllib
import urllib2

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
            # del request.session['manager_id']
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
            print manager_id
            store_list = Shop.objects.filter(manager=manager_id)
            for store in store_list:
                new_option = {}
                option = json.loads(store.option)
                for index, item in enumerate(option):
                    n = dict[item]
                    new_option[n] = option[item]
                store.option = new_option
            return render(request, 'manager/list.html', {
                'store_list': store_list,
                'lib_path': lib_path
            })



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
                                'offset': ''
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
        stores = Shop.objects.filter(manager=manager_id).order_by('-created_time')
        total = stores.count()

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
        stores = stores.values()
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
            sales_count = Sale.objects.filter(store_id=store_id, name='Insta360 Nano').count()
            store['sales_count'] = sales_count
        data = {
            'total': total
        }
        return render(request, 'manager/stores.html', {
            'stores': stores,
            'data': data,
            'lib_path': lib_path
        })