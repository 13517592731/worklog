from django.db import models
from django.contrib.auth.models import User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=True)
    name = models.CharField(max_length=10)
    avator = models.ImageField(upload_to="icons")
    phone = models.CharField(max_length=11, null=True, blank=True)
    class Meta:
        db_table = 'profile'

# Create your models here.
