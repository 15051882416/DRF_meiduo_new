from django.conf.urls import url
from django.contrib import admin

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.utils import jwt_response_payload_handler

from meiduo_admin.views.user_login_views import *

urlpatterns = [
    # 手动定义视图和序列化器，认证用户身份并且签发jwt_token
    url(r'^authorizations/$', UserLoginView.as_view()),

    # obtain_jwt_token视图能够认证用户身份并且签发jwt_token，
    # 但是给我们返回的前端数据只有token,而没有其他额外数据
    # url(r'^authorizations/$', obtain_jwt_token),

]
