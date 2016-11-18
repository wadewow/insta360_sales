from django.contrib import admin
from .models import Store
from .models import Shop
from .models import Clerk
from .models import Sale
from .models import Token
from .models import Exhibition
from .models import Manager
from .models import Agent
from .models import CashRecord
from .models import SaleNano
from .models import Promotion
from .models import SerialToInter

# Register your models here.

class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'name', 'password', 'phone', 'manager', 'created_time', 'pwd', 'openid')

class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_id', 'code', 'name', 'online', 'province', 'city', 'location', 'exhibition', 'option', 'agent', 'photo','machine_serial', 'remark', 'created_time', 'promotion', 'manager', 'reason', 'sales_count')

class ClerkAdmin(admin.ModelAdmin):
    list_display = ('id', 'store_id', 'name', 'password', 'phone', 'created_time', 'update_time', 'base', 'bonus', 'balance', 'promotion', 'pwd', 'openid')

class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_id', 'store_id', 'clerk_id','serial_number', 'name', 'created_time', 'active', 'active_time', 'base', 'cashed', 'device_code', 'valid', 'manager')

class TokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'created_time', 'type')

class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'active', 'active_time')

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'area')

class AgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password')

class SerialToInterAdmin(admin.ModelAdmin):
    list_display = ('id', 'update_time')

class SaleNanoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location')

class CashRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'clerk_id', 'name', 'phone', 'base', 'bonus', 'money', 'code', 'created_time', 'wechat')

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'created_time', 'benchmark', 'bonus', 'benchmark1', 'bonus1', 'benchmark2', 'bonus2')

admin.site.register(Store, StoreAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Clerk, ClerkAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(Exhibition, ExhibitionAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(CashRecord, CashRecordAdmin)
admin.site.register(SaleNano, SaleNanoAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(SerialToInter, SerialToInterAdmin)