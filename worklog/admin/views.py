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
from django.core.paginator import PageNotAnInteger,Paginator,InvalidPage,EmptyPage
from login.models import Profile
def admin(req):
    is_login = req.session.get('is_login', False)
    # 如果为真，就说明用户是正常登陆的
    if is_login:
        return render(req, "admin/index.html", locals())
    else:
        """
        如果访问的时候没有携带正确的session，
        就直接被重定向url回login页面
        """
        return render(req, "admin/login.html")
def login(req):
    return render(req, "admin/login.html")

def admin_login(req):
    if req.method == "POST":
        username = req.POST.get('user')
        password = req.POST.get('pwd')
        user_is_exits = User.objects.filter(username=username)
        if len(user_is_exits) == 0:
            return render(req, 'admin/login.html', {"user_error": "该用户不存在"})
        else:
            # 是否记住密码
            status = req.POST.get('status')
            # 认证用户
            if username != "" and password != "":
                user = authenticate(username=username, password=password)
                if user is not None:
                    if status == None:
                        req.session['is_login'] = False
                        req.session['status'] = False
                    req.session['is_login'] = True
                    req.session['username'] = username
                    req.session['status'] = True
                    # 登陆成功就跳转到管理员首页
                    return redirect('admin')
                else:
                    return render(req, 'admin/login.html', {"pwd_error": "密码错误"})
    #登陆不成功停留在登陆界面
    return render(req, 'admin/login.html')

def logout(req):
    """
    直接通过request.session['is_login']回去返回的时候，
    如果is_login对应的value值不存在会导致程序异常。所以
    需要做异常处理
    """
    try:
        # 删除is_login对应的value值
        del req.session['is_login']
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
    username = req.session['username']
    context = {
        "username": username
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
        return JsonResponse({'msg': "success"})
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

def test(req):
    return render(req,'admin/PersonalTimeline.html')
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

def test2(req):
    return render(req,'admin/personal.html')
@csrf_exempt
def ordinary(req):
    list=[]
    ids=req.POST.getlist('mans[]')
    for id in ids:
        man=User.objects.get(id=id)
        if(man.is_superuser==0):
            list.append(man.id)
    if(len(list)>0):
        return JsonResponse({'msg':'already'})
    else:
        User.objects.filter(id__in=ids).update(is_superuser=0)
        return JsonResponse({'msg': 'OK'})




