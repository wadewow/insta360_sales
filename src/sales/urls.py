from django.conf.urls import url
from django.views.generic import RedirectView
from . import views
# from internal import settings

urlpatterns = [
    # url( r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root':settings.STATIC_ROOT }),
    # url(r'^$', views.index, name='index'),
    url(r'^import_manager$', views.import_manager, name='import_manager'),
    url(r'^import_exhibition$', views.import_exhibition, name='import_exhibition'),
    url(r'^import_sale_nano$', views.import_sale_nano, name='import_sale_nano'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),

    url(r'^shopkeeper/register$', views.shopkeeper_register, name='shopkeeper_register'),
    url(r'^shopkeeper/register_wx$', views.shopkeeper_register_wx, name='shopkeeper_register_wx'),
    url(r'^shopkeeper/login$', views.shopkeeper_login, name='shopkeeper_login'),
    url(r'^shopkeeper/login_wx$', views.shopkeeper_login_wx, name='shopkeeper_login_wx'),
    url(r'^shopkeeper/info$', views.shopkeeper_info, name='shopkeeper_info'),
    url(r'^shopkeeper/modify$', views.shopkeeper_modify, name='shopkeeper_modify'),
    url(r'^shopkeeper/reset$', views.shopkeeper_reset, name='shopkeeper_reset'),
    url(r'^shopkeeper/sales$', views.shopkeeper_sales, name='shopkeeper_sales'),

    url(r'^store/stores$', views.stores, name='stores'),
    url(r'^store/add_store$', views.store_add, name='store_add'),
    url(r'^store/store_info$', views.store_info, name='store_info'),
    url(r'^store/modify_store$', views.store_modify, name='store_modify'),
    url(r'^store/store_validate$', views.store_validate, name='store_validate'),

    url(r'^logout$', views.logout, name='logout'),

    url(r'^clerk/register$', views.clerk_register, name='clerk_register'),
    url(r'^clerk/register_wx$', views.clerk_register_wx, name='clerk_register_wx'),
    url(r'^clerk/login$', views.clerk_login, name='clerk_login'),
    url(r'^clerk/login_wx$', views.clerk_login_wx, name='clerk_login_wx'),
    url(r'^clerk/info$', views.clerk_info, name='clerk_info'),
    url(r'^clerk/modify$', views.clerk_modify, name='clerk_modify'),
    url(r'^clerk/reset$', views.clerk_reset, name='clerk_reset'),
    url(r'^clerk/account$', views.account_account, name='account_account'),

    url(r'^sale/scan$', views.sale_scan, name='sale_scan'),
    url(r'^sale/sales$', views.sale_sales, name='sale_sales'),
    # url(r'^sale/cash$', views.sale_cash, name='sale_cash'),
    url(r'^sale/test$', views.sale_test, name='sale_test'),

    url(r'^account/cash$', views.account_cash, name='account_cash'),
    url(r'^account/record$', views.account_record, name='account_record'),

    url(r'^manager/login$', views.manager_login, name='manager_login'),
    url(r'^manager/login_pc$', views.manager_login_pc, name='manager_login_pc'),
    url(r'^manager/list$', views.manager_list, name='manager_list'),
    url(r'^manager/stores$', views.manager_stores, name='manager_stores'),
    # url(r'^manager/shopkeeper_info', views.manager_shopkeeper_info, name='manager_shopkeeper_info'),
    url(r'^manager/modify_store$', views.manager_modify_store, name='manager_modify_store'),

    url(r'^agent/login$', views.agent_login, name='agent_login'),
    url(r'^agent/list$', views.agent_list, name='agent_list'),
    url(r'^agent/sales$', views.agent_sales, name='agent_sales'),
    url(r'^agent/search$', views.agent_search, name='agent_search'),

    url(r'^promotion/store_filter$', views.store_filter, name='store_filter'),

    url(r'^cash_query$', views.cash_query, name='cash_query'),
    url(r'^service/cloud_query$', views.service_cloud_query, name='service_cloud_query'),
    url(r'^service_cash$', views.service_cash, name='service_cash'),
    url(r'^service/serial_to_inter$', views.service_serial_to_inter, name='service_serial_to_inter'),
    url(r'^service/unbind_cloud$', views.service_unbind_cloud, name='service_unbind_cloud'),
    url(r'^service/cloud_home$', views.service_cloud_home, name='service_cloud_home'),
    url(r'^service/login$', views.service_login, name='service_login'),

    url(r'^guide$', views.sale_guide, name='sale_guide'),

    url(r'^weixin$', views.weixin, name='weixin'),

    url(r'^upload_pic$', views.upload_pic, name='upload_pic'),

    url(r'^QR_code$', views.QR_code, name='QR_code'),

    url(r'^test$', views.test, name='test'),
    url(r'^test1$', views.test1, name='test1'),

    url(r'^util/set_active$', views.set_active, name='set_active'),
    url(r'^util/query_ex$', views.query_ex, name='query_ex'),
    url(r'^util/set_offset$', views.set_offset, name='set_offset'),
    url(r'^util/import_exhibition$', views.util_import_exhibition, name='util_import_exhibition'),
    url(r'^util/convert_type', views.util_convert_type, name='util_convert_type'),
    url(r'^util/import_nano$', views.util_import_nano, name='util_import_nano'),
    url(r'^util/login$', views.util_login, name='util_login'),

    url(r'^bi/stores$', views.bi_stores, name='bi_stores'),
    url(r'^bi/managers$', views.bi_managers, name='bi_managers'),
    url(r'^bi/sales$', views.bi_sales, name='bi_sales'),
    url(r'^bi/login$', views.bi_login, name='bi_login'),
    url(r'^bi/store_trend$', views.bi_store_trend, name='bi_store_trend'),
    url(r'^bi/sales_map$', views.bi_sales_map, name='bi_sales_map'),
    url(r'^bi/trend$', views.bi_trend, name='bi_trend'),
    url(r'^bi/map$', views.bi_map, name='bi_map'),
    url(r'^bi/nano_detail$', views.bi_nano_detail, name='bi_nano_detail'),
    url(r'^bi/inter_list$', views.bi_inter_list, name='bi_inter_list'),
    url(r'^bi/export$', views.bi_export, name='bi_export'),
    url(r'^bi/promotion$', views.bi_promotion, name='bi_promotion'),

    url(r'^wx/wx_mass_message$', views.wx_mass_message, name='wx_mass_message'),
]