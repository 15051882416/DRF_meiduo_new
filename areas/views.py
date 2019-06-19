from django.shortcuts import render
from django.views import View
from .models import Area
from django import http
from meiduo_mall.utils.response_code import RETCODE
from django.core.cache import cache

import logging
logger = logging.getLogger('django')


class AreasView(View):
    """省市区数据"""
    def get(self, request):
        """提供省市区数据"""
        area_id = request.GET.get("area_id")
        if not area_id:
            # 读取省份缓存数据
            province_list = cache.get("province_list")
            if not province_list:
                # 提供省份数据
                try:
                    province_qs = Area.objects.filter(parent=None)
                    province_list = []
                    for province_model in province_qs:
                        province_list.append({'id': province_model.id, 'name': province_model.name})
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({"code": RETCODE.DBERR, 'errmsg': '省份数据错误'})
                # 存储省份缓存数据
                cache.set("province_list", province_list, 3600)
            # 响应省份数据
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "province_list": province_list})

        else:
            # 读取市或区缓存数据
            sub_data = cache.get("sub_model_%s" % area_id)
            if not sub_data:
                # 提供市或区的数据
                try:
                    # 查询市或区的父级数据
                    parent_model = Area.objects.get(id=area_id)
                    sub_model_qs = parent_model.subs.all()
                    sub_model_list = []
                    for sub_model in sub_model_qs:
                        sub_model_list.append({"id": sub_model.id, "name": sub_model.name})

                    sub_data = {
                        "id": parent_model.id,  # 父级pk
                        "name": parent_model.name,  # 父级name
                        "subs": sub_model_list  # 父级的子集
                    }
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})
                # 存储市或区缓存数据
                cache.set("sub_model_%s" % area_id, sub_data, 3600)

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', "sub_data": sub_data})





