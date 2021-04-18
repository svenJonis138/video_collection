from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),  # home screen or default
    path('add', views.add, name='add_video'),  # add videos ar url/add
    path('video_list', views.video_list, name='video_list')  # path to the video list page

]

