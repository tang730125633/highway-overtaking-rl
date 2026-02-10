"""配置文件加载工具"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_yaml(file_path: str) -> Dict[str, Any]:
    """加载YAML配置文件

    Args:
        file_path: YAML文件路径

    Returns:
        配置字典
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    print(f"✓ 加载配置: {file_path}")
    return config


def load_all_configs(config_dir: str = "configs") -> Dict[str, Dict]:
    """加载所有配置文件

    Args:
        config_dir: 配置文件目录

    Returns:
        包含所有配置的字典
    """
    config_dir = Path(config_dir)

    configs = {
        'env': load_yaml(config_dir / "env_config.yaml"),
        'train': load_yaml(config_dir / "train_config.yaml"),
        'eval': load_yaml(config_dir / "eval_config.yaml"),
    }

    return configs


def merge_configs(*configs: Dict) -> Dict:
    """合并多个配置字典

    Args:
        *configs: 多个配置字典

    Returns:
        合并后的配置字典
    """
    merged = {}
    for config in configs:
        merged.update(config)
    return merged
