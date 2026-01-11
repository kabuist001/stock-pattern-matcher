"""
データ読み込みモジュール

様々な形式のデータソースから株価・FXデータを読み込む機能を提供
"""

import pandas as pd
import json
from typing import Optional, Dict, Any
from pathlib import Path


class DataLoader:
    """
    データ読み込みクラス
    
    CSV、JSON、APIなど複数のデータソースに対応
    """
    
    @staticmethod
    def load_csv(
        filepath: str,
        date_column: str = 'date',
        parse_dates: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        CSVファイルからデータを読み込み
        
        Parameters:
        -----------
        filepath : str
            CSVファイルのパス
        date_column : str
            日付カラム名
        parse_dates : bool
            日付を自動パース
        **kwargs : dict
            pd.read_csvに渡す追加パラメータ
        
        Returns:
        --------
        df : DataFrame
            読み込んだデータ
        """
        df = pd.read_csv(filepath, **kwargs)
        
        if date_column in df.columns and parse_dates:
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.set_index(date_column)
        
        return df.sort_index()
    
    @staticmethod
    def load_json(
        filepath: str,
        orient: str = 'records',
        date_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        JSONファイルからデータを読み込み
        
        Parameters:
        -----------
        filepath : str
            JSONファイルのパス
        orient : str
            JSONの構造 ('records', 'index', 'columns', 'values')
        date_column : str, optional
            日付カラム名
        
        Returns:
        --------
        df : DataFrame
            読み込んだデータ
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            # 辞書形式の場合、orientに応じて変換
            df = pd.DataFrame.from_dict(data, orient=orient)
        else:
            df = pd.DataFrame(data)
        
        if date_column and date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.set_index(date_column)
        
        return df.sort_index()
    
    @staticmethod
    def load_from_yahoo(
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        Yahoo Finance APIからデータを取得（将来実装）
        
        Parameters:
        -----------
        symbol : str
            銘柄コード
        start_date : str, optional
            開始日
        end_date : str, optional
            終了日
        interval : str
            取得間隔 ('1m', '5m', '1h', '1d', '1wk', '1mo')
        
        Returns:
        --------
        df : DataFrame
            取得したデータ
        """
        raise NotImplementedError("Yahoo Finance API integration is not yet implemented")
    
    @staticmethod
    def validate_ohlc_data(df: pd.DataFrame, ohlc_cols: Dict[str, str]) -> bool:
        """
        OHLCデータの妥当性をチェック
        
        Parameters:
        -----------
        df : DataFrame
            チェック対象データ
        ohlc_cols : dict
            OHLCカラムのマッピング
        
        Returns:
        --------
        is_valid : bool
            データが妥当かどうか
        """
        # 必須カラムの存在チェック
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if ohlc_cols.get(col) not in df.columns:
                print(f"エラー: '{ohlc_cols.get(col)}' カラムが見つかりません")
                return False
        
        # データ型チェック
        for col in required_cols:
            col_name = ohlc_cols[col]
            if not pd.api.types.is_numeric_dtype(df[col_name]):
                print(f"エラー: '{col_name}' が数値型ではありません")
                return False
        
        # 価格の論理チェック（high >= low など）
        high_col = ohlc_cols['high']
        low_col = ohlc_cols['low']
        
        if (df[high_col] < df[low_col]).any():
            print("警告: 高値が安値より低いデータがあります")
            return False
        
        return True


def convert_to_standard_format(
    df: pd.DataFrame,
    column_mapping: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    データを標準フォーマットに変換
    
    Parameters:
    -----------
    df : DataFrame
        変換対象データ
    column_mapping : dict, optional
        カラム名のマッピング
        例: {'始値': 'open', '高値': 'high', ...}
    
    Returns:
    --------
    df_converted : DataFrame
        標準フォーマットに変換されたデータ
    """
    df_converted = df.copy()
    
    if column_mapping:
        df_converted = df_converted.rename(columns=column_mapping)
    
    # カラム名を小文字に統一
    df_converted.columns = df_converted.columns.str.lower()
    
    return df_converted
