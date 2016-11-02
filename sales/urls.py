from django.conf.urls import url
from django.views.generic import RedirectView
from . import views
# from internal import settings

urlpatterns = [
    # url( r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root':settings.STATIC_ROOT }),
    # url(r'^$', views.index, name='index'),
    url(r'^import_manager', views.import_manager, name='import_manager'),
    url(r'^import_exhibition', views.import_exhibition, name='import_exhibition'),
    url(r'^import_sale_nano', views.import_sale_nano, name='import_sale_nano'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),

    url(r'^shopkeeper/register$', views.shopkeeper_register, name='shopkeeper_register'),
    url(r'^shopkeeper/login$', views.shopkeeper_login, name='shopkeeper_login'),
    url(r'^shopkeeper/info$', views.shopkeeper_info, name='shopkeeper_info'),
    url(r'^shopkeeper/modify$', views.shopkeeper_modify, name='shopkeeper_modify'),
    url(r'^shopkeeper/reset$', views.shopkeeper_reset, name='shopkeeper_reset'),
    url(r'^shopkeeper/sales$', views.shopkeeper_sales, name='shopkeeper_sales'),

    url(r'^store/stores$', views.stores, name='stores'),
    url(r'^store/add_store$', views.store_add, name='store_add'),
    url(r'^store/store_info$', views.store_info, name='store_info'),
    url(r'^store/modify_store$', views.store_modify, name='store_modify'),
    url(r'^store/store_validate$', views.store_validate, name='store_validate'),
    # url(r'^store/guide', views.store_guide, name='store_guide'),

    url(r'^logout$', views.logout, name='logout'),

    url(r'^clerk/register$', views.clerk_register, name='clerk_register'),
    url(r'^clerk/login$', views.clerk_login, name='clerk_login'),
    url(r'^clerk/info$', views.clerk_info, name='clerk_info'),
    url(r'^clerk/modify$', views.clerk_modify, name='clerk_modify'),
    url(r'^clerk/reset$', views.clerk_reset, name='clerk_reset'),
    url(r'^clerk/account$', views.account_account, name='account_account'),

    url(r'^sale/scan$', views.sale_scan, name='sale_scan'),
    url(r'^sale/sales$', views.sale_sales, name='sale_sales'),
    url(r'^sale/cash$', views.sale_cash, name='sale_cash'),
    url(r'^sale/test$', views.sale_test, name='sale_test'),

    url(r'^account/cash$', views.account_cash, name='account_cash'),
    url(r'^account/record$', views.account_record, name='account_record'),

    url(r'^manager/login$', views.manager_login, name='manager_login'),
    url(r'^manager/list$', views.manager_list, name='manager_list'),
    # url(r'^manager/shopkeeper_info', views.manager_shopkeeper_info, name='manager_shopkeeper_info'),
    url(r'^manager/modify_store$', views.manager_modify_store, name='manager_modify_store'),

    url(r'^guide$', views.sale_guide, name='sale_guide'),

    url(r'^weixin', views.weixin, name='weixin'),

    url(r'^upload_pic', views.upload_pic, name='upload_pic'),

    url(r'^QR_code', views.QR_code, name='QR_code'),



]