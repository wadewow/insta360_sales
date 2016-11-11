# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-31 02:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0030_auto_20161030_2016'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('benchmark', models.IntegerField(default=30)),
                ('bonus', models.FloatField(default=0.0)),
            ],
        ),
        migrations.AddField(
            model_name='shop',
            name='promotion',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]