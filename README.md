# 基于强化学习的高速公路超车决策系统

本项目实现了基于强化学习的高速公路超车决策，包含基线策略、PPO算法和安全约束机制。

## 功能特性

- ✅ 高速公路超车仿真环境（基于highway-env）
- ✅ 规则基线策略（Rule-based Baseline）
- ✅ PPO强化学习算法
- ✅ Safety Shield安全约束层
- ✅ 完整评测指标体系（成功率、碰撞率、违规率等）
- ✅ 三组对比实验（Baseline vs RL vs RL+Safety）
- ✅ Windows一键运行

## 快速开始（Windows系统）

### 1. 环境安装

双击运行 `setup.bat`，或在命令行执行：

```bash
setup.bat
```

这将自动：
- 创建Python虚拟环境（使用conda或venv）
- 安装所有依赖包
- 验证安装是否成功

### 2. 训练模型

```bash
# 训练PPO模型
scripts\1_train_ppo.bat
```

训练日志保存在 `outputs/logs/`，模型保存在 `outputs/models/`

### 3. 运行评测

```bash
# 评测基线策略
scripts\2_eval_baseline.bat

# 评测RL策略
scripts\3_eval_rl.bat

# 评测RL+Safety策略
scripts\4_eval_rl_safety.bat
```

评测结果保存在 `outputs/results/`

### 4. 生成论文图表

```bash
# 生成所有图表和表格
scripts\5_generate_plots.bat
```

图表保存在 `outputs/figures/`

## 项目结构

```
highway_overtaking_rl/
├── configs/              # 配置文件
│   ├── env_config.yaml
│   ├── train_config.yaml
│   └── eval_config.yaml
├── src/
│   ├── env/              # 环境封装
│   ├── baseline/         # 基线策略
│   ├── rl/               # RL训练与评测
│   ├── metrics/          # 指标计算
│   └── utils/            # 工具函数
├── scripts/              # 运行脚本
├── outputs/              # 输出结果
└── demo/                 # 可视化演示
```

## 核心指标

- **超车成功率**：成功完成超车的比例
- **碰撞率**：发生碰撞的比例
- **违规率**：危险换道、距离过近的比例
- **平均速度**：episode平均速度
- **超车耗时**：成功超车所需平均时间

## 配置说明

### 交通密度

在 `configs/env_config.yaml` 中配置：

```yaml
traffic_density:
  low: 10      # 低密度：10辆车
  medium: 20   # 中密度：20辆车
  high: 30     # 高密度：30辆车
```

### 训练超参数

在 `configs/train_config.yaml` 中配置PPO超参数、训练步数等。

### 评测配置

在 `configs/eval_config.yaml` 中配置评测轮数、随机种子等。

## 论文支持

本项目输出的结果可直接用于论文写作：

- 第2章：环境设计 → 配置文件 + 代码注释
- 第3章：基线方法 → `src/baseline/rule_based.py`
- 第4章：RL算法 → `src/rl/train.py` + 训练日志
- 第5章：安全约束 → `src/rl/safety_shield.py`
- 第6章：实验结果 → `outputs/results/` + `outputs/figures/`

## 常见问题

### 1. 安装失败怎么办？

确保Python版本为3.8-3.10（推荐3.10），避免使用3.14。

### 2. 训练太慢？

可以减少 `train_config.yaml` 中的 `total_timesteps`，或使用更少的CPU核心。

### 3. 可视化界面？

运行 `streamlit run demo/streamlit_app.py` 启动Web界面。

## 技术支持

如有问题，请查看 `outputs/logs/` 中的日志文件。

---

**Python版本**：3.8-3.10
**主要依赖**：highway-env, stable-baselines3, gymnasium
