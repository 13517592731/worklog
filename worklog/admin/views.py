from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import JsonResponse
import smtplib
import random
from django.views.decorators.csrf import csrf_exempt
from email.mime.text import MIMEText
from .email_base import email
from .models import Captch
from mycalendar.models import calendar
from django.core.paginator import PageNotAnInteger,Paginator, EmptyPage
from login.models import Profile
from datetime import datetime
from mycalendar.models import message
from myproject.models import task, project
import time
def admin(req):
    is_login = req.session.get('admin_status', False)
    # 如果为真，就说明用户是正常登陆的
    if is_login:
        id_exit = req.session.get('admin_id', False)
        if id_exit and User.objects.get(id=id_exit).is_superuser:
            return redirect("admin_index")
        else:
            return render(req, 'admin/login.html', {"user_error": "抱歉，你没有权限执行此操作，请联系管理员"})
    else:
        """
        如果访问的时候没有携带正确的session，
        就直接被重定向url回login页面
        """
        return redirect('login')

def admin_index(req):
    user_id = req.session.get("admin_id")
    from mycalendar.models import message
    cal_number = len(calendar.objects.all())
    user_number = len(User.objects.all())
    messege_number = len(message.objects.filter(target_id=user_id))
    return render(req, "admin/index.html", locals())
def login(req):
    return render(req, "admin/login.html")

def admin_login(req):
    if req.method == "POST":
        username = req.POST.get('user')
        password = req.POST.get('pwd')
        # 判断用户是否以用户名登陆
        user = authenticate(username=username, password=password)
        if user is None:
            try:
                user1 = User.objects.filter(email=username)
                name = user1.values('username')[0]['username']
                # 判断用户是否以邮箱登陆
                user = authenticate(username=name, password=password)
            except:
                return render(req, 'admin/login.html', {"pwd_error": "用户名和密码不匹配"})
        if user is not None:
            is_super = user.is_superuser
            if is_super == True:
                # 是否记住密码
                status = req.POST.get('status')
                # 认证用户
                req.session['admin_id'] = user.id
                req.session['admin_status'] = True
                if status == None:
                    req.session['admin_status'] = False
                # 登陆成功就跳转到管理员首页
                return redirect('admin_index')
            else:
                return render(req, 'admin/login.html', {"user_error": "抱歉，你没有权限执行此操作，请联系管理员"})
        else:
            return render(req, 'admin/login.html', {"pwd_error": "用户名和密码不匹配"})
    #登陆不成功停留在登陆界面
    return render(req, 'admin/login.html')

def get_trends(req):
    create_date = datetime.now().strftime("%Y-%m-%d")
    id = req.session.get("admin_id")
    users = Profile.objects.exclude(user_id=id)
    avator_list = []
    name_list = []
    user_list = []
    for us in users:
        name_list.append(us.name)
        user_list.append(us.user_id)
        avator_list.append(str(us.avator))
    results = []
    all_trends = 0
    all = len(calendar.objects.filter(create_date=create_date, auth_id__in=user_list))
    for l in range(len(user_list)):
        temp = []
        temp.append(name_list[l])
        temp.append(avator_list[l])
        cal = calendar.objects.filter(auth_id=user_list[l], create_date=create_date)
        all_trends += len(cal)
        temp.append(len(cal))
        times = 0.0
        for c in cal:
            if c.auth_id == l:
                times += float(c.order_time)
        temp.append("%.2f"%times)
        if all == 0:
            type = 0
        else:
            type = "%.f"%((len(cal))/all)
        temp.append(type)
        results.append(temp)
    return JsonResponse({"result": results, "all_trends": all_trends})





def logout(req):
    """
    直接通过request.session['is_login']回去返回的时候，
    如果is_login对应的value值不存在会导致程序异常。所以
    需要做异常处理
    """
    try:
        # 删除is_login对应的value值
        del req.session['admin_id']
        del req.session['admin_status']
    except KeyError:
        pass
    # 点击注销之后，直接重定向回登录页面
    return redirect('login')
