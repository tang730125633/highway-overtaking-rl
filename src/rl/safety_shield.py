"""Safety Shield - 安全约束层

对RL策略输出的动作进行安全检查和修正
"""

import numpy as np
from typing import Tuple, Dict


class SafetyShield:
    """安全约束层，用于过滤/修正不安全的动作"""

    def __init__(self, config: Dict):
        """初始化Safety Shield

        Args:
            config: 环境配置
        """
        self.config = config
        self.safety_config = config.get('safety', {})

        # 安全参数
        self.min_safe_distance = self.safety_config.get('min_safe_distance', 15.0)
        self.min_time_headway = self.safety_config.get('min_time_headway', 1.5)

        # 动作映射
        self.ACTIONS = {
            'LANE_LEFT': 0,
            'IDLE': 1,
            'LANE_RIGHT': 2,
            'FASTER': 3,
            'SLOWER': 4,
        }

        # 统计
        self.total_checks = 0
        self.total_interventions = 0
        self.intervention_reasons = {
            'unsafe_lane_change_left': 0,
            'unsafe_lane_change_right': 0,
            'too_close_front': 0,
        }

        print("✓ Safety Shield 初始化")
        print(f"  最小安全距离: {self.min_safe_distance}m")
        print(f"  最小时间头距: {self.min_time_headway}s")

    def check_and_correct(self, obs: np.ndarray, action: int) -> Tuple[int, bool]:
        """检查并修正动作

        Args:
            obs: 观测向量
            action: 原始动作

        Returns:
            (corrected_action, was_corrected)
        """
        self.total_checks += 1

        # 解析观测
        try:
            ego = obs[0]
            ego_vx = ego[3]
            vehicles = obs[1:]

            # 检查左换道
            if action == self.ACTIONS['LANE_LEFT']:
                if not self._is_safe_lane_change(vehicles, 'left', ego_vx):
                    self.total_interventions += 1
                    self.intervention_reasons['unsafe_lane_change_left'] += 1
                    return self.ACTIONS['IDLE'], True

            # 检查右换道
            elif action == self.ACTIONS['LANE_RIGHT']:
                if not self._is_safe_lane_change(vehicles, 'right', ego_vx):
                    self.total_interventions += 1
                    self.intervention_reasons['unsafe_lane_change_right'] += 1
                    return self.ACTIONS['IDLE'], True

            # 检查加速（是否会导致距离过近）
            elif action == self.ACTIONS['FASTER']:
                front = self._find_vehicle(vehicles, 'front', 'same')
                if front is not None:
                    distance = front[1]
                    if distance < self.min_safe_distance * 1.5:  # 留出余量
                        self.total_interventions += 1
                        self.intervention_reasons['too_close_front'] += 1
                        return self.ACTIONS['IDLE'], True

            # 动作安全，通过
            return action, False

        except Exception as e:
            # 解析失败，保持安全
            return self.ACTIONS['IDLE'], True

    def _is_safe_lane_change(self, vehicles: np.ndarray, direction: str, ego_vx: float) -> bool:
        """检查换道是否安全

        Args:
            vehicles: 车辆数组
            direction: 'left' or 'right'
            ego_vx: 自车速度

        Returns:
            是否安全
        """
        # 找到目标车道的前后车
        front = self._find_vehicle(vehicles, 'front', direction)
        rear = self._find_vehicle(vehicles, 'rear', direction)

        # 检查前车
        if front is not None:
            distance = front[1]
            if distance < self.min_safe_distance:
                return False

            # 检查时间头距
            relative_speed = front[3] - ego_vx
            if relative_speed < 0:
                time_headway = distance / abs(relative_speed) if abs(relative_speed) > 0.1 else float('inf')
                if time_headway < self.min_time_headway:
                    return False

        # 检查后车
        if rear is not None:
            distance = abs(rear[1])
            if distance < self.min_safe_distance:
                return False

        return True

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
            if v[0] < 0.5:  # presence
                continue

            x = v[1]  # 纵向
            y = v[2]  # 横向

            # 位置过滤
            if position == 'front' and x < 0:
                continue
            if position == 'rear' and x > 0:
                continue

            # 车道过滤
            if lane == 'same' and abs(y) > 0.1:
                continue
            if lane == 'left' and y < 0.1:
                continue
            if lane == 'right' and y > -0.1:
                continue

            candidates.append((abs(x), v))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    def get_statistics(self) -> Dict:
        """获取统计信息

        Returns:
            统计字典
        """
        intervention_rate = (self.total_interventions / self.total_checks * 100) if self.total_checks > 0 else 0

        return {
            'total_checks': self.total_checks,
            'total_interventions': self.total_interventions,
            'intervention_rate': intervention_rate,
            'intervention_reasons': self.intervention_reasons.copy(),
        }

    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("Safety Shield 统计")
        print("=" * 60)
        print(f"总检查次数:     {stats['total_checks']}")
        print(f"总干预次数:     {stats['total_interventions']}")
        print(f"干预率:         {stats['intervention_rate']:.2f}%")
        print("\n干预原因分布:")
        for reason, count in stats['intervention_reasons'].items():
            print(f"  {reason}: {count}")
        print("=" * 60 + "\n")

    def reset(self):
        """重置统计"""
        self.total_checks = 0
        self.total_interventions = 0
        self.intervention_reasons = {
            'unsafe_lane_change_left': 0,
            'unsafe_lane_change_right': 0,
            'too_close_front': 0,
        }
