import json, base64, pickle
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response):
    """ 登录时合并购物车"""
    user = request.user
    # 先取出cookie中的数据
    cart_str = request.COOKIES.get("carts")
    # 判断cookie中是否有数据
    if not cart_str:
        # 没有数据直接返回
        return
    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    # 创建redis连接对象
    redis_conn = get_redis_connection("carts")
    pl = redis_conn.pipeline()
    # 遍历cookie中的大字典，将sku_id和count添加到hash中
    for sku_id in cart_dict:
        # 将cookie中的sku_id和count添加到hash中，如果redis已经存在对应，就覆盖原有数据
        pl.hset("carts_%s" % user.id, sku_id, cart_dict[sku_id]["count"])
        # 判断当前cookie中的商品是否勾选,如果勾选直接把勾选的商品sku_id 存储到set集合
        if cart_dict[sku_id]["selected"]:
            pl.sadd("selected_%s" % user.id, sku_id)
        else:
            pl.srem("selected_%s" % user.id, sku_id)
    # 执行管道
    pl.execute()

    # 删除cookie购物车数据
    # response.delete_cookie("carts")
