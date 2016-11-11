from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'index/index.html', {
        'title': 'Index - Insta360 ',
        'msg': 'Sales.Internal For Insta360.',
        'detail': 'PYTHON / SALES.'
    })

def txt(request):
    return render(request, 'MP_verify_jE8pmmBE5j4S2gnJ.txt', {

    })