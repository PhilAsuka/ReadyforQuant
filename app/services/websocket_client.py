# app/services/websocket_client.py
import asyncio
import websockets
import json
from datetime import datetime
from app.core.database import add_market_data, add_market_data_batch
from app.models.market_data import MarketData


def parse_message_and_create_market_data(data_item):
    # Create MarketData instance and assign data to fields
    market_data_entry = MarketData(
        inst_type=data_item.get('instType'),
        inst_id=data_item.get('instId'),
        last=float(data_item.get('last', 0)),  # Providing a default value if 'last' is not present
        last_sz=float(data_item.get('lastSz', 0)),
        ask_px=float(data_item.get('askPx', 0)),
        ask_sz=float(data_item.get('askSz', 0)),
        bid_px=float(data_item.get('bidPx', 0)),
        bid_sz=float(data_item.get('bidSz', 0)),
        open_24h=float(data_item.get('open24h', 0)),
        high_24h=float(data_item.get('high24h', 0)),
        low_24h=float(data_item.get('low24h', 0)),
        vol_ccy_24h=float(data_item.get('volCcy24h', 0)),
        vol_24h=float(data_item.get('vol24h', 0)),
        ts=int(data_item.get('ts')),  # Assuming 'ts' will always be present
        sod_utc0=data_item.get('sodUtc0'),
        sod_utc8=data_item.get('sodUtc8'),
        received_time = datetime.utcnow()
    )

    return market_data_entry

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri

    async def connect(self, BATCH_SIZE=10):
        buffer = []
        buffer_size = 100  # 选择适当的缓冲区大小
        flush_interval = 2  # 每隔几秒钟将缓冲区数据写入数据库

        async def flush_buffer():
            while True:
                if buffer:
                    await add_market_data_batch(buffer.copy())
                    print("heartbeats!!!")
                    buffer.clear()
                await asyncio.sleep(flush_interval)

        asyncio.create_task(flush_buffer())
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    subscribe_message = {
                        "op": "subscribe",
                        "args": [{"channel": "tickers", "instId": "ETH-USDT-SWAP"}]
                    }
                    await websocket.send(json.dumps(subscribe_message))
                    while True:
                        message = await websocket.recv()
                        data_list = json.loads(message).get('data', [])
                        # Process each item in the data list
                        for data_item in data_list:
                            market_data_entry = parse_message_and_create_market_data(data_item)
                            buffer.append(market_data_entry)

                            if len(buffer) >= buffer_size:
                                # Here, ensure that your add_market_data_batch function
                                # can handle a list of MarketData instances
                                await add_market_data_batch(buffer.copy())
                                buffer.clear()
            except websockets.ConnectionClosed:
                print("Connection closed, attempting to reconnect")
                await asyncio.sleep(5)  # 等待一段时间后重试


async def main():
    client = WebSocketClient("wss://ws.okx.com:8443/ws/v5/public")
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main())