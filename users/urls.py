
from django.conf.urls import url
from django.contrib import admin

from users import views

urlpatterns = [
    # 注册界面
    url(r'^register/$', views.RegisterView.as_view(), name="register"),
    # 判断用户名是否重复注册
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    # 判断手机号是否重复注册
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 用户登录
    url(r'^login/$', views.LoginView.as_view()),
    # 退出登录
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # 用户中心
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),

    # 添加邮箱
    url(r'^emails/$', views.EmailView.as_view()),
    # 激活邮箱
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    # 用户收货地址
    url(r'^addresses/$', views.AddressView.as_view(), name="address"),


    # 省市区数据
    # url(r'^areas/$', views.AreasView.as_view()),


    # 新增地址
    url(r'^addresses/create/$', views.CreatAddressView.as_view()),
    # 修改地址
    url(r'addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 设置默认收货地址
    url(r'addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    # 设置更新地址title
    url(r'addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
    # 修改用户登录密码
    url(r'^password/$', views.ChangePasswordView.as_view()),
    # 商品浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),

    # 找回密码界面
    url(r'^find_password/$', views.FindPasswordView.as_view(), name='findPassword'),
    # 输入用户名
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/sms/token/$', views.EnterAccountsView.as_view()),
    # 验证身份--发送短信验证码
    url(r'^sms_codes/$', views.SendSmsCodeView.as_view()),
    # 验证手机号
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/password/token/$', views.VerifyMobileView.as_view()),
    # 重置密码
    url(r'^users/(?P<user_id>\d+)/password/$', views.ResetPasswordView.as_view()),








]
