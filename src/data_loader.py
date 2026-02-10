"""
データ読み込みモジュール
Google DriveからJSONファイルを読み込み、pandas DataFrameに変換
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class StockDataLoader:
    """株価データ読み込みクラス"""
    
    def __init__(self, data_path: str):
        """
        Args:
            data_path: JSONファイルが格納されているフォルダパス
        """
        self.data_path = Path(data_path)
        self.symbols_data: Dict[str, pd.DataFrame] = {}
        self.metadata: Dict[str, any] = {}
    
    def load_all_data(self, max_files: int = 0) -> Dict[str, pd.DataFrame]:
        """
        全てのJSONファイルを読み込み、銘柄ごとのDataFrameを返す

        Args:
            max_files: 読み込むJSONファイル数の上限（0=無制限）

        Returns:
            銘柄コードをキー、DataFrameを値とする辞書
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path not found: {self.data_path}")

        # JSONファイルを取得
        json_files = list(self.data_path.glob('*.json')) + list(self.data_path.glob('*'))
        json_files = [f for f in json_files if f.is_file() and not f.name.startswith('.')]

        if not json_files:
            raise FileNotFoundError(f"No JSON files found in {self.data_path}")

        if max_files > 0:
            json_files = json_files[:max_files]

        print(f"📂 Loading {len(json_files)} JSON files")
        
        all_symbols = {}
        total_records = 0
        
        for json_file in json_files:
            try:
                symbols = self._load_single_file(json_file)
                all_symbols.update(symbols)
                total_records += sum(len(df) for df in symbols.values())
                
            except Exception as e:
                print(f"⚠️  Failed to load {json_file.name}: {e}")
                continue
        
        self.symbols_data = all_symbols
        
        # メタデータを記録
        self.metadata = {
            'total_symbols': len(all_symbols),
            'total_records': total_records,
            'load_time': datetime.now().isoformat(),
            'data_path': str(self.data_path)
        }
        
        print(f"✅ Loaded {len(all_symbols)} symbols with {total_records} total records")
        
        return all_symbols
    
    def _load_single_file(self, json_file: Path) -> Dict[str, pd.DataFrame]:
        """
        単一のJSONファイルを読み込み
        
        JSONファイル構造:
        {
            "1001": {"Date": [...], "open": [...], "high": [...], "low": [...], "close": [...], "volume": [...]},
            "1002": {...},
            ...
        }
        
        Args:
            json_file: JSONファイルのパス
            
        Returns:
            銘柄コードをキー、DataFrameを値とする辞書
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        symbols = {}
        
        for symbol_code, symbol_data in data.items():
            if not isinstance(symbol_data, dict):
                continue
            
            # 必須カラムの確認
            required_cols = ['Date', 'open', 'high', 'low', 'close']
            if not all(col in symbol_data for col in required_cols):
                continue
            
            try:
                df = self._create_dataframe(symbol_code, symbol_data)
                if len(df) > 0:
                    symbols[symbol_code] = df
                    
            except Exception as e:
                print(f"⚠️  Failed to process symbol {symbol_code}: {e}")
                continue
        
        return symbols
    
    def _create_dataframe(self, symbol_code: str, symbol_data: Dict) -> pd.DataFrame:
        """
        銘柄データからDataFrameを作成
        
        Args:
            symbol_code: 銘柄コード
            symbol_data: 銘柄の生データ
            
        Returns:
            整形されたDataFrame
        """
        # DataFrameを作成
        df = pd.DataFrame({
            'date': symbol_data['Date'],
            'open': pd.to_numeric(symbol_data['open'], errors='coerce'),
            'high': pd.to_numeric(symbol_data['high'], errors='coerce'),
            'low': pd.to_numeric(symbol_data['low'], errors='coerce'),
            'close': pd.to_numeric(symbol_data['close'], errors='coerce'),
            'volume': pd.to_numeric(
                symbol_data.get('volume', [0] * len(symbol_data['Date'])), 
                errors='coerce'
            )
        })
        
        # 日付をDatetimeIndexに変換
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.set_index('date')
        df = df.sort_index()
        
        # NaNを除外
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        # 銘柄コードを追加
        df['symbol'] = symbol_code
        
        return df
    
    def get_symbol_data(self, symbol_code: str) -> Optional[pd.DataFrame]:
        """
        特定の銘柄のデータを取得
        
        Args:
            symbol_code: 銘柄コード
            
        Returns:
            DataFrame or None
        """
        return self.symbols_data.get(symbol_code)
    
    def get_date_range(self, symbol_code: str = None) -> tuple:
        """
        データの日付範囲を取得
        
        Args:
            symbol_code: 銘柄コード（Noneの場合は全銘柄）
            
        Returns:
            (開始日, 終了日)のタプル
        """
        if symbol_code:
            df = self.get_symbol_data(symbol_code)
            if df is not None:
                return df.index.min(), df.index.max()
        else:
            all_dates = []
            for df in self.symbols_data.values():
                all_dates.extend([df.index.min(), df.index.max()])
            if all_dates:
                return min(all_dates), max(all_dates)
        
        return None, None
    
    def get_summary(self) -> pd.DataFrame:
        """
        全銘柄のサマリー情報を取得
        
        Returns:
            サマリーDataFrame
        """
        summary_data = []
        
        for symbol, df in self.symbols_data.items():
            summary_data.append({
                'symbol': symbol,
                'records': len(df),
                'start_date': df.index.min(),
                'end_date': df.index.max(),
                'latest_close': df['close'].iloc[-1] if len(df) > 0 else None,
                'avg_volume': df['volume'].mean()
            })
        
        return pd.DataFrame(summary_data).sort_values('records', ascending=False)
    
    def filter_by_min_records(self, min_records: int) -> Dict[str, pd.DataFrame]:
        """
        最小レコード数でフィルタリング
        
        Args:
            min_records: 最小レコード数
            
        Returns:
            フィルタリングされた銘柄データ
        """
        return {
            symbol: df 
            for symbol, df in self.symbols_data.items() 
            if len(df) >= min_records
        }
    
    def save_cache(self, cache_path: str) -> None:
        """
        読み込み済みデータをpickleファイルに保存

        Args:
            cache_path: 保存先ファイルパス（.pkl）
        """
        import pickle
        cache_path = Path(cache_path)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'wb') as f:
            pickle.dump(self.symbols_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"💾 Cache saved: {cache_path} ({len(self.symbols_data)} symbols)")

    @classmethod
    def load_cache(cls, cache_path: str) -> 'StockDataLoader':
        """
        pickleキャッシュからデータを復元

        Args:
            cache_path: キャッシュファイルパス（.pkl）

        Returns:
            復元されたStockDataLoaderインスタンス
        """
        import pickle
        cache_path = Path(cache_path)
        if not cache_path.exists():
            raise FileNotFoundError(f"Cache not found: {cache_path}")
        with open(cache_path, 'rb') as f:
            symbols_data = pickle.load(f)
        loader = cls.__new__(cls)
        loader.data_path = Path('')
        loader.symbols_data = symbols_data
        loader.metadata = {'loaded_from_cache': str(cache_path)}
        print(f"⚡ Cache loaded: {len(symbols_data)} symbols from {cache_path}")
        return loader

    def __len__(self) -> int:
        """読み込まれた銘柄数を返す"""
        return len(self.symbols_data)

    def __repr__(self) -> str:
        return f"StockDataLoader(symbols={len(self.symbols_data)}, path={self.data_path})"
