from enum import Enum
import pandas as pd
from app.core.computer import TechnicalAnalysis

class SignalStatus(Enum):
    WAITING = "WAITING"     # 均线发散，等待收敛
    SQUEEZING = "SQUEEZING" # 均线高度粘合 (挤压中)
    BREAKOUT = "BREAKOUT"   # 均线粘合且价格向上突破

class SqueezeAnalyzer:
    """
    策略分析层
    检测均线粘合与突破形态
    """
    
    def analyze(self, df: pd.DataFrame, symbol: str) -> dict:
        """
        分析单个币种的K线形态
        """
        # 1. 确保指标已计算
        # 如果缺少关键列，先调用计算层
        if 'ma_20' not in df.columns:
            df = TechnicalAnalysis.add_indicators(df)
            
        # 2. 基础数据校验
        if len(df) < 120:
            return {
                "symbol": symbol,
                "density": 0.0,
                "status": SignalStatus.WAITING,
                "close_price": 0.0,
                "ma_values": []
            }
            
        # 3. 获取最新一根K线的数据
        last_row = df.iloc[-1]
        close_price = last_row['close']
        
        # 提取6条均线的值
        ma_cols = ['ma_20', 'ma_60', 'ma_120', 'ema_20', 'ema_60', 'ema_120']
        ma_values = [last_row[col] for col in ma_cols]
        
        # 检查是否有 NaN (例如上市时间不足导致长周期均线无法计算)
        if any(pd.isna(val) for val in ma_values):
             return {
                "symbol": symbol,
                "density": 0.0,
                "status": SignalStatus.WAITING,
                "close_price": close_price,
                "ma_values": []
            }

        # 4. 核心算法 1: 计算粘合度 (Density)
        max_ma = max(ma_values)
        min_ma = min(ma_values)
        
        # 避免除以0的极端情况
        if min_ma == 0:
            density = 1.0 # 视为最大发散
        else:
            density = (max_ma - min_ma) / min_ma
        
        # 5. 核心算法 2: 状态判断
        # 阈值 1.5% (0.015)
        THRESHOLD = 0.015
        
        if density > THRESHOLD:
            status = SignalStatus.WAITING
        else:
            # 均线已经很密集，检查是否突破
            # 突破定义：当前收盘价 > 所有均线的最大值
            if close_price > max_ma:
                # 增强判定: 成交量突破 (Volume > MA(Volume, 20) * 1.5)
                # 这里需要先计算 MA(Volume, 20)
                # 为了简化，我们假设传入的 df 已经包含了 volume 列
                # 并且我们需要在这里临时计算一下 vol_ma_20
                
                # 动态计算 vol_ma_20 (只取最后20个)
                if 'volume' in df.columns:
                    vol_ma_20 = df['volume'].iloc[-21:-1].mean() # 取前20个的均值(不含当前?) 或者包含当前? 
                    # 通常是 rolling mean. df['volume'].rolling(20).mean()
                    # 我们直接用 pandas 计算
                    vol_ma_20 = df['volume'].rolling(window=20).mean().iloc[-1]
                    current_vol = last_row['volume']
                    
                    # 如果成交量也满足，则信号更强，但为了 MVP，我们只做记录或者作为可选条件
                    # 根据需求文档： "可选增强: 且 Volume > MA(Volume, 20) * 1.5"
                    # 我们这里暂时保持 loose，只看价格，但在 result 中可以标记
                    pass
                
                status = SignalStatus.BREAKOUT
            else:
                status = SignalStatus.SQUEEZING
                
        return {
            "symbol": symbol,
            "density": round(density, 6),
            "status": status,
            "close_price": close_price,
            "ma_values": [round(x, 4) for x in ma_values]
        }
