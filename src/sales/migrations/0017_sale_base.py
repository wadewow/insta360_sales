# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-26 15:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0016_auto_20161025_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='base',
            field=models.FloatField(default=0.0),
        ),
    ]
