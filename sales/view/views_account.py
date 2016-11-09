# coding=utf-8
from __future__ import division
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from ..models import Clerk
from ..models import Shop
from ..models import Sale
from ..models import Promotion
from ..models import CashRecord
from ..util.util import getCode1
from ..util.util import calBonus
from ..util.option import lib_path

import sys


reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def account_account(request):
    if request.method == 'GET':
        try:
            if not request.session.__contains__('clerk_id'):
                return redirect('/sales/clerk/login_wx')
            else:
                clerk_id = request.session['clerk_id']
                account = Clerk.objects.get(id=clerk_id)
                store_id = account.store_id
                store = Shop.objects.get(id=store_id)
                sale_count = Sale.objects.filter(clerk_id=clerk_id,valid=1).count()
                promotion_id = store.promotion
                promotion = ''
                store_count = 0
                clerk_count = 0
                achieve_benchmark = 0
                achieve_bonus = 0
                next_benchmark = 0
                next_bonus = 0
                delta = 0
                clerk_base = 0
                clerk_bonus = 0
                clerk_sales = Sale.objects.filter(
                        clerk_id=clerk_id,
                        name='Insta360 Nano',
                        valid=1,
                        cashed=0
                    )
                for s in clerk_sales:
                    clerk_base += s.base
                if promotion_id != '':
                    promotion = Promotion.objects.get(id=promotion_id)
                    start_time = promotion.start_time
                    end_time = promotion.end_time
                    benchmark = promotion.benchmark
                    delta = benchmark - store_count
                    bonus = promotion.bonus
                    store_sales = Sale.objects.filter(
                        store_id=store_id,
                        name='Insta360 Nano',
                        valid=1,
                        active_time__range=(start_time, end_time)
                    )

                    store_count = store_sales.count()
                    clerk_count = store_sales.filter(clerk_id=clerk_id).count()

                    store_uncashed= store_sales.filter(cashed=0)
                    store_uncashed_count = store_uncashed.count()

                    benchmark1 = promotion.benchmark1
                    bonus1 = promotion.bonus1
                    benchmark2 = promotion.benchmark2
                    bonus2 = promotion.bonus2


                    ####################

                    sum_bonus = 0
                    next_benchmark = benchmark
                    next_bonus = bonus
                    if store_count >= benchmark and store_count < benchmark1:
                        sum_bonus = store_uncashed_count * bonus
                        achieve_benchmark = benchmark
                        achieve_bonus = bonus
                        next_benchmark = benchmark1
                        next_bonus = bonus1
                    if store_count >= benchmark1 and store_count < benchmark2:
                        sum_bonus = store_uncashed_count * bonus1
                        achieve_benchmark = benchmark1
                        achieve_bonus = bonus1
                        next_benchmark = benchmark2
                        next_bonus = bonus2
                    if store_count >= benchmark2:
                        sum_bonus = store_uncashed_count * bonus2
                        achieve_benchmark = benchmark2
                        achieve_bonus = bonus2
                        next_benchmark = -1
                        next_bonus = -1

                    ####################
                    # sum_bonus = calBonus(benchmark,benchmark1,benchmark2,bonus,bonus1,bonus2,store_count) - calBonus(benchmark,benchmark1,benchmark2,bonus,bonus1,bonus2,store_count - store_uncashed_count)


                    # if store_count >= benchmark:
                    clerk_uncashed = store_uncashed.filter(
                        clerk_id=clerk_id,
                    )
                    clerk_uncashed_count = clerk_uncashed.count()
                    # clerk_sales.update(cashed=1)
                    if store_uncashed_count == 0:
                        ratio = 0
                    else:
                        ratio = clerk_uncashed_count / store_uncashed_count
                    print ratio
                    clerk_bonus = round((sum_bonus * ratio), 2)

                account.bonus = clerk_bonus
                account.balance = clerk_bonus + clerk_base
                account.base = clerk_base
                account.save()

                return render(request, 'clerk/account.html', {
                    'account': account,
                    'promotion': promotion,
                    'sale_count': sale_count,
                    'store_count': store_count,
                    'clerk_count': clerk_count,
                    'delta': delta,
                    'achieve_benchmark': achieve_benchmark,
                    'achieve_bonus': achieve_bonus,
                    'next_benchmark': next_benchmark,
                    'next_bonus': next_bonus,
                    'lib_path': lib_path
                })
        except:
            return redirect('/sales/clerk/login_wx')
    if request.method == 'POST':
        return HttpResponse('post')




@csrf_exempt
def account_cash(request):
    if request.method == 'GET':
        return HttpResponse('GET')

    if request.method == 'POST':
        para = request.POST
        if not request.session.__contains__('clerk_id'):
            return redirect('/sales/clerk/login_wx')
        else:
            clerk_id = request.session['clerk_id']
            # if not para.__contains__('money'):
            #     return HttpResponse("Missing parameter: money")
            # money = para.__getitem__('money')
            # try:
            #     money = float(money)
            # except:
            #     return HttpResponse("Illegal parameter: money")

            ##提现之前要重新计算一遍金额!!!!!!!!!!!!!!!!   。。。也不一定哦。。



            try:
                account = Clerk.objects.get(id=clerk_id)
            except:
                return HttpResponse("请重新注册")

            Sale.objects.filter(
                clerk_id=clerk_id,
                name='Insta360 Nano',
                valid=1,
                cashed=0,
            ).update(cashed=1)



            ###############balance这个字段没用了啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊
            balance = account.balance
            money = balance
            # if balance < money:
            #     return HttpResponse("余额不足！")
            # else:
            # balance = balance - money




            code = getCode1(8)
            # codes = CashRecord.objects.all().values_list("code", flat=True).distinct()
            # while code in codes:
            #     code = getCode1(8)

            while True:
                try:
                    CashRecord.objects.get(code=code)
                    code = getCode1(8)
                except ObjectDoesNotExist:
                    break
                except MultipleObjectsReturned:
                    code = getCode1(8)


            result = {
                'result': 'success',
                'code': code,
                'money': money
            }
            print money
            print money == 0
            if money == 0:
                return JsonResponse(result, safe=False)

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
            account.balance = 0
            account.bonus = 0
            account.base = 0
            account.save()
            return JsonResponse(result, safe=False)


@csrf_exempt
def account_record(request):
    if request.method == 'GET':
        if not request.session.__contains__('clerk_id'):
            return redirect('/sales/clerk/login_wx')
        else:
            clerk_id = request.session['clerk_id']
            records = CashRecord.objects.filter(clerk_id=clerk_id).order_by("-created_time")
            return render(request, 'clerk/records.html', {
                'records': records,
                'lib_path': lib_path
            })

    if request.method == 'POST':
        return HttpResponse('POST')


