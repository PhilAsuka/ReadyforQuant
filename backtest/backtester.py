# app/backtest/backtester.py
import asyncio

from sqlalchemy import func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.market_data import MarketData
from app.core.config import DATABASE_URL
from app.strategies.simple_strategy import MovingAverageStrategy
import pandas as pd

# Set up the async engine and session for database interaction
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def fetch_historical_data(symbol, start_date, end_date):
    async with AsyncSessionLocal() as session:
        try:
            query = select(MarketData).where(
                MarketData.inst_id == symbol,
                MarketData.received_time >= start_date,
                MarketData.received_time <= end_date
            ).order_by(MarketData.received_time.asc())
            result = await session.execute(query)
            data = result.scalars().all()
            print(f"Fetched {len(data)} records")
            return data
        finally:
            await session.close()




def convert_to_dataframe(market_data_records):
    data = {
        "timestamp": [record.received_time for record in market_data_records],
        "last": [record.last for record in market_data_records],
        "last_sz": [record.last_sz for record in market_data_records],
        "ask_px": [record.ask_px for record in market_data_records],
        "ask_sz": [record.ask_sz for record in market_data_records],
        "bid_px": [record.bid_px for record in market_data_records],
        "bid_sz": [record.bid_sz for record in market_data_records],
        "open_24h": [record.open_24h for record in market_data_records],
        "high_24h": [record.high_24h for record in market_data_records],
        "low_24h": [record.low_24h for record in market_data_records],
        "vol_ccy_24h": [record.vol_ccy_24h for record in market_data_records],
        "vol_24h": [record.vol_24h for record in market_data_records],
        'ts': [record.ts for record in market_data_records],
        "sodUtc0": [record.sod_utc0 for record in market_data_records],
        "sodUtc8": [record.sod_utc8 for record in market_data_records]
        # ... include all other relevant fields
    }
    df = pd.DataFrame(data)
    print(f"Converted data to DataFrame with {len(df)} rows")
    return df


def generate_signal(row):
    # 示例策略：简单移动平均线交叉
    short_window = 5
    long_window = 20

    if row['short_mavg'] > row['long_mavg']:
        return 'buy'
    elif row['short_mavg'] < row['long_mavg']:
        return 'sell'
    else:
        return None


TRADE_FEE_RATE = 0.0001
def simulate_trades(data_frame, strategy):
    trade_log = []
    position_opened = False
    entry_price = 0

    # Calculate moving averages for the entire DataFrame
    data_frame['short_mavg'] = data_frame['last'].rolling(window=strategy.short_window).mean()
    data_frame['long_mavg'] = data_frame['last'].rolling(window=strategy.long_window).mean()

    for index, row in data_frame.iterrows():
        # Update the strategy's moving averages synchronously
        strategy.update_data_sync(row['short_mavg'], row['long_mavg'])

        # Determine the action based on the strategy's state
        if strategy.last_action == 'buy' and not position_opened:
            entry_price = row['last']
            entry_fee = entry_price * TRADE_FEE_RATE
            trade_log.append({
                'timestamp': row['timestamp'],
                'action': 'buy',
                'price': entry_price,
                'fee': entry_fee
            })
            position_opened = True

        elif strategy.last_action == 'sell' and position_opened:
            exit_price = row['last']
            exit_fee = exit_price * TRADE_FEE_RATE
            profit = (exit_price - entry_price) - (entry_fee + exit_fee)
            trade_log.append({
                'timestamp': row['timestamp'],
                'action': 'sell',
                'price': exit_price,
                'profit': profit,
                'fee': exit_fee
            })
            position_opened = False

    return trade_log


async def check_data_range(symbol):
    async with AsyncSessionLocal() as session:
        try:
            earliest_query = select(func.min(MarketData.received_time)).where(MarketData.inst_id == symbol)
            latest_query = select(func.max(MarketData.received_time)).where(MarketData.inst_id == symbol)

            earliest_result = await session.execute(earliest_query)
            latest_result = await session.execute(latest_query)

            earliest_time = earliest_result.scalar()
            latest_time = latest_result.scalar()

            print(f"Earliest data time: {earliest_time}")
            print(f"Latest data time: {latest_time}")
        finally:
            await session.close()


def calculate_performance_metrics(trade_log):
    total_profit = sum([trade['profit'] for trade in trade_log if 'profit' in trade])
    total_trades = sum(['profit' in trade for trade in trade_log])
    profit_trades = sum([trade['profit'] > 0 for trade in trade_log if 'profit' in trade])
    loss_trades = sum([trade['profit'] < 0 for trade in trade_log if 'profit' in trade])

    # 最大回撤，夏普比率等更复杂的指标需要更多的时间序列信息来计算
    performance_metrics = {
        'total_profit': total_profit,
        'total_trades': total_trades,
        'profit_trades': profit_trades,
        'loss_trades': loss_trades,
        'profit_trades_ratio': profit_trades / total_trades if total_trades else 0
    }

    print(f"Calculated performance metrics: {performance_metrics}")
    return performance_metrics


async def backtest(symbol, start_date, end_date):
    # 从数据库获取历史数据
    historical_data = await fetch_historical_data(symbol, start_date, end_date)
    df = convert_to_dataframe(historical_data)

    # 添加计算1分钟和2分钟移动平均线所需的列
    df['one_minute_avg'] = df['last'].rolling(window=1).mean()
    df['two_minute_avg'] = df['last'].rolling(window=2).mean()

    # 实例化您的交易策略
    strategy = MovingAverageStrategy(short_window=1, long_window=2, trade_service=None, symbol=symbol)

    # 模拟交易
    trade_log = simulate_trades(df, strategy)
    performance_metrics = calculate_performance_metrics(trade_log)

    return {
        "trade_log": trade_log,
        "performance_metrics": performance_metrics
    }



async def main():
    symbol = "ETH-USDT-SWAP"
    start_date = "2023-12-10T00:00:00Z"  # 调整为实际存在数据的开始日期
    end_date = "2023-12-15T23:59:59Z"  # 调整为实际存在数据的结束日期
    await check_data_range(symbol)
    results = await backtest(symbol, start_date, end_date)

    # 打印交易日志
    for trade in results['trade_log']:
        print(f"{trade['timestamp']} - {trade['action']} at {trade['price']} with fee {trade.get('fee', 0)}")
        if 'profit' in trade:
            print(f"Profit: {trade['profit']}")

    # 打印性能指标
    print("Performance Metrics:")
    for metric, value in results['performance_metrics'].items():
        print(f"{metric}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
