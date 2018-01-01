from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from myproject.models import file
import datetime
from qiniu import Auth, put_file
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

import qiniu.config
# Create your views here.
@csrf_exempt
def uploads(request):
    if request.method == 'POST':
        myfile=request.FILES.get('file')
        print(myfile.name)
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        with open('upload/%s' %myfile.name, 'wb') as fn:
            fn.write(myfile.read())
            url = 'upload/%s' % myfile.name
        filename = file(file_name=myfile.name, file_url=url, date=date)
        filename.save()
        return HttpResponse('POST')
    else:
        return HttpResponse(u'不支持此请求')
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
    print(info)
    # print('******************')
    url='http://ou3b2kevh.bkt.clouddn.com/'+info+'?attname='
    # print(url)
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = file(file_name=info, file_url=url, date=date)
    filename.save()
    return HttpResponse('POST')