def user_admin(req):
    after_range_num=2
    bevor_range_num=1
    info = User.objects.all()
    paginator = Paginator(info, 5)
    try:
        page = int(req.GET.get('page'))
    except:
        page=1
    try:
        list_items = paginator.page(page)
    except PageNotAnInteger:  # 如果页面不是整数，则传递第一页。
        list_items = paginator.page(1)
    except EmptyPage:  # 如果page超过范围//跳到最后一页
        list_items = paginator.page(paginator.num_pages)
    if page>=after_range_num:
        page_range=paginator.page_range[page-after_range_num:page+bevor_range_num]
    else:
        page_range=paginator.page_range[0:int(page)+bevor_range_num]
    return render(req, 'admin/user_admin.html',locals())

def ForgetPwd(req):
    return render(req, "admin/ForgetPwd.html")

@csrf_exempt
def send_captch(req):
    email = str(req.POST.get('email'))
    number_email = workEmail()
    number_email.set_to(email)
    number = number_email.send_email()
    if number != False:
        Captch.objects.create(number=number).save()
        return JsonResponse({"status": True})
    else:
        return JsonResponse({"status": False})

def edit_pwd(req):
    email = str(req.POST.get('email'))
    pwd = str(req.POST.get('pwd'))
    try:
        user = User.objects.get(email=email)
        user.set_password(pwd)
        user.save()
        return redirect('logout')
    except:
        return render(req, "admin/editPwd.html", {"error": "发生未知异常,请稍后重试"})

def get_user(req):
    from login.models import Profile
    user_id = req.session.get("admin_id")
    user = Profile.objects.get(user_id=user_id)
    name = user.name
    avator = user.avator
    context = {
        "name": name,
        "avator": str(avator)
    }
    return JsonResponse(context)

@csrf_exempt
def delete_user(req):
    ids = req.POST.getlist("users[]")
    Profile.objects.filter(user_id__in=ids).delete()
    User.objects.filter(id__in=ids).delete()
    context = {
        "status": True
    }
    return JsonResponse(context)

def get_captch(req):
    captch = req.POST.get('captch')
    email= req.POST.get('email')
    cap = Captch.objects.filter(number=captch)
    caps = []
    for c in cap:
        caps.append(c.number)
    if captch in caps:
        Captch.objects.filter(number=captch).delete()
        return render(req, "admin/editPwd.html", {"email": email})
    else:
        return render(req, "admin/ForgetPwd.html", {"number_error": "验证码不正确"})


class workEmail(email):
    def send_email(self):
        number = self.captcha()
        msg = MIMEText("你正在使用邮箱找回密码, 您的验证码为:" + number + "；如果您没有此操作，请忽略。谢谢！")
        msg["Subject"] = "worklog管理员找回密码"
        msg["From"] = self._user
        msg["To"] = self._to
        try:
            s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            s.login(self._user, self._pwd)
            s.sendmail(self._user, self._to, msg.as_string())
            s.quit()
            return number
        except smtplib.SMTPException as e:
            print(e)
            return False

    def captcha(self):
        temp = ""
        for i in range(4):
            if i == 0 or i == 1:
                number = str(random.randint(1, 5))
                temp += number
            else:
                number = str(random.randint(6, 9))
                temp += number
        return temp

@csrf_exempt
def add_user(req):    #新添用户
    Username=req.POST.get('u')
    Password=req.POST.get('p')
    Fullname=req.POST.get('t')
    Email= req.POST.get('ee')
    user_is_exits=User.objects.filter(username=Username)
    if(len(user_is_exits)==0):
        user=User.objects.create_user(username=Username,password=Password, email=Email)
        user.save()
        pp=Profile.objects.create(user_id=user.id,name=Fullname)
        pp.save()
        return JsonResponse({'msg':"success"})
    else:
        return JsonResponse({'msg': "exist"})

