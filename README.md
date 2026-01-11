# Stock Pattern Matcher

株価・FXのローソク足パターンマッチングシステム

## 概要

過去の株価・FXデータから、指定したパターンと類似する値動きを検索し、その後の価格変動を分析するPythonライブラリです。

### 主な機能

- **パターンマッチング**: 指定期間のローソク足パターンと類似する過去のパターンを検索
- **複数の類似度計算方法**: 相関係数、ユークリッド距離、重み付き相関
- **柔軟な正規化**: 相対値正規化、Min-Max正規化
- **統計分析**: パターン後のリターン分析、確率計算
- **可視化**: ローソク足チャート、比較グラフ、分布図
- **GPU対応**: Google Colab環境での高速処理

## インストール

### 必要な環境

- Python 3.8+
- Google Colab（推奨）または Jupyter Notebook

### 依存ライブラリ

```bash
pip install -r requirements.txt
```

## クイックスタート

### 1. Google Colabでの使用

```python
# Googleドライブをマウント
from google.colab import drive
drive.mount('/content/drive')

# モジュールのパスを追加
import sys
sys.path.append('/content/drive/MyDrive/stock_pattern_matcher')

# インポート
from pattern_matcher import CandlePatternMatcher
from visualizer import PatternVisualizer
import pandas as pd

# データ読み込み
df = pd.read_csv('your_data.csv', index_col='date', parse_dates=True)

# パターンマッチャーの初期化
matcher = CandlePatternMatcher(df)

# 類似パターン検索
results, target = matcher.find_similar_patterns(
    window_size=10,
    lookahead=10,
    top_n=20
)

# 可視化
visualizer = PatternVisualizer()
visualizer.plot_pattern_comparison(target, results)
```

### 2. ローカル環境での使用

```python
from stock_pattern_matcher import CandlePatternMatcher, PatternVisualizer
import pandas as pd

# データ読み込み
df = pd.read_csv('data/sample_data.csv', index_col='date', parse_dates=True)

# 分析実行
matcher = CandlePatternMatcher(df)
results, target = matcher.find_similar_patterns()
```

## データ形式

### 必須カラム

CSVまたはPandas DataFrameで以下のカラムが必要です：

| カラム名 | 説明 | 型 |
|---------|------|-----|
| date | 日付・時刻 | datetime |
| open | 始値 | float |
| high | 高値 | float |
| low | 安値 | float |
| close | 終値 | float |
| volume | 出来高 | int/float |

### データ例

```csv
date,open,high,low,close,volume
2024-01-01 09:00:00,150.0,152.5,149.8,151.2,10000
2024-01-01 09:10:00,151.2,153.0,151.0,152.5,12000
...
```

## 使用例

### 基本的な使い方

```python
# パターンマッチング
matcher = CandlePatternMatcher(df)
results, target_data = matcher.find_similar_patterns(
    target_end_index=-1,      # 最新データを対象
    window_size=20,           # 20本のローソク足でパターン比較
    lookahead=10,             # その後10本の動きを分析
    top_n=15,                 # 上位15件を取得
    min_similarity=0.7,       # 類似度0.7以上
    method='correlation'      # 相関係数で類似度計算
)

# 統計分析
from pattern_matcher import calculate_statistics
stats = calculate_statistics(results)
print(f"平均リターン: {stats['mean_return']:.2f}%")
print(f"上昇確率: {stats['positive_rate']:.1f}%")
```

### カスタムOHLCカラム名

```python
# カラム名が異なる場合
ohlc_cols = {
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}

matcher = CandlePatternMatcher(df, ohlc_cols=ohlc_cols)
```

### 複数の正規化・類似度計算方法

```python
# Min-Max正規化 + ユークリッド距離
results1, _ = matcher.find_similar_patterns(
    normalize_method='minmax',
    method='euclidean'
)

# 相対値正規化 + 重み付き相関
results2, _ = matcher.find_similar_patterns(
    normalize_method='relative',
    method='weighted'
)
```

## API リファレンス

### CandlePatternMatcher

主要なパターンマッチングクラス

#### `__init__(df, ohlc_cols=None)`

**パラメータ:**
- `df` (DataFrame): OHLCデータ（DatetimeIndexが必須）
- `ohlc_cols` (dict): カラム名のマッピング

#### `find_similar_patterns(...)`

類似パターンを検索

**パラメータ:**
- `target_end_index` (int): 対象パターンの終了位置（-1で最新）
- `window_size` (int): パターンのウィンドウサイズ
- `lookahead` (int): パターン後の予測期間
- `top_n` (int): 返す類似パターン数
- `min_similarity` (float): 最小類似度閾値 (0-1)
- `method` (str): 類似度計算方法
  - `'correlation'`: ピアソン相関係数
  - `'euclidean'`: ユークリッド距離
  - `'weighted'`: 重み付き相関
- `normalize_method` (str): 正規化方法
  - `'relative'`: 基準終値からの変化率
  - `'minmax'`: Min-Max正規化 (0-1)
- `exclude_recent_days` (int): 検索から除外する直近データ数

**戻り値:**
- `results_df` (DataFrame): 類似パターンの結果
- `target_data` (DataFrame): 対象パターンのデータ

### PatternVisualizer

可視化クラス

#### `plot_pattern_comparison(target_data, similar_patterns_df, top_n=5)`

パターン比較グラフを表示

#### `plot_return_distribution(similar_patterns_df, bins=20)`

リターン分布のヒストグラムを表示

#### `plot_candlestick(df, title, ma_periods=None)`

ローソク足チャートを表示

## プロジェクト構成

```
stock-pattern-matcher/
├── README.md                          # このファイル
├── LICENSE                            # ライセンス
├── requirements.txt                   # 依存ライブラリ
├── setup.py                           # パッケージ設定
├── .gitignore                         # Git除外設定
├── pyproject.toml                     # プロジェクト設定
│
├── stock_pattern_matcher/             # メインパッケージ
│   ├── __init__.py
│   ├── pattern_matcher.py             # パターンマッチングコア
│   ├── visualizer.py                  # 可視化機能
│   ├── data_loader.py                 # データ読み込み
│   ├── indicators.py                  # テクニカル指標
│   └── utils.py                       # ユーティリティ
│
├── notebooks/                         # Jupyter/Colabノートブック
│   ├── quickstart.ipynb               # クイックスタート
│   ├── advanced_analysis.ipynb        # 応用分析
│   └── backtesting.ipynb              # バックテスト
│
├── examples/                          # サンプルコード
│   ├── basic_usage.py
│   ├── custom_similarity.py
│   └── batch_analysis.py
│
├── tests/                             # テストコード
│   ├── __init__.py
│   ├── test_pattern_matcher.py
│   ├── test_visualizer.py
│   └── test_data_loader.py
│
├── data/                              # サンプルデータ
│   ├── sample_stock.csv
│   ├── sample_fx.csv
│   └── README.md
│
├── docs/                              # ドキュメント
│   ├── getting_started.md
│   ├── api_reference.md
│   ├── examples.md
│   └── contributing.md
│
└── scripts/                           # ユーティリティスクリプト
    ├── download_data.py
    └── create_dataset.py
```

## パフォーマンス

### ベンチマーク（参考値）

| データ件数 | ウィンドウサイズ | 処理時間 | 環境 |
|-----------|----------------|---------|------|
| 10,000件 | 20 | ~5秒 | Google Colab (GPU) |
| 50,000件 | 20 | ~25秒 | Google Colab (GPU) |
| 100,000件 | 20 | ~50秒 | Google Colab (GPU) |

### 最適化のヒント

1. **GPUの活用**: Google ColabでランタイムタイプをGPUに設定
2. **ウィンドウサイズの調整**: 大きすぎるウィンドウは処理時間が増加
3. **最小類似度の設定**: 高めに設定することで計算量を削減
4. **データの前処理**: 不要な期間のデータを事前に除外

## 今後の機能拡張予定

- [ ] Dynamic Time Warping (DTW) サポート
- [ ] 機械学習モデル（LSTM, Transformer）の統合
- [ ] テクニカル指標の自動計算・組み込み
- [ ] バックテスト機能の追加
- [ ] リアルタイムデータ取得
- [ ] WebUI/ダッシュボード
- [ ] 複数銘柄の一括分析
- [ ] アラート機能

## コントリビューション

プルリクエストを歓迎します！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

詳細は [CONTRIBUTING.md](docs/contributing.md) を参照してください。

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

## 作者

あなたの名前 - [@your_twitter](https://twitter.com/your_twitter)

プロジェクトリンク: [https://github.com/yourusername/stock-pattern-matcher](https://github.com/yourusername/stock-pattern-matcher)

## 謝辞

- [mplfinance](https://github.com/matplotlib/mplfinance) - ローソク足チャート描画
- [pandas](https://pandas.pydata.org/) - データ処理
- [scipy](https://scipy.org/) - 統計計算

## よくある質問（FAQ）

### Q: どのようなデータ形式に対応していますか？
A: CSV、JSON、Pandas DataFrameに対応しています。日付がインデックスになっているDataFrameが最も扱いやすいです。

### Q: リアルタイムデータに対応していますか？
A: 現在は過去データの分析に特化していますが、将来的にリアルタイムデータ対応を予定しています。

### Q: 株価だけでなくFXにも使えますか？
A: はい、OHLCデータであれば株価、FX、仮想通貨など様々な金融商品に対応しています。

### Q: GPU必須ですか？
A: 必須ではありませんが、大量データの処理にはGPUが推奨されます。

## サポート

問題が発生した場合は [Issues](https://github.com/yourusername/stock-pattern-matcher/issues) で報告してください。

## 更新履歴

### v1.0.0 (2025-01-11)
- 初回リリース
- 基本的なパターンマッチング機能
- 複数の類似度計算方法
- 可視化機能
