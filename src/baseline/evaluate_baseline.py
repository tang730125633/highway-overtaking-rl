"""基线策略评测脚本"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.env.overtaking_env import create_overtaking_env
from src.baseline import RuleBasedPolicy
from src.metrics import evaluate_policy
from src.utils.config_loader import load_all_configs
from src.utils.seed_utils import set_seed


def evaluate_baseline(config_dir: str = "configs", output_dir: str = "outputs",
                      n_episodes: int = 50, render: bool = False):
    """评测基线策略

    Args:
        config_dir: 配置文件目录
        output_dir: 输出目录
        n_episodes: 评测轮数
        render: 是否渲染
    """
    print("\n" + "=" * 60)
    print("评测规则基线策略")
    print("=" * 60 + "\n")

    # 加载配置
    configs = load_all_configs(config_dir)
    env_config = configs['env']
    eval_config = configs['eval']

    # 创建基线策略
    policy = RuleBasedPolicy(env_config)
    print()

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
            prefix = f"baseline_{density}_seed{seed}_"
            metrics = evaluator.save_results(str(results_dir), prefix)

            # 打印摘要
            evaluator.print_summary()

            # 记录结果
            result_key = f"{density}_seed{seed}"
            all_results[result_key] = metrics

            env.close()

    print("\n" + "=" * 60)
    print("评测完成")
    print("=" * 60 + "\n")

    return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="评测规则基线超车策略")
    parser.add_argument("--config-dir", type=str, default="configs", help="配置文件目录")
    parser.add_argument("--output-dir", type=str, default="outputs", help="输出目录")
    parser.add_argument("--n-episodes", type=int, default=50, help="评测轮数")
    parser.add_argument("--render", action="store_true", help="渲染环境")

    args = parser.parse_args()

    evaluate_baseline(
        config_dir=args.config_dir,
        output_dir=args.output_dir,
        n_episodes=args.n_episodes,
        render=args.render,
    )
