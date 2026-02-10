"""可视化工具

生成论文所需的图表
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import List, Dict


# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("Set2")


def load_results(results_dir: str, prefix: str) -> Dict:
    """加载评测结果

    Args:
        results_dir: 结果目录
        prefix: 文件名前缀

    Returns:
        结果字典
    """
    results_dir = Path(results_dir)
    metrics_file = results_dir / f"{prefix}metrics_summary.json"

    with open(metrics_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_comparison_bar(data: pd.DataFrame, output_path: str, title: str = "性能对比"):
    """绘制对比柱状图

    Args:
        data: 数据DataFrame
        output_path: 输出路径
        title: 图标题
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')

    metrics = [
        ('success_rate', '超车成功率 (%)'),
        ('collision_rate', '碰撞率 (%)'),
        ('violation_rate', '违规率 (%)'),
        ('avg_speed', '平均速度 (km/h)'),
        ('avg_reward', '平均奖励'),
        ('avg_episode_length', '平均Episode长度'),
    ]

    for idx, (metric, label) in enumerate(metrics):
        ax = axes[idx // 3, idx % 3]

        # 绘制柱状图
        x = np.arange(len(data))
        width = 0.35

        bars = ax.bar(x, data[metric], width, alpha=0.8)

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('策略', fontsize=11)
        ax.set_ylabel(label, fontsize=11)
        ax.set_title(label, fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(data['policy'], rotation=15, ha='right')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 保存对比图: {output_path}")
    plt.close()


def plot_training_curves(log_dir: str, output_path: str):
    """绘制训练曲线

    Args:
        log_dir: TensorBoard日志目录
        output_path: 输出路径
    """
    # 这里简化处理，实际需要读取TensorBoard日志
    # 可以使用 tensorboard.backend.event_processing 读取

    print(f"提示: 训练曲线请使用 TensorBoard 查看")
    print(f"  命令: tensorboard --logdir {log_dir}")


def plot_density_comparison(results_dict: Dict, output_path: str):
    """绘制不同密度下的性能对比

    Args:
        results_dict: 结果字典 {density: {method: metrics}}
        output_path: 输出路径
    """
    densities = list(results_dict.keys())
    methods = list(results_dict[densities[0]].keys())

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('不同交通密度下的性能对比', fontsize=16, fontweight='bold')

    metrics_to_plot = [
        ('success_rate', '超车成功率 (%)'),
        ('collision_rate', '碰撞率 (%)'),
        ('avg_speed', '平均速度 (km/h)'),
    ]

    x = np.arange(len(densities))
    width = 0.25

    for idx, (metric, label) in enumerate(metrics_to_plot):
        ax = axes[idx]

        for i, method in enumerate(methods):
            values = [results_dict[d][method][metric] for d in densities]
            offset = width * (i - len(methods)/2 + 0.5)
            bars = ax.bar(x + offset, values, width, label=method, alpha=0.8)

            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=8)

        ax.set_xlabel('交通密度', fontsize=11)
        ax.set_ylabel(label, fontsize=11)
        ax.set_title(label, fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([d.upper() for d in densities])
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 保存密度对比图: {output_path}")
    plt.close()


def generate_all_plots(results_dir: str, output_dir: str):
    """生成所有论文图表

    Args:
        results_dir: 结果目录
        output_dir: 输出目录
    """
    print("\n" + "=" * 60)
    print("生成论文图表")
    print("=" * 60 + "\n")

    results_dir = Path(results_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 收集所有结果
    all_results = {}
    densities = ['low', 'medium', 'high']
    methods = ['baseline', 'rl', 'rl_safety']
    seeds = [42, 123, 456]

    for density in densities:
        all_results[density] = {}

        for method in methods:
            # 收集所有seed的结果并平均
            method_results = []

            for seed in seeds:
                prefix = f"{method}_{density}_seed{seed}_"
                try:
                    result = load_results(results_dir, prefix)
                    method_results.append(result)
                except FileNotFoundError:
                    print(f"  警告: 未找到 {prefix} 的结果文件")
                    continue

            if method_results:
                # 计算平均值
                avg_result = {}
                for key in method_results[0].keys():
                    if isinstance(method_results[0][key], (int, float)):
                        avg_result[key] = np.mean([r[key] for r in method_results])
                    else:
                        avg_result[key] = method_results[0][key]

                all_results[density][method] = avg_result

    # 生成图表

    # 1. 中等密度下的方法对比
    if 'medium' in all_results and all_results['medium']:
        df_medium = pd.DataFrame([
            {'policy': 'Baseline', **all_results['medium'].get('baseline', {})},
            {'policy': 'RL', **all_results['medium'].get('rl', {})},
            {'policy': 'RL+Safety', **all_results['medium'].get('rl_safety', {})},
        ])
        plot_comparison_bar(
            df_medium,
            str(output_dir / 'comparison_medium_density.png'),
            '中等密度下的性能对比'
        )

    # 2. 不同密度下的对比
    if all_results:
        plot_density_comparison(
            all_results,
            str(output_dir / 'comparison_across_densities.png')
        )

    print("\n" + "=" * 60)
    print("图表生成完成")
    print("=" * 60 + "\n")
    print(f"图表保存在: {output_dir}/")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="生成论文图表")
    parser.add_argument("--results-dir", type=str, default="outputs/results", help="结果目录")
    parser.add_argument("--output-dir", type=str, default="outputs/figures", help="输出目录")

    args = parser.parse_args()

    generate_all_plots(args.results_dir, args.output_dir)