@csrf_exempt
def save_user(req):
    username=req.POST.get('username')
    true_name=req.POST.get('true_name')
    email=req.POST.get('email')
    id = req.POST.get('id')
    user=User.objects.filter(id=id)
    if(len(user)>0):
        try:
            pp=Profile.objects.create(user_id=id)
            pp.save()
        except:
            pass
        user.update(username=username, email=email)
        users=Profile.objects.get(user_id=id)
        users.name = true_name
        users.save()
        return JsonResponse({'msg': "ok"})
    else:
        return JsonResponse({'msg': "error"})

@csrf_exempt
def manager(req):
    list=[]
    ids=req.POST.getlist('mans[]')
    for id in ids:
        man=User.objects.get(id=id)
        if(man.is_superuser==1):
            list.append(man.id)
    if(len(list)>0):
        return JsonResponse({'msg':'already'})
    else:
        User.objects.filter(id__in=ids).update(is_superuser=1)
        return JsonResponse({'msg':'OK'})

@csrf_exempt
def ordinary(req):
    list=[]
    ids=req.POST.getlist('mans[]')
    for id in ids:
        man=User.objects.get(id=id)
        if(man.is_superuser==0):
            list.append(man.id)
    if(len(list)>0):
        return JsonResponse({'msg': 'already'})
    else:
        User.objects.filter(id__in=ids).update(is_superuser=0)
        return JsonResponse({'msg': 'OK'})

def PersonalTimeline(req):
    after_range_num = 2
    bevor_range_num = 1
    info = Profile.objects.all()
    paginator = Paginator(info, 8)
    try:
        page = int(req.GET.get('page'))
    except:
        page = 1
    try:
        list_items = paginator.page(page)
    except PageNotAnInteger:  # 如果页面不是整数，则传递第一页。
        list_items = paginator.page(1)
    except EmptyPage:  # 如果page超过范围//跳到最后一页
        list_items = paginator.page(paginator.num_pages)
    if page >= after_range_num:
        page_range = paginator.page_range[page - after_range_num:page + bevor_range_num]
    else:
        page_range = paginator.page_range[0:int(page) + bevor_range_num]
    return render(req,'admin/PersonalTimeline.html',locals())

@csrf_exempt
def search(req):
    name = req.POST.get('name')
    search = Profile.objects.filter(name=name)
    if (len(search)) > 0:
        return render(req , 'admin/PersonalTimeline.html', {'list_items': search})
    else:
        return render(req,'admin/PersonalTimeline.html',{'msg':'没有搜到该用户'})

def select(req):
    id=req.GET.get('id')
    name = Profile.objects.get(user_id=id).name
    return render(req,'admin/select.html', locals())

def tableshows(req):
    id=req.GET.get('id')
    user_name = Profile.objects.get(user_id=id)
    cals=calendar.objects.filter(auth_id=id)
    now = datetime.now()
    return render(req,'admin/tableshows.html', locals())

