from django.contrib.auth.models import User, Group
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from guardian.core import ObjectPermissionChecker
from qiniu import Auth
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Permission

from login.models import Profile
from mycalendar.models import calendar
from mycalendar.models import message
from myproject.models import file
from .models import project, Comment, task, project_member

import datetime


def upfile(req):
    pro_id =req.GET.get("id")
    return render(req, "myproject/FileUpload.html", locals())

# 定义获取七牛服务器上的tocken

@require_http_methods(['GET'])
def get_token(request):
    # 1. 先要设置AccessKey和SecretKey
    access_key = "plqZCCbafZBr9nC_VML5eI6ktVd_QGH31LHyDnYT"
    secret_key = "O3edQrML3AZHv6KIIvvp0Oy5CsA5NCOqzgq_FtYa"
    # 2. 授权
    q = Auth(access_key, secret_key)

    # 3. 设置七牛空间(自己刚刚创建的)
    bucket_name = 'xgwphoto'
    # 4. 生成token
    token = q.upload_token(bucket_name)
    # 5. 返回token,key必须为uptoken
    return JsonResponse({'uptoken': token})
@require_http_methods(['GET'])
def download(request):
    info = request.GET.get("value")
    pro_id = request.GET.get("pro_id")
    url = 'http://ou3b2kevh.bkt.clouddn.com/'+info+'?attname='
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = file(pro_id=pro_id, file_name=info, file_url=url, date=date)
    filename.save()
    return HttpResponse('POST')



import os
# Create your views here.
def projects(req):
    return render(req, 'myproject/project.html')

def create_project(req):
    user_id = req.session.get("user_id")
    data = Profile.objects.exclude(user_id=user_id)
    return render(req, "myproject/create_project.html", {'data': data})

@csrf_exempt
def all_project(req):
    obj = project.objects.all().values('pro_id', 'pro_name')
    info = list(obj)
    return JsonResponse({"data": info})


@csrf_exempt
def save_project(request):
    auth_id = request.session.get("user_id")
    user = User.objects.get(id=auth_id)
    now = datetime.datetime.now()
    auth = Profile.objects.get(user_id=auth_id).name
    name = request.POST.get('name')
    start = request.POST.get('begin')
    end = request.POST.get('end')
    days = request.POST.get('days')
    type = request.POST.get('type')
    content = request.POST.get('content')
    members = request.POST.getlist('members[]')
    times = len(project.objects.filter(pro_name=name))
    mytask = Permission.objects.get(codename='assign_task', name=u'分配任务')
    mycomment = Permission.objects.get(codename='send_comment', name=u'发表评论')
    up = Permission.objects.get(codename='up_file', name='上传文件')
    down = Permission.objects.get(codename='down_file', name=u'下载文件')
    members.append(auth_id)
    if times > 0:
        return JsonResponse({"error": "该项目已存在"})
    else:
        pro = project(
            pro_name=name,
            pro_title=content,
            pro_start=start,
            pro_end=end,
            pro_type=type,
            pro_days=days,
            pro_status=False,
            pro_auth_id=auth_id,
        )
        pro.save()
        group = Group.objects.create(name=name)
        pro_mem_pro_id = pro.pro_id
        for i in members:
            User.objects.get(id=i).groups.add(group)  # 用户加入用户组
            if(i!=auth_id):
                description = auth + "邀请你加入了项目：" + name
                message.objects.create(auth=auth,
                                   title=name,
                                   description=description,
                                   create_date=now.strftime("%Y-%m-%d"),
                                   target_id=int(i),
                                   status=False,
                                   type='project',
                                   create_time=now
                                   ).save()
            pro_mem = project_member(pro_id=pro_mem_pro_id, pro_member_id=i)
            pro_mem.save()
        user.user_permissions.add(mytask)
        add_perm(mytask, user, pro)  #当前user权限未写入
        group.permissions.add(mycomment, up, down)
        return JsonResponse({"status": 1})

def add_perm(permission, objects, obj):
    assign_perm(permission, objects, obj)

def project_detail(request):
    pro_id = request.GET.get('pro_id')
    project_info = project.objects.get(pro_id=pro_id)
    pro_auth = project_info.pro_auth_id
    name = project_info.pro_name
    member = project_member.objects.filter(pro_id=pro_id)
    members_id = []
    members_id.append(pro_auth)
    for i in member:
        members_id.append(i.pro_member_id)
    members = Profile.objects.filter(user_id__in=members_id)
    return render(request, "myproject/project_detail.html", {
        'name': name,
        'members': members,
        'pro_id': pro_id,
    })
