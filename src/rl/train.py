"""PPO训练脚本"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor

from src.env import create_overtaking_env
from src.utils.config_loader import load_all_configs
from src.utils.logger import create_logger
from src.utils.seed_utils import set_seed


def make_env(env_config, rank=0, seed=0):
    """创建环境的辅助函数（用于并行）"""
    def _init():
        env = create_overtaking_env(env_config)
        env = Monitor(env)
        env.reset(seed=seed + rank)
        return env
    return _init


def train_ppo(config_dir: str = "configs", output_dir: str = "outputs"):
    """训练PPO模型

    Args:
        config_dir: 配置文件目录
        output_dir: 输出目录
    """
    print("\n" + "=" * 60)
    print("开始PPO训练")
    print("=" * 60 + "\n")

    # 加载配置
    configs = load_all_configs(config_dir)
    env_config = configs['env']
    train_config = configs['train']

    # 设置随机种子
    set_seed(env_config.get('seeds', [42])[0])

    # 创建输出目录
    model_dir = Path(output_dir) / train_config['output']['model_dir']
    log_dir = Path(output_dir) / train_config['output']['log_dir']
    model_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 创建日志记录器
    logger = create_logger(str(log_dir), "ppo_training")
    logger.save_config({**env_config, **train_config})

    # 设置交通密度
    env_config['traffic_density'] = train_config.get('traffic_density', 'medium')

    # 创建并行环境
    n_envs = train_config.get('n_envs', 4)
    print(f"创建 {n_envs} 个并行环境...")

    env_fns = [make_env(env_config, i, seed=42) for i in range(n_envs)]
    env = DummyVecEnv(env_fns)

    # 可选：环境归一化
    # env = VecNormalize(env, norm_obs=True, norm_reward=True)

    # 创建评估环境
    eval_env = create_overtaking_env(env_config)
    eval_env = Monitor(eval_env)

    print("✓ 环境创建完成\n")

    # 创建PPO模型
    ppo_config = train_config['ppo']
    network_config = train_config['network']

    model = PPO(
        policy=network_config['policy_type'],
        env=env,
        learning_rate=ppo_config['learning_rate'],
        n_steps=ppo_config['n_steps'],
        batch_size=ppo_config['batch_size'],
        n_epochs=ppo_config['n_epochs'],
        gamma=ppo_config['gamma'],
        gae_lambda=ppo_config['gae_lambda'],
        clip_range=ppo_config['clip_range'],
        ent_coef=ppo_config['ent_coef'],
        vf_coef=ppo_config['vf_coef'],
        max_grad_norm=ppo_config['max_grad_norm'],
        policy_kwargs=dict(
            net_arch=network_config['net_arch'],
        ),
        verbose=train_config['output']['verbose'],
        tensorboard_log=str(log_dir) if train_config['output']['tensorboard'] else None,
        device=train_config.get('device', 'auto'),
    )

    print("✓ PPO模型创建完成")
    print(f"  网络结构: {network_config['net_arch']}")
    print(f"  学习率: {ppo_config['learning_rate']}")
    print(f"  设备: {train_config.get('device', 'auto')}\n")

    # 创建回调
    callbacks = []

    # 模型保存回调
    checkpoint_callback = CheckpointCallback(
        save_freq=train_config['save_freq'],
        save_path=str(model_dir),
        name_prefix='ppo_highway',
        save_replay_buffer=False,
        save_vecnormalize=True,
    )
    callbacks.append(checkpoint_callback)

    # 评估回调
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(model_dir / 'best'),
        log_path=str(log_dir),
        eval_freq=train_config['eval_freq'],
        n_eval_episodes=train_config['eval_episodes'],
        deterministic=True,
        render=False,
    )
    callbacks.append(eval_callback)

    print("开始训练...\n")
    logger.log("训练开始")

    # 训练
    try:
        model.learn(
            total_timesteps=train_config['total_timesteps'],
            callback=callbacks,
            progress_bar=False,  # 禁用进度条（后台运行时不需要）
        )

        logger.log("训练完成")
        print("\n✓ 训练完成！")

        # 保存最终模型
        final_model_path = model_dir / "ppo_highway_final"
        model.save(final_model_path)
        logger.log(f"最终模型已保存: {final_model_path}")
        print(f"✓ 最终模型已保存: {final_model_path}.zip\n")

    except KeyboardInterrupt:
        logger.log("训练被用户中断", level="WARNING")
        print("\n训练被中断，保存当前模型...")
        model.save(model_dir / "ppo_highway_interrupted")
        print("✓ 中断模型已保存\n")

    finally:
        env.close()
        eval_env.close()

    print("=" * 60)
    print("训练结束")
    print("=" * 60 + "\n")

    return model


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="训练PPO超车策略")
    parser.add_argument("--config-dir", type=str, default="configs", help="配置文件目录")
    parser.add_argument("--output-dir", type=str, default="outputs", help="输出目录")

    args = parser.parse_args()

    train_ppo(args.config_dir, args.output_dir)
