# coding=utf-8

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..util.option import lib_path
from ..models import Exhibition

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


@csrf_exempt
def util_import_exhibition(request):
    if request.method == 'GET':
        return render(request, 'util/import_exhibition.html', {
            'lib_path': lib_path
        })
    if request.method == 'POST':
        para = request.POST
        if not para.__contains__("exhibitions"):
            return redirect('sales/util/import_exhibition')
        exhibitions = para.__getitem__("exhibitions")
        # print exhibitions
        temps = exhibitions.split('\n')
        added = []
        for temp in temps:
            temp = str(temp)
            temp = temp.strip()
            length = len(temp)
            if not temp.startswith('INA'):
                continue
            if length < 13 and length >15:
                continue
            res = Exhibition.objects.update_or_create(id=temp)
            if res[1]:
                added.append(temp)
                print temp
        return render(request, 'util/import_exhibition.html', {
            'lib_path': lib_path,
            'added': added,
            'flag': 1
        })