"""RL策略评测脚本"""

import os
import sys
from pathlib import Path
import argparse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from stable_baselines3 import PPO
import numpy as np

from src.env.overtaking_env import create_overtaking_env
from src.metrics import evaluate_policy
from src.utils.config_loader import load_all_configs
from src.utils.seed_utils import set_seed
from src.rl.safety_shield import SafetyShield


class SafetyShieldWrapper:
    """Safety Shield包装器，用于兼容evaluate_policy接口"""

    def __init__(self, model, shield: SafetyShield):
        self.model = model
        self.shield = shield

    def predict(self, obs, deterministic=True):
        # 获取模型预测
        action, _ = self.model.predict(obs, deterministic=deterministic)

        # Safety Shield检查
        corrected_action, was_corrected = self.shield.check_and_correct(obs, action)

        return corrected_action, None

    def reset(self):
        pass


def evaluate_rl(model_path: str, config_dir: str = "configs", output_dir: str = "outputs",
                use_safety_shield: bool = False, n_episodes: int = 50, render: bool = False):
    """评测RL策略

    Args:
        model_path: 模型路径
        config_dir: 配置文件目录
        output_dir: 输出目录
        use_safety_shield: 是否使用Safety Shield
        n_episodes: 评测轮数
        render: 是否渲染
    """
    print("\n" + "=" * 60)
    print(f"评测RL策略 {'(with Safety Shield)' if use_safety_shield else ''}")
    print("=" * 60 + "\n")

    # 加载配置
    configs = load_all_configs(config_dir)
    env_config = configs['env']
    eval_config = configs['eval']

    # 加载模型
    print(f"加载模型: {model_path}")
    model = PPO.load(model_path)
    print("✓ 模型加载完成\n")

    # 创建Safety Shield（如果需要）
    shield = None
    if use_safety_shield:
        shield = SafetyShield(env_config)
        policy = SafetyShieldWrapper(model, shield)
    else:
        policy = model

    # 创建结果目录
    results_dir = Path(output_dir) / eval_config['output']['results_dir']
    results_dir.mkdir(parents=True, exist_ok=True)

    # 评测不同密度
    all_results = {}

    for density in eval_config['scenarios']['traffic_densities']:
        print(f"\n{'=' * 60}")
        print(f"评测场景: {density.upper()} 密度")
        print(f"{'=' * 60}\n")

        env_config['traffic_density'] = density

        # 评测不同随机种子
        for seed in eval_config['scenarios']['seeds']:
            print(f"\n随机种子: {seed}")
            print("-" * 40)

            set_seed(seed)

            # 创建环境
            env = create_overtaking_env(
                env_config,
                render_mode='human' if render else None
            )

            # 评测
            evaluator, episodes = evaluate_policy(
                env=env,
                policy=policy,
                n_episodes=n_episodes,
                deterministic=True,
                render=render,
                seed=seed,
            )

            # 保存结果
            prefix = f"rl{'_safety' if use_safety_shield else ''}_{density}_seed{seed}_"
            metrics = evaluator.save_results(str(results_dir), prefix)

            # 打印摘要
            evaluator.print_summary()

            # 记录结果
            result_key = f"{density}_seed{seed}"
            all_results[result_key] = metrics

            env.close()

    # Safety Shield统计
    if use_safety_shield and shield:
        shield.print_statistics()

    print("\n" + "=" * 60)
    print("评测完成")
    print("=" * 60 + "\n")

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="评测RL超车策略")
    parser.add_argument("--model", type=str, required=True, help="模型路径")
    parser.add_argument("--config-dir", type=str, default="configs", help="配置文件目录")
    parser.add_argument("--output-dir", type=str, default="outputs", help="输出目录")
    parser.add_argument("--safety-shield", action="store_true", help="使用Safety Shield")
    parser.add_argument("--n-episodes", type=int, default=50, help="评测轮数")
    parser.add_argument("--render", action="store_true", help="渲染环境")

    args = parser.parse_args()

    evaluate_rl(
        model_path=args.model,
        config_dir=args.config_dir,
        output_dir=args.output_dir,
        use_safety_shield=args.safety_shield,
        n_episodes=args.n_episodes,
        render=args.render,
    )
