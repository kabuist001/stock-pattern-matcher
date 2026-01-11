"""
ユーティリティ関数モジュール
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def calculate_returns(prices: pd.Series) -> pd.Series:
    """
    リターン（変化率）を計算
    
    Parameters:
    -----------
    prices : Series
        価格データ
    
    Returns:
    --------
    returns : Series
        リターン
    """
    return prices.pct_change()


def calculate_log_returns(prices: pd.Series) -> pd.Series:
    """
    対数リターンを計算
    
    Parameters:
    -----------
    prices : Series
        価格データ
    
    Returns:
    --------
    log_returns : Series
        対数リターン
    """
    return np.log(prices / prices.shift(1))


def calculate_volatility(
    returns: pd.Series,
    window: int = 20,
    annualize: bool = True
) -> pd.Series:
    """
    ボラティリティを計算
    
    Parameters:
    -----------
    returns : Series
        リターンデータ
    window : int
        計算ウィンドウ
    annualize : bool
        年率換算するか
    
    Returns:
    --------
    volatility : Series
        ボラティリティ
    """
    vol = returns.rolling(window=window).std()
    
    if annualize:
        # 日次データの場合、252営業日で年率換算
        vol = vol * np.sqrt(252)
    
    return vol


def detect_outliers(
    data: pd.Series,
    method: str = 'iqr',
    threshold: float = 1.5
) -> pd.Series:
    """
    外れ値を検出
    
    Parameters:
    -----------
    data : Series
        データ
    method : str
        検出方法 ('iqr', 'zscore')
    threshold : float
        閾値
    
    Returns:
    --------
    is_outlier : Series
        外れ値フラグ
    """
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        is_outlier = (data < lower_bound) | (data > upper_bound)
        
    elif method == 'zscore':
        z_scores = np.abs((data - data.mean()) / data.std())
        is_outlier = z_scores > threshold
        
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return is_outlier


def resample_data(
    df: pd.DataFrame,
    freq: str,
    ohlc_cols: Optional[dict] = None
) -> pd.DataFrame:
    """
    データをリサンプリング
    
    Parameters:
    -----------
    df : DataFrame
        元データ
    freq : str
        リサンプリング頻度 ('1H', '1D', '1W', etc.)
    ohlc_cols : dict, optional
        OHLCカラムのマッピング
    
    Returns:
    --------
    df_resampled : DataFrame
        リサンプリング後のデータ
    """
    if ohlc_cols is None:
        ohlc_cols = {
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        }
    
    agg_dict = {
        ohlc_cols['open']: 'first',
        ohlc_cols['high']: 'max',
        ohlc_cols['low']: 'min',
        ohlc_cols['close']: 'last',
    }
    
    if ohlc_cols.get('volume') and ohlc_cols['volume'] in df.columns:
        agg_dict[ohlc_cols['volume']] = 'sum'
    
    df_resampled = df.resample(freq).agg(agg_dict)
    df_resampled = df_resampled.dropna()
    
    return df_resampled


def split_train_test(
    df: pd.DataFrame,
    train_ratio: float = 0.8
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    データを訓練用とテスト用に分割
    
    Parameters:
    -----------
    df : DataFrame
        データ
    train_ratio : float
        訓練データの比率
    
    Returns:
    --------
    train_df : DataFrame
        訓練データ
    test_df : DataFrame
        テストデータ
    """
    split_index = int(len(df) * train_ratio)
    
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]
    
    return train_df, test_df


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods: int = 252
) -> float:
    """
    シャープレシオを計算
    
    Parameters:
    -----------
    returns : Series
        リターンデータ
    risk_free_rate : float
        無リスク金利（年率）
    periods : int
        年間期間数（日次の場合252）
    
    Returns:
    --------
    sharpe_ratio : float
        シャープレシオ
    """
    excess_returns = returns - (risk_free_rate / periods)
    
    if excess_returns.std() == 0:
        return 0.0
    
    sharpe_ratio = np.sqrt(periods) * excess_returns.mean() / excess_returns.std()
    
    return sharpe_ratio


def calculate_max_drawdown(prices: pd.Series) -> Tuple[float, pd.Timestamp, pd.Timestamp]:
    """
    最大ドローダウンを計算
    
    Parameters:
    -----------
    prices : Series
        価格データ
    
    Returns:
    --------
    max_drawdown : float
        最大ドローダウン（%）
    peak_date : Timestamp
        ピーク日
    trough_date : Timestamp
        谷日
    """
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    max_drawdown = drawdown.min()
    trough_date = drawdown.idxmin()
    
    # ピーク日を見つける
    peak_date = cumulative[:trough_date].idxmax()
    
    return max_drawdown * 100, peak_date, trough_date


def format_number(value: float, decimals: int = 2, percentage: bool = False) -> str:
    """
    数値を整形して文字列に変換
    
    Parameters:
    -----------
    value : float
        数値
    decimals : int
        小数点以下の桁数
    percentage : bool
        パーセント表記にするか
    
    Returns:
    --------
    formatted : str
        整形された文字列
    """
    if percentage:
        return f"{value:.{decimals}f}%"
    else:
        return f"{value:,.{decimals}f}"


def is_trading_day(date: pd.Timestamp, country: str = 'JP') -> bool:
    """
    取引日かどうかを判定（簡易版）
    
    Parameters:
    -----------
    date : Timestamp
        日付
    country : str
        国コード
    
    Returns:
    --------
    is_trading : bool
        取引日かどうか
    """
    # 週末は取引なし
    if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # 祝日判定は将来実装
    # TODO: 各国の祝日カレンダーを追加
    
    return True
