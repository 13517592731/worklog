# -*- coding: UTF-8 -*-
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import JsonResponse
import smtplib
import random
from django.views.decorators.csrf import csrf_exempt
from email.mime.text import MIMEText
from admin.email_base import email
from admin.models import Captch
from login.models import Profile

def get_userinfo(req):
    user_id = req.session.get("user_id")
    user = User.objects.get(id=user_id)
    name = user.profile.name
    avator = user.profile.avator
    username = user.username
    email = user.email
    context = {
        "name": name,
        "avator": str(avator),
        "username": username,
        "email": email
    }
    return JsonResponse(context)
def edit_userinfo(req):
    user_id = req.session.get("user_id")
    username = req.GET.get("username")
    email = req.GET.get("email")
    user = User.objects.get(id=user_id)
    user.username = username
    user.email = email
    user.save()
    context = {
        "status": True,
    }
    return JsonResponse(context)
@csrf_exempt
def page_not_found(request):
    return render_to_response('login/404.html')

@csrf_exempt
def page_error(request):
    return render_to_response('login/500.html')


def welcome(req):
    is_login = req.session.get('status', False)
    # 如果为真，就说明用户是正常登陆的
    if is_login:
        # 获取字典的内容并传入页面文件
        return redirect("index")
    else:
        """
        如果访问的时候没有携带正确的session，
        就直接被重定向url回login页面
        """
        return redirect("tologin")
def tologin(req):
    return render(req, "login/login.html")

def index(req):
    return render(req, "user_base.html")

def user_login(req):
    if req.method == "POST":
        username = req.POST.get('user')
        password = req.POST.get('pwd')
        status = req.POST.get('status')
        #判断用户是否以用户名登陆
        user = authenticate(username=username, password=password)
        if user is None:
            try:
                user1 = User.objects.filter(email=username)
                name = user1.values('username')[0]['username']
                # 判断用户是否以邮箱登陆
                user = authenticate(username=name, password=password)
            except:
                return render(req, 'login/login.html', {"user_error": "用户名和密码不匹配"})
        if user is not None:
            user_id = user.id
            req.session['user_id'] = user_id
            req.session['status'] = True
            if status == None:
                req.session['status'] = False
            # 登陆成功就跳转到用户首页
            return redirect("index")
        else:
            return render(req, 'login/login.html', {"user_error": "用户名和密码不匹配"})
    #登陆不成功停留在登陆界面
    return render(req, 'login/login.html')


def user_logout(req):
    """
    直接通过request.session['is_login']回去返回的时候，
    如果is_login对应的value值不存在会导致程序异常。所以
    需要做异常处理
    """
    try:
        # 删除is_login对应的value值
        del req.session['status']
        del req.session['user_id']
    except KeyError:
        pass
    # 点击注销之后，直接重定向回登录页面
    return redirect('user_login')

def ForgetPwd(req):
    return render(req, "login/ForgetPwd.html")

#发送验证码
def send_captch(req, email):
    email = str(email)
    user_is_exits = User.objects.filter(email=email)
    if len(user_is_exits) != 0:
        return ["error", ""]
    number_email = workEmail()
    number_email.set_to(email)
    number = number_email.captcha()
    content = "你正在使用邮箱进行注册, 您的验证码为:" + number + "；如果您不知道是怎么回事，请忽略。谢谢！"
    number_email.setContent(content)
    number_email.setTitle("worklog注册")
    result = number_email.send_email()
    req.session["email"] = email
    return [result, number]

def edit_pwd(req):
    email = req.session.get("email")
    pwd1 = str(req.POST.get('password1'))
    pwd2 = str(req.POST.get('password2'))
    if pwd1 != pwd2:
        return render(req, "login/find_new.html", {"error": "请输入相同的密码"})
    else:
        try:
            user = User.objects.get(email=email)
            user.set_password(pwd1)
            user.save()
            del req.session["email"]
            return redirect('user_logout')
        except:
            return render(req, "login/find_new.html", {"error": "发生未知异常,请稍后重试"})

#获取验证码
def get_captch(req):
    captch = req.POST.get('captch')
    email= req.session["email"]
    cap = Captch.objects.filter(number=captch)
    caps = []
    for c in cap:
        caps.append(c.number)
    if captch in caps:
        Captch.objects.filter(number=captch).delete()
        return render(req, "login/test_captch.html", {"status": True})
    else:
        return render(req, "login/get.html", {"number_error": "验证码不正确"})


