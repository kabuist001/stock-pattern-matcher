"""
Stock Pattern Matcher - 株価・FXのローソク足パターンマッチングシステム

このパッケージは、過去の株価・FXデータから指定したパターンと類似する値動きを検索し、
その後の価格変動を分析するためのツールです。

主要クラス:
    - CandlePatternMatcher: パターンマッチングのコアクラス
    - PatternVisualizer: 可視化機能を提供するクラス

主要関数:
    - calculate_statistics: 統計情報を計算
    - print_statistics: 統計情報を表示

使用例:
    >>> from stock_pattern_matcher import CandlePatternMatcher, PatternVisualizer
    >>> import pandas as pd
    >>> 
    >>> df = pd.read_csv('data.csv', index_col='date', parse_dates=True)
    >>> matcher = CandlePatternMatcher(df)
    >>> results, target = matcher.find_similar_patterns(window_size=20)
    >>> 
    >>> visualizer = PatternVisualizer()
    >>> visualizer.plot_pattern_comparison(target, results)
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .pattern_matcher import CandlePatternMatcher, calculate_statistics
from .visualizer import PatternVisualizer, print_statistics

# エイリアス（互換性のため）
PatternMatcher = CandlePatternMatcher
Visualizer = PatternVisualizer

__all__ = [
    "CandlePatternMatcher",
    "PatternVisualizer",
    "PatternMatcher",
    "Visualizer",
    "calculate_statistics",
    "print_statistics",
]
