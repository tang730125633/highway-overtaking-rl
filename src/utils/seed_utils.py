"""随机种子管理工具"""

import random
import numpy as np


def set_seed(seed: int):
    """设置全局随机种子，确保可复现性

    Args:
        seed: 随机种子值
    """
    random.seed(seed)
    np.random.seed(seed)
    print(f"✓ 设置随机种子: {seed}")


def get_seeds_from_config(config):
    """从配置文件获取随机种子列表

    Args:
        config: 配置字典

    Returns:
        seeds列表
    """
    if isinstance(config.get('seeds'), list):
        return config['seeds']
    return [42]  # 默认种子
