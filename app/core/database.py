# app/core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.market_data import MarketData
from app.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def add_market_data(symbol, last_price, timestamp):
    async with SessionLocal() as session:
        new_data = MarketData(symbol=symbol, last_price=last_price, timestamp=timestamp)
        session.add(new_data)
        await session.commit()

async def add_market_data_batch(data_batch):
    # data_batch is expected to be a list of MarketData instances
    async with SessionLocal() as session:
        async with session.begin():
            # Add all the MarketData instances to the session
            for data_item in data_batch:
                session.add(data_item)  # Add each MarketData instance to the session
        # Commit the transaction
        await session.commit()