@csrf_exempt
def personal(req):
    now_year = datetime.now().strftime("%Y")
    now_week = datetime.now().strftime("%W")
    month = [1 , 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    week = []
    year = []
    s = []
    for i in range(7):
        s.append(0)
    id=req.GET.get('id')
    user_name=Profile.objects.get(user_id=id)
    cals=calendar.objects.filter(auth_id=id)
    for c in cals:
        year.append(c.create_year)
        week.append(c.create_week)
    years = list(set(year))
    weeks = list(set(week))
    years.sort()
    weeks.sort()
    nows=calendar.objects.filter(auth_id=id,create_year=now_year,create_week=now_week)
    for now in nows:
        try:
            endarray=time.strptime(str(now.end_time),"%Y-%m-%d %H:%M:%S")
            startarray=time.strptime(str(now.start_time),"%Y-%m-%d %H:%M:%S")
            end=time.mktime(endarray)
            start=time.mktime(startarray)
            s[int(now.create_weekday)] = (int(end) - int(start)) / (60 * 60)
        except:
            end=0
            start=0
            s[int(now.create_weekday)] = (int(end) - int(start)) / (60 * 60)
    return render(req,'admin/personal.html', locals())

def personal_change(req):
    m=[]
    for i in range(7):
        m.append(0)
    id = req.GET.get('id')
    select_year=req.GET.get('select_year')
    select_week = req.GET.get('select_week')
    selects = calendar.objects.filter(auth_id=id, create_year=select_year, create_week=select_week)
    for select in selects:
        try:
            endarray=time.strptime(str(select.end_time),"%Y-%m-%d %H:%M:%S")
            startarray=time.strptime(str(select.start_time),"%Y-%m-%d %H:%M:%S")
            end=time.mktime(endarray)
            start=time.mktime(startarray)
            m[int(select.create_weekday)] = (int(end) - int(start)) / (60 * 60)
        except:
            end=0
            start=0
            m[int(select.create_weekday)] = (int(end) - int(start)) / (60 * 60)
    return JsonResponse({'msg': 'ok', 'm':m})

def timeline(req):
    year = []
    id=req.GET.get('id')
    user_name = Profile.objects.get(user_id=id)
    cals = calendar.objects.filter(auth_id=id)
    for c in cals:
        year.append(c.create_year)
    years = list(set(year))
    years.sort()
    return render(req,'admin/timeline.html', locals())

def get_message(req):
    type = req.GET.get("type")
    user_id = req.session.get("admin_id")
    messages = message.objects.filter(target_id=user_id, status=False)
    now = datetime.now()
    result = []
    for m in messages:
        temp = []
        temp.append(m.description)
        start = now - m.create_time
        day = start.days
        hour = round(start.seconds/3600)
        minute = round(start.seconds/60)
        if day >= 1:
            content = str(day) + "天前"
        elif hour >= 1:
            content = str(hour) + "小时前"
        else:
            content = str(minute) + "分钟前"
        temp.append(content)
        result.append(temp)
    if type == "less":
        result = result[:3]
    contxet = {
        "times": len(messages),
        "messages": result
    }
    return JsonResponse(contxet)

def get_message_read(req):
    user_id = req.session.get("admin_id")
    messages = message.objects.filter(target_id=user_id, status=True)
    now = datetime.now()
    result = []
    for m in messages:
        temp = []
        temp.append(m.description)
        start = now - m.create_time
        day = start.days
        hour = round(start.seconds/3600)
        minute = round(start.seconds/60)
        if day >= 1:
            content = str(day) + "天前"
        elif hour >= 1:
            content = str(hour) + "小时前"
        else:
            content = str(minute) + "分钟前"
        temp.append(content)
        result.append(temp)
    contxet = {
        "messages": result
    }
    return JsonResponse(contxet)

def project_process(req):
    type = req.GET.get("type")
    result = type_project(type)
    contxet = {
        "tasks": result
    }
    return JsonResponse(contxet)
def type_project(type):
    result = []
    #未完成的项目
    temp = []
    if type == "img":
        projects = project.objects.filter(pro_status=False)
        for p in projects:
            temp.append([p.pro_id, p.pro_name])
        for t in temp:
            all_tasks = task.objects.filter(pro_id=t[0])
            tasked = task.objects.filter(pro_id=t[0], status=True)
            process = (len(tasked) / len(all_tasks))*100
            result.append([t[1], process, t[0]])
        return result
    # 已完成或延期完成的项目
    else:
        from datetime import datetime
        now = datetime.today()
        projects = project.objects.filter(pro_status=True)
        for p in projects:
            day = (now - p.pro_end)
            status = str(day) + "天前"
            if day.day < 1:
                hour = day.hour
                status = str(hour) + "小时前"
            result.append([p.pro_name, status, p.pro_id])
        return result


def admin_messages(req):
    return render(req, "admin/admin_messages.html")
def admin_create_project(req):
    return render(req, "admin/create_project.html")

def admin_project(req):
    return render(req, "admin/admin_projects.html")

def admin_project_detail(request):
    from myproject.models import project, project_member
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
    return render(request, "admin/project_detail.html", {
        'name': name,
        'members': members,
        'pro_id': pro_id,
    })