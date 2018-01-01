from django.urls import path
from . import views
urlpatterns = [
    path('calendar/', views.calendars, name='calendar'),
    path('add/', views.add, name='add'),
    path('show/', views.show, name='show'),
    path('details/', views.details, name='details'),
    path('delete/', views.delete, name='delete'),
    path('editor/', views.editor, name='editor'),
    path('update/', views.update, name='update'),
]