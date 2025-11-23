from typing import List

class Settings:
    # 过滤掉的稳定币和非交易型代币
    BLACKLIST: List[str] = ["USDC", "USDP", "TUSD", "FDUSD", "DAI", "WBTC"]
    
    # 最小成交额阈值 (1000万美元)
    MIN_VOLUME: float = 10000000.0
    
    # K线获取数量
    KLINE_LIMIT: int = 500

settings = Settings()
