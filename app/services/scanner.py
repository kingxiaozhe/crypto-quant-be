import asyncio
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.fetcher import BinanceFetcher
from app.core.computer import TechnicalAnalysis
from app.core.analyzer import SqueezeAnalyzer
from app.config import settings

# 全局系统状态
GLOBAL_SYSTEM_STATE = {
    "server_status": "ok",      # ok, warning, error
    "server_time": 0,           # 当前服务器时间
    "data_updated_at": 0,       # 数据最后更新时间戳
    "scan_count": 0,            # 最近一次扫描的币种数量
    "results": []               # 扫描结果列表
}

class ScannerService:
    """
    扫描调度服务 (增强版)
    支持多周期、熔断机制、丰富数据结构
    """
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.analyzer = SqueezeAnalyzer()
        
        # 熔断计数器
        self.fail_count = 0
        self.MAX_FAILURES = 5
        
        # 扫描周期配置
        self.TIMEFRAMES = ['15m', '4h']

    async def scan_job(self):
        """
        核心扫描任务
        """
        # 熔断检查
        if self.fail_count >= self.MAX_FAILURES:
            print(f"[{time.strftime('%H:%M:%S')}] System in MELTDOWN mode. Skipping scan.")
            GLOBAL_SYSTEM_STATE["server_status"] = "error"
            return

        print(f"[{time.strftime('%H:%M:%S')}] Starting full market scan...")
        fetcher = BinanceFetcher()
        
        # 临时结果存储
        new_results = []
        
        try:
            # 1. 获取 Top 活跃币种 (带基础行情)
            top_coins = await fetcher.get_top_coins(limit=100)
            
            for coin in top_coins:
                symbol = coin['symbol']
                
                # 构建基础数据结构
                coin_data = {
                    "symbol": symbol,
                    "price": coin['close'],
                    "change_24h": coin['change_24h'],
                    "volume": coin['quote_volume'],
                    "signals": {} # 存放各周期的信号
                }
                
                has_valid_signal = False
                
                # 2. 遍历多周期 (15m, 4h)
                for tf in self.TIMEFRAMES:
                    # 获取 K线
                    df = await fetcher.get_klines(symbol, tf)
                    
                    # 严格过滤：K线不足 500 根直接跳过该周期
                    if df.empty or len(df) < settings.KLINE_LIMIT:
                        continue
                        
                    # 计算技术指标
                    df = TechnicalAnalysis.add_indicators(df)
                    
                    # 策略分析
                    analysis = self.analyzer.analyze(df, symbol)
                    
                    # 存入信号结构
                    coin_data["signals"][tf] = {
                        "status": analysis["status"].value,
                        "density": analysis["density"],
                        "breakout_price": analysis["close_price"] if analysis["status"].value == "BREAKOUT" else None
                    }
                    
                    has_valid_signal = True
                
                # 只有当至少有一个周期的有效数据时，才加入结果集
                if has_valid_signal:
                    new_results.append(coin_data)
                    # 简单日志抽样
                    status_15m = coin_data["signals"].get("15m", {}).get("status", "N/A")
                    if status_15m != "WAITING":
                         print(f"Found Signal: {symbol} [15m] -> {status_15m}")
            
            # 3. 更新全局状态 (原子操作)
            GLOBAL_SYSTEM_STATE["results"] = new_results
            GLOBAL_SYSTEM_STATE["scan_count"] = len(new_results)
            GLOBAL_SYSTEM_STATE["data_updated_at"] = int(time.time())
            GLOBAL_SYSTEM_STATE["server_status"] = "ok"
            GLOBAL_SYSTEM_STATE["server_time"] = int(time.time())
            
            # 重置熔断计数
            self.fail_count = 0
            print(f"[{time.strftime('%H:%M:%S')}] Scan finished. Updated {len(new_results)} coins.")
                
        except Exception as e:
            self.fail_count += 1
            print(f"Scan job failed ({self.fail_count}/{self.MAX_FAILURES}): {e}")
            if self.fail_count >= self.MAX_FAILURES:
                GLOBAL_SYSTEM_STATE["server_status"] = "error"
        finally:
            await fetcher.close()

    def start(self):
        """启动调度器"""
        self.scheduler.add_job(self.scan_job, 'interval', seconds=60)
        self.scheduler.start()
        print("Scanner scheduler started.")
