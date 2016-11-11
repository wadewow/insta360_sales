from django.conf.urls import url
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^MP_verify_jE8pmmBE5j4S2gnJ\.txt$', views.txt, name='txt'),
]