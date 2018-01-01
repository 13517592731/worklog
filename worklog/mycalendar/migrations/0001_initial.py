# Generated by Django 2.0 on 2017-12-30 21:56

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='calendar',
            fields=[
                ('calendar_id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField(max_length=50, verbose_name='内容')),
                ('type', models.CharField(max_length=10, verbose_name='分类')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('order_time', models.DateTimeField()),
                ('auth_id', models.CharField(max_length=6, verbose_name='创建者')),
                ('create_date', models.DateField(verbose_name='创建日期')),
                ('create_week', models.CharField(max_length=4, verbose_name='创建周数')),
                ('create_weekday', models.CharField(max_length=4, verbose_name='创建星期')),
                ('create_month', models.CharField(max_length=4, verbose_name='创建月份')),
                ('create_year', models.CharField(max_length=4, verbose_name='创建年份')),
            ],
            options={
                'db_table': 'calendar',
            },
        ),
        migrations.CreateModel(
            name='message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=80)),
                ('auth', models.CharField(max_length=10)),
                ('create_date', models.DateField()),
                ('remaining_time', models.DateTimeField(blank=True, null=True)),
                ('status', models.BooleanField()),
                ('type', models.CharField(max_length=10)),
                ('group_id', models.IntegerField(blank=True, null=True)),
                ('target', models.ForeignKey(on_delete=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'message',
            },
        ),
    ]