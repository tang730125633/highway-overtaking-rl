"""日志管理工具"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path


class ExperimentLogger:
    """实验日志记录器"""

    def __init__(self, log_dir: str, experiment_name: str = None):
        """初始化日志记录器

        Args:
            log_dir: 日志目录
            experiment_name: 实验名称，默认使用时间戳
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        if experiment_name is None:
            experiment_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.experiment_name = experiment_name
        self.log_file = self.log_dir / f"{experiment_name}.log"
        self.metrics_file = self.log_dir / f"{experiment_name}_metrics.csv"

        self.log(f"实验开始: {experiment_name}")

    def log(self, message: str, level: str = "INFO"):
        """记录日志消息

        Args:
            message: 日志消息
            level: 日志级别
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')

    def log_metrics(self, metrics: dict, step: int = None):
        """记录指标

        Args:
            metrics: 指标字典
            step: 步数（可选）
        """
        metrics_with_step = {"step": step, **metrics} if step is not None else metrics

        # 写入CSV
        file_exists = self.metrics_file.exists()

        with open(self.metrics_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=metrics_with_step.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(metrics_with_step)

    def save_config(self, config: dict):
        """保存配置文件

        Args:
            config: 配置字典
        """
        config_file = self.log_dir / f"{self.experiment_name}_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        self.log(f"配置已保存: {config_file}")


def create_logger(log_dir: str, name: str = None) -> ExperimentLogger:
    """创建日志记录器的便捷函数

    Args:
        log_dir: 日志目录
        name: 实验名称

    Returns:
        ExperimentLogger实例
    """
    return ExperimentLogger(log_dir, name)
