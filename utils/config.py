"""
設定管理モジュール
YAMLファイルから設定を読み込み、Pythonオブジェクトとして提供
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """設定管理クラス"""
    
    def __init__(self, config_path: str = None):
        """
        Args:
            config_path: 設定ファイルのパス。Noneの場合はデフォルトパスを使用
        """
        if config_path is None:
            # デフォルトの設定ファイルパス
            config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        ドット記法で設定値を取得
        
        Args:
            key: 設定キー（例: "debug.mode", "analysis.pattern_matching.window_size"）
            default: キーが存在しない場合のデフォルト値
            
        Returns:
            設定値
            
        Examples:
            >>> config = Config()
            >>> config.get("debug.mode")
            True
            >>> config.get("analysis.pattern_matching.window_size")
            20
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        設定値を動的に変更（メモリ上のみ、ファイルには保存されない）
        
        Args:
            key: 設定キー
            value: 設定値
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def reload(self) -> None:
        """設定ファイルを再読み込み"""
        self._config = self._load_config()
    
    # 便利なプロパティ
    @property
    def debug_mode(self) -> bool:
        """デバッグモードが有効かどうか"""
        return self.get("debug.mode", False)
    
    @property
    def gpu_enabled(self) -> bool:
        """GPU使用が有効かどうか"""
        return self.get("gpu.enabled", False)
    
    @property
    def github_owner(self) -> str:
        """GitHubオーナー名"""
        return self.get("github.owner", "")
    
    @property
    def github_repo(self) -> str:
        """GitHubリポジトリ名"""
        return self.get("github.repo", "")
    
    @property
    def window_size(self) -> int:
        """パターンマッチングのウィンドウサイズ"""
        return self.get("analysis.pattern_matching.window_size", 20)
    
    @property
    def lookahead(self) -> int:
        """将来予測期間"""
        return self.get("analysis.pattern_matching.lookahead", 10)
    
    @property
    def top_n(self) -> int:
        """返す上位マッチ数"""
        return self.get("analysis.pattern_matching.top_n", 15)
    
    @property
    def min_similarity(self) -> float:
        """最小類似度"""
        return self.get("analysis.pattern_matching.min_similarity", 0.7)
    
    def __repr__(self) -> str:
        return f"Config(config_path={self.config_path})"
    
    def __str__(self) -> str:
        return yaml.dump(self._config, allow_unicode=True, default_flow_style=False)


# グローバル設定インスタンス（シングルトン的に使用）
_global_config = None


def get_config(config_path: str = None) -> Config:
    """
    グローバル設定インスタンスを取得
    
    Args:
        config_path: 設定ファイルのパス（初回のみ指定）
        
    Returns:
        Config インスタンス
    """
    global _global_config
    
    if _global_config is None or config_path is not None:
        _global_config = Config(config_path)
    
    return _global_config
