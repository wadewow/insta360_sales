# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from ..models import Shop
from ..models import Clerk
from ..models import Store
from ..models import Promotion
from ..models import Exhibition
from ..models import Manager
from ..util.util import getCode
from ..util.option import dict
from ..util.option import lib_path
from PIL import Image

import json
import os
import time
import urllib2



@csrf_exempt
def stores(request):
    if request.method == 'POST':
        return HttpResponse('error')
    elif request.method == 'GET':
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login_wx')
            else:
                business_id = request.session['shopkeeper_id']
                Store.objects.get(id=business_id)
                results = Shop.objects.filter(business_id=business_id)
                return render(request, 'store/stores.html', {
                    "store_list" : results,
                    'lib_path': lib_path
                })
        except:
            return redirect('/sales/shopkeeper/login_wx')

@csrf_exempt
def store_add(request):
    if request.method == 'GET':
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login_wx')
            else:
                url = 'http://api.internal.insta360.com:8088/insta360_nano/camera/index/getAgentNumberInfo'
                req = urllib2.Request(url=url)
                try:
                    res_data = urllib2.urlopen(req)
                except:
                    res_data = '["默认"]'
                data = res_data.read()
                agent_list = json.loads(data)
                option = dict
                return render(request, 'store/add_store.html', {
                    "options": option,
                    "agent_list": agent_list,
                    'lib_path': lib_path
                })
        except:
            return render(request, 'shopkeeper/login.html', {
                'lib_path': lib_path
            })

    if request.method == 'POST':
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login_wx')
            else:
                print 'add_store'
                business_id = request.session['shopkeeper_id']
                print business_id
                para = request.POST
                print para.keys()
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
                remark = para.__getitem__("remark")
                agent = para.__getitem__("agent")
                manager = para.__getitem__("manager")
                print manager
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
                print option
                code = getCode(6)
                codes = Shop.objects.all().values_list("code", flat=True).distinct()
                while code in codes:
                    code = getCode(6)

                print code
                try:
                    photo_num = int(para.__getitem__("photo_num"))
                except:
                    photo_num = 1

                print photo_num

                path_join = ''
                for i in range(0, photo_num):
                    if (not request.FILES.__contains__("photo" + str(i))) or para.__contains__('removephoto' + str(i)):
                        continue
                    file = request.FILES.__getitem__("photo"+str(i))
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
                store = Shop.objects.create(
                    business_id=business_id,
                    name=name,
                    online=online,
                    province=province,
                    city=city,
                    location=location,
                    photo=path_join,
                    code=code,
                    exhibition=exhibition,
                    option=json.dumps(option),
                    machine_serial=machine_serial,
                    remark = remark,
                    agent=agent,
                    manager=manager
                )
                result = {
                    'result': 'success',
                    'store_id': store.id
                }
                return JsonResponse(result, safe=False)
        except:
            return HttpResponse('error')



@csrf_exempt
def store_info(request):
    if request.method == 'POST':
        return HttpResponse('Do nothing')
    elif request.method == 'GET':
        try:
            para = request.GET
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login_wx')
            elif not para.__contains__('store_id'):
                return redirect('/sales/store/stores')
            else:
                store_id = para.__getitem__('store_id')
                first = 0
                if para.__contains__('first'):
                    first = para.__getitem__('first')
                result = Shop.objects.get(id=store_id)
                business_id = result.business_id
                if request.session['shopkeeper_id'] != int(business_id):
                    return redirect('/sales/store/stores')
                photo_join = result.photo
                photos = photo_join.split(':')
                option = json.loads(result.option)
                new_option = {}
                for index, item in enumerate(option):
                    n = dict[item]
                    new_option[n] = option[item]
                return render(request, 'store/store_info.html', {
                    'store_info': {
                        'name': result.name,
                        'code': result.code,
                        'location': result.province + ' ' + result.city + ' ' + result.location,
                        'online': result.online,
                        'photos': photos,
                        'id': result.id,
                        'option': new_option,
                        'first': first,
                        'remark': result.remark,
                        'machine_serial': result.machine_serial,
                        'agent': result.agent,
                        'manager': result.manager
                    },
                    'lib_path': lib_path
                })
        except:
            return render(request, 'shopkeeper/login.html', {
                'lib_path': lib_path
            })



