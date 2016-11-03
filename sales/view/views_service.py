# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
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
        return HttpResponse('Do nothing')
    elif request.method == 'GET':
        return render(request, 'service/cash_query.html', {
        })
