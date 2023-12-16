# app/strategies/simple_strategy.py

import asyncio
from collections import deque
from app.services.trade_service import OKXTradeService  # 引入交易服务

class MovingAverageStrategy:
    def __init__(self, short_window, long_window, trade_service, symbol):
        self.short_window = short_window
        self.long_window = long_window
        self.trade_service = trade_service
        self.symbol = symbol
        self.short_moving_avg = deque(maxlen=short_window)
        self.long_moving_avg = deque(maxlen=long_window)
        self.last_action = None
        self.trade_queue = asyncio.Queue()  # 用于交易请求的队列

    async def update_data(self, one_minute_avg, two_minute_avg):
        if one_minute_avg > two_minute_avg and self.last_action != 'buy':
            await self.trade_queue.put('buy')
            self.last_action = 'buy'
        elif one_minute_avg < two_minute_avg and self.last_action != 'sell':
            await self.trade_queue.put('sell')
            self.last_action = 'sell'

    def update_data_sync(self, one_minute_avg, two_minute_avg):
        # 这是同步版本的update_data函数
        if one_minute_avg > two_minute_avg and self.last_action != 'buy':
            self.last_action = 'buy'
        elif one_minute_avg < two_minute_avg and self.last_action != 'sell':
            self.last_action = 'sell'
        else:
            self.last_action = None

    async def process_trades(self):
        while True:  # 持续运行的循环
            action = await self.trade_queue.get()  # 从队列中获取交易请求
            await self.execute_trade(action)
            self.trade_queue.task_done()

    async def execute_trade(self, action):
        print(f"Executing {action} trade")
        order_size = "1"
        order_response = await self.trade_service.place_order(self.symbol, action, order_size)
        print(order_response)