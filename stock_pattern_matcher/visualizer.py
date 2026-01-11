"""
ローソク足パターン可視化モジュール
"""

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import numpy as np
from typing import List, Optional
import warnings
warnings.filterwarnings('ignore')


class PatternVisualizer:
    """
    パターンマッチング結果の可視化クラス
    """
    
    def __init__(self, ohlc_cols: dict = None):
        """
        Parameters:
        -----------
        ohlc_cols : dict
            OHLCカラム名の辞書
        """
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
    
    def plot_candlestick(
        self, 
        df: pd.DataFrame, 
        title: str = "Candlestick Chart",
        ma_periods: List[int] = None,
        style: str = 'yahoo',
        figsize: tuple = (12, 6)
    ):
        """
        ローソク足チャートを表示
        
        Parameters:
        -----------
        df : DataFrame
            OHLCデータ
        title : str
            グラフタイトル
        ma_periods : List[int]
            移動平均線の期間リスト
        style : str
            mplfinanceのスタイル
        figsize : tuple
            図のサイズ
        """
        # カラム名をmplfinanceの形式に変換
        plot_df = df.copy()
        plot_df = plot_df.rename(columns={
            self.ohlc_cols['open']: 'Open',
            self.ohlc_cols['high']: 'High',
            self.ohlc_cols['low']: 'Low',
            self.ohlc_cols['close']: 'Close',
            self.ohlc_cols['volume']: 'Volume'
        })
        
        # 移動平均線の追加
        addplot = []
        if ma_periods:
            for period in ma_periods:
                ma = plot_df['Close'].rolling(window=period).mean()
                addplot.append(mpf.make_addplot(ma, width=1.5))
        
        # プロット
        kwargs = {
            'type': 'candle',
            'style': style,
            'title': title,
            'volume': True if 'Volume' in plot_df.columns else False,
            'figsize': figsize,
            'tight_layout': True
        }
        
        if addplot:
            kwargs['addplot'] = addplot
        
        mpf.plot(plot_df, **kwargs)
    
    def plot_pattern_comparison(
        self,
        target_data: pd.DataFrame,
        similar_patterns_df: pd.DataFrame,
        top_n: int = 5,
        figsize: tuple = (15, 10)
    ):
        """
        対象パターンと類似パターンを比較表示（正規化）
        
        Parameters:
        -----------
        target_data : DataFrame
            対象パターンのデータ
        similar_patterns_df : DataFrame
            類似パターンの結果
        top_n : int
            表示する類似パターン数
        figsize : tuple
            図のサイズ
        """
        if len(similar_patterns_df) == 0:
            print("表示する類似パターンがありません")
            return
        
        fig, axes = plt.subplots(2, 1, figsize=figsize)
        
        # 対象パターンの正規化
        target_close = target_data[self.ohlc_cols['close']].values
        target_norm = (target_close - target_close.min()) / (target_close.max() - target_close.min())
        
        # 上段: パターン部分の比較
        ax1 = axes[0]
        x_target = np.arange(len(target_norm))
        ax1.plot(x_target, target_norm, label='Target Pattern', 
                linewidth=3, color='red', marker='o', markersize=8)
        
        # 類似パターンをプロット
        colors = plt.cm.viridis(np.linspace(0, 1, min(top_n, len(similar_patterns_df))))
        
        for idx, (i, row) in enumerate(similar_patterns_df.head(top_n).iterrows()):
            pattern_data = row['pattern_data']
            pattern_close = pattern_data[self.ohlc_cols['close']].values
            pattern_norm = (pattern_close - pattern_close.min()) / (pattern_close.max() - pattern_close.min())
            
            label = f"{row['start_date'].strftime('%Y-%m-%d')} (sim={row['similarity']:.3f})"
            ax1.plot(x_target, pattern_norm, label=label, 
                    alpha=0.6, color=colors[idx], linewidth=2, marker='s')
        
        ax1.set_title('Pattern Comparison (Normalized)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Time Steps', fontsize=12)
        ax1.set_ylabel('Normalized Price', fontsize=12)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # 下段: その後の動き
        ax2 = axes[1]
        
        for idx, (i, row) in enumerate(similar_patterns_df.head(top_n).iterrows()):
            future_data = row['future_data']
            future_close = future_data[self.ohlc_cols['close']].values
            
            # 最初の値を100として正規化
            future_norm = (future_close / future_close[0]) * 100
            x_future = np.arange(len(future_norm))
            
            label = f"{row['start_date'].strftime('%Y-%m-%d')} ({row['future_return_%']:.2f}%)"
            ax2.plot(x_future, future_norm, label=label,
                    alpha=0.7, color=colors[idx], linewidth=2, marker='o')
        
        ax2.axhline(y=100, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        ax2.set_title('Future Price Movements (Index: Start=100)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Days/Periods After Pattern', fontsize=12)
        ax2.set_ylabel('Price Index (Start=100)', fontsize=12)
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_return_distribution(
        self,
        similar_patterns_df: pd.DataFrame,
        bins: int = 20,
        figsize: tuple = (12, 6)
    ):
        """
        リターン分布のヒストグラム表示
        
        Parameters:
        -----------
        similar_patterns_df : DataFrame
            類似パターンの結果
        bins : int
            ヒストグラムのビン数
        figsize : tuple
            図のサイズ
        """
        if len(similar_patterns_df) == 0:
            print("表示するデータがありません")
            return
        
        returns = similar_patterns_df['future_return_%']
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # ヒストグラム
        n, bins_arr, patches = ax.hist(returns, bins=bins, alpha=0.7, 
                                        edgecolor='black', color='skyblue')
        
        # 色分け（プラスは緑、マイナスは赤）
        for i, patch in enumerate(patches):
            if bins_arr[i] >= 0:
                patch.set_facecolor('lightgreen')
            else:
                patch.set_facecolor('lightcoral')
        
        # 統計線
        ax.axvline(returns.mean(), color='red', linestyle='--', 
                  label=f'Mean: {returns.mean():.2f}%', linewidth=2)
        ax.axvline(returns.median(), color='green', linestyle='--', 
                  label=f'Median: {returns.median():.2f}%', linewidth=2)
        ax.axvline(0, color='black', linestyle='-', alpha=0.3, linewidth=1)
        
        ax.set_xlabel('Return (%)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of Future Returns After Similar Patterns', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        # テキスト情報
        positive_rate = (returns > 0).sum() / len(returns) * 100
        text = f'Samples: {len(returns)}\n'
        text += f'Positive: {positive_rate:.1f}%\n'
        text += f'Std: {returns.std():.2f}%'
        
        ax.text(0.02, 0.98, text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.show()
    
    def plot_multiple_candles(
        self,
        similar_patterns_df: pd.DataFrame,
        top_n: int = 6,
        figsize: tuple = (16, 10),
        include_future: bool = True
    ):
        """
        複数の類似パターンをローソク足で表示
        
        Parameters:
        -----------
        similar_patterns_df : DataFrame
            類似パターンの結果
        top_n : int
            表示するパターン数
        figsize : tuple
            図のサイズ
        include_future : bool
            将来データも含めるか
        """
        if len(similar_patterns_df) == 0:
            print("表示するパターンがありません")
            return
        
        n_patterns = min(top_n, len(similar_patterns_df))
        n_cols = 3
        n_rows = (n_patterns + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if n_patterns > 1 else [axes]
        
        for idx, (i, row) in enumerate(similar_patterns_df.head(n_patterns).iterrows()):
            ax = axes[idx]
            
            # データ結合
            if include_future and 'future_data' in row:
                combined_data = pd.concat([row['pattern_data'], row['future_data']])
            else:
                combined_data = row['pattern_data']
            
            # ローソク足の描画（簡易版）
            for j, (date, candle) in enumerate(combined_data.iterrows()):
                open_p = candle[self.ohlc_cols['open']]
                close_p = candle[self.ohlc_cols['close']]
                high_p = candle[self.ohlc_cols['high']]
                low_p = candle[self.ohlc_cols['low']]
                
                # 陽線・陰線の色分け
                color = 'red' if close_p >= open_p else 'blue'
                
                # 実体
                height = abs(close_p - open_p)
                bottom = min(open_p, close_p)
                ax.bar(j, height, bottom=bottom, color=color, alpha=0.7, width=0.8)
                
                # ヒゲ
                ax.plot([j, j], [low_p, high_p], color='black', linewidth=1)
            
            # パターンと将来の境界線
            if include_future:
                pattern_len = len(row['pattern_data'])
                ax.axvline(x=pattern_len - 0.5, color='green', 
                          linestyle='--', linewidth=2, alpha=0.7)
            
            # タイトルと情報
            title = f"{row['start_date'].strftime('%Y-%m-%d')}\n"
            title += f"Sim: {row['similarity']:.3f} | Ret: {row['future_return_%']:.2f}%"
            ax.set_title(title, fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('Time', fontsize=8)
            ax.set_ylabel('Price', fontsize=8)
        
        # 余分な軸を非表示
        for idx in range(n_patterns, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        plt.show()


def print_statistics(stats: dict):
    """
    統計情報を整形して表示
    
    Parameters:
    -----------
    stats : dict
        calculate_statisticsの結果
    """
    if not stats:
        print("統計情報がありません")
        return
    
    print("=" * 70)
    print("類似パターン後のリターン統計分析")
    print("=" * 70)
    print(f"サンプル数:           {stats['count']}")
    print(f"平均リターン:         {stats['mean_return']:.2f}%")
    print(f"中央値リターン:       {stats['median_return']:.2f}%")
    print(f"標準偏差:             {stats['std_return']:.2f}%")
    print(f"最大リターン:         {stats['max_return']:.2f}%")
    print(f"最小リターン:         {stats['min_return']:.2f}%")
    print(f"上昇確率:             {stats['positive_rate']:.1f}%")
    print("-" * 70)
    print(f"平均最高値リターン:   {stats['avg_max_return']:.2f}%")
    print(f"平均最低値リターン:   {stats['avg_min_return']:.2f}%")
    print("=" * 70)