class workEmail(email):
    def send_email(self):
        msg = MIMEText(self.content)
        msg["Subject"] = self.title
        msg["From"] = self._user
        msg["To"] = self._to
        try:
            s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            s.login(self._user, self._pwd)
            s.sendmail(self._user, self._to, msg.as_string())
            s.quit()
        except smtplib.SMTPException as e:
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

#注册前获取验证码
def regist(req):
    return render(req, "login/get.html")
def user_regist(req):
    username = req.POST.get("user")
    pwd1 = req.POST.get("pwd")
    pwd2 = req.POST.get("pwd1")
    email = req.session.get("email")
    name = req.POST.get("name")
    user_isxeit = User.objects.filter(username=username)
    if len(user_isxeit) != 0:
        context = {
            "error": "用户名已存在",
            "name": name,
            "email": email,
            "username": username
        }
        return render(req, "login/register.html", context)
    else:
        if pwd1 != pwd2:
            context = {
                "error": "请输入相同的密码",
                "name": name,
                "email": email,
                "username": username
            }
            return render(req, "login/register.html", context)
        else:
            if username != None and email != None and pwd1 != None:
                user = User.objects.create_user(username=username, email=email, password=pwd1)
                profile = Profile(
                    user_id=user.id,
                    name=name,
                    avator="/static/zui/images/emoji.png"
                )
                user.save()
                profile.save()
                req.session['user_id'] = user.id
                req.session['status'] = False
                del req.session["email"]
                return redirect("index")
            else:
                return render(req, "login/index.html", {"error": "您还有信息没有填写"})


#调用send_captch函数发送验证码
def get_email(req):
    email = req.POST.get("email")
    number = send_captch(req, email)
    if number[0] != False:
        if number[0] != "error":
            Captch.objects.create(number=number[1]).save()
            return render(req, "login/test_captch.html", {"status": True})
        else:
            return render(req, "login/get.html", {"error": "邮箱已被注册"})
    else:
        return render(req, "login/get.html", {"error": "邮箱格式有误"})

def get_passwd(req):
    email = req.POST.get("email")
    req.session["email"] = email
    number_email = workEmail()
    number = number_email.captcha()
    content = "你正在使用邮箱找回密码, 您的验证码为:" + number + "；如果您不知道是怎么回事，请忽略。谢谢！"
    number_email.setContent(content)
    number_email.setTitle("worklog找回密码")
    number_email.set_to(email)
    result = number_email.send_email()         #获取邮件发送结果
    if result != False:
        Captch.objects.create(number=number).save()
        return render(req, "login/pwd_captch.html", {"status": True})
    else:
        return render(req, "login/ForgetPwd.html", {"error": "邮箱格式有误"})

#找回密码验证码
def pwd_captch(req):
    captch = req.POST.get('captch')
    cap = Captch.objects.filter(number=captch)
    caps = []
    for c in cap:
        caps.append(c.number)
    if captch in caps:
        Captch.objects.filter(number=captch).delete()
        return render(req, "login/find_new.html")
    else:
        return render(req, "login/test_captch.html", {"error": "验证码不正确"})

#注册验证码
def test_captch(req):
    captch = req.POST.get('captch')
    cap = Captch.objects.filter(number=captch)
    caps = []
    for c in cap:
        caps.append(c.number)
    if captch in caps:
        Captch.objects.filter(number=captch).delete()
        return render(req, "login/register.html")
    else:
        return render(req, "login/test_captch.html", {"error": "验证码不正确"})

#任务提醒
def task_notice():
    from datetime import datetime
    now = datetime.now()
    task = []
    from mycalendar.models import calendar
    obj = calendar.objects.all()
    for o in obj:
        end = (o.end_time - now)
        if end.days > 0:
            end = end.seconds/3600
            if end <= 1:
                dic = dict()
                dic["user"] = o.auth_id
                dic["task"] = o.content
                task.append(dic)
    if len(task) != 0:
        for t in task:
            notice = workEmail()
            user_obj = User.objects.get(id=t["user"])
            email = user_obj.email
            name = user_obj.profile.name
            content = name + ",您好,您的任务:" + t['task'] + ",即将过期,请尽快完成！"
            notice.setTitle("任务即将过期提醒邮件")
            notice.setContent(content)
            notice.set_to(email)
            notice.send_email()



