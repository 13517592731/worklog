from . import views
from django.urls import path
urlpatterns = [
    path('get_token/', views.get_token, name="get_token"),
    path('download/', views.download, name="download"),
    path('project.html', views.projects, name='projects'),
    path('create_project.html', views.create_project, name='create-project'),
    path('project_detail.html', views.project_detail, name='project_detail'),
    path('all_project.html', views.all_project, name='all_project'),
    path('save_project.html', views.save_project, name='save-project'),
    path('tasks.html', views.tasks, name='tasks'),
    path('mymembers.html', views.mymembers, name='mymembers'),
    path('ajax.html', views.ajax_calendar, name='ajax_calendar'),
    path('upfile', views.upfile, name='upfile'),
    path('ajax-send.html', views.ajax_send, name='ajax_send'),
    path('ajax-getcomment.html', views.ajax_getcomment, name='ajax_getcomment'),
    path('get_project_number/', views.get_project_number, name="get_project_number"),
]