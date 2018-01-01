from . import views
from django.urls import path
urlpatterns = [
    path('upload/', views.uploads, name="uploads"),
    path('get_token/', views.get_token, name="get_token"),
    path('download/', views.download, name="download"),
]