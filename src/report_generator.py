"""
HTMLレポート生成モジュール
分析結果とグラフを含む自己完結型HTMLレポートを生成
"""

import pandas as pd
from typing import Dict
from datetime import datetime
import plotly.graph_objects as go


class ReportGenerator:
    """HTMLレポート生成クラス"""
    
    def __init__(self, config):
        self.config = config
        self.title = config.get('report.title', 'Stock Pattern Analysis Report')
        self.author = config.get('report.author', 'Stock Analysis System')
        self.max_results = config.get('report.max_results_display', 50)
    
    def generate(self, results_df: pd.DataFrame, plots: Dict[str, go.Figure], stats: Dict = None, metadata: Dict = None, symbols_data: Dict = None, target_patterns: Dict = None) -> str:
        """HTMLレポートを生成"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 統計グラフとローソク足チャートを分離
        stat_plots = {}
        candlestick_plots = {}
        for name, fig in plots.items():
            if name.startswith('target_') or name.startswith('match_'):
                candlestick_plots[name] = fig
            else:
                stat_plots[name] = fig

        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>{self._get_css()}</style>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
</head>
<body>
    <div class="container">
        <header><h1>{self.title}</h1><p class="meta">Generated: {timestamp} | Author: {self.author}</p></header>
        <section class="summary"><h2>📊 分析サマリー</h2>{self._generate_summary_html(results_df, stats, metadata)}</section>
        <section class="graphs"><h2>📈 グラフ</h2>{self._generate_graphs_html(stat_plots)}</section>
        <section class="candlestick"><h2>🕯️ パターン詳細（ローソク足）</h2>{self._generate_candlestick_section_html(candlestick_plots)}</section>
        <section class="results"><h2>📋 上位マッチ結果（Top {self.max_results}）</h2>{self._generate_results_table_html(results_df)}</section>
        <footer><p>Stock Pattern Matcher - Powered by Claude AI & Google Colab</p><p>Generated at {timestamp}</p></footer>
    </div>
</body>
</html>"""
        return html
    
    def _get_css(self) -> str:
        """CSSスタイルを返す"""
        return """*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px;color:#333}.container{max-width:1400px;margin:0 auto;background:white;border-radius:10px;box-shadow:0 10px 40px rgba(0,0,0,0.1);overflow:hidden}header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:40px;text-align:center}header h1{font-size:2.5em;margin-bottom:10px}.meta{font-size:0.9em;opacity:0.9}section{padding:40px;border-bottom:1px solid #eee}section:last-of-type{border-bottom:none}h2{color:#667eea;margin-bottom:20px;font-size:1.8em}.summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-top:20px}.stat-card{background:#f8f9fa;padding:20px;border-radius:8px;border-left:4px solid #667eea}.stat-card h3{font-size:0.9em;color:#666;margin-bottom:10px}.stat-card .value{font-size:2em;font-weight:bold;color:#333}.stat-card .unit{font-size:0.8em;color:#999}.graph-container{margin-bottom:40px;background:#f8f9fa;padding:20px;border-radius:8px}.graph-container h3{color:#333;margin-bottom:15px}table{width:100%;border-collapse:collapse;margin-top:20px;font-size:0.9em}thead{background:#667eea;color:white}th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd}tbody tr:hover{background:#f8f9fa}.positive{color:#28a745;font-weight:bold}.negative{color:#dc3545;font-weight:bold}footer{background:#f8f9fa;padding:30px;text-align:center;color:#666;font-size:0.9em}.badge{display:inline-block;padding:4px 8px;border-radius:4px;font-size:0.85em;font-weight:bold}.badge-high{background:#d4edda;color:#155724}.badge-medium{background:#fff3cd;color:#856404}.badge-low{background:#f8d7da;color:#721c24}.symbol-pattern-group{margin-bottom:40px;padding:20px;background:#f0f2f5;border-radius:8px}.symbol-pattern-group h3{color:#333;font-size:1.4em;margin-bottom:15px;padding-bottom:10px;border-bottom:2px solid #667eea}"""
    
    def _generate_summary_html(self, results_df: pd.DataFrame, stats: Dict = None, metadata: Dict = None) -> str:
        """サマリーHTMLを生成"""
        total_matches = len(results_df)
        unique_symbols = results_df['symbol'].nunique()
        avg_similarity = results_df['similarity'].mean()
        returns = results_df['future_return'].dropna()
        avg_return = returns.mean() * 100 if len(returns) > 0 else 0
        win_rate = (returns > 0).sum() / len(returns) * 100 if len(returns) > 0 else 0
        
        return f"""<div class="summary-grid">
            <div class="stat-card"><h3>総マッチ数</h3><div class="value">{total_matches:,}</div><div class="unit">件</div></div>
            <div class="stat-card"><h3>分析銘柄数</h3><div class="value">{unique_symbols:,}</div><div class="unit">銘柄</div></div>
            <div class="stat-card"><h3>平均類似度</h3><div class="value">{avg_similarity:.3f}</div></div>
            <div class="stat-card"><h3>平均リターン</h3><div class="value {'positive' if avg_return > 0 else 'negative'}">{avg_return:+.2f}%</div></div>
            <div class="stat-card"><h3>勝率</h3><div class="value">{win_rate:.1f}%</div><div class="unit">({(returns > 0).sum()}/{len(returns)})</div></div>
        </div>"""
    
    def _generate_graphs_html(self, plots: Dict[str, go.Figure]) -> str:
        """グラフHTMLを生成"""
        html = ""
        graph_titles = {'similarity_distribution': '類似度の分布', 'top_matches_by_symbol': '銘柄別マッチ数', 'future_return_distribution': '将来リターンの分布', 'similarity_vs_return': '類似度 vs 将来リターン', 'pattern_heatmap': 'パターンヒートマップ'}
        for graph_name, fig in plots.items():
            title = graph_titles.get(graph_name, graph_name)
            graph_html = fig.to_html(include_plotlyjs=False, div_id=f"graph_{graph_name}")
            html += f'<div class="graph-container"><h3>{title}</h3>{graph_html}</div>'
        return html
    
    def _generate_candlestick_section_html(self, candlestick_plots: Dict[str, go.Figure]) -> str:
        """ローソク足チャートセクションのHTMLを生成"""
        if not candlestick_plots:
            return '<p>ローソク足チャートデータがありません</p>'

        html = ''
        # target_SYMBOL と match_SYMBOL_N をグループ化
        symbols = []
        for name in candlestick_plots:
            if name.startswith('target_'):
                symbols.append(name[len('target_'):])

        for symbol in symbols:
            html += f'<div class="symbol-pattern-group"><h3>{symbol}</h3>'
            # ターゲット
            target_key = f'target_{symbol}'
            if target_key in candlestick_plots:
                graph_html = candlestick_plots[target_key].to_html(
                    include_plotlyjs=False, div_id=f"graph_{target_key}"
                )
                html += f'<div class="graph-container">{graph_html}</div>'
            # マッチ
            rank = 1
            while True:
                match_key = f'match_{symbol}_{rank}'
                if match_key not in candlestick_plots:
                    break
                graph_html = candlestick_plots[match_key].to_html(
                    include_plotlyjs=False, div_id=f"graph_{match_key}"
                )
                html += f'<div class="graph-container">{graph_html}</div>'
                rank += 1
            html += '</div>'

        return html

    def _generate_results_table_html(self, results_df: pd.DataFrame) -> str:
        """結果テーブルHTMLを生成"""
        top_results = results_df.head(self.max_results).copy()
        html = '<div style="overflow-x: auto;"><table><thead><tr><th>順位</th><th>銘柄コード</th><th>類似度</th><th>開始日</th><th>終了日</th><th>開始価格</th><th>終了価格</th><th>将来リターン</th></tr></thead><tbody>'
        for idx, row in enumerate(top_results.itertuples(), 1):
            similarity_badge = self._get_similarity_badge(row.similarity)
            return_class = 'positive' if pd.notna(row.future_return) and row.future_return > 0 else 'negative' if pd.notna(row.future_return) else ''
            return_text = f"{row.future_return * 100:+.2f}%" if pd.notna(row.future_return) else '-'
            html += f'<tr><td>{idx}</td><td><strong>{row.symbol}</strong></td><td>{similarity_badge}</td><td>{row.start_date}</td><td>{row.end_date}</td><td>¥{row.start_price:,.0f}</td><td>¥{row.end_price:,.0f}</td><td class="{return_class}">{return_text}</td></tr>'
        html += '</tbody></table></div>'
        return html
    
    def _get_similarity_badge(self, similarity: float) -> str:
        """類似度のバッジHTMLを返す"""
        badge_class = 'badge-high' if similarity >= 0.9 else 'badge-medium' if similarity >= 0.8 else 'badge-low'
        return f'<span class="badge {badge_class}">{similarity:.3f}</span>'
