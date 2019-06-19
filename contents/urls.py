
from django.conf.urls import url
from django.contrib import admin

from contents import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

]
