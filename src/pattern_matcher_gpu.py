"""
GPU対応パターンマッチングモジュール
CuPyを使用してGPUで高速に計算
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Union
from datetime import datetime

# GPU/CPU切り替え
try:
    import cupy as cp
    GPU_AVAILABLE = cp.cuda.is_available()
except ImportError:
    GPU_AVAILABLE = False
    cp = None


class PatternMatcher:
    """GPU対応パターンマッチャー"""
    
    def __init__(
        self,
        window_size: int = 20,
        lookahead: int = 10,
        top_n: int = 15,
        min_similarity: float = 0.7,
        method: str = 'correlation',
        use_gpu: bool = True,
        normalize_method: str = 'minmax'
    ):
        """
        Args:
            window_size: パターンの長さ（日数）
            lookahead: 将来予測の期間（日数）
            top_n: 返す上位マッチ数
            min_similarity: 最小類似度
            method: 類似度計算方法 ('correlation', 'euclidean', 'weighted')
            use_gpu: GPU使用フラグ
            normalize_method: 正規化方法 ('minmax', 'zscore', 'robust')
        """
        self.window_size = window_size
        self.lookahead = lookahead
        self.top_n = top_n
        self.min_similarity = min_similarity
        self.method = method
        self.normalize_method = normalize_method
        
        # GPU使用の決定
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.xp = cp if self.use_gpu else np
        
        if use_gpu and not GPU_AVAILABLE:
            print("⚠️  GPU requested but not available. Using CPU instead.")
        elif self.use_gpu:
            print(f"✅ Using GPU: {cp.cuda.Device().name}")
        else:
            print("📊 Using CPU")
    
    def normalize_pattern(self, pattern: np.ndarray) -> np.ndarray:
        """
        パターンを正規化
        
        Args:
            pattern: 正規化するパターン
            
        Returns:
            正規化されたパターン
        """
        if self.normalize_method == 'minmax':
            # Min-Max正規化 [0, 1]
            min_val = pattern.min(axis=0, keepdims=True)
            max_val = pattern.max(axis=0, keepdims=True)
            return (pattern - min_val) / (max_val - min_val + 1e-8)
        
        elif self.normalize_method == 'zscore':
            # Z-score正規化
            mean = pattern.mean(axis=0, keepdims=True)
            std = pattern.std(axis=0, keepdims=True)
            return (pattern - mean) / (std + 1e-8)
        
        elif self.normalize_method == 'robust':
            # Robust正規化（中央値とIQR）
            median = np.median(pattern, axis=0, keepdims=True)
            q75, q25 = np.percentile(pattern, [75, 25], axis=0, keepdims=True)
            iqr = q75 - q25
            return (pattern - median) / (iqr + 1e-8)
        
        return pattern
    
    def calculate_similarity(
        self, 
        pattern1: np.ndarray, 
        pattern2: np.ndarray
    ) -> float:
        """
        2つのパターン間の類似度を計算
        
        Args:
            pattern1: パターン1
            pattern2: パターン2
            
        Returns:
            類似度スコア
        """
        if self.use_gpu:
            pattern1_gpu = self.xp.array(pattern1)
            pattern2_gpu = self.xp.array(pattern2)
            
            if self.method == 'correlation':
                # 相関係数
                corr = self._correlation_gpu(pattern1_gpu, pattern2_gpu)
                return float(corr.get())
            
            elif self.method == 'euclidean':
                # ユークリッド距離（類似度に変換）
                dist = self.xp.linalg.norm(pattern1_gpu - pattern2_gpu)
                similarity = 1 / (1 + float(dist.get()))
                return similarity
            
            elif self.method == 'weighted':
                # 加重類似度（最近のデータに重み）
                weights = self.xp.linspace(0.5, 1.0, len(pattern1))
                weighted_diff = self.xp.sum(weights[:, None] * (pattern1_gpu - pattern2_gpu) ** 2)
                similarity = 1 / (1 + float(weighted_diff.get()))
                return similarity
        
        else:
            # CPU実装
            if self.method == 'correlation':
                corr_matrix = np.corrcoef(pattern1.flatten(), pattern2.flatten())
                return corr_matrix[0, 1]
            
            elif self.method == 'euclidean':
                dist = np.linalg.norm(pattern1 - pattern2)
                return 1 / (1 + dist)
            
            elif self.method == 'weighted':
                weights = np.linspace(0.5, 1.0, len(pattern1))
                weighted_diff = np.sum(weights[:, None] * (pattern1 - pattern2) ** 2)
                return 1 / (1 + weighted_diff)
        
        return 0.0
    
    def _correlation_gpu(self, x: 'cp.ndarray', y: 'cp.ndarray') -> 'cp.ndarray':
        """GPU上で相関係数を計算"""
        x_flat = x.flatten()
        y_flat = y.flatten()
        
        # 平均を引く
        x_centered = x_flat - self.xp.mean(x_flat)
        y_centered = y_flat - self.xp.mean(y_flat)
        
        # 相関係数
        numerator = self.xp.sum(x_centered * y_centered)
        denominator = self.xp.sqrt(self.xp.sum(x_centered ** 2) * self.xp.sum(y_centered ** 2))
        
        return numerator / (denominator + 1e-8)
    
    def find_similar_patterns(
        self,
        data: pd.DataFrame,
        target_pattern: np.ndarray,
        symbol: str = None
    ) -> List[Dict]:
        """
        類似パターンを検索
        
        Args:
            data: 株価データのDataFrame
            target_pattern: 検索するターゲットパターン
            symbol: 銘柄コード（オプション）
            
        Returns:
            マッチ結果のリスト
        """
        # ターゲットパターンを正規化
        target_normalized = self.normalize_pattern(target_pattern)
        
        results = []
        ohlc_cols = ['open', 'high', 'low', 'close']
        
        # スライディングウィンドウでパターンを抽出
        for i in range(len(data) - self.window_size - self.lookahead + 1):
            window_data = data.iloc[i:i + self.window_size][ohlc_cols].values
            
            # 正規化
            window_normalized = self.normalize_pattern(window_data)
            
            # 類似度計算
            similarity = self.calculate_similarity(target_normalized, window_normalized)
            
            if similarity >= self.min_similarity:
                # 将来のリターンを計算
                future_data = data.iloc[i + self.window_size:i + self.window_size + self.lookahead]
                
                if len(future_data) > 0:
                    start_price = data.iloc[i + self.window_size - 1]['close']
                    end_price = future_data['close'].iloc[-1]
                    future_return = (end_price - start_price) / start_price
                else:
                    future_return = None
                
                results.append({
                    'symbol': symbol if symbol else data['symbol'].iloc[0],
                    'similarity': similarity,
                    'start_date': data.index[i].strftime('%Y-%m-%d'),
                    'end_date': data.index[i + self.window_size - 1].strftime('%Y-%m-%d'),
                    'start_price': float(data.iloc[i]['close']),
                    'end_price': float(data.iloc[i + self.window_size - 1]['close']),
                    'future_return': float(future_return) if future_return is not None else None,
                    'match_index': i
                })
        
        # 類似度でソート
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:self.top_n]
    
    def analyze_all_symbols(
        self,
        symbols_data: Dict[str, pd.DataFrame],
        progress_callback: Optional[callable] = None
    ) -> pd.DataFrame:
        """
        全銘柄のパターンマッチング分析
        
        Args:
            symbols_data: 銘柄データの辞書
            progress_callback: 進捗コールバック関数
            
        Returns:
            結果のDataFrame
        """
        all_results = []
        total_symbols = len(symbols_data)
        
        print(f"🔍 Analyzing {total_symbols} symbols...")
        
        for idx, (symbol, df) in enumerate(symbols_data.items(), 1):
            try:
                # データが十分にあるかチェック
                if len(df) < self.window_size + self.lookahead:
                    continue
                
                # 最新のパターンを抽出
                target_pattern = df.iloc[-self.window_size:][['open', 'high', 'low', 'close']].values
                
                # パターンマッチング
                results = self.find_similar_patterns(df, target_pattern, symbol)
                all_results.extend(results)
                
                # 進捗表示
                if progress_callback:
                    progress_callback(idx, total_symbols, symbol)
                elif idx % 10 == 0:
                    print(f"  Progress: {idx}/{total_symbols} ({idx/total_symbols*100:.1f}%)")
                
            except Exception as e:
                print(f"⚠️  Error processing {symbol}: {e}")
                continue
        
        if all_results:
            results_df = pd.DataFrame(all_results)
            results_df = results_df.sort_values('similarity', ascending=False)
            print(f"✅ Found {len(results_df)} pattern matches")
            return results_df
        else:
            print("❌ No pattern matches found")
            return pd.DataFrame()
    
    def get_stats(self) -> Dict:
        """分析統計情報を取得"""
        return {
            'window_size': self.window_size,
            'lookahead': self.lookahead,
            'top_n': self.top_n,
            'min_similarity': self.min_similarity,
            'method': self.method,
            'use_gpu': self.use_gpu,
            'gpu_available': GPU_AVAILABLE,
            'normalize_method': self.normalize_method
        }
