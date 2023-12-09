# main.py
from app.services.okx_service import OKXService
import asyncio
from fastapi import FastAPI
from app.api.user import router as user_router

app = FastAPI()

app.include_router(user_router)

# 填入你的 API 密钥信息
api_key = "bab34581-f703-4b9d-b72a-6faec9620702"
secret_key = "CC17E3389F7288C738BDE7BA8AF77AD3"
passphrase = "Zhangzehang1234..."

okx_service = OKXService(api_key, secret_key, passphrase)

# 假设你要获取 BTC-USDT 的市场数据
asyncio.run(okx_service.start_receiving_data("ETH-USDT-SWAP"))