from django.conf.urls import patterns, url
from taskmaster_app import views

urlpatterns = patterns('',
    url(r'^$', views.taskmaster_main, name='taskmaster_main'),
)
