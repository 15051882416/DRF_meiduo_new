from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from users.models import User
from orders.models import OrderInfo
from goods.models import GoodsVisitCount
from meiduo_admin.serializers.home_serializers import *
import pytz
from rest_framework import settings


# class HomeViews(APIView):
#     """首页用户数的相关据统计"""
#
#     def get(self, request):
#
#         # 获得用户总数量
#         count = User.objects.filter(is_active=True).count()
#         # 获取当天查询日期
#         # timezone.now() --> 2019-6-17 12：12：12
#         now_date = timezone.now().date()
#
#         return Response({
#             "count": count,
#             "date": now_date
#         })

# 定义视图接口的原则：
# 1.同类功能尽可能放在一个视图中完成
# 2.对统一资源处理尽可能放在一个视图中完成


class HomeViews(ViewSet):
    """首页用户的相关数据统计"""

    @action(methods=['get'], detail=False)
    def total_count(self, request):
        """用户总量统计"""

        # 获得用户总数量
        count = User.objects.filter(is_active=True).count()
        # 获取当天查询日期

        # astimezone(pytz.timezone(settings.TIME_ZONE))  获取配置中的当前时区信息
        # cur_date = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))  # Shanghai  2019-6-18  16:10:34  --->  UTC   2019-6-18  8:04:34
        # cur_date------获取配置中当前时区下的当前时间
        # # 2、根据当日日期过滤出，当体登陆的用户
        # # UTC  2019-6-18  0：0：0  --->  UTC  2019-6-17  15：54：0 --> Shanghai  2019-6-18  0：0：0
        # shanghai_0_utc = cur_date.replace(hour=0, minute=0, second=0)


        # timezone.now() --> 2019-6-17 12：12：12
        now_date = timezone.now().date()

        return Response({
            "count": count,
            "date": now_date
        })

    @action(methods=['get'], detail=False)
    def day_increment(self, request):
        """日增用户统计"""

        # 获取当天的日期
        current_date = timezone.now()
        # print("current_date:", current_date)

        # 过滤出当天新建的用户数量
        # print("零时间： ", current_date.replace(hour=0, minute=0, second=0))

        count = User.objects.filter(
            date_joined__gte=current_date.replace(hour=0, minute=0, second=0)
        ).count()

        return Response({
            "count": count,
            "date": current_date.date()
        })

    @action(methods=["get"], detail=False)
    def day_active(self, request):
        """日活跃用户统计"""
        # 获取当天日期
        current_date = timezone.now()

        # 过滤出当天登录过的用户数量
        count = User.objects.filter(
            last_login__gte=current_date.replace(hour=0, minute=0, second=0)
        ).count()

        # 构建返回数据
        return Response({
            "count": count,
            "date": current_date.date()
        })

    @action(methods=['get'], detail=False)
    def day_orders(self, request):
        """日下单用户量统计"""

        # 获取当天日期
        current_date = timezone.now()

        # 过滤出当天登录过的用户数量
        count = User.objects.filter(
            orderinfo__create_time__gte=current_date.replace(hour=0, minute=0, second=0)
        ).count()

        # 构建返回数据
        return Response({
            "count": count,
            "date": current_date.date()
        })

    @action(methods=["get"], detail=False)
    def month_increment(self, request):
        """月增用户统计"""

        # 1.获取当天日期
        current_date = timezone.now().replace(hour=0, minute=0, second=0)
        # 2.获取一个月前的日期
        start_date = current_date - timedelta(days=29)
        # 3.过滤出这个月的用户数量
        # 创建空列表保存每天的用户量
        count_list = []
        for i in range(30):
            # 遍历获取某天当天日期
            index_date = start_date + timedelta(days=i)
            # 获取某天当天的下一天日期
            next_date = index_date + timedelta(days=1)

            # 查询条件是大于当前日期index_date，小于明天日期的用户next_date，得到当天用户量
            count = User.objects.filter(
                date_joined__gte=index_date,
                date_joined__lt=next_date
            ).count()

            count_list.append({
                "count": count,
                "date": index_date.date()

            })

        return Response(count_list)

    @action(methods=["get"], detail=False)
    def goods_day_views(self, request):
        """商品访问量"""

        # 获取当天访问的商品分类数量信息
        goods_visit_query = GoodsVisitCount.objects.filter(date=timezone.now())
        # 获取商品访问量的序列化器对象
        serializer = GoodsVisitSerializer(goods_visit_query, many=True)

        return Response(serializer.data)






























