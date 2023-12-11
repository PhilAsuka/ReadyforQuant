# main.py
from app.services.okx_service import OKXService
import asyncio
from fastapi import FastAPI
from app.api.user import router as user_router
from app.core.config import DATABASE_URL,API_KEY,SECRET_KEY,PASSPHRASE
app = FastAPI()

app.include_router(user_router)


okx_service = OKXService(API_KEY, SECRET_KEY, PASSPHRASE)

# 假设你要获取 BTC-USDT 的市场数据
asyncio.run(okx_service.start_receiving_data("ETH-USDT-SWAP"))