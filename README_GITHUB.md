# 🚗 高速公路超车强化学习系统

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 基于强化学习的高速公路自动超车决策系统 - 完整的研究项目与可视化界面

---

## 🌟 在线体验

**🎮 [点击这里访问在线演示](https://share.streamlit.io)** ← 无需安装，直接使用！

---

## 📚 项目简介

本项目实现了一个完整的高速公路自动超车决策系统，对比了**规则基线**、**强化学习(PPO)** 和 **安全约束强化学习(RL+Safety Shield)** 三种方法。

### 🎯 核心功能

- ✅ **高速公路仿真环境** - 基于 highway-env 的真实交通模拟
- ✅ **规则基线策略** - 基于安全距离的状态机决策
- ✅ **PPO强化学习** - 使用 Stable-Baselines3 训练的自主决策策略
- ✅ **Safety Shield** - 动作过滤层，保证安全约束
- ✅ **完整评测体系** - 3密度 × 3种子 × 3方法 = 27组对比实验
- ✅ **可视化Web界面** - 基于 Streamlit 的交互式界面

---

## 🖼️ 界面预览

### 主控面板
![Dashboard](https://via.placeholder.com/800x400/1f77b4/ffffff?text=Dashboard+-+项目总览)

### 交互式评测
![Evaluation](https://via.placeholder.com/800x400/2ca02c/ffffff?text=Interactive+Evaluation+-+实时评测)

### 结果可视化
![Results](https://via.placeholder.com/800x400/ff7f0e/ffffff?text=Results+Visualization+-+数据分析)

---

## 📊 实验结果

| 方法 | 成功率 | 碰撞率 | 违规率 | 特点 |
|------|--------|--------|--------|------|
| **规则基线** | 15-25% | 0-10% | 50-70% | 稳定但保守 |
| **RL (PPO)** | 0% | 45-60% | 40-60% | 训练不足* |
| **RL+Safety** | 10-20% | 20-40% | 20-40% | **安全性提升** |

> *训练步数仅100k，增加到300k-500k可显著提升性能

**关键发现**：Safety Shield将碰撞率从60%降低至20-40%，证明了安全约束机制的有效性。

---

## 🚀 快速开始

### 方式一：在线体验（推荐）

直接访问 → **[在线演示链接](https://share.streamlit.io)** ← 无需任何配置！

### 方式二：本地运行

#### Windows
```cmd
1. 解压项目文件夹
2. 双击 setup.bat 安装环境
3. 双击 start_app.bat 启动Web界面
```

#### Mac/Linux
```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/highway-overtaking-rl.git
cd highway-overtaking-rl

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动Web界面
python -m streamlit run app.py
```

浏览器自动打开：`http://localhost:8501`

---

## 🛠️ 技术栈

### 核心框架
- **环境**: [highway-env](https://github.com/Farama-Foundation/HighwayEnv) 1.10.2
- **强化学习**: [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3) 2.7.1
- **深度学习**: PyTorch 2.10.0
- **可视化**: Streamlit 1.28+ / Plotly 5.17+

### 算法
- **PPO** (Proximal Policy Optimization) - 主要RL算法
- **Safety Shield** - 基于规则的安全过滤层
- **State Machine** - 规则基线决策逻辑

---

## 📂 项目结构

```
highway_overtaking_rl/
├── app.py                      # Streamlit Web应用主程序
├── src/
│   ├── env/
│   │   └── overtaking_env.py   # 环境封装
│   ├── baseline/
│   │   ├── rule_based.py       # 规则基线策略
│   │   └── evaluate_baseline.py
│   ├── rl/
│   │   ├── train.py            # PPO训练
│   │   ├── evaluate.py         # RL评测
│   │   └── safety_shield.py    # 安全约束层
│   ├── metrics/
│   │   └── evaluator.py        # 指标计算
│   └── utils/
│       ├── config_loader.py
│       └── visualize.py        # 图表生成
├── configs/
│   ├── env_config.yaml         # 环境配置
│   ├── train_config.yaml       # 训练配置
│   └── eval_config.yaml        # 评测配置
├── outputs/
│   ├── models/                 # 训练好的模型
│   ├── results/                # 评测结果(JSON+CSV)
│   └── figures/                # 论文图表(PNG)
└── docs/                       # 完整文档
```

---

## 📈 使用场景

### 1. 学术研究
- 强化学习算法对比研究
- 安全约束机制验证
- 毕业论文/课程项目

### 2. 教学演示
- 强化学习入门教学
- 自动驾驶决策展示
- 交互式实验平台

### 3. 二次开发
- 完整的代码框架
- 详细的配置文件
- 可扩展的模块设计

---

## 🎓 论文支持

本项目提供完整的论文写作支持：

### 第2章：环境设计
- 环境配置：`configs/env_config.yaml`
- 实现代码：`src/env/overtaking_env.py`

### 第3章：基线方法
- 策略实现：`src/baseline/rule_based.py`
- 评测结果：`outputs/results/baseline_*.json`

### 第4章：强化学习
- 训练代码：`src/rl/train.py`
- 算法配置：`configs/train_config.yaml`
- 评测结果：`outputs/results/rl_*.json`

### 第5章：安全约束
- Shield实现：`src/rl/safety_shield.py`
- 评测结果：`outputs/results/rl_safety_*.json`
- 干预统计：46.92%干预率

### 第6章：实验结果
- 可视化图表：`outputs/figures/*.png`
- 详细数据：所有JSON和CSV文件

---

## 📊 数据说明

### 评测指标
- **成功率**：完成超车的episode比例
- **碰撞率**：发生碰撞的episode比例
- **违规率**：发生违规行为的episode比例
- **平均奖励**：episode平均累积奖励
- **平均速度**：episode平均行驶速度
- **Episode长度**：平均决策步数

### 文件格式
- **JSON**: 汇总指标（27个文件）
- **CSV**: 详细数据（27个文件，每个包含20个episodes）
- **PNG**: 可视化图表（2张对比图）

---

## ⚙️ 系统要求

- **操作系统**: Windows 10/11, macOS, Linux
- **Python**: 3.8 - 3.10（⚠️ 不支持3.14）
- **内存**: 建议 ≥8GB
- **硬盘**: ≥2GB 空闲空间

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📮 联系方式

- **项目主页**: [GitHub Repository](https://github.com/YOUR_USERNAME/highway-overtaking-rl)
- **问题反馈**: [Issues](https://github.com/YOUR_USERNAME/highway-overtaking-rl/issues)

---

## 🙏 致谢

- [highway-env](https://github.com/Farama-Foundation/HighwayEnv) - 高速公路仿真环境
- [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3) - 强化学习算法库
- [Streamlit](https://streamlit.io/) - Web应用框架

---

## 📚 相关资源

- [强化学习入门教程](https://spinningup.openai.com/)
- [PPO算法论文](https://arxiv.org/abs/1707.06347)
- [Gymnasium文档](https://gymnasium.farama.org/)

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**

---
