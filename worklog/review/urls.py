from django.urls import path
from . import views
urlpatterns = [
    path('review_index/', views.review_index, name="review_index"),
    path('timeline/', views.timeline, name="person_timeline"),
    path('week_list/', views.week_list, name="week_list"),
    path('table_list/', views.table_list, name="table_list"),
    path('time_show/', views.time_show, name="time_show"),
    path('table_show/', views.table_show, name="table_show"),
    path('week_show/', views.week_show, name="week_show"),
]