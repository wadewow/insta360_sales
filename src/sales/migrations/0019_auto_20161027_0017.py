# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-26 16:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0018_auto_20161027_0010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='name',
        ),
        migrations.RemoveField(
            model_name='account',
            name='phone',
        ),
    ]