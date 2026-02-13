"""
可視化モジュール
Plotly（インタラクティブ）とMatplotlib（静的）でグラフを生成
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import plotly.graph_objects as go
from datetime import datetime


class Visualizer:
    """グラフ生成クラス"""
    
    def __init__(self, config):
        self.config = config
        self.plotly_theme = config.get('visualization.plotly.theme', 'plotly_white')
        self.plotly_height = config.get('visualization.plotly.height', 600)
        self.plotly_width = config.get('visualization.plotly.width', 1000)
    
    def create_similarity_distribution(self, results_df: pd.DataFrame) -> go.Figure:
        """類似度の分布をヒストグラムで表示"""
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=results_df['similarity'],
            nbinsx=50,
            name='類似度',
            marker_color='rgba(0, 123, 255, 0.7)',
            hovertemplate='類似度: %{x:.3f}<br>件数: %{y}<extra></extra>'
        ))
        
        mean_sim = results_df['similarity'].mean()
        fig.add_vline(
            x=mean_sim,
            line_dash="dash",
            line_color="red",
            annotation_text=f"平均: {mean_sim:.3f}",
            annotation_position="top"
        )
        
        fig.update_layout(
            title='類似度の分布',
            xaxis_title='類似度',
            yaxis_title='頻度',
            template=self.plotly_theme,
            height=self.plotly_height,
            width=self.plotly_width,
            showlegend=False
        )
        return fig
    
    def create_top_matches_by_symbol(self, results_df: pd.DataFrame, top_n: int = 15) -> go.Figure:
        """銘柄別マッチ数の棒グラフ"""
        symbol_counts = results_df['symbol'].value_counts().head(top_n)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=symbol_counts.index,
            x=symbol_counts.values,
            orientation='h',
            marker_color='rgba(0, 123, 255, 0.7)',
            hovertemplate='銘柄: %{y}<br>マッチ数: %{x}<extra></extra>'
        ))
        fig.update_layout(
            title=f'銘柄別マッチ数（Top {top_n}）',
            xaxis_title='マッチ数',
            yaxis_title='銘柄コード',
            template=self.plotly_theme,
            height=self.plotly_height,
            width=self.plotly_width,
            showlegend=False
        )
        return fig
    
    def create_future_return_distribution(self, results_df: pd.DataFrame) -> go.Figure:
        """将来リターンの分布"""
        df_filtered = results_df[results_df['future_return'].notna()].copy()
        if len(df_filtered) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="将来リターンデータがありません",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df_filtered['future_return'] * 100,
            nbinsx=50,
            name='将来リターン',
            marker_color='rgba(40, 167, 69, 0.7)',
            hovertemplate='リターン: %{x:.2f}%<br>件数: %{y}<extra></extra>'
        ))
        fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="0%", annotation_position="top")
        mean_return = df_filtered['future_return'].mean() * 100
        fig.add_vline(x=mean_return, line_dash="dot", line_color="blue", annotation_text=f"平均: {mean_return:.2f}%", annotation_position="bottom")
        fig.update_layout(
            title='将来リターンの分布',
            xaxis_title='リターン (%)',
            yaxis_title='頻度',
            template=self.plotly_theme,
            height=self.plotly_height,
            width=self.plotly_width,
            showlegend=False
        )
        return fig
    
    def create_similarity_vs_return(self, results_df: pd.DataFrame) -> go.Figure:
        """類似度 vs 将来リターンの散布図"""
        df_filtered = results_df[results_df['future_return'].notna()].copy()
        if len(df_filtered) == 0:
            fig = go.Figure()
            fig.add_annotation(text="将来リターンデータがありません", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=20))
            return fig
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_filtered['similarity'],
            y=df_filtered['future_return'] * 100,
            mode='markers',
            marker=dict(size=6, color=df_filtered['future_return'] * 100, colorscale='RdYlGn', showscale=True, colorbar=dict(title="リターン (%)")),
            text=df_filtered['symbol'],
            hovertemplate='銘柄: %{text}<br>類似度: %{x:.3f}<br>リターン: %{y:.2f}%<extra></extra>'
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.update_layout(
            title='類似度 vs 将来リターン',
            xaxis_title='類似度',
            yaxis_title='将来リターン (%)',
            template=self.plotly_theme,
            height=self.plotly_height,
            width=self.plotly_width,
            showlegend=False
        )
        return fig
    
    def create_pattern_heatmap(self, results_df: pd.DataFrame, top_n: int = 20) -> go.Figure:
        """上位マッチのヒートマップ"""
        top_matches = results_df.head(top_n).copy()
        heatmap_data = []
        for _, row in top_matches.iterrows():
            heatmap_data.append({
                'symbol': row['symbol'],
                'similarity': row['similarity'],
                'future_return': row.get('future_return', 0) * 100 if pd.notna(row.get('future_return')) else 0
            })
        df_heatmap = pd.DataFrame(heatmap_data)
        fig = go.Figure()
        fig.add_trace(go.Heatmap(
            z=[df_heatmap['similarity'].values, df_heatmap['future_return'].values],
            x=df_heatmap['symbol'].values,
            y=['類似度', '将来リターン (%)'],
            colorscale='Viridis',
            hovertemplate='銘柄: %{x}<br>指標: %{y}<br>値: %{z:.3f}<extra></extra>'
        ))
        fig.update_layout(
            title=f'上位{top_n}件のパターンマッチ',
            xaxis_title='銘柄コード',
            template=self.plotly_theme,
            height=self.plotly_height,
            width=self.plotly_width
        )
        return fig
    
    def create_candlestick_chart(self, ohlc_df: pd.DataFrame, title: str) -> go.Figure:
        """単体ローソク足チャートを生成"""
        fig = go.Figure(data=[go.Candlestick(
            x=list(range(len(ohlc_df))),
            open=ohlc_df['open'],
            high=ohlc_df['high'],
            low=ohlc_df['low'],
            close=ohlc_df['close'],
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        )])
        y_min = ohlc_df['low'].min()
        y_max = ohlc_df['high'].max()
        y_margin = (y_max - y_min) * 0.05
        fig.update_layout(
            title=title,
            xaxis_title='日数',
            yaxis_title='価格',
            yaxis_range=[y_min - y_margin, y_max + y_margin],
            template=self.plotly_theme,
            height=350,
            width=self.plotly_width,
            xaxis_rangeslider_visible=False,
            showlegend=False
        )
        return fig

    def create_match_detail_charts(
        self,
        results_df: pd.DataFrame,
        symbols_data: Dict,
        target_patterns: Dict,
        top_n_symbols: int = 5,
        top_n_matches: int = 3
    ) -> Dict[str, go.Figure]:
        """銘柄ごとにターゲットと上位マッチのローソク足チャートを生成"""
        charts = {}
        if target_patterns is None or symbols_data is None:
            return charts

        # 銘柄ごとに最高類似度でソートして上位を取得
        if len(results_df) == 0:
            return charts
        best_per_symbol = results_df.groupby('symbol')['similarity'].max().sort_values(ascending=False)
        top_symbols = best_per_symbol.head(top_n_symbols).index.tolist()

        for symbol in top_symbols:
            if symbol not in target_patterns or symbol not in symbols_data:
                continue

            # ターゲットパターンのチャート
            target_df = target_patterns[symbol]
            charts[f'target_{symbol}'] = self.create_candlestick_chart(
                target_df, f'{symbol} - ターゲットパターン（直近{len(target_df)}日）'
            )

            # 上位マッチのチャート
            symbol_matches = results_df[results_df['symbol'] == symbol].head(top_n_matches)
            full_df = symbols_data[symbol]
            window_size = len(target_df)

            for rank, (_, row) in enumerate(symbol_matches.iterrows(), 1):
                match_idx = int(row['match_index'])
                match_df = full_df.iloc[match_idx:match_idx + window_size][['open', 'high', 'low', 'close']]
                if len(match_df) == 0:
                    continue
                similarity = row['similarity']
                future_ret = row.get('future_return')
                ret_text = f' | リターン: {future_ret*100:+.2f}%' if pd.notna(future_ret) else ''
                title = f'{symbol} - マッチ#{rank}（類似度: {similarity:.3f}{ret_text}）'
                charts[f'match_{symbol}_{rank}'] = self.create_candlestick_chart(match_df, title)

        return charts

    def create_all_plots(self, results_df: pd.DataFrame, symbols_data: Dict = None, target_patterns: Dict = None) -> Dict[str, go.Figure]:
        """全てのグラフを生成"""
        plots = {}
        print("📊 グラフを生成中...")
        graph_types = self.config.get('visualization.graphs', ['similarity_distribution', 'top_matches_by_symbol', 'future_return_distribution', 'similarity_vs_return', 'pattern_heatmap'])
        
        if 'similarity_distribution' in graph_types:
            plots['similarity_distribution'] = self.create_similarity_distribution(results_df)
            print("  ✓ 類似度分布")
        if 'top_matches_by_symbol' in graph_types:
            plots['top_matches_by_symbol'] = self.create_top_matches_by_symbol(results_df)
            print("  ✓ 銘柄別マッチ数")
        if 'future_return_distribution' in graph_types:
            plots['future_return_distribution'] = self.create_future_return_distribution(results_df)
            print("  ✓ 将来リターン分布")
        if 'similarity_vs_return' in graph_types:
            plots['similarity_vs_return'] = self.create_similarity_vs_return(results_df)
            print("  ✓ 類似度vsリターン")
        if 'pattern_heatmap' in graph_types:
            plots['pattern_heatmap'] = self.create_pattern_heatmap(results_df)
            print("  ✓ パターンヒートマップ")

        # ローソク足チャート
        if target_patterns and symbols_data:
            candlestick_charts = self.create_match_detail_charts(
                results_df, symbols_data, target_patterns
            )
            plots.update(candlestick_charts)
            print(f"  ✓ ローソク足チャート（{len(candlestick_charts)}個）")

        print(f"✅ {len(plots)}個のグラフを生成しました")
        return plots
    
    def create_summary_stats(self, results_df: pd.DataFrame) -> Dict:
        """サマリー統計を生成"""
        stats = {
            'total_matches': len(results_df),
            'unique_symbols': results_df['symbol'].nunique(),
            'avg_similarity': results_df['similarity'].mean(),
            'max_similarity': results_df['similarity'].max(),
            'min_similarity': results_df['similarity'].min()
        }
        if 'future_return' in results_df.columns:
            returns = results_df['future_return'].dropna()
            if len(returns) > 0:
                stats.update({
                    'avg_return': returns.mean() * 100,
                    'median_return': returns.median() * 100,
                    'positive_returns': (returns > 0).sum(),
                    'negative_returns': (returns < 0).sum(),
                    'win_rate': (returns > 0).sum() / len(returns) * 100
                })
        return stats
