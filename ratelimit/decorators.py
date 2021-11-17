"""一些装饰器"""
from ratelimit.utils.over_limit_handle import OverLimitHandle


def rate_limit(key_name, default_return=None):
    """
    方法限流装饰器
    :param key_name: 键名，必传，理论上同一个系统中要唯一
    :param default_return: 默认返回值，不传则会抛出异常
    """
    class RateLimitDecorator:
        def __init__(self, func):
            self.func = func

        def __call__(self, *args, **kwargs):
            return OverLimitHandle(
                func=self.func,
                func_params={
                    'args': args,
                    'kwargs': kwargs,
                },
                key_name=key_name,
                default_return=default_return
            ).execute()

    return RateLimitDecorator


if __name__ == '__main__':
    def test_limit():
        @rate_limit('test', default_return=False)
        def test(number):
            from datetime import datetime
            print('*********', datetime.now(), number)

        import random
        import time
        from ratelimit.base.constants import LimitConfig
        LimitConfig.total_quota = 0
        LimitConfig.limit_quota = 1
        LimitConfig.default_handle = 'queue'
        LimitConfig.default_handle_params = {
            'delay': 3,
            'limit_delay': 1,
            'queue_type': 'redis'
        }

        test(random.random())
        test(random.random())
        test(random.random())

        time.sleep(5)

        test(random.random())
        print('----------------3')
        test(random.random())
        test(random.random())
        print('----------------4')
        time.sleep(10)

    test_limit()
