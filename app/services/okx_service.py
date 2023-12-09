# app/services/okx_service.py
from .okx_v5_client import OKXV5Client

class OKXService:
    def __init__(self, api_key, secret_key, passphrase):
        self.client = OKXV5Client(api_key, secret_key, passphrase)

    async def start_receiving_data(self, symbol):
        data = await self.client.get_market_data(symbol)
        # 解析和处理数据
        print(data)
        # 可能需要调用 save_market_data 等函数来存储数据