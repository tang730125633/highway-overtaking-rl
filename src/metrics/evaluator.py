"""指标评估器

计算和统计各类评测指标
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from pathlib import Path
import json


class MetricsEvaluator:
    """指标评估器"""

    def __init__(self):
        """初始化评估器"""
        self.episodes = []

    def add_episode(self, episode_data: Dict[str, Any]):
        """添加一个episode的数据

        Args:
            episode_data: episode数据字典
        """
        self.episodes.append(episode_data)

    def compute_metrics(self) -> Dict[str, float]:
        """计算汇总指标

        Returns:
            指标字典
        """
        if not self.episodes:
            return {}

        # 提取各项数据
        successes = [ep['overtaking_complete'] for ep in self.episodes]
        collisions = [ep['collision_occurred'] for ep in self.episodes]
        violations = [ep['total_violations'] for ep in self.episodes]
        rewards = [ep['total_reward'] for ep in self.episodes]
        speeds = [ep['avg_speed'] for ep in self.episodes]
        lengths = [ep['episode_length'] for ep in self.episodes]

        # 计算指标
        metrics = {
            'success_rate': np.mean(successes) * 100,  # 百分比
            'collision_rate': np.mean(collisions) * 100,
            'violation_rate': np.mean([v > 0 for v in violations]) * 100,
            'avg_violations_per_episode': np.mean(violations),
            'avg_reward': np.mean(rewards),
            'avg_speed': np.mean(speeds),
            'avg_episode_length': np.mean(lengths),
            'total_episodes': len(self.episodes),
        }

        # 成功案例的平均时间
        success_times = [ep['episode_length'] for ep in self.episodes if ep['overtaking_complete']]
        if success_times:
            metrics['avg_success_time'] = np.mean(success_times)
        else:
            metrics['avg_success_time'] = 0

        return metrics

    def get_detailed_results(self) -> pd.DataFrame:
        """获取详细结果DataFrame

        Returns:
            包含所有episode详细数据的DataFrame
        """
        return pd.DataFrame(self.episodes)

    def save_results(self, output_dir: str, prefix: str = ""):
        """保存评测结果

        Args:
            output_dir: 输出目录
            prefix: 文件名前缀
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存汇总指标
        metrics = self.compute_metrics()

        # 转换numpy类型为Python原生类型
        metrics_serializable = {}
        for key, value in metrics.items():
            if isinstance(value, np.floating):
                metrics_serializable[key] = float(value)
            elif isinstance(value, np.integer):
                metrics_serializable[key] = int(value)
            else:
                metrics_serializable[key] = value

        metrics_file = output_dir / f"{prefix}metrics_summary.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_serializable, f, indent=2, ensure_ascii=False)

        print(f"✓ 保存汇总指标: {metrics_file}")

        # 保存详细数据
        df = self.get_detailed_results()
        csv_file = output_dir / f"{prefix}episodes_detail.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        print(f"✓ 保存详细数据: {csv_file}")

        return metrics

    def print_summary(self):
        """打印指标摘要"""
        metrics = self.compute_metrics()

        print("\n" + "=" * 60)
        print("评测结果摘要")
        print("=" * 60)
        print(f"总Episodes数:        {metrics['total_episodes']}")
        print(f"超车成功率:          {metrics['success_rate']:.2f}%")
        print(f"碰撞率:              {metrics['collision_rate']:.2f}%")
        print(f"违规率:              {metrics['violation_rate']:.2f}%")
        print(f"平均奖励:            {metrics['avg_reward']:.2f}")
        print(f"平均速度:            {metrics['avg_speed']:.2f} km/h")
        print(f"平均Episode长度:     {metrics['avg_episode_length']:.1f} 步")
        if metrics['avg_success_time'] > 0:
            print(f"成功超车平均时间:    {metrics['avg_success_time']:.1f} 步")
        print("=" * 60 + "\n")


def evaluate_policy(env, policy, n_episodes: int = 10, deterministic: bool = True,
                   render: bool = False, seed: int = None) -> Tuple[MetricsEvaluator, List[Dict]]:
    """评估策略性能

    Args:
        env: 环境实例
        policy: 策略（可以是SB3模型或自定义策略）
        n_episodes: 评测轮数
        deterministic: 是否使用确定性策略
        render: 是否渲染
        seed: 随机种子

    Returns:
        (evaluator, episodes_data)
    """
    evaluator = MetricsEvaluator()
    episodes_data = []

    for episode_idx in range(n_episodes):
        # 设置种子（如果提供）
        if seed is not None:
            episode_seed = seed + episode_idx
            obs, info = env.reset(seed=episode_seed)
        else:
            obs, info = env.reset()

        # 重置策略状态（如果有reset方法）
        if hasattr(policy, 'reset'):
            policy.reset()

        episode_data = {
            'episode': episode_idx,
            'total_reward': 0,
            'episode_length': 0,
            'collision_occurred': False,
            'overtaking_complete': False,
            'total_violations': 0,
            'speeds': [],
        }

        done = False
        truncated = False

        while not (done or truncated):
            # 预测动作
            action, _ = policy.predict(obs, deterministic=deterministic)

            # 执行动作
            obs, reward, done, truncated, info = env.step(action)

            # 记录数据
            episode_data['total_reward'] += reward
            episode_data['episode_length'] += 1
            episode_data['total_violations'] += (1 if info.get('violation', False) else 0)

            # 记录速度
            try:
                ego_speed = obs[0][3] if len(obs) > 0 else 0
                episode_data['speeds'].append(ego_speed)
            except:
                pass

            # 渲染
            if render:
                env.render()

        # 更新episode数据
        episode_data['collision_occurred'] = info.get('crashed', False)
        episode_data['overtaking_complete'] = info.get('overtaking_complete', False)
        episode_data['avg_speed'] = np.mean(episode_data['speeds']) if episode_data['speeds'] else 0

        # 移除speeds列表（太大）
        del episode_data['speeds']

        # 添加到评估器
        evaluator.add_episode(episode_data)
        episodes_data.append(episode_data)

        # 打印进度
        if (episode_idx + 1) % 10 == 0:
            print(f"  评测进度: {episode_idx + 1}/{n_episodes}")

    return evaluator, episodes_data
