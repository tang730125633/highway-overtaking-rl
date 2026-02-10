"""环境测试脚本

快速验证环境是否正常工作
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.env import create_overtaking_env
from src.baseline import RuleBasedPolicy
from src.utils.config_loader import load_all_configs


def test_environment():
    """测试环境是否正常工作"""
    print("\n" + "=" * 60)
    print("环境测试")
    print("=" * 60 + "\n")

    try:
        # 加载配置
        print("1. 加载配置...")
        configs = load_all_configs("configs")
        env_config = configs['env']
        print("✓ 配置加载成功\n")

        # 创建环境
        print("2. 创建环境...")
        env = create_overtaking_env(env_config)
        print("✓ 环境创建成功\n")

        # 重置环境
        print("3. 重置环境...")
        obs, info = env.reset()
        print(f"✓ 观测空间形状: {obs.shape}")
        print(f"✓ 动作空间: {env.action_space}\n")

        # 创建基线策略
        print("4. 创建基线策略...")
        policy = RuleBasedPolicy(env_config)
        print()

        # 运行几步
        print("5. 运行10步测试...")
        for step in range(10):
            action, _ = policy.predict(obs)
            obs, reward, done, truncated, info = env.step(action)

            if done or truncated:
                obs, info = env.reset()

        print("✓ 运行成功\n")

        env.close()

        print("=" * 60)
        print("✓ 所有测试通过！环境工作正常。")
        print("=" * 60 + "\n")

        return True

    except Exception as e:
        print(f"\n[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
