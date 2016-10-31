# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-21 07:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_auto_20161021_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='exhibition',
            name='option',
            field=models.CharField(default="{'ball':'true','machine':'true','demo':'true','board':'true'}", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shop',
            name='option',
            field=models.CharField(default="{'ball':'true','machine':'true','demo':'true','board':'true'}", max_length=200),
            preserve_default=False,
        ),
    ]
