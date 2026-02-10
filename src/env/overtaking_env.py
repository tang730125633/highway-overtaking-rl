"""高速公路超车环境封装

基于highway-env实现的超车决策环境
"""

import gymnasium as gym
import highway_env
import numpy as np
from typing import Dict, Any, Tuple


class OvertakingEnvWrapper(gym.Wrapper):
    """超车环境包装器，用于自定义奖励和终止条件"""

    def __init__(self, env, config: Dict[str, Any]):
        """初始化环境包装器

        Args:
            env: highway-env环境实例
            config: 环境配置字典
        """
        super().__init__(env)
        self.config = config
        self.safety_config = config.get('safety', {})
        self.reward_weights = config.get('reward_weights', {})

        # 超车追踪
        self.target_vehicle = None
        self.overtaking_started = False
        self.overtaking_complete = False
        self.steps_ahead = 0

        # 统计信息
        self.episode_length = 0
        self.total_reward = 0
        self.collision_occurred = False
        self.violation_count = 0

    def reset(self, **kwargs):
        """重置环境"""
        obs, info = self.env.reset(**kwargs)

        # 重置追踪变量
        self.target_vehicle = None
        self.overtaking_started = False
        self.overtaking_complete = False
        self.steps_ahead = 0

        self.episode_length = 0
        self.total_reward = 0
        self.collision_occurred = False
        self.violation_count = 0

        # 找到目标超车车辆（前方最近的慢车）
        self._find_target_vehicle()

        return obs, info

    def step(self, action):
        """执行一步

        Args:
            action: 动作

        Returns:
            observation, reward, terminated, truncated, info
        """
        obs, reward, terminated, truncated, info = self.env.step(action)

        self.episode_length += 1

        # 自定义奖励计算
        custom_reward, reward_info = self._compute_custom_reward(obs, action, info)

        # 检查违规
        violation = self._check_violation(obs)
        if violation:
            self.violation_count += 1

        # 检查超车状态
        self._update_overtaking_status(obs)

        # 更新info
        info.update({
            'reward_components': reward_info,
            'violation': violation,
            'overtaking_complete': self.overtaking_complete,
            'episode_length': self.episode_length,
            'violation_count': self.violation_count,
        })

        # 检查碰撞
        if info.get('crashed', False):
            self.collision_occurred = True

        self.total_reward += custom_reward

        return obs, custom_reward, terminated, truncated, info

    def _find_target_vehicle(self):
        """寻找目标超车车辆"""
        try:
            ego = self.env.unwrapped.vehicle
            vehicles = self.env.unwrapped.road.vehicles

            # 找到前方车道上最近的慢车
            candidates = []
            for v in vehicles:
                if v is not ego:
                    # 在ego前方
                    if v.position[0] > ego.position[0]:
                        # 速度较慢
                        threshold = self.config.get('overtaking_success', {}).get(
                            'reference_speed_threshold', 25
                        )
                        if v.velocity[0] < threshold:
                            distance = v.position[0] - ego.position[0]
                            candidates.append((distance, v))

            if candidates:
                # 选择最近的
                candidates.sort(key=lambda x: x[0])
                self.target_vehicle = candidates[0][1]

        except Exception as e:
            # 如果环境还没准备好，稍后再找
            pass

    def _compute_custom_reward(self, obs, action, info) -> Tuple[float, Dict]:
        """计算自定义奖励

        Args:
            obs: 观测
            action: 动作
            info: 信息字典

        Returns:
            (total_reward, reward_components)
        """
        weights = self.reward_weights
        components = {}

        # 基础奖励（来自原始环境）
        base_reward = info.get('rewards', {})

        # 碰撞惩罚
        if info.get('crashed', False):
            components['collision'] = weights.get('collision', -100)
        else:
            components['collision'] = 0

        # 速度奖励
        components['high_speed'] = base_reward.get('high_speed_reward', 0) * weights.get('high_speed_reward', 0.4)

        # 保持车道奖励
        components['right_lane'] = base_reward.get('right_lane_reward', 0) * weights.get('right_lane_reward', 0.1)

        # 在路上奖励
        components['on_road'] = base_reward.get('on_road_reward', 0) * weights.get('on_road_reward', 1.0)

        # 危险距离惩罚
        dangerous = self._check_dangerous_distance(obs)
        if dangerous:
            components['dangerous_distance'] = weights.get('dangerous_distance', -10)
        else:
            components['dangerous_distance'] = 0

        # 超车成功奖励
        if self.overtaking_complete and not hasattr(self, '_overtaking_rewarded'):
            components['overtaking_success'] = 50.0
            self._overtaking_rewarded = True
        else:
            components['overtaking_success'] = 0

        total = sum(components.values())

        return total, components

    def _check_dangerous_distance(self, obs) -> bool:
        """检查是否距离过近

        Args:
            obs: 观测向量

        Returns:
            是否危险
        """
        try:
            ego = self.env.unwrapped.vehicle
            vehicles = self.env.unwrapped.road.vehicles

            min_distance = self.safety_config.get('min_safe_distance', 15.0)

            for v in vehicles:
                if v is not ego:
                    distance = np.linalg.norm(v.position - ego.position)
                    if distance < min_distance:
                        return True

            return False
        except:
            return False

    def _check_violation(self, obs) -> bool:
        """检查是否违规（危险距离、换道等）

        Args:
            obs: 观测

        Returns:
            是否违规
        """
        return self._check_dangerous_distance(obs)

    def _update_overtaking_status(self, obs):
        """更新超车状态

        Args:
            obs: 观测
        """
        if self.target_vehicle is None or self.overtaking_complete:
            return

        try:
            ego = self.env.unwrapped.vehicle

            # 检查是否超过目标车辆
            if ego.position[0] > self.target_vehicle.position[0]:
                self.steps_ahead += 1

                # 保持领先一定步数则认为超车成功
                maintain_steps = self.config.get('overtaking_success', {}).get('maintain_steps', 30)
                if self.steps_ahead >= maintain_steps:
                    self.overtaking_complete = True
            else:
                self.steps_ahead = 0

        except:
            pass


