from django.db import models
class Captch(models.Model):
    number = models.CharField(max_length=4, verbose_name='验证码')
    class Meta:
        db_table = 'captch'


# Create your models here.
