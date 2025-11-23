import asyncio
import ccxt.async_support as ccxt
import pandas as pd
from app.config import settings

class BinanceFetcher:
    """
    币安数据获取器
    直接对接 CCXT，负责获取行情和K线数据
    """
    def __init__(self):
        # 初始化币安交易所，不加载市场详情以加快启动
        self.exchange = ccxt.binance({'enableRateLimit': True})

    async def close(self):
        """关闭连接"""
        await self.exchange.close()

    async def get_top_coins(self, limit: int = 100):
        """
        获取成交额靠前的币种
        1. 获取所有 Tickers
        2. 过滤 USDT 交易对
        3. 排除黑名单
        4. 按成交额排序取前 N
        """
        try:
            tickers = await self.exchange.fetch_tickers()
            
            valid_coins = []
            for symbol, ticker in tickers.items():
                # 基础过滤：必须以 USDT 结尾
                if not symbol.endswith('/USDT'):
                    continue
                
                # 提取基础币种 (例如 BTC/USDT -> BTC)
                base_currency = symbol.split('/')[0]
                
                # 黑名单过滤
                if base_currency in settings.BLACKLIST:
                    continue
                
                # 成交额过滤 (quoteVolume)
                quote_volume = ticker.get('quoteVolume', 0)
                if quote_volume < settings.MIN_VOLUME:
                    continue
                    
                valid_coins.append({
                    'symbol': symbol,
                    'quote_volume': quote_volume,
                    'close': ticker['close'],
                    'change_24h': ticker.get('percentage', 0.0) # 24h 涨跌幅
                })
            
            # 按成交额降序排序
            sorted_coins = sorted(valid_coins, key=lambda x: x['quote_volume'], reverse=True)
            return sorted_coins[:limit]
            
        except Exception as e:
            print(f"Error fetching top coins: {e}")
            return []

    async def get_klines(self, symbol: str, timeframe: str):
        """
        获取K线数据
        返回包含 open, high, low, close, volume 的 DataFrame
        """
        # 防止触发频率限制
        await asyncio.sleep(0.1)
        
        try:
            # 获取 OHLCV 数据: [timestamp, open, high, low, close, volume]
            ohlcv = await self.exchange.fetch_ohlcv(
                symbol, 
                timeframe, 
                limit=settings.KLINE_LIMIT
            )
            
            # 转换为 DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # 转换时间戳
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # 此时只保留 OHLCV 数据列，或者保留 timestamp 作为索引，这里按用户要求主要关注 OHLCV
            # 但通常保留 timestamp 是必须的，这里不做额外删除，直接返回完整 DF
            return df
            
        except Exception as e:
            print(f"Error fetching klines for {symbol}: {e}")
            return pd.DataFrame()
