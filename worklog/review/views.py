from django.shortcuts import render
from mycalendar.models import calendar
from django.http import JsonResponse
import datetime
#回顾首页
def review_index(req):
    return render(req, "review/review_index.html")
#时间轴主页
def timeline(req):
    return render(req, "review/timeline.html")
#图表展示首页
def week_list(req):
    return render(req, "review/week_list.html")
#表格展示首页
def table_list(req):
    return render(req, "review/table_list.html")
#时间轴展示数据
def table_show(req):
    now = datetime.datetime.now()
    date = req.GET.get("date")
    user_id = req.session.get("user_id")
    obj = None
    if date == "now":
        year = now.strftime("%Y")
        month = now.strftime("%m")
        obj = calendar.objects.filter(auth_id=user_id, create_year=year, create_month=month).order_by("create_date")
    else:
        data = date.split("-")
        if(len(data) == 2):
            year = data[0]
            month = data[1]
            obj = calendar.objects.filter(auth_id=user_id, create_year=year, create_month=month).order_by("create_date")
        elif(len(data) == 4):
            format = "%Y-%m-%d"
            data1 = data[0].strip() + "-" + data[1].strip() + "-01"
            data2 = data[2].strip() + "-" + data[3].strip() + "-28"
            data1 = datetime.datetime.strptime(data1, format)
            data2 = datetime.datetime.strptime(data2, format)
            obj = calendar.objects.filter(auth_id=user_id, create_date__range=[data1, data2]).order_by("create_date")
    datas = format_table(obj)
    return JsonResponse({"info": datas})
#导出数据
def export_data(req):
    import xlsxwriter

def format_table(obj):
    now = datetime.datetime.now()
    datas = []
    i = 1
    for o in obj:
        now_time = (now - o.start_time).seconds / 3600
        order = float(o.order_time)
        process = "%.0f" % (now_time / order *100)
        if now > o.end_time:
            process = 100
        start = o.start_time.strftime("%Y-%m-%d %H:%M")
        end = o.end_time.strftime("%Y-%m-%d %H:%M")
        type = o.type
        if type == "work":
            type = "工作"
        elif type == "study":
            type = "学习"
        else:
            type = "其他"
        datas.append(
            [i, o.content, type, start, end, process]
        )
        i += 1
    return datas
#时间轴展示数据
def time_show(req):
    user_id = req.session.get("user_id")
    year = req.GET.get("year")
    date_list = []
    year_obj = calendar.objects.filter(auth_id=user_id, create_year=year)
    for d in year_obj:
        date = d.create_date
        date_list.append(date)
    #获取每天的日期
    dates = list(set(date_list))
    #字典格式化返回的结果
    dts = {}
    year_times = 0.0
    for da in dates:
        obj = calendar.objects.filter(auth_id=user_id, create_date=da).order_by("create_date")
        contents = []
        all_time = 0.0
        das = da.strftime("%m-%d")
        for o in obj:
            #一天的工作内容
            contents.append([o.content, float(o.order_time)])
            # 一天的工总时间
            all_time += float(o.order_time)
            year_times += float(o.order_time)
        dts[das] = [contents, "%.1f"%all_time]
    dts = sorted(dts.items(), key=lambda d:d[0], reverse=True)
    context = {
        "info": dts,
        "times": "%.1f"%year_times
    }
    return JsonResponse(context)


#图表展示数据
def week_show(req):
    from datetime import datetime
    user_id = req.session.get("user_id")
    data = req.GET.getlist("data[]")
    year = data[0]
    week = data[1]
    if week == "now_week":
        week = datetime.now().strftime('%V')
    if week.startswith("0"):
        week = week[1]
    study_data = type_data(user_id, year, week, "study")
    work_data = type_data(user_id, year, week, "work")
    other_data = type_data(user_id, year, week, "other")
    all_data = type_data(user_id, year, week, "all")
    context = {
        "study_data": formart_data(study_data),
        "work_data": formart_data(work_data),
        "other_data": formart_data(other_data),
        "all_data": formart_data(all_data),
        "weekday": "第" + str(week) + "周",
        "title": year + "年" + "第" + week + "周"
    }
    return JsonResponse(context)

#将数据转换成周的格式
def formart_data(old):
    weeks = []
    for i in range(7):
        weeks.append(0.0)
    for o in old:
        weekday = o.create_weekday
        for n in range(7):
            if int(weekday) == n+1:
                weeks[n] += float(o.order_time)
    for i in range(len(weeks)):
        weeks[i] = "%.1f"%weeks[i]
    return weeks




#获取工作学习的数据
def type_data(user_id, year, week, type):
    obj = calendar.objects.filter(auth_id=user_id, create_year=year, create_week=week, type=type)
    if type == "all":
        obj = calendar.objects.filter(auth_id=user_id, create_year=year, create_week=week)
    return obj

# Create your views here.
