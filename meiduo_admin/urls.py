from django.conf.urls import url
from django.contrib import admin
from rest_framework.routers import SimpleRouter
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.utils import jwt_response_payload_handler

from meiduo_admin.views.user_login_views import *
from meiduo_admin.views.home_views import *
from meiduo_admin.views.user_manage_view import *
from meiduo_admin.views.sku_views import *
from meiduo_admin.views.spu_views import *
from meiduo_admin.views.Specification_views import *
from meiduo_admin.views.specOption_views import *
from meiduo_admin.views.goods_channel_views import *
from meiduo_admin.views.brand_views import *
from meiduo_admin.views.sku_image_views import *
from meiduo_admin.views.orders_views import *
from meiduo_admin.views.permission_views import *
from meiduo_admin.views.group_views import *
from meiduo_admin.views.admin_views import *


urlpatterns = [
    # 手动定义视图和序列化器，认证用户身份并且签发jwt_token
    # url(r'^authorizations/$', UserLoginView.as_view()),

    # obtain_jwt_token视图能够认证用户身份并且签发jwt_token，
    # 但是给我们返回的前端数据只有token,而没有其他额外数据
    url(r'^authorizations/$', obtain_jwt_token),

    # 用户总量统计(继承APIView，手动定义请求方法)
    # url(r'^statistical/total_count/$', HomeViews.as_view()),

    # 用户数据的获取，增加用户
    url(r'^users/$', UserManageView.as_view()),
    # 获取SKU数据
    # url(r'^skus/$', SKUView.as_view()),
    # 获取SKU数据, 新建保存SKU数据
    url(r'^skus/$', SKUView.as_view({"get": "list", "post": "create"})),
    # 获取三级分类信息
    url(r'^skus/categories/$', GoodsCategoryView.as_view()),
    # 获取spu表名称数据
    url(r'^goods/simple/$', SPUSimpleView.as_view()),
    # 获取SPU商品规格信息
    url(r'^goods/(?P<pk>\d+)/specs/$', SPUSpecView.as_view()),
    # url(r'^goods/(?P<pk>\d+)/specs/$', SPUSpecView.as_view({"get": "retrieve"})),
    # url(r'^goods/specs/$', SPUSpecView.as_view({"get": "list"})),
    # 删除SKU表数据
    url(r'^skus/(?P<pk>\d+)/$', SKUView.as_view({"delete": "destroy", "get": "retrieve", "put": "update"})),


    # 查询获取和新增SPU表列表数据
    # url(r'^goods/$', SPUView.as_view()),
    url(r'^goods/$', SPUView.as_view({"get": "list", "post": "create"})),
    # 获取品牌信息
    url(r'^goods/brands/simple/$', BrandSimpleView.as_view()),
    # 查询获取获取商品一级分类信息
    url(r'^goods/channel/categories/$', GoodsView.as_view()),
    # 查询获取获取商品二三级分类信息
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', GoodsView.as_view()),
    # 修改和删除SKU表数据
    url(r'^goods/(?P<pk>\d+)/$', SPUView.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),


    # 查询获取和新增商品SPU规格表列表数据
    url(r'^goods/specs/$', SPUSpecificationView.as_view({"get": "list", "post": "create"})),
    # 修改和删除商品SPU规格表列表数据
    url(r'^goods/specs/(?P<pk>\d+)/$', SPUSpecificationView.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),


    # 获取和新增规格选项表列表数据
    url(r'^specs/options/$', SpecOptionView.as_view({"get": "list", "post": "create"})),
    # 获取商品SPU规格相关数据
    url(r'^goods/specs/simple/$', GetSPUSpecView.as_view()),
    # 更新和删除规格选项表数据
    url(r'^specs/options/(?P<pk>\d+)/$', SpecOptionView.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),


    # 获取和新增商品频道信息
    url(r'^goods/channels/$', GoodsChannelView.as_view({"get": "list", "post": "create"})),
    # 获取商品频道组信息
    url(r'^goods/channel_types/$', GoodsChannelGroupView.as_view()),
    # 获取获取商品一级分类信息
    url(r'^goods/categories/$', GetGoodsCategoryView.as_view()),
    # 更新和删除商品频道信息
    url(r'^goods/channels/(?P<pk>\d+)/$', GoodsChannelView.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),


    # 查询获取和新增SPU表列表数据
    url(r'^goods/brands/$', BrandView.as_view({"get": "list", "post": "create"})),
    # 查询获取和新增SPU表列表数据
    url(r'^goods/brands/(?P<pk>\d+)/$', BrandView.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),


    # 获取和新增SKU图片表数据
    url(r'^skus/images/$', SKUImageView.as_view({"get": "list", "post": "create"})),
    # 获取商品SKU表id、name信息
    url(r'^skus/simple/$', SKUSimpleView.as_view()),
    # 更新和删除SKU图片表数据
    url(r'^skus/images/(?P<pk>\d+)/$', SKUImageView.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),


    # 获取订单信息列表数据
    url(r'^orders/$', OrderInfoViewSet.as_view({"get": "list"})),
    # 获取订单信息列表详情数据
    # url(r'^orders/(?P<pk>\d+)/$', OrderInfoViewSet.as_view({"get": "retrieve"})),
    url(r'^orders/(?P<order_id>\d+)/$', OrderInfoViewSet.as_view({"get": "retrieve"})),
    # 更新订单信息表的订单状态
    # url(r'^orders/(?P<pk>\d+)/status/$', OrderInfoViewSet.as_view({"put": "status"})),
    # url(r'^orders/(?P<order_id>\d+)/status/$', OrderInfoViewSet.as_view({"put": "status"})),
    url(r'^orders/(?P<order_id>\d+)/status/$', OrderInfoViewSet.as_view({"patch": "partial_update"})),


    # 获取和新增用户权限列表数据
    url(r'^permission/perms/$', PermissionViewSet.as_view({"get": "list", "post": "create"})),
    # 获取权限类型列表数据
    url(r'^permission/content_types/$', PermissionViewSet.as_view({"get": "content_types"})),
    # 更新和删除权限表数据
    url(r'^permission/perms/(?P<pk>\d+)/$', PermissionViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),


    # 获取和新增用户组列表数据
    url(r'^permission/groups/$', GroupViewSet.as_view({"get": "list", "post": "create"})),
    # 获取权限表数据
    url(r'^permission/simple/$', GroupViewSet.as_view({"get": "simple"})),
    # 更新和删除用户组列表数据
    url(r'^permission/groups/(?P<pk>\d+)/$', GroupViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),


    # 获取和新增管理员用户列表数据
    url(r'^permission/admins/$', AdminViewSet.as_view({"get": "list", "post": "create"})),
    # 获取分组表数据
    url(r'^permission/groups/simple/$', AdminViewSet.as_view({"get": "groups_simple"})),
    # 更新和删除管理员用户列表数据
    url(r'^permission/admins/(?P<pk>\d+)/$', AdminViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),



]

# 1.创建router对象
router = SimpleRouter()
# 2.注册router对象
router.register(prefix="statistical", viewset=HomeViews, base_name="home")
# 3.添加router路由
urlpatterns += router.urls