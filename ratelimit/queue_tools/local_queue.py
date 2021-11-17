"""基于本地队列，可能会出现数据丢失的问题"""
import time
from queue import Queue

from ratelimit.limits.redis_limit import RedisRateLimit
from ratelimit.queue_tools.base import BaseQueue


class LocalQueueTools(BaseQueue):
    """本地内存队列工具类"""

    _queue = Queue()
    queue_type = 'local'

    def add_item(self, item):
        """
        加入队列
        :param item: 这里队列的格式如下：
            {
                "func": func
                "func_args": [],
                "func_kwargs": {},
                "limit_config": {},
                "delay": 3
            }
        """
        delay = int(item.get('delay') or 0)
        item['handle_ts'] = int(time.time()) + delay
        self._queue.put(item)

    def get_item(self):
        """获取队列信息"""
        if not self._queue._qsize():
            return None

        item = self._queue.get()
        if item['handle_ts'] <= time.time():
            return item

        # 未到时间处理，则放回队列中
        item['delay'] = item['handle_ts'] - time.time()
        self.add_item(item)

    def _consume(self):
        """消费队列【内存队列，这里可能会存在任务丢失的情况】"""
        while True:
            item = self.get_item()
            if not item:
                time.sleep(1)
                continue

            func = item.get('func')
            func_args = item.get('func_args')
            func_kwargs = item.get('func_kwargs')
            limit_config = item.get('limit_config')
            key_name = limit_config.get('key_name')

            # 这里也要判断是否超限
            result, _ = RedisRateLimit().attempt_get_token(key_name, limit_config)
            if not result:
                # 若再次被限制时，延时执行时间修改为limit_delay
                handle_params = limit_config.get('handle_params') or {}
                next_limit_delay = handle_params.get('limit_delay') or 0
                item['delay'] = next_limit_delay
                self.add_item(item)
                continue

            func(*func_args, **func_kwargs)
            time.sleep(0)
