from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django import http
from django.core.paginator import Paginator, EmptyPage

from contents.utils import get_categories
from .models import GoodsCategory, SKU, GoodsVisitCount
from .utils import get_breadcrumb
from meiduo_mall.utils.response_code import RETCODE


class ListView(View):
    """商品列表界面--分页和排序"""

    def get(self, request, category_id, page_num):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseNotFound('商品类别不存在')

        # 获取前端传入的排序规则
        sort = request.GET.get('sort')
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = '-create_time'

        # 获取当前三级类别中所有上架的sku数据
        # sku_qs = category.sku_set.filter(is_launched=True)
        sku_qs = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        # 创建分页对象Paginator(要分页的所有数据, 每页显示多个条数据)
        paginator = Paginator(sku_qs, 5)
        try:
            # 获取指定页的数据
            page_skus = paginator.page(page_num)
        except EmptyPage:
            return http.HttpResponseForbidden('当前页不存在')
        # 获取总页数据
        total_page = paginator.num_pages

        # 准备要到模板中渲染的数据
        context = {
            'categories': get_categories(),  # 频道分类
            'breadcrumb': get_breadcrumb(category),  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request, 'list.html', context)


class HotGoodsView(View):
    """商品热销排行"""
    def get(self, request, category_id):

        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('商品类别不存在')

        # sku_qs = category.sku_set.filter(is_launched=True).order_by('-sales')[:2]
        sku_qs = SKU.objects.filter(category=category, is_launched=True).order_by('-sales')[:2]
        # 用来包装转换成的sku字典
        hot_skus = []

        # 遍历查询集,将模型转换成字典
        for sku in sku_qs:
            hot_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


# class DetailView(View):
#     """商品详情页面初步展示"""
#
#     def get(self, request, sku_id):
#         """提供商品详情页"""
#         try:
#             sku = SKU.objects.get(id=sku_id)
#         except SKU.DoesNotExist:
#             return render(request, "404.html")
#         category = sku.category
#
#         # 渲染页面
#         context = {
#             'categories': get_categories(),  # 商品分类
#             'breadcrumb': get_breadcrumb(category),  # 面包屑导航
#             'sku': sku,  # 当前要显示的sku模型对象
#         }
#         return render(request, "detail.html", context)


class DetailView(View):
    """商品详情页面数据展示"""

    def get(self, request, sku_id):

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        category = sku.category
        spu = sku.spu

        """1.准备当前商品的规格选项列表 [8, 11]"""
        # 获取出当前正显示的sku商品的规格选项id列表
        current_sku_spec_qs = sku.specs.order_by('spec_id')
        current_sku_option_ids = []  # [8, 11]
        for current_sku_spec in current_sku_spec_qs:
            current_sku_option_ids.append(current_sku_spec.option_id)

        """2.构造规格选择仓库
        {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        """
        # 构造规格选择仓库
        temp_sku_qs = spu.sku_set.all()  # 获取当前spu下的所有sku
        # 选项仓库大字典
        spec_sku_map = {}  # {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        for temp_sku in temp_sku_qs:
            # 查询每一个sku的规格数据
            temp_spec_qs = temp_sku.specs.order_by('spec_id')
            temp_sku_option_ids = []  # 用来包装每个sku的选项值
            for temp_spec in temp_spec_qs:
                temp_sku_option_ids.append(temp_spec.option_id)
            spec_sku_map[tuple(temp_sku_option_ids)] = temp_sku.id

        """3.组合 并找到sku_id 绑定"""
        spu_spec_qs = spu.specs.order_by('id')  # 获取当前spu中的所有规格

        for index, spec in enumerate(spu_spec_qs):  # 遍历当前所有的规格
            spec_option_qs = spec.options.all()  # 获取当前规格中的所有选项
            temp_option_ids = current_sku_option_ids[:]  # 复制一个新的当前显示商品的规格选项列表
            for option in spec_option_qs:  # 遍历当前规格下的所有选项
                temp_option_ids[index] = option.id  # [8, 12]
                option.sku_id = spec_sku_map.get(tuple(temp_option_ids))  # 给每个选项对象绑定下他sku_id属性

            spec.spec_options = spec_option_qs  # 把规格下的所有选项绑定到规格对象的spec_options属性上

        context = {
            'categories': get_categories(),  # 商品分类
            'breadcrumb': get_breadcrumb(category),  # 面包屑导航
            'sku': sku,  # 当前要显示的sku模型对象
            'category': category,  # 当前的显示sku所属的三级类别
            'spu': spu,  # sku所属的spu
            'spec_qs': spu_spec_qs,  # 当前商品的所有规格数据
        }

        return render(request, 'detail.html', context)


class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request, category_id):
        """记录分类商品访问量"""

        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden("商品类别不存在")
        # 获取当天的日期
        today = timezone.now()
        try:
            # 查询当天有没有访问过此类别商品
            goods_visit = GoodsVisitCount.objects.get(category=category, date=today)
        except GoodsVisitCount.DoesNotExist:
            # 如果没有访问过就创建一个新的记录
            # goods_visit = GoodsVisitCount.objects.create(category=category)
            goods_visit = GoodsVisitCount(category=category)

            goods_visit.count += 1  # 增加访问量
            goods_visit.save()

        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})
