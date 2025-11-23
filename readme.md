# Crypto Quant Backend

简易加密货币量化分析后端系统，基于 FastAPI 构建。提供实时市场扫描与数据分析服务。

## 核心功能

- **市场扫描**: 自动扫描全市场币种，基于策略筛选机会 (`/api/v1/scan`)。
- **数据获取**: 集成 CCXT 对接 Binance 等交易所数据。
- **K 线服务**: 提供标准化的 OHLCV 数据接口 (`/api/v1/kline`)。
- **实时计算**: 后台异步任务周期性更新市场状态。

## 技术栈

- **Framework**: FastAPI
- **Data**: Pandas, Numpy
- **Exchange**: CCXT (Binance)
- **Task**: Asyncio / APScheduler

## 快速开始

### 1. 环境准备

需要 Python 3.9+

```bash
# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行服务

```bash
python app/main.py
# 或
uvicorn app.main:app --reload
```

服务启动后访问: `http://127.0.0.1:8000/docs` 查看 Swagger 文档。

## API 接口

- `GET /api/v1/scan`: 获取最新市场扫描结果。
- `GET /api/v1/kline?symbol=BTC/USDT&interval=15m`: 获取 K 线数据。

## 目录结构

```text
app/
├── core/           # 核心逻辑 (Fetcher, Computer, Analyzer)
├── services/       # 业务服务 (Scanner)
├── main.py         # 入口与路由
└── config.py       # 配置定义
```
