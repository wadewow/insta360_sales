# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


# Create your models here.

class Store(models.Model):
    store = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    phone = models.CharField(max_length=200, unique=True)
    manager = models.CharField(max_length=200,blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    pwd = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return str(self.id)

class Shop(models.Model):
    business_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    online = models.CharField(max_length=200)
    province = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    exhibition = models.CharField(max_length=200)
    option = models.CharField(max_length=200)
    agent = models.CharField(max_length=200,default='')
    machine_serial = models.CharField(max_length=200,blank=True)
    photo = models.CharField(max_length=400)
    created_time = models.DateTimeField(auto_now_add=True)
    remark = models.CharField(max_length=200, blank=True)
    promotion = models.CharField(max_length=200, blank=True)
    manager = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return str(self.id)

class Clerk(models.Model):
    store_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    phone = models.CharField(max_length=200, unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    base = models.FloatField(default=0.0)
    bonus = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)
    promotion = models.CharField(max_length=200, blank=True)
    pwd = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return str(self.id)


class Sale(models.Model):
    business_id = models.CharField(max_length=200)
    store_id = models.CharField(max_length=200)
    clerk_id = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    created_time = models.DateTimeField()
    active = models.IntegerField(default=0)
    active_time = models.DateTimeField()
    cashed = models.IntegerField(default=0)
    base = models.FloatField(default=0.0)
    valid = models.IntegerField(default=0)
    device_code = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return str(self.id)


class Token(models.Model):
    token = models.CharField(max_length=200)
    created_time = models.DateTimeField(auto_now=True)
    type = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.id)


class Exhibition(models.Model):
    id = models.CharField(max_length=200,primary_key=True)
    active = models.IntegerField(default=0)
    active_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.id)


class SaleNano(models.Model):
    id = models.CharField(max_length=200,primary_key=True)
    name = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return str(self.id)



class Manager(models.Model):
    id = models.CharField(max_length=200,primary_key=True)

    def __unicode__(self):
        return str(self.id)


class CashRecord(models.Model):
    clerk_id = models.CharField(max_length=200)
    created_time = models.DateTimeField(auto_now_add=True)
    base = models.FloatField(default=0.0)
    bonus = models.FloatField(default=0.0)
    money = models.FloatField(default=0.0)
    code = models.CharField(max_length=200,blank=True)
    wechat = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return str(self.id)


class Promotion(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_time = models.DateTimeField(auto_now_add=True)
    benchmark = models.IntegerField(default=30)
    bonus = models.FloatField(default=0.0)
    benchmark1 = models.IntegerField(default=50)
    bonus1 = models.FloatField(default=0.0)
    benchmark2 = models.IntegerField(default=100)
    bonus2 = models.FloatField(default=0.0)

    def __unicode__(self):
        return str(self.id)