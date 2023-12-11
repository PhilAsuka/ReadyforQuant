# app/services/trade_service.py

import hmac
import base64
import httpx
import json
from datetime import datetime
from app.core.config import API_KEY, SECRET_KEY, PASSPHRASE

class OKXTradeService:
    def __init__(self):
        self.base_url = "https://www.okx.com"

    def sign(self, timestamp, method, request_path, body=''):
        message = timestamp + method + request_path + body
        mac = hmac.new(bytes(SECRET_KEY, encoding='utf8'),
                       msg=bytes(message, encoding='utf-8'),
                       digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)

    async def place_order(self, symbol, side, size, leverage=5):
        timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
        method = "POST"
        request_path = "/api/v5/trade/order"

        body = json.dumps({
            "instId": symbol,
            "tdMode": "isolated",  # 使用孤立保证金模式
            "side": side,
            "ordType": "market",  # 市价单
            "sz": size,
            "lever": leverage
        })

        sign = self.sign(timestamp, method, request_path, body)
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json',
            'x-simulated-trading': '1'  # 添加模拟交易的header
        }

        async with httpx.AsyncClient() as client:
            url = self.base_url + request_path
            response = await client.post(url, headers=headers, data=body)
            return response.json()

# 使用示例
async def main():
    trade_service = OKXTradeService()
    # 假设批大小为 0.1，确保您的订单大小是它的倍数
    order_size = "1"  # 这里调整为符合批大小要求的值
    order_response = await trade_service.place_order("ETH-USDT-SWAP", "buy", order_size)
    print(order_response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())