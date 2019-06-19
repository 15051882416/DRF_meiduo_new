from django.shortcuts import render
from django.views import View

from contents.utils import get_categories
from goods.models import GoodsCategory, GoodsChannel
from .models import ContentCategory, Content


class IndexView(View):
    """首页"""

    def get(self, request):
        # 查询出商品类别数据

        # 查询出首页广告数据
        """
        {
            'index_lbt': [lbt1, lbt2, lbt3],
            'index_kx' : []
        }
        """
        # 定义一个字典用来包装所有广告数据
        contents = {}
        # 获取所有广告类别
        content_category_qs = ContentCategory.objects.all()
        # 遍历广告类别查询集构建广告数据格式
        for cat in content_category_qs:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': get_categories(),  # 类别数据
            'contents': contents  # 广告数据
        }
        return render(request, 'index.html', context)
