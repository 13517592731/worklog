from django.db import models
from django.contrib.auth.models import User

class project(models.Model):
    pro_id = models.AutoField(primary_key=True)
    pro_name = models.CharField(max_length=20, verbose_name='项目名称')
    pro_title = models.TextField(verbose_name='项目内容', max_length=50)
    pro_start = models.DateField(verbose_name='发布时间', max_length=20)
    pro_end = models.DateField(verbose_name='截止时间', max_length=20)
    pro_days = models.IntegerField(verbose_name='预计时间')
    pro_type = models.CharField(max_length=10, verbose_name='项目类型')
    pro_status = models.BooleanField(verbose_name='项目状态')
    pro_auth_id = models.CharField(verbose_name='项目管理员', max_length=3)

    class Meta:
        permissions = (
            ("assign_task", "分配任务"),
            ("up_file", "上传文件"),
            ("down_file", "下载文件"),
        )
        db_table = 'project'

class project_member(models.Model):
    pro_id = models.CharField(max_length=5)
    pro_member_id = models.IntegerField()
    class Meta:
        db_table = 'project_member'



class task(models.Model):
    pro_id = models.CharField(max_length=5, default="")
    auth_id = models.IntegerField(null=False, blank=False)
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=100)
    status = models.BooleanField()
    create_date = models.DateField()
    order_time = models.DateField(verbose_name='预期时间')
    true_date = models.DateField(verbose_name='实际完成时间')
    class Meta:
        db_table = 'project_task'

class file(models.Model):
    pro_id = models.CharField(max_length=5, default="")
    file_name = models.CharField(max_length=50)
    file_url = models.CharField(max_length=255)
    date = models.CharField(max_length=20)
    class Meta:
        db_table = 'project_file'

class Comment(models.Model):
    pro_id = models.CharField(max_length=5, default="")
    auth_name = models.CharField(max_length=10)
    auth_id = models.IntegerField()
    word = models.CharField(max_length=500)
    avator = models.ImageField(upload_to="icons")
    send_time = models.DateField()
    class Meta:
        permissions = (
            ("send_comment", "发表评论"),
        )
        db_table = 'project_comment'
# Create your models here.
