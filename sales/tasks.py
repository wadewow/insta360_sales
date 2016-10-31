# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from celery import shared_task
from celery.utils.log import get_task_logger
from .models import UseCondition


import datetime
import time


logger = get_task_logger(__name__)


@shared_task
def test(a, b):
    print a + b
    return a + b


@shared_task
def get_use_condition():

    return 'Finished.'
