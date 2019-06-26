from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# 自定义分页器实现分页效果
class MyPagination(PageNumberPagination):

    page_query_param = "page"
    page_size_query_param = "pagesize"
    page_size = 5
    max_page_size = 10

    #   # 重写分页返回方法，按照指定的字段进行分页数据返回
    def get_paginated_response(self, data):

        """
        :param data: 分页子集的序列化结果
        :return: 该函数返回对是一个响应对象
        """
        return Response({
            "counts": self.page.paginator.count,  # 总数量
            "lists": data,  # 当前分页的数据子集
            "page": self.page.number,  # 当前页数
            "pages": self.page.paginator.num_pages,  # 总页数
            "pagesize": self.page_size,  # 后端指定的页容量
        })