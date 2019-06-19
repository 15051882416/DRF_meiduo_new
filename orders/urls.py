from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    # 结算订单
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),

    # 提交订单
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),

    # 提交订单成功
    url(r'^orders/success/$', views.OrderSuccessView.as_view()),

    # 用户订单展示
    url(r'^orders/info/(?P<current>\d+)/$', views.UserAllOrdersView.as_view()),

    # 订单待评价页面
    url(r'^orders/comment/$', views.OrderWaitCommentView.as_view()),

    # 提交订单成功
    # url(r'^goods_judge.html/$', views.OrderWaitCommentView.as_view()),

    # 订单待评价
    # url(r'^/goods/(?P<sku_id>\d+)/.html$', views.OrderWaitCommentView.as_view()),




]
