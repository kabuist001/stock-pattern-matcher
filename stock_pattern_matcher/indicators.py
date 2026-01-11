"""
テクニカル指標計算モジュール

移動平均、RSI、MACDなどのテクニカル指標を計算
"""

import pandas as pd
import numpy as np
from typing import Optional


class TechnicalIndicators:
    """
    テクニカル指標を計算するクラス
    """
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """
        単純移動平均 (Simple Moving Average)
        
        Parameters:
        -----------
        data : Series
            価格データ
        period : int
            期間
        
        Returns:
        --------
        sma : Series
            移動平均
        """
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """
        指数移動平均 (Exponential Moving Average)
        
        Parameters:
        -----------
        data : Series
            価格データ
        period : int
            期間
        
        Returns:
        --------
        ema : Series
            指数移動平均
        """
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        RSI (Relative Strength Index)
        
        Parameters:
        -----------
        data : Series
            価格データ
        period : int
            期間（デフォルト: 14）
        
        Returns:
        --------
        rsi : Series
            RSI値
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> tuple:
        """
        MACD (Moving Average Convergence Divergence)
        
        Parameters:
        -----------
        data : Series
            価格データ
        fast_period : int
            短期EMAの期間
        slow_period : int
            長期EMAの期間
        signal_period : int
            シグナル線の期間
        
        Returns:
        --------
        macd : Series
            MACDライン
        signal : Series
            シグナルライン
        histogram : Series
            ヒストグラム
        """
        ema_fast = TechnicalIndicators.ema(data, fast_period)
        ema_slow = TechnicalIndicators.ema(data, slow_period)
        
        macd = ema_fast - ema_slow
        signal = TechnicalIndicators.ema(macd, signal_period)
        histogram = macd - signal
        
        return macd, signal, histogram
    
    @staticmethod
    def bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> tuple:
        """
        ボリンジャーバンド
        
        Parameters:
        -----------
        data : Series
            価格データ
        period : int
            期間
        std_dev : float
            標準偏差の倍数
        
        Returns:
        --------
        upper : Series
            上側バンド
        middle : Series
            中央線（移動平均）
        lower : Series
            下側バンド
        """
        middle = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    @staticmethod
    def atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        ATR (Average True Range)
        
        Parameters:
        -----------
        high : Series
            高値
        low : Series
            安値
        close : Series
            終値
        period : int
            期間
        
        Returns:
        --------
        atr : Series
            ATR値
        """
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> tuple:
        """
        ストキャスティクス
        
        Parameters:
        -----------
        high : Series
            高値
        low : Series
            安値
        close : Series
            終値
        k_period : int
            %Kの期間
        d_period : int
            %Dの期間
        
        Returns:
        --------
        k : Series
            %K
        d : Series
            %D
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        
        return k, d
    
    @staticmethod
    def add_all_indicators(
        df: pd.DataFrame,
        ohlc_cols: Optional[dict] = None
    ) -> pd.DataFrame:
        """
        DataFrameに全てのテクニカル指標を追加
        
        Parameters:
        -----------
        df : DataFrame
            OHLCデータ
        ohlc_cols : dict, optional
            カラム名のマッピング
        
        Returns:
        --------
        df_with_indicators : DataFrame
            指標が追加されたデータ
        """
        if ohlc_cols is None:
            ohlc_cols = {
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close'
            }
        
        df_result = df.copy()
        close = df[ohlc_cols['close']]
        high = df[ohlc_cols['high']]
        low = df[ohlc_cols['low']]
        
        # 移動平均
        for period in [5, 25, 75]:
            df_result[f'SMA_{period}'] = TechnicalIndicators.sma(close, period)
            df_result[f'EMA_{period}'] = TechnicalIndicators.ema(close, period)
        
        # RSI
        df_result['RSI_14'] = TechnicalIndicators.rsi(close, 14)
        
        # MACD
        macd, signal, histogram = TechnicalIndicators.macd(close)
        df_result['MACD'] = macd
        df_result['MACD_Signal'] = signal
        df_result['MACD_Histogram'] = histogram
        
        # ボリンジャーバンド
        upper, middle, lower = TechnicalIndicators.bollinger_bands(close)
        df_result['BB_Upper'] = upper
        df_result['BB_Middle'] = middle
        df_result['BB_Lower'] = lower
        
        # ATR
        df_result['ATR_14'] = TechnicalIndicators.atr(high, low, close, 14)
        
        # ストキャスティクス
        k, d = TechnicalIndicators.stochastic(high, low, close)
        df_result['Stoch_K'] = k
        df_result['Stoch_D'] = d
        
        return df_result
