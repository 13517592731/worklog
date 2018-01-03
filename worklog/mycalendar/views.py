# -*- coding: UTF-8 -*-
import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from login.models import Profile
from .models import calendar


def calendars(request):
    return render(request, "mycalendar/calendar.html")

def details(req):
    calendar_id = req.GET.get('id')
    calendar_obj = calendar.objects.get(calendar_id=calendar_id)
    content = calendar_obj.content
    start_time = calendar_obj.start_time
    create_date = calendar_obj.create_date
    auth_id = calendar_obj.auth_id
    profile_obj = Profile.objects.get(user_id=auth_id)
    auth_avator = profile_obj.avator
    name = profile_obj.name
    return render(req,"mycalendar/details.html", {
        'content': content,
        'calendar_id': calendar_id,
        'start_time': start_time,
        'create_date': create_date,
       'auth_avator':auth_avator,
       'title': content + "详情",
        'name': name
    })

def editor(req):
    calendar_id = req.GET.get('id')
    content = calendar.objects.get(calendar_id=calendar_id).content
    start_time = calendar.objects.get(calendar_id=calendar_id).start_time
    type = calendar.objects.get(calendar_id=calendar_id).type
    auth_id = req.session.get("user_id")
    auth_avator = Profile.objects.get(user_id=auth_id).avator
    return  render(req,"mycalendar/editor.html",{
        'content': content,
        'calendar_id': calendar_id,
        'start_time': start_time,
        'type': type,
        'auth_avator': auth_avator
    })

#添加日志 内容、开始时间、结束时间、预期时间、
@csrf_exempt
def add(req):
    if req.method == 'POST':
        content = req.POST.get("content")
        type = req.POST.get("type")
        if type == "学习":
            type = "study"
        elif type == "工作":
            type = "work"
        elif type == "其他":
            type = "other"
        start_time = req.POST.get("start_time")
        end_time = req.POST.get("end_time")
        start_time = StrToDate(start_time)
        end_time = StrToDate(end_time)
        order = "%.1f"%((end_time - start_time).seconds/3600)
        auth_id = req.session.get("user_id")
        create_date = req.POST.get("create_date")
        now = datetime.datetime.strptime(create_date, "%Y-%m-%d")
        create_week = now.strftime('%V')#周
        if create_week.startswith("0"):
            create_week = create_week[1]
        create_weekday = now.isoweekday()#星期
        create_month = now.strftime('%m') #月
        create_year = now.strftime('%Y')#年
        work = calendar(
            content=content,
            type=type,
            start_time=start_time,
            end_time=end_time,
            order_time=order,
            auth_id=auth_id,
            create_date=create_date,
            create_week=create_week,
            create_weekday =create_weekday,
            create_month=create_month,
            create_year=create_year,
            )
        work.save()
        return JsonResponse({"status": 1})
    else:
        return JsonResponse({"status": 0})


def StrToDate(date):
    result = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return result

#当天的work显示在日历上,返回当前用户的所有日程
def show(req):
    events = []
    auth_id = req.session.get("user_id")
    data = calendar.objects.filter(auth_id=auth_id)
    now = datetime.datetime.now()
    for i in list(data):
        dit =dict()
        minutes = i.start_time.minute
        if minutes < 10:
            minutes = "0" + str(i.start_time.minute)
        else:
            minutes = str(minutes)
        time = str(i.start_time.hour) + ":" + minutes
        dit['content'] = i.content + "" + time
        dit['start_time'] = i.create_date
        dit['id'] = i.calendar_id
        dit['color'] = "green"
        if i.end_time >= now:
            dit['color'] = "#1197C1"
        events.append(dit)
    return JsonResponse({'event': events})
#查看详情
#def workinfo(req):

#编辑当前work
@csrf_exempt
def update(req):
    if req.method == 'POST':
        id = req.POST.get('event_id')
        content = req.POST.get('content')
        id = int(id)
        obj = calendar.objects.get(calendar_id=id)
        obj.content=content
        obj.save()
        return JsonResponse({"status": 1})
    else:
        return JsonResponse({"status": 0})
#删除work
@csrf_exempt
def delete(req):
    if req.method == 'POST':
        id = req.POST.get('id')
        id = int(id)
        obj = calendar.objects.get(calendar_id=id)
        obj.delete()
        return JsonResponse({"status": 1})

    else:
        return JsonResponse({"status": 0})