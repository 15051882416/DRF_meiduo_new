from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings


def generate_openid_signature(openid):
    """传入openid对其进行加密
    openid:要加密的openid
    :return: 加密后的openid
    """

    # 1.创建加密对象
    serializer = Serializer(settings.SECRET_KEY, 600)
    # 2.包装数据为字典类型
    data = {'openid': openid}
    # 3.调用dumps方法进行加密，加密后返回的是bytes类型
    openid_sign = serializer.dumps(data)
    return openid_sign.decode()


def check_openid_signature(openid):
    """对openid进行解密"""
    # 1.创建加密对象
    serializer = Serializer(settings.SECRET_KEY, 600)
    try:
        data = serializer.loads(openid)
    except BadData:
        return None
    return data.get("openid")















