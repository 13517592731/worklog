"""worklog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from login import views
from django.views import static
from django.conf import settings

urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT }, name='static'),
    path('admin/', include("admin.urls")),
    path('login/', include("login.urls")),
    path('myproject/', include("myproject.urls")),
    path('mycalendar/', include("mycalendar.urls")),
    path('review/', include("review.urls")),
    path('', views.welcome, name="welcome"),
]
handler404 = "login.views.page_not_found"
handler500 = "login.views.page_error"

from apscheduler.schedulers.background import BackgroundScheduler
from login.views import task_notice
sched = BackgroundScheduler()
def send_email():
    task_notice()
sched.add_job(send_email, "interval", seconds=3600)
sched.start()
