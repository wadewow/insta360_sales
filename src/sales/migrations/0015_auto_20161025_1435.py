# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-25 06:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0014_sale_business_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='created_time',
            field=models.DateTimeField(),
        ),
    ]