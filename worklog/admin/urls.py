from django.urls import path
from admin import views

urlpatterns = [
    path('', views.admin, name='admin'),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('user_admin/', views.user_admin, name='user_admin'),
    path('forgetPwd/', views.ForgetPwd, name='ForgetPwd'),
    path('send_captch/', views.send_captch, name='send_captch'),
    path('get_captch/', views.get_captch, name='get_captch'),
    path('get_user/', views.get_user, name='get_user'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('edit_pwd/', views.edit_pwd, name='edit_pwd'),
    path('admin_login/', views.admin_login, name="admin_login"),
    path('save_user/', views.save_user,name='save_user'),
    path('test/', views.test, name='test'),
    path('test2/', views.test2, name='test2'),
    path('save_user/', views.save_user,name='save_user'),
    path('add_user/', views.add_user, name='add_user'),
    path('manager/', views.manager,name='manager'),
    path('ordinary/', views.ordinary,name='ordinary'),
]