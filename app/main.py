import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.services.scanner import ScannerService, GLOBAL_SYSTEM_STATE
from app.core.fetcher import BinanceFetcher

app = FastAPI(title="CryptoQuant API")

# 配置 CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
scanner_service = ScannerService()

@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行
    """
    scanner_service.start()
    # 可选：启动时立即在后台运行一次扫描，避免等待60秒
    asyncio.create_task(scanner_service.scan_job())

@app.get("/api/v1/scan")
async def get_scan_results():
    """
    获取最新的全市场扫描结果
    返回符合 V1.0.0 规格书的标准结构
    """
    return {
        "server_status": GLOBAL_SYSTEM_STATE["server_status"],
        "server_time": int(time.time()),
        "data_updated_at": GLOBAL_SYSTEM_STATE["data_updated_at"],
        "config": { 
            "scanned_count": GLOBAL_SYSTEM_STATE["scan_count"] 
        },
        "results": GLOBAL_SYSTEM_STATE["results"]
    }

@app.get("/api/v1/kline")
async def get_kline(symbol: str, interval: str = "15m"):
    """
    获取指定币种的K线数据 (用于前端绘图)
    """
    fetcher = BinanceFetcher()
    try:
        df = await fetcher.get_klines(symbol, interval)
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # 转换为字典列表返回，Pandas Timestamp 需要处理
        # 将 timestamp 转为 int (毫秒) 以便前端图表库使用
        # 假设 df['timestamp'] 已经是 datetime 对象 (在 fetcher 中转换过)
        # 这里为了 json 序列化，将其转回 int timestamp 或者 ISO string
        # 很多前端库喜欢 timestamp 毫秒数
        
        # 在 fetcher.py 中我们做了 pd.to_datetime。这里为了序列化方便，转回 int
        # 或者在 output 中直接输出
        
        result = df.to_dict(orient='records')
        # 这里 records 输出 timestamp 是 Timestamp('...') 对象，FastAPI 默认 json encoder 可能报错
        # 简单处理：手动转换 timestamp 列
        
        data = []
        for _, row in df.iterrows():
            data.append({
                "time": int(row['timestamp'].timestamp() * 1000), # 转回毫秒
                "open": row['open'],
                "high": row['high'],
                "low": row['low'],
                "close": row['close'],
                "volume": row['volume']
            })
            
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await fetcher.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
