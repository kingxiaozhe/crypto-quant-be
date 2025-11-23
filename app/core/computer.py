import pandas as pd

class TechnicalAnalysis:
    """
    技术分析计算层
    负责在原始K线数据上添加技术指标
    """
    
    @staticmethod
    def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        添加均线指标 (SMA & EMA)
        直接修改传入的 DataFrame
        """
        # 确保按时间排序 (通常获取时已经是排序的，但在计算指标前再次确认是个好习惯)
        # df = df.sort_values('timestamp') 
        
        # 计算 Simple Moving Average (SMA)
        for period in [20, 60, 120]:
            df[f'ma_{period}'] = df['close'].rolling(window=period).mean()
            
        # 计算 Exponential Moving Average (EMA)
        for period in [20, 60, 120]:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
            
        return df
