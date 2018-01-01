from django.urls import path
from . import views
urlpatterns = [
    path('upload/', views.upload, name="upload"),
    path('user_login/', views.user_login, name="user_login"),
    path('regist/', views.regist, name="regist"),
    path('send_captc', views.send_captch, name="user_send_captch"),
    path('get_email/', views.get_email, name="get_email"),
    path('test_captch/', views.test_captch, name="test_captch"),
    path('user_regist/', views.user_regist, name="user_regist"),
    path('index/', views.index, name="index"),
    path('user_logout/', views.user_logout, name="user_logout"),
    path('ForgetPwd/', views.ForgetPwd, name="ForgetPwd"),
    path('get_passwd/', views.get_passwd, name='get_passwd'),
    path('pwd_capach/', views.pwd_captch, name='pwd_captch'),
    path('user_edit_pwd/', views.edit_pwd, name='user_edit_pwd'),
    path('get_userinfo/', views.get_userinfo, name='get_userinfo'),
    path('edit_userinfo/', views.edit_userinfo, name='edit_userinfo'),

]
