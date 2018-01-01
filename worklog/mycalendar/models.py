#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User
class calendar(models.Model):
    calendar_id = models.AutoField(primary_key=True)
    content = models.TextField(verbose_name='内容', max_length=50)
    type = models.CharField(max_length=10, verbose_name='分类')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    order_time = models.DecimalField(max_digits=3, decimal_places=1)
    auth_id = models.CharField(max_length=6, verbose_name='创建者')
    create_date = models.DateField(verbose_name='创建日期')
    create_week = models.CharField(max_length=4, verbose_name='创建周数')
    create_weekday = models.CharField(max_length=4, verbose_name='创建星期')
    create_month = models.CharField(max_length=4, verbose_name='创建月份')
    create_year = models.CharField(max_length=4, verbose_name='创建年份')
    class Meta:
        db_table = "calendar"

class message(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=80)
    target = models.ForeignKey(User, on_delete=True)
    auth = models.CharField(max_length=10)
    create_date = models.DateField()
    remaining_time = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField()
    type = models.CharField(max_length=10)
    group_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'message'


# Create your models here.
