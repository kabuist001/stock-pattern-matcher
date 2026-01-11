"""
設定管理モジュール

環境変数や設定ファイルからパスや設定を読み込む
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import json


class Config:
    """
    設定を管理するクラス
    
    環境変数 > 設定ファイル > デフォルト値 の優先順位で設定を読み込む
    """
    
    # デフォルト設定
    DEFAULT_CONFIG = {
        # データパス
        'data_dir': 'data',
        'output_dir': 'outputs',
        
        # Google Colab設定（環境変数で上書き可能）
        'colab_drive_mount': '/content/drive',
        'colab_module_path': None,  # 環境変数 COLAB_MODULE_PATH で指定
        'colab_data_path': None,    # 環境変数 COLAB_DATA_PATH で指定
        
        # パターンマッチング デフォルト設定
        'default_window_size': 20,
        'default_lookahead': 10,
        'default_top_n': 15,
        'default_min_similarity': 0.6,
        'default_method': 'correlation',
        'default_normalize_method': 'relative',
        
        # 可視化設定
        'default_figsize': (12, 6),
        'default_style': 'seaborn',
        
        # OHLCカラム名（デフォルト）
        'ohlc_columns': {
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
            'date': 'date'
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Parameters:
        -----------
        config_file : str, optional
            設定ファイルのパス（JSON形式）
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        # 設定ファイルから読み込み
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)
        
        # 環境変数から読み込み（最優先）
        self._load_from_env()
    
    def _load_from_file(self, filepath: str):
        """設定ファイルから読み込み"""
        with open(filepath, 'r', encoding='utf-8') as f:
            file_config = json.load(f)
        self.config.update(file_config)
    
    def _load_from_env(self):
        """環境変数から読み込み"""
        # Colabモジュールパス
        if os.getenv('COLAB_MODULE_PATH'):
            self.config['colab_module_path'] = os.getenv('COLAB_MODULE_PATH')
        
        # Colabデータパス
        if os.getenv('COLAB_DATA_PATH'):
            self.config['colab_data_path'] = os.getenv('COLAB_DATA_PATH')
        
        # ドライブマウントポイント
        if os.getenv('DRIVE_MOUNT_POINT'):
            self.config['colab_drive_mount'] = os.getenv('DRIVE_MOUNT_POINT')
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        設定値を取得
        
        Parameters:
        -----------
        key : str
            設定キー
        default : Any
            デフォルト値
        
        Returns:
        --------
        value : Any
            設定値
        """
        return self.config.get(key, default)
    
    def get_colab_module_path(self) -> str:
        """
        Colabでのモジュールパスを取得
        
        Returns:
        --------
        path : str
            モジュールパス
        """
        module_path = self.config.get('colab_module_path')
        
        if not module_path:
            # デフォルト: マウントされたドライブのルート
            drive_mount = self.config['colab_drive_mount']
            module_path = f"{drive_mount}/MyDrive/stock_pattern_matcher"
        
        return module_path
    
    def get_colab_data_path(self) -> str:
        """
        Colabでのデータパスを取得
        
        Returns:
        --------
        path : str
            データディレクトリパス
        """
        data_path = self.config.get('colab_data_path')
        
        if not data_path:
            # デフォルト: マウントされたドライブのルート
            drive_mount = self.config['colab_drive_mount']
            data_path = f"{drive_mount}/MyDrive/data"
        
        return data_path
    
    def save_to_file(self, filepath: str):
        """
        現在の設定をファイルに保存
        
        Parameters:
        -----------
        filepath : str
            保存先のパス
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)


# グローバル設定インスタンス
_global_config = None


def get_config(config_file: Optional[str] = None) -> Config:
    """
    グローバル設定インスタンスを取得
    
    Parameters:
    -----------
    config_file : str, optional
        設定ファイルのパス
    
    Returns:
    --------
    config : Config
        設定インスタンス
    """
    global _global_config
    
    if _global_config is None:
        _global_config = Config(config_file)
    
    return _global_config


def is_colab_environment() -> bool:
    """
    Google Colab環境かどうかを判定
    
    Returns:
    --------
    is_colab : bool
        Colab環境ならTrue
    """
    try:
        import google.colab
        return True
    except ImportError:
        return False


def setup_colab_paths(
    module_path: Optional[str] = None,
    data_path: Optional[str] = None
) -> Dict[str, str]:
    """
    Colab環境のパスをセットアップ
    
    Parameters:
    -----------
    module_path : str, optional
        モジュールのパス（指定しない場合は環境変数またはデフォルトを使用）
    data_path : str, optional
        データディレクトリのパス
    
    Returns:
    --------
    paths : dict
        設定されたパス
    """
    if not is_colab_environment():
        raise RuntimeError("この関数はGoogle Colab環境でのみ使用できます")
    
    config = get_config()
    
    # モジュールパスの設定
    if module_path:
        os.environ['COLAB_MODULE_PATH'] = module_path
        config.config['colab_module_path'] = module_path
    
    final_module_path = config.get_colab_module_path()
    
    # sys.pathに追加
    import sys
    if final_module_path not in sys.path:
        sys.path.insert(0, final_module_path)
    
    # データパスの設定
    if data_path:
        os.environ['COLAB_DATA_PATH'] = data_path
        config.config['colab_data_path'] = data_path
    
    final_data_path = config.get_colab_data_path()
    
    return {
        'module_path': final_module_path,
        'data_path': final_data_path,
        'drive_mount': config.get('colab_drive_mount')
    }
