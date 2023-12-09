# app/models/market_data.py
from sqlalchemy import Column, Integer, String, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MarketData(Base):
    __tablename__ = 'market_data'

    id = Column(Integer, primary_key=True)
    inst_type = Column(String(50))
    inst_id = Column(String(50))
    last = Column(Float)
    last_sz = Column(Float)
    ask_px = Column(Float)
    ask_sz = Column(Float)
    bid_px = Column(Float)
    bid_sz = Column(Float)
    open_24h = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    vol_ccy_24h = Column(Float)
    vol_24h = Column(Float)
    ts = Column(BigInteger)
    sod_utc0 = Column(String(50))
    sod_utc8 = Column(String(50))
