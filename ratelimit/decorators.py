"""一些装饰器"""
import functools

from ratelimit.utils.over_limit_handle import OverLimitHandle


def rate_limit(key_name, default_return=None):
    """
    方法限流装饰器
    :param key_name: 键名，必传，理论上同一个系统中要唯一
    :param default_return: 默认返回值，不传则会抛出异常
    """
    def rate_limit_decorator(func):

        @functools.wraps(func)
        def _wrapped_func(*args, **kwargs):
            return OverLimitHandle(
                func=func,
                func_params={
                    'args': args,
                    'kwargs': kwargs,
                },
                key_name=key_name,
                default_return=default_return
            ).execute()
        return _wrapped_func

    return rate_limit_decorator


if __name__ == '__main__':
    def test_limit():

        class TestLimit:
            @rate_limit('test', default_return=False)
            def test(self, number):
                from datetime import datetime
                print('*********', datetime.now(), number)

        import random
        from ratelimit.base.constants import LimitConfig
        LimitConfig.total_quota = 0
        LimitConfig.limit_quota = 1
        LimitConfig.default_handle = 'queue'
        LimitConfig.default_handle_params = {
            'delay': 3,
            'limit_delay': 1,
            'queue_type': 'redis'
        }

        TestLimit().test(random.random())
        TestLimit().test(random.random())

    test_limit()
