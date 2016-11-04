# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from ..models import CashRecord


import sys

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def cash_query(request):
    if request.method == 'POST':
        para = request.POST
        code = para.get('code','')
        try:
            record = CashRecord.objects.get(code=code)
        except ObjectDoesNotExist:
            return render(request, 'service/cash_query.html', {
                'exsit': 0
            })


        return render(request, 'service/cash_query.html', {
            'exsit': 1,
            'record': record
        })

    elif request.method == 'GET':
        return render(request, 'service/cash_query.html', {
        })

@csrf_exempt
def service_cash(request):
    if request.method == 'GET':
        return redirect('/sales/cash_query')
    if request.method == 'POST':
        para = request.POST
        id = para.get('id', '')
        wechat = para.get('wechat','')
        if id == '':
            return redirect('/sales/cash_query')
        try:
            record = CashRecord.objects.get(id=id)
        except ObjectDoesNotExist:
            return render(request, 'service/cash_query.html', {
                'exsit': 0
            })
        record.wechat = wechat
        record.save()

        return render(request, 'service/cash_query.html', {
            'exsit': 1,
            'record': record
        })