@csrf_exempt
def store_modify(request):
    if request.method == 'POST':
        try:
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login_wx')
            else:
                print 'modify store'

                print request.FILES
                para = request.POST
                # print para
                # print para.keys()
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
                # ball = para.__getitem__("ball")
                # machine = para.__getitem__("machine")
                # board = para.__getitem__("board")
                # demo = para.__getitem__("demo")
                # option = {
                #     'ball': ball,
                #     'machine': machine,
                #     'board': board,
                #     'demo': demo
                # }

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
                print photo_num
                for i in range(0, photo_num):
                    if (not request.FILES.__contains__("photo" + str(i))) or para.__contains__('removephoto' + str(i)):
                        continue
                    file = request.FILES.__getitem__("photo" + str(i))
                    # timestamp = str(int(time.time()))
                    path = 'sales/static/store/' + file.name
                    path = default_storage.save(path, file)

                    # if os.path.isfile(path):
                    #     # 打开原图片缩小后保存，可以用if srcFile.endswith(".jpg")或者split，splitext等函数等针对特定文件压缩
                    #     sImg = Image.open(path)
                    #     w, h = sImg.size
                    #     dImg = sImg.resize((w / 4, h / 4), Image.ANTIALIAS)  # 设置压缩尺寸和选项，注意尺寸要用括号
                    #     dImg.save(path)  # 也可以用srcFile原路径保存,或者更改后缀保存，save这个函数后面可以加压缩编码选项JPEG之类的
                    #     print path
                    path_join += path[5:] + ':'
                    print path_join
                if len(path_join) > 0:
                    path_join = path_join[:-1]

                res.active = 1
                res.save()
                if len(path_join) > 0:
                    try:
                        res = Shop.objects.filter(id=store_id).update(
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
                            # agent=agent,
                            manager=manager
                        )
                    except:
                        return HttpResponse('fail')
                else:
                    try:
                        res = Shop.objects.filter(id=store_id).update(
                            name=name,
                            online=online,
                            province=province,
                            city=city,
                            location=location,
                            exhibition=exhibition,
                            option=json.dumps(option),
                            machine_serial=machine_serial,
                            remark=remark,
                            # agent=agent,
                            manager=manager
                        )
                    except:
                        return HttpResponse('fail')
                if res == 0:
                    return HttpResponse('fail')
                else:
                    result = {
                        'result': 'success',
                        'store_id': store_id
                    }
                    return JsonResponse(result, safe=False)
        except:
            return HttpResponse('图片太大上传失败，请减少图片并重试')
    elif request.method == 'GET':
        try:
            para = request.GET
            if not request.session.__contains__('shopkeeper_id'):
                return redirect('/sales/shopkeeper/login_wx')
            elif not para.__contains__('store_id'):
                return redirect('/sales/store/stores')
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
                business_id = result.business_id
                if request.session['shopkeeper_id'] != int(business_id):
                    return redirect('/sales/store/stores')
                option = json.loads(result.option)
                print option
                return render(request, 'store/modify_store.html', {
                    'store_info': {
                        'name': result.name,
                        'province': result.province,
                        'city': result.city,
                        'location': result.location,
                        'online': result.online,
                        'id': result.id,
                        'exhibition': result.exhibition,
                        'option': option,
                        'machine_serial': result.machine_serial,
                        'remark': result.remark,
                        'agent': result.agent,
                        'manager': result.manager
                    },
                    "options": dict,
                    "agent_list": agent_list,
                    'lib_path': lib_path
                })
        except:
            return render(request, 'shopkeeper/login.html', {
                'lib_path': lib_path
            })


@csrf_exempt
def store_validate(request):
    if request.method == 'POST':
        para = request.POST
        if para.__contains__('serial_num'):
            serial_num = para.__getitem__('serial_num')
        else:
            return HttpResponse("Need parament serial_num")
        try :
            Exhibition.objects.get(id=serial_num)
            return HttpResponse("success")
        except ObjectDoesNotExist:
            return HttpResponse("error")


def store_promotion(request):
    if request.method == 'POST':
        try:
            para = request.POST
            start_time = para.__getitem__('start_time')
            end_time = para.__getitem__('end_time')
            benchmark = para.__getitem__('benchmark')
            bonus = para.__getitem__('bonus')
            stores = para.__getitem__('stores')
            promotion = Promotion.objects.create(
                start_time=start_time,
                end_time=end_time,
                benchmark=benchmark,
                bonus=bonus
            )
            stores = json.loads(stores)
            for store in stores:
                Shop.objects.filter(id=store).update(promotion=promotion.id)
        except:
            return HttpResponse('error')