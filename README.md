# ReadyforQuant(DEMO)

此项目是量化交易系统的框架，目前只是demo状态

目前只实现了以下功能：
与OKX交易所建立websocket通信，接收行情数据，并写入数据库；
通过OKX交易所的REST api获取单个产品行情；
通过OKX交易所的REST api下单；
通过获取数据库数据进行策略回测；
根据策略执行交易。

项目进行：
修改config.py文件
通过docker容器，运行dockerfile文件，可以运行websocket_client.py文件(接收数据，并执行策略交易)

Further development：
在fastapi的基础上进行前端的拓展，优化代码，补充功能块(风险监控模块)。

Core Components
config.py: Configuration settings for database connections and API keys.
database.py: Management of database sessions and connections.
event_loop.py: (Incomplete)Handling the asynchronous event loop for non-blocking operations.
init_db.py: Initialization of the database with required tables and schemas.

Data Models and Market Interaction:
market_data.py: Definition of the market data model and how market data is structured.

Services:
okx_service.py(Incomplete) & okx_v5_client.py: Interaction with OKX Exchange API for market data and order execution.
trade_service.py: Service for executing trades based on signals from strategies.('x-simulated-trading': '1'  # 添加模拟交易的header, 真实交易需删除)
websocket_client.py: Managing real-time data streams through WebSocket connections and execute trading based on signals

Strategies:
simple_strategy.py: Implementation of a sample trading strategy, such as moving average crossover.

Backtesting:
backtester.py: Detailed walkthrough of backtesting capabilities for historical data analysis and strategy refinement.
Emphasize the importance of backtesting for strategy validation.
Utilities:
indicators.py(Incomplete): Discuss various technical indicators provided as utilities. （自定义指标的method库）
logger.py(Incomplete): Explain the logging system for monitoring and debugging.
