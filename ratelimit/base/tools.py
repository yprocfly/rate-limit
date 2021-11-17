import base64

import dill as pickle
import redis

from ratelimit.base.constants import RedisConfig


def encode_serialize(obj):
    """
    将对象序列化成字符串
    :param obj: 要序列化的对象
    :return: obj_str
    """
    return base64.b64encode(pickle.dumps(obj)).decode()


def decode_serialize(obj_str):
    """
    将字符串反序列化成对象
    :param obj_str: 被序列化的字符串
    :return: obj
    """
    try:
        return pickle.loads(base64.b64decode(obj_str))
    except Exception as err:
        print(err)
        return None


def get_redis_connection():
    """获取一个redis连接"""
    if RedisConfig.conn is None:
        connection_pool = redis.ConnectionPool(
            host=RedisConfig.host,
            port=RedisConfig.port,
            password=RedisConfig.password,
            db=RedisConfig.db,
            socket_timeout=RedisConfig.timeout,
            max_connections=RedisConfig.maxsize
        )
        RedisConfig.conn = redis.Redis(connection_pool=connection_pool)

    return RedisConfig.conn
