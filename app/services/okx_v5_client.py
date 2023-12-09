# app/services/okx_v5_client.py
import httpx
import asyncio
import hmac
import base64
import datetime
import json

class OKXV5Client:
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = "https://www.okx.com"

    def sign(self, timestamp, method, request_path, body=''):
        message = timestamp + method + request_path + body
        mac = hmac.new(bytes(self.secret_key, encoding='utf8'),
                       msg=bytes(message, encoding='utf-8'),
                       digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)

    async def get_market_data(self, symbol):
        timestamp = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
        method = "GET"
        request_path = f"/api/v5/market/ticker?instId={symbol}"

        sign = self.sign(timestamp, method, request_path)
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            url = self.base_url + request_path
            response = await client.get(url, headers=headers)
            return response.json()