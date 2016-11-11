# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-20 06:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_shop_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clerk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_id', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('password', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=200, unique=True)),
            ],
        ),
    ]