# Generated by Django 2.0 on 2018-01-02 20:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0002_auto_20171230_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='create_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