def tasks(request):
    pro_id = request.GET.get('pro_id')
    if task.objects.filter(pro_id=pro_id) is None:
        fail = 0
        success = 0
        all = 0
    else:
        fail = task.objects.filter(pro_id=pro_id).filter(status=False)
        success = task.objects.filter(pro_id=pro_id).filter(status=True)
        all = project.objects.filter(pro_id=pro_id).all()
    mytask = {
        'fail': fail,
        'success': success,
        'all': all
    }
    return render(request, 'myproject/tasks.html', mytask)

def mymembers(request):
    pro_id = request.GET.get('pro_id')
    members = project_member.objects.filter(pro_id=pro_id)
    ids = []
    for i in members:
        ids.append(i.pro_member_id)
    profile_obj = Profile.objects.filter(user_id__in=ids)
    return render(request, 'myproject/mymembers.html', {'user': profile_obj})



def write_file(file, filePath):
    file_obj = open(filePath, 'wb+')
    for i in file.chunks():
        file_obj.write(i)
    file_obj.close()


def documentUpload(request):
    file = request.FILES.get('file')
    basePath = 'media/需求文档'
    filePath = os.path.join(basePath, file.name).replace('\\', '/')
    write_file(file, filePath)
    return JsonResponse({
    'result': 'ok',
    'id': 10001,
})

@csrf_exempt
def ajax_calendar(request):
    if request.method == "POST":
        re_user_id = request.session.get("user_id")
        title = request.POST.get("title")
        member = request.POST.getlist("auth[]")
        order_time = request.POST.get('order_time')
        pro_id = request.POST.get("pro_id")
        members = list(Profile.objects.filter(user_id__in=member))
        auth = Profile.objects.get(user_id=re_user_id).name
        obj = project.objects.get(pro_id=pro_id)
        project_auth = User.objects.get(id=obj.pro_auth_id)
        check = ObjectPermissionChecker(project_auth)
        if(check.has_perm('assign_task', obj)):
            create = datetime.datetime.today() + datetime.timedelta(days=int(order_time))
            now = datetime.datetime
            times = len(task.objects.filter(content=title))
            if times > 0:
                return JsonResponse({"status": 0})
            else:
                for i in range(len(member)):
                    mytask = task.objects.create(pro_id=pro_id, content=title, create_date=now.today(), order_time=create, auth_id=member[i], status=False, true_date=create)
                    mytask.save()
                for i in members:
                    if (i.user_id != project_auth):
                        description = auth + "为你分配了任务:" + title
                        message.objects.create(auth=auth, title=title, description=description, create_date=now.today(),
                                           target_id=i.user_id, status=False, type='project', create_time=now.now()).save()
                return JsonResponse({"status": 1})
        else:
            return JsonResponse({"error": "你没有权限执行此操作哦"})


@csrf_exempt
def ajax_send(request):
    pro_id = request.POST.get('pro_id')
    obj = project.objects.get(pro_id=pro_id)
    pro_auth_id = obj.pro_auth_id
    user_id = request.session.get("user_id")
    user = User.objects.get(id=user_id)
    check = ObjectPermissionChecker(user)
    if check.has_perm('myproject.send_comment', obj):
        word = request.POST.get('word')
        send_time = datetime.datetime.now()
        profile_obj = Profile.objects.get(user_id=user_id)
        auth = profile_obj.name
        avator = profile_obj.avator
        c = Comment.objects.create(auth_name=auth, auth_id=user_id, pro_id=pro_id, word=word, avator=avator,
                                   send_time=send_time)
        c.save()
        now = datetime.datetime.now()
        title = obj.pro_name
        description = auth + "在" + "项目:" + obj.pro_name + "中评论了你"
        message.objects.create(auth=auth, title=title, description=description, create_date=now.strftime("%Y-%m-%d"),
                               target_id=pro_auth_id, status=False, type='project', create_time=now).save()
        data = get_comment(pro_id)
        return JsonResponse({"status": 1, "info": data})
    else:
        return JsonResponse({"error": "你没有权限发表评论"})

@csrf_exempt
def ajax_getcomment(request):
    pro_id = request.POST.get('pro_id')
    data = get_comment(pro_id)
    return JsonResponse({"info": data})

@csrf_exempt
def get_comment(pro_id):
    info = []
    data = Comment.objects.filter(pro_id=pro_id)
    for i in range(len(list(data))):
        dit = dict()
        dit['name'] = data[i].auth_name
        dit['avator'] = str(data[i].avator)
        dit['word'] = data[i].word
        dit['send_time'] = data[i].send_time
        info.append(dit)
    return info

def get_project_number(req):
    pro_id = req.GET.get("pro_id")
    numbers = len(project_member.objects.filter(pro_id=pro_id))
    tasks = len(task.objects.filter(pro_id=pro_id))
    context = {
        "numbers": numbers,
        "tasks": tasks
    }
    return JsonResponse(context)