def create_overtaking_env(config: Dict[str, Any], render_mode: str = None):
    """创建超车环境

    Args:
        config: 环境配置
        render_mode: 渲染模式 ('human', 'rgb_array', None)

    Returns:
        配置好的环境实例
    """
    # 获取交通密度
    # 支持三种输入方式：
    # 1. 字典 {'low': 10, 'medium': 20, 'high': 30} -> 使用'medium'
    # 2. 字符串 'medium' -> 从字典中查找
    # 3. 整数 20 -> 直接使用
    traffic_density = config.get('traffic_density', 'medium')

    if isinstance(traffic_density, dict):
        # 如果是字典，取'medium'（默认）
        vehicles_count = traffic_density.get('medium', 20)
    elif isinstance(traffic_density, str):
        # 如果是字符串，需要查找对应的数值
        # 尝试从同级配置中找density定义
        density_map = {
            'low': 10,
            'medium': 20,
            'high': 30
        }
        vehicles_count = density_map.get(traffic_density, 20)
    elif isinstance(traffic_density, int):
        # 如果是整数，直接使用
        vehicles_count = traffic_density
    else:
        # 默认值
        vehicles_count = 20

    # 创建highway-env环境
    env_config = {
        "observation": {
            "type": "Kinematics",
            "vehicles_count": config['observation']['vehicles_count'],
            "features": config['observation']['features'],
            "normalize": config['observation']['normalize'],
        },
        "action": {
            "type": "DiscreteMetaAction",
        },
        "lanes_count": config.get('lanes_count', 3),
        "vehicles_count": vehicles_count,
        "duration": config['episode']['duration'],
        "simulation_frequency": config['episode']['simulation_frequency'],
        "policy_frequency": config['episode']['policy_frequency'],
        "reward_speed_range": [config['speed']['min'], config['speed']['max']],
        "collision_reward": config['safety']['collision_reward'],
        "normalize_reward": False,
    }

    # 创建环境
    env = gym.make(
        config.get('env_name', 'highway-v0'),
        render_mode=render_mode or config.get('render_mode', 'rgb_array'),
        config=env_config
    )

    # 包装环境
    env = OvertakingEnvWrapper(env, config)

    # 确定密度名称（用于打印）
    density_name = 'custom'
    if isinstance(traffic_density, dict):
        density_name = 'medium (default)'
    elif isinstance(traffic_density, str):
        density_name = traffic_density

    print(f"✓ 创建环境: {density_name} 密度 ({vehicles_count} 辆车)")

    return env
