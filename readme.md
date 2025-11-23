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

## 部署指南 (Docker)

本项目支持 Docker 一键部署，推荐使用海外服务器 (如新加坡 AWS/DigitalOcean) 以确保连接 Binance 顺畅。

### 1. 首次部署

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash

# 克隆代码
git clone https://github.com/kingxiaozhe/crypto-quant-be.git
cd crypto-quant-be

# 启动服务
docker compose up -d
```

### 2. 更新代码

```bash
# 给脚本执行权限 (仅需一次)
chmod +x deploy.sh

# 一键更新
./deploy.sh
```

### 3. 查看日志

```bash
docker compose logs -f
```

## 目录结构

```text
app/
├── core/           # 核心逻辑 (Fetcher, Computer, Analyzer)
├── services/       # 业务服务 (Scanner)
├── main.py         # 入口与路由
└── config.py       # 配置定义
```
