# Windows 用户使用说明

> 📦 **高速公路超车RL系统 - 本地版**
>
> 这是一个已经训练好的强化学习系统，包含完整的评测结果和可视化界面。

---

## ⚡ 快速开始（3步）

### 步骤 1: 安装 Python（如果没有）

1. 下载 Python 3.10：https://www.python.org/downloads/release/python-31013/
2. 安装时**务必勾选** "Add Python to PATH"
3. 安装完成后重启电脑

**验证安装**：
- 按 `Win + R`，输入 `cmd`，回车
- 输入 `python --version`，应该显示 `Python 3.10.13`

---

### 步骤 2: 解压项目文件

将 `highway_overtaking_rl.zip` 解压到任意位置，比如：
```
C:\Users\你的用户名\Desktop\highway_overtaking_rl\
```

⚠️ **注意**：路径中不要有中文！

---

### 步骤 3: 双击启动

在解压后的文件夹中，**双击** 👇

```
start_app.bat
```

等待几秒，浏览器会自动打开：`http://localhost:8501`

---

## 📂 项目文件说明

```
highway_overtaking_rl/
│
├── start_app.bat          ⭐ 双击这个启动Web界面
├── setup.bat              🔧 首次运行自动安装依赖
├── quick_start.bat        🚀 完整流程（训练+评测，需30-60分钟）
│
├── app.py                 📱 Web界面主程序
├── requirements.txt       📦 依赖列表
│
├── outputs/               📊 所有结果（已生成）
│   ├── results/           ├─ CSV评测数据（27组）
│   ├── figures/           └─ 论文图表（PNG）
│   └── models/            └─ 训练好的模型
│
└── src/                   💻 源代码
    ├── env/               ├─ 环境定义
    ├── baseline/          ├─ 基线策略
    ├── rl/                ├─ PPO强化学习
    └── metrics/           └─ 评测指标
```

---

## 🎯 Web 界面功能

启动后，你可以：

1. **📊 查看Dashboard**
   - 项目概览
   - 27组评测结果汇总

2. **📈 查看评测结果**
   - 按方法筛选（Baseline / RL / RL+Safety）
   - 按场景筛选（低/中/高密度）
   - 查看详细指标（成功率、碰撞率、效率等）

3. **📊 方法对比**
   - 多方法性能对比图表
   - 雷达图、柱状图、箱线图

4. **📖 论文图表**
   - 直接显示论文中的所有图表
   - 高分辨率PNG，可直接用于论文

5. **💾 下载数据**
   - 下载原始CSV数据
   - 用于进一步分析

---

## ❓ 常见问题

### Q1: 双击 `start_app.bat` 后闪退怎么办？

**原因**：没有安装 Python 或 Python 未添加到 PATH

**解决**：
1. 重新安装 Python，**务必勾选** "Add Python to PATH"
2. 或手动添加 Python 到环境变量

### Q2: 提示 "未找到Python" 怎么办？

**解决**：
1. 打开 `cmd`，输入 `python --version` 检查
2. 如果显示版本号，说明已安装，可能是路径问题
3. 尝试以**管理员身份**运行 `start_app.bat`

### Q3: 浏览器没有自动打开怎么办？

**解决**：
- 手动打开浏览器，访问：`http://localhost:8501`

### Q4: 启动后显示 "在线演示模式" 怎么办？

**原因**：模型文件缺失（通常是因为打包时排除了大文件）

**影响**：
- ✅ 可以查看所有27组评测结果
- ✅ 可以查看所有图表和对比
- ❌ 无法运行新的评测（不影响查看已有结果）

**解决**（如果需要完整功能）：
- 从云端下载完整项目：https://highway-overtaking-rl-nqix5tw3ry3vbxkymfjnj5.streamlit.app

### Q5: 如何重新训练模型？

如果你想从头训练模型：

1. 双击 `quick_start.bat`（需要30-60分钟）
2. 或者按步骤手动运行：
   ```
   scripts\1_train_ppo.bat        # 训练模型
   scripts\2_eval_baseline.bat    # 评测基线
   scripts\3_eval_rl.bat          # 评测RL
   scripts\4_eval_rl_safety.bat   # 评测RL+Safety
   scripts\5_generate_plots.bat   # 生成图表
   ```

---

## 🌐 在线版本

如果本地运行有问题，可以直接访问在线版：

**🔗 https://highway-overtaking-rl-nqix5tw3ry3vbxkymfjnj5.streamlit.app**

（在线版功能完全相同，但无法重新训练模型）

---

## 📞 技术支持

如果遇到问题：
1. 查看上方 "常见问题"
2. 检查 Python 版本是否为 3.10-3.13（不要用3.14）
3. 确保路径中没有中文
4. 以管理员身份运行

---

## ✅ 确认检查清单

在联系支持前，请确认：

- [ ] 已安装 Python 3.10-3.13
- [ ] Python 已添加到 PATH（`python --version` 可以运行）
- [ ] 项目已完整解压（包含 `outputs` 文件夹）
- [ ] 路径中没有中文
- [ ] 以管理员身份运行 `start_app.bat`
- [ ] 防火墙允许 Python 访问网络

---

**祝你使用愉快！** 🎉
