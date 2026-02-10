"""规则基线策略

基于状态机的超车决策策略
"""

import numpy as np
from typing import Dict, Any


class RuleBasedPolicy:
    """规则基线超车策略

    策略逻辑：
    1. 若前车速度过慢，尝试超车
    2. 选择更快的车道（左侧优先）
    3. 检查安全距离
    4. 超车后回到右车道
    """

    def __init__(self, config: Dict[str, Any]):
        """初始化基线策略

        Args:
            config: 配置字典
        """
        self.config = config
        self.safety_config = config.get('safety', {})

        # 参数
        self.min_safe_distance = self.safety_config.get('min_safe_distance', 15.0)
        self.min_time_headway = self.safety_config.get('min_time_headway', 1.5)
        self.slow_vehicle_threshold = config.get('overtaking_success', {}).get(
            'reference_speed_threshold', 25
        )

        # 动作映射
        self.ACTIONS = {
            'LANE_LEFT': 0,
            'IDLE': 1,
            'LANE_RIGHT': 2,
            'FASTER': 3,
            'SLOWER': 4,
        }

        # 冷却时间（防止频繁换道）
        self.lane_change_cooldown = 0
        self.cooldown_steps = 10

        print("✓ 规则基线策略初始化")
        print(f"  最小安全距离: {self.min_safe_distance}m")
        print(f"  慢车阈值: {self.slow_vehicle_threshold}km/h")

    def predict(self, observation, deterministic: bool = True):
        """预测动作

        Args:
            observation: 观测向量
            deterministic: 是否确定性（基线策略始终确定）

        Returns:
            (action, None) - 为了兼容SB3接口
        """
        action = self._compute_action(observation)
        return action, None

    def _compute_action(self, obs: np.ndarray) -> int:
        """计算动作

        Args:
            obs: 观测向量 [presence, x, y, vx, vy] × vehicles_count

        Returns:
            动作ID
        """
        # 更新冷却时间
        if self.lane_change_cooldown > 0:
            self.lane_change_cooldown -= 1

        # 解析观测（假设第一个是ego，后续是周围车辆）
        # highway-env的Kinematics观测格式：
        # [[presence, x, y, vx, vy], ...] for each vehicle

        try:
            # ego车辆（第一个）
            ego = obs[0]
            ego_y = ego[2]  # 横向位置（车道）
            ego_vx = ego[3]  # 纵向速度

            # 周围车辆
            vehicles = obs[1:]

            # 找到各个位置的车辆
            front_vehicle = self._find_vehicle(vehicles, position='front', lane='same')
            left_front = self._find_vehicle(vehicles, position='front', lane='left')
            left_rear = self._find_vehicle(vehicles, position='rear', lane='left')
            right_front = self._find_vehicle(vehicles, position='front', lane='right')
            right_rear = self._find_vehicle(vehicles, position='rear', lane='right')

            # 决策逻辑

            # 1. 如果前车很慢，尝试超车
            if front_vehicle is not None:
                front_vx = front_vehicle[3]
                front_distance = front_vehicle[1]  # x相对位置

                # 前车慢且距离较近
                if front_vx < self.slow_vehicle_threshold and front_distance < 50:
                    # 尝试换到左车道
                    if self._is_safe_to_change_lane(left_front, left_rear, ego_vx):
                        if self.lane_change_cooldown == 0:
                            self.lane_change_cooldown = self.cooldown_steps
                            return self.ACTIONS['LANE_LEFT']

                    # 如果左车道不安全，减速跟车
                    if front_distance < self.min_safe_distance:
                        return self.ACTIONS['SLOWER']

            # 2. 如果在左车道且右边安全，回到右车道
            if ego_y > 0.1:  # 在左车道（y>0表示左侧）
                if self._is_safe_to_change_lane(right_front, right_rear, ego_vx):
                    if self.lane_change_cooldown == 0:
                        self.lane_change_cooldown = self.cooldown_steps
                        return self.ACTIONS['LANE_RIGHT']

            # 3. 加速到目标速度
            target_speed = self.config.get('speed', {}).get('ego_target', 30)
            if ego_vx < target_speed:
                return self.ACTIONS['FASTER']

            # 4. 默认保持
            return self.ACTIONS['IDLE']

        except Exception as e:
            # 如果解析失败，保持安全
            return self.ACTIONS['IDLE']

    def _find_vehicle(self, vehicles: np.ndarray, position: str, lane: str) -> np.ndarray:
        """找到指定位置和车道的车辆

        Args:
            vehicles: 车辆数组
            position: 'front' or 'rear'
            lane: 'same', 'left', 'right'

        Returns:
            车辆向量或None
        """
        candidates = []

        for v in vehicles:
            if v[0] < 0.5:  # presence < 0.5表示不存在
                continue

            x = v[1]  # 纵向相对位置
            y = v[2]  # 横向相对位置

            # 检查位置（前/后）
            if position == 'front' and x < 0:
                continue
            if position == 'rear' and x > 0:
                continue

            # 检查车道
            if lane == 'same' and abs(y) > 0.1:
                continue
            if lane == 'left' and y < 0.1:  # 左车道 y > 0
                continue
            if lane == 'right' and y > -0.1:  # 右车道 y < 0
                continue

            candidates.append((abs(x), v))

        if not candidates:
            return None

        # 返回最近的
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    def _is_safe_to_change_lane(self, front: np.ndarray, rear: np.ndarray, ego_vx: float) -> bool:
        """检查换道是否安全

        Args:
            front: 前车
            rear: 后车
            ego_vx: 自车速度

        Returns:
            是否安全
        """
        # 检查前车
        if front is not None:
            distance = front[1]  # x相对位置
            if distance < self.min_safe_distance:
                return False

            # 检查时间头距
            relative_speed = front[3] - ego_vx
            if relative_speed < 0:  # 前车更慢
                time_headway = distance / abs(relative_speed) if abs(relative_speed) > 0.1 else float('inf')
                if time_headway < self.min_time_headway:
                    return False

        # 检查后车
        if rear is not None:
            distance = abs(rear[1])
            if distance < self.min_safe_distance:
                return False

        return True

    def reset(self):
        """重置策略状态"""
        self.lane_change_cooldown = 0
