# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from ..models import Clerk
from ..models import Shop
from ..models import Sale
from ..models import Promotion
from ..models import CashRecord
from ..util.util import getCode1

import sys


reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def account_account(request):
    if request.method == 'GET':
        if not request.session.__contains__('clerk_id'):
            return redirect('/sales/clerk/login')
        else:
            clerk_id = request.session.__getitem__('clerk_id')
            account = Clerk.objects.get(id=clerk_id)
            store_id = account.store_id
            store = Shop.objects.get(id=store_id)
            sale_count = Sale.objects.filter(clerk_id=clerk_id,valid=1).count()
            promotion_id = store.promotion
            promotion = ''
            store_count = 0
            print promotion_id
            print promotion_id == ''
            if promotion_id != '':
                promotion = Promotion.objects.get(id=promotion_id)
                start_time = promotion.start_time
                end_time = promotion.end_time
                benchmark = promotion.benchmark
                bonus = promotion.bonus
                store_sales = Sale.objects.filter(
                    store_id=store_id,
                    name='Insta360 Nano',
                    valid=1,
                    active_time__range=(start_time, end_time)
                )

                store_count = store_sales.count()
                if store_count >= benchmark:
                    clerk_sales = store_sales.filter(
                        clerk_id=clerk_id,
                        cashed=0
                    )
                    clerk_count = clerk_sales.count()
                    clerk_sales.update(cashed=1)

                    bonus *= clerk_count
                    account.balance += bonus
                    account.bonus += bonus
                    account.save()
                print '123'
            print '123'
            return render(request, 'clerk/account.html', {
                'account': account,
                'promotion': promotion,
                'sale_count': sale_count,
                'store_count': store_count,
                'delta': promotion.benchmark - store_count
            })
            # return HttpResponse('123213')
    if request.method == 'POST':
        return HttpResponse('post')


@csrf_exempt
def account_cash(request):
    if request.method == 'GET':
        return HttpResponse('GET')

    if request.method == 'POST':
        para = request.POST
        if not request.session.__contains__('clerk_id'):
            return redirect('/sales/clerk/login')
        else:
            clerk_id = request.session.__getitem__('clerk_id')
            if not para.__contains__('money'):
                return HttpResponse("Missing parameter: money")
            money = para.__getitem__('money')
            try:
                money = float(money)
            except:
                return HttpResponse("Illegal parameter: money")
            try:
                account = Clerk.objects.get(id=clerk_id)
            except:
                return HttpResponse("请重新注册")
            balance = account.balance
            if balance < money:
                return HttpResponse("余额不足！")
            else:
                balance = balance - money
                account.balance = balance
                account.save()
                code = getCode1(8)
                codes = CashRecord.objects.all().values_list("code").distinct()
                while code in codes:
                    code = getCode1(8)
                clerk = Clerk.objects.get(id=clerk_id)

                CashRecord.objects.create(
                    clerk_id=clerk_id,
                    base=account.base,
                    bonus=account.bonus,
                    money=money,
                    code=code,
                    name=clerk.name,
                    phone=clerk.phone
                )
            result = {
                'result': 'success',
                'code': code,
                'money': money
            }

            return JsonResponse(result, safe=False)


@csrf_exempt
def account_record(request):
    if request.method == 'GET':
        if not request.session.__contains__('clerk_id'):
            return redirect('/sales/clerk/login')
        else:
            clerk_id = request.session.__getitem__('clerk_id')
            records = CashRecord.objects.filter(clerk_id=clerk_id).order_by("-created_time")
            return render(request, 'clerk/records.html', {
                'records': records
            })

    if request.method == 'POST':
        return HttpResponse('POST')