"""
株価・FXのパターンマッチングモジュール
"""

import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from typing import List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class CandlePatternMatcher:
    """
    ローソク足パターンのマッチングを行うクラス
    """
    
    def __init__(self, df: pd.DataFrame, ohlc_cols: dict = None):
        """
        Parameters:
        -----------
        df : DataFrame
            株価データ (index: datetime, columns: open, high, low, close, volume)
        ohlc_cols : dict
            OHLCカラム名の辞書 {'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'volume': 'volume'}
        """
        self.df = df.copy()
        
        # デフォルトのカラム名
        if ohlc_cols is None:
            self.ohlc_cols = {
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
        else:
            self.ohlc_cols = ohlc_cols
            
        # インデックスがdatetimeか確認
        if not isinstance(self.df.index, pd.DatetimeIndex):
            raise ValueError("DataFrameのindexはDatetimeIndexである必要があります")
    
    def normalize_window(self, window_df: pd.DataFrame, base_close: float = None) -> pd.DataFrame:
        """
        ウィンドウ内のデータを正規化
        
        Parameters:
        -----------
        window_df : DataFrame
            正規化対象のウィンドウデータ
        base_close : float
            基準となる終値（Noneの場合は最後の終値を使用）
        
        Returns:
        --------
        normalized_df : DataFrame
            正規化されたデータ
        """
        normalized_df = window_df.copy()
        
        # 基準となる終値を設定
        if base_close is None:
            base_close = window_df[self.ohlc_cols['close']].iloc[-1]
        
        # 価格データの正規化（基準終値からの変化率）
        for col in ['open', 'high', 'low', 'close']:
            col_name = self.ohlc_cols[col]
            normalized_df[f'{col}_norm'] = (window_df[col_name] - base_close) / base_close
        
        # 出来高の正規化
        base_volume = window_df[self.ohlc_cols['volume']].iloc[-1]
        if base_volume > 0:
            normalized_df['volume_norm'] = (window_df[self.ohlc_cols['volume']] - base_volume) / base_volume
        else:
            normalized_df['volume_norm'] = 0
            
        return normalized_df
    
    def min_max_normalize(self, window_df: pd.DataFrame) -> pd.DataFrame:
        """
        Min-Max正規化（0-1の範囲）
        
        Parameters:
        -----------
        window_df : DataFrame
            正規化対象のウィンドウデータ
        
        Returns:
        --------
        normalized_df : DataFrame
            正規化されたデータ
        """
        normalized_df = window_df.copy()
        
        for col in ['open', 'high', 'low', 'close']:
            col_name = self.ohlc_cols[col]
            min_val = window_df[col_name].min()
            max_val = window_df[col_name].max()
            
            if max_val != min_val:
                normalized_df[f'{col}_minmax'] = (window_df[col_name] - min_val) / (max_val - min_val)
            else:
                normalized_df[f'{col}_minmax'] = 0.5
        
        # 出来高の正規化
        vol_col = self.ohlc_cols['volume']
        min_vol = window_df[vol_col].min()
        max_vol = window_df[vol_col].max()
        
        if max_vol != min_vol:
            normalized_df['volume_minmax'] = (window_df[vol_col] - min_vol) / (max_vol - min_vol)
        else:
            normalized_df['volume_minmax'] = 0.5
            
        return normalized_df
    
    def calculate_pattern_similarity(
        self, 
        target_norm: pd.DataFrame, 
        comparison_norm: pd.DataFrame,
        method: str = 'correlation',
        weights: dict = None
    ) -> float:
        """
        2つの正規化されたパターンの類似度を計算
        
        Parameters:
        -----------
        target_norm : DataFrame
            対象パターン（正規化済み）
        comparison_norm : DataFrame
            比較パターン（正規化済み）
        method : str
            類似度計算方法 ('correlation', 'euclidean', 'weighted')
        weights : dict
            重み付け {'close': 0.5, 'volume': 0.2, 'high': 0.15, 'low': 0.15}
        
        Returns:
        --------
        similarity : float
            類似度スコア
        """
        if len(target_norm) != len(comparison_norm):
            return 0.0
        
        if weights is None:
            weights = {
                'close': 0.5,
                'open': 0.2,
                'high': 0.15,
                'low': 0.15
            }
        
        if method == 'correlation':
            # 終値ベースの相関係数
            try:
                corr, _ = pearsonr(
                    target_norm['close_norm'].values,
                    comparison_norm['close_norm'].values
                )
                return corr if not np.isnan(corr) else 0.0
            except:
                return 0.0
                
        elif method == 'weighted':
            # 重み付き相関係数
            total_similarity = 0.0
            total_weight = 0.0
            
            for col, weight in weights.items():
                try:
                    corr, _ = pearsonr(
                        target_norm[f'{col}_norm'].values,
                        comparison_norm[f'{col}_norm'].values
                    )
                    if not np.isnan(corr):
                        total_similarity += corr * weight
                        total_weight += weight
                except:
                    continue
            
            return total_similarity / total_weight if total_weight > 0 else 0.0
            
        elif method == 'euclidean':
            # ユークリッド距離ベース（Min-Max正規化使用）
            distances = []
            for col in ['close', 'open', 'high', 'low']:
                norm_col = f'{col}_minmax'
                if norm_col in target_norm.columns and norm_col in comparison_norm.columns:
                    dist = np.sqrt(np.mean((
                        target_norm[norm_col].values - 
                        comparison_norm[norm_col].values
                    ) ** 2))
                    distances.append(dist)
            
            avg_distance = np.mean(distances) if distances else 1.0
            # 距離を類似度に変換（0-1、1が最も類似）
            return 1 / (1 + avg_distance)
        
        return 0.0
    
    def find_similar_patterns(
        self,
        target_end_index: int = -1,
        window_size: int = 10,
        lookahead: int = 10,
        top_n: int = 10,
        min_similarity: float = 0.6,
        method: str = 'correlation',
        normalize_method: str = 'relative',
        exclude_recent_days: int = 0
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        類似パターンを検索
        
        Parameters:
        -----------
        target_end_index : int
            対象パターンの終了インデックス（-1で最新）
        window_size : int
            パターンのウィンドウサイズ（日数/本数）
        lookahead : int
            パターン後の予測期間（日数/本数）
        top_n : int
            返す類似パターン数
        min_similarity : float
            最小類似度閾値
        method : str
            類似度計算方法
        normalize_method : str
            正規化方法 ('relative', 'minmax')
        exclude_recent_days : int
            検索から除外する直近のデータ数
        
        Returns:
        --------
        results_df : DataFrame
            類似パターンの結果
        target_data : DataFrame
            対象パターンのデータ
        """
        # 対象パターンの取得
        if target_end_index < 0:
            target_end_index = len(self.df) + target_end_index
        
        target_start = max(0, target_end_index - window_size + 1)
        target_window = self.df.iloc[target_start:target_end_index + 1]
        
        if len(target_window) < window_size:
            raise ValueError(f"対象パターンのデータが不足: {len(target_window)}/{window_size}")
        
        # 対象パターンの正規化
        if normalize_method == 'relative':
            target_norm = self.normalize_window(target_window)
        else:
            target_norm = self.min_max_normalize(target_window)
        
        # 全期間でスライディングウィンドウ検索
        results = []
        search_end = len(self.df) - lookahead - exclude_recent_days
        
        for i in range(window_size - 1, search_end):
            # 対象パターンと重複する期間をスキップ
            if abs(i - target_end_index) < window_size:
                continue
            
            # 比較ウィンドウの取得
            comp_start = i - window_size + 1
            comp_window = self.df.iloc[comp_start:i + 1]
            
            # 正規化
            if normalize_method == 'relative':
                comp_norm = self.normalize_window(comp_window)
            else:
                comp_norm = self.min_max_normalize(comp_window)
            
            # 類似度計算
            similarity = self.calculate_pattern_similarity(
                target_norm, comp_norm, method=method
            )
            
            if similarity >= min_similarity:
                # その後の動きを取得
                future_start = i + 1
                future_end = min(i + lookahead + 1, len(self.df))
                future_data = self.df.iloc[future_start:future_end]
                
                if len(future_data) == lookahead:
                    # リターン計算
                    start_price = comp_window[self.ohlc_cols['close']].iloc[-1]
                    end_price = future_data[self.ohlc_cols['close']].iloc[-1]
                    future_return = (end_price - start_price) / start_price * 100
                    
                    # 最高値・最低値の変化
                    max_price = future_data[self.ohlc_cols['high']].max()
                    min_price = future_data[self.ohlc_cols['low']].min()
                    max_return = (max_price - start_price) / start_price * 100
                    min_return = (min_price - start_price) / start_price * 100
                    
                    results.append({
                        'start_date': comp_window.index[0],
                        'end_date': comp_window.index[-1],
                        'similarity': similarity,
                        'future_return_%': future_return,
                        'max_return_%': max_return,
                        'min_return_%': min_return,
                        'pattern_data': comp_window,
                        'future_data': future_data
                    })
        
        # 結果をDataFrameに変換
        if results:
            results_df = pd.DataFrame([
                {k: v for k, v in r.items() if k not in ['pattern_data', 'future_data']}
                for r in results
            ])
            results_df = results_df.sort_values('similarity', ascending=False).head(top_n)
            
            # pattern_dataとfuture_dataを追加
            for idx, row_idx in enumerate(results_df.index):
                results_df.at[row_idx, 'pattern_data'] = results[row_idx]['pattern_data']
                results_df.at[row_idx, 'future_data'] = results[row_idx]['future_data']
        else:
            results_df = pd.DataFrame()
        
        return results_df, target_window


def calculate_statistics(similar_patterns_df: pd.DataFrame) -> dict:
    """
    類似パターン後のリターン統計を計算
    
    Parameters:
    -----------
    similar_patterns_df : DataFrame
        find_similar_patternsの結果
    
    Returns:
    --------
    stats : dict
        統計情報
    """
    if len(similar_patterns_df) == 0:
        return {}
    
    returns = similar_patterns_df['future_return_%']
    
    stats = {
        'count': len(returns),
        'mean_return': returns.mean(),
        'median_return': returns.median(),
        'std_return': returns.std(),
        'max_return': returns.max(),
        'min_return': returns.min(),
        'positive_rate': (returns > 0).sum() / len(returns) * 100,
        'avg_max_return': similar_patterns_df['max_return_%'].mean(),
        'avg_min_return': similar_patterns_df['min_return_%'].mean()
    }
    
    return stats
