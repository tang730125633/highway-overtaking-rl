"""高速公路超车RL系统 - 可视化Web界面

使用方法：
    python -m streamlit run app.py
    或双击 start_app.bat (Windows) / start_app.command (Mac)
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import subprocess
import time
from datetime import datetime

# 添加项目路径 - 支持本地和Streamlit Cloud
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.env.overtaking_env import create_overtaking_env
from src.baseline.rule_based import RuleBasedPolicy
from src.rl.safety_shield import SafetyShield
from src.metrics.evaluator import MetricsEvaluator, evaluate_policy
from src.utils.config_loader import load_yaml
from stable_baselines3 import PPO

# 配置页面
st.set_page_config(
    page_title="高速公路超车RL系统",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_all_results():
    """加载所有评测结果"""
    results_dir = Path("outputs/outputs/results")
    if not results_dir.exists():
        return {}

    results = {}
    for json_file in results_dir.glob("*_metrics_summary.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results[json_file.stem] = data

    return results


@st.cache_resource
def load_model(model_path):
    """加载训练好的模型"""
    try:
        model = PPO.load(model_path)
        return model
    except Exception as e:
        st.error(f"加载模型失败: {e}")
        return None


def show_dashboard():
    """显示项目Dashboard"""
    st.markdown('<div class="main-header">🚗 高速公路超车强化学习系统</div>', unsafe_allow_html=True)

    # 项目信息
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("项目状态", "✅ 完成", delta="100%")

    with col2:
        st.metric("训练步数", "100,000", delta="已完成")

    with col3:
        results = load_all_results()
        st.metric("评测结果", f"{len(results)}组", delta="27组完成")

    with col4:
        model_path = Path("outputs/outputs/models/best/best_model.zip")
        if model_path.exists():
            st.metric("运行模式", "💻 本地完整版", delta="可训练")
        else:
            st.metric("运行模式", "☁️ 在线演示版", delta="查看结果")

    st.markdown("---")

    # 快速概览
    st.subheader("📊 快速概览")

    if results:
        # 提取各方法的平均性能
        baseline_results = [v for k, v in results.items() if k.startswith("baseline_")]
        rl_results = [v for k, v in results.items() if k.startswith("rl_") and "safety" not in k]
        rl_safety_results = [v for k, v in results.items() if k.startswith("rl_safety_")]

        # 计算平均值
        def avg_metric(results_list, metric):
            if not results_list:
                return 0
            return np.mean([r.get(metric, 0) for r in results_list])

        metrics_df = pd.DataFrame({
            "方法": ["规则基线", "RL (PPO)", "RL + Safety Shield"],
            "成功率 (%)": [
                avg_metric(baseline_results, "success_rate"),
                avg_metric(rl_results, "success_rate"),
                avg_metric(rl_safety_results, "success_rate")
            ],
            "碰撞率 (%)": [
                avg_metric(baseline_results, "collision_rate"),
                avg_metric(rl_results, "collision_rate"),
                avg_metric(rl_safety_results, "collision_rate")
            ],
            "违规率 (%)": [
                avg_metric(baseline_results, "violation_rate"),
                avg_metric(rl_results, "violation_rate"),
                avg_metric(rl_safety_results, "violation_rate")
            ]
        })

        # 显示表格
        st.dataframe(metrics_df.style.format({
            "成功率 (%)": "{:.2f}",
            "碰撞率 (%)": "{:.2f}",
            "违规率 (%)": "{:.2f}"
        }), use_container_width=True)

        # 对比柱状图
        fig = go.Figure()

        for metric in ["成功率 (%)", "碰撞率 (%)", "违规率 (%)"]:
            fig.add_trace(go.Bar(
                name=metric,
                x=metrics_df["方法"],
                y=metrics_df[metric],
                text=metrics_df[metric].round(2),
                textposition='outside'
            ))

        fig.update_layout(
            title="三种方法性能对比",
            xaxis_title="方法",
            yaxis_title="百分比 (%)",
            barmode='group',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无评测结果，请先运行评测。")

    # 项目说明
    st.markdown("---")
    st.subheader("📖 项目说明")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **核心功能**：
        - ✅ 高速公路超车环境模拟
        - ✅ 规则基线策略
        - ✅ PPO强化学习算法
        - ✅ Safety Shield安全约束
        - ✅ 多场景对比实验
        - ✅ 完整评测指标
        """)

    with col2:
        st.markdown("""
        **技术栈**：
        - 环境: highway-env 1.10.2
        - 算法: Stable-Baselines3 PPO
        - 可视化: Streamlit + Plotly
        - Python: 3.10.13
        """)


def show_evaluation():
    """交互式评测页面"""
    st.header("🔬 交互式评测")

    # 检查模型是否存在
    model_path = Path("outputs/outputs/models/best/best_model.zip")
    model_available = model_path.exists()

    if not model_available:
        st.info("""
        ℹ️ **在线演示模式**

        由于模型文件较大（约100MB），未上传到云端。

        **在线可用功能**：
        - ✅ 查看已有评测结果（27组完整数据）
        - ✅ 多方法对比分析
        - ✅ 论文图表展示
        - ✅ 数据下载

        **本地可用功能**：
        - 📍 交互式评测（需要下载完整项目）
        - 📍 模型训练

        如需完整功能，请下载项目到本地运行。
        """)

        st.markdown("---")
        st.subheader("📥 如何在本地运行？")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Windows用户**：
            ```cmd
            1. 下载项目压缩包
            2. 双击 start_app.bat
            3. 浏览器自动打开
            ```
            """)

        with col2:
            st.markdown("""
            **Mac/Linux用户**：
            ```bash
            git clone https://github.com/tang730125633/highway-overtaking-rl.git
            cd highway-overtaking-rl
            python -m streamlit run app.py
            ```
            """)

        return  # 不显示评测界面

    # 评测配置
    col1, col2, col3 = st.columns(3)

    with col1:
        method = st.selectbox(
            "选择评测方法",
            ["规则基线", "RL (PPO)", "RL + Safety Shield"],
            help="选择要评测的策略方法"
        )

    with col2:
        density = st.selectbox(
            "交通密度",
            ["low", "medium", "high"],
            index=1,
            help="low=10辆车, medium=20辆车, high=30辆车"
        )

    with col3:
        seed = st.selectbox(
            "随机种子",
            [42, 123, 456],
            help="不同种子会产生不同的随机场景"
        )

    n_episodes = st.slider("评测轮数", min_value=5, max_value=50, value=20, step=5)

    # 运行评测按钮
    if st.button("🚀 开始评测", type="primary"):
        with st.spinner("正在运行评测，请稍候..."):
            try:
                # 加载配置
                env_config = load_yaml("configs/env_config.yaml")

                # 创建环境
                env_config['traffic_density'] = density
                env = create_overtaking_env(env_config)

                # 选择策略
                if method == "规则基线":
                    policy = RuleBasedPolicy()
                    prefix = f"baseline_{density}_seed{seed}_"
                elif method == "RL (PPO)":
                    model_path = "outputs/outputs/models/best/best_model"
                    model = load_model(model_path)
                    if model is None:
                        st.error("未找到训练好的模型，请先训练模型！")
                        return
                    policy = model
                    prefix = f"rl_{density}_seed{seed}_"
                else:  # RL + Safety Shield
                    model_path = "outputs/outputs/models/best/best_model"
                    model = load_model(model_path)
                    if model is None:
                        st.error("未找到训练好的模型，请先训练模型！")
                        return

                    # 包装Safety Shield
                    class SafetyWrappedPolicy:
                        def __init__(self, model, env):
                            self.model = model
                            self.safety_shield = SafetyShield(env)

                        def predict(self, obs, deterministic=True):
                            action, _ = self.model.predict(obs, deterministic=deterministic)
                            safe_action = self.safety_shield.filter_action(obs, action)
                            return safe_action, None

                    policy = SafetyWrappedPolicy(model, env)
                    prefix = f"rl_safety_{density}_seed{seed}_"

                # 运行评测
                evaluator, episodes_data = evaluate_policy(
                    env, policy, n_episodes=n_episodes,
                    deterministic=True, seed=seed
                )

                # 保存结果
                results_dir = Path("outputs/outputs/results")
                metrics = evaluator.save_results(str(results_dir), prefix)

                # 显示结果
                st.success("✅ 评测完成！")

                # 显示指标
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("成功率", f"{metrics['success_rate']:.2f}%")

                with col2:
                    st.metric("碰撞率", f"{metrics['collision_rate']:.2f}%")

                with col3:
                    st.metric("违规率", f"{metrics['violation_rate']:.2f}%")

                with col4:
                    st.metric("平均奖励", f"{metrics['avg_reward']:.2f}")

                # 详细结果表
                st.subheader("详细结果")
                df = pd.DataFrame(episodes_data)
                st.dataframe(df, use_container_width=True)

                # 刷新缓存
                load_all_results.clear()

            except Exception as e:
                st.error(f"评测过程中出错: {e}")
                st.exception(e)


def show_results():
    """查看评测结果页面"""
    st.header("📈 评测结果查看")

    results = load_all_results()

    if not results:
        st.warning("暂无评测结果，请先运行评测。")
        return

    # 结果选择
    result_names = sorted(results.keys())
    selected_result = st.selectbox("选择查看的结果", result_names)

    if selected_result:
        data = results[selected_result]

        # 显示指标卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("成功率", f"{data['success_rate']:.2f}%")

        with col2:
            st.metric("碰撞率", f"{data['collision_rate']:.2f}%")

        with col3:
            st.metric("违规率", f"{data['violation_rate']:.2f}%")

        with col4:
            st.metric("平均奖励", f"{data['avg_reward']:.2f}")

        # 详细数据
        st.subheader("详细指标")

        metrics_data = {
            "指标": [
                "总Episodes数",
                "成功率 (%)",
                "碰撞率 (%)",
                "违规率 (%)",
                "平均违规次数",
                "平均奖励",
                "平均速度 (km/h)",
                "平均Episode长度 (步)",
                "成功超车平均时间 (步)"
            ],
            "数值": [
                data['total_episodes'],
                f"{data['success_rate']:.2f}",
                f"{data['collision_rate']:.2f}",
                f"{data['violation_rate']:.2f}",
                f"{data['avg_violations_per_episode']:.2f}",
                f"{data['avg_reward']:.2f}",
                f"{data['avg_speed']:.2f}",
                f"{data['avg_episode_length']:.1f}",
                f"{data['avg_success_time']:.1f}" if data['avg_success_time'] > 0 else "N/A"
            ]
        }

        st.table(pd.DataFrame(metrics_data))

        # CSV详细数据
        csv_file = Path("outputs/outputs/results") / f"{selected_result.replace('_metrics_summary', '_episodes_detail')}.csv"
        if csv_file.exists():
            st.subheader("Episode详细数据")
            df = pd.read_csv(csv_file)
            st.dataframe(df, use_container_width=True)

            # 下载按钮
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载CSV数据",
                data=csv_data,
                file_name=csv_file.name,
                mime="text/csv"
            )


def show_comparison():
    """多方法对比页面"""
    st.header("📊 多方法对比分析")

    results = load_all_results()

    if not results:
        st.warning("暂无评测结果，请先运行评测。")
        return

    # 分组结果
    baseline_results = {k: v for k, v in results.items() if k.startswith("baseline_")}
    rl_results = {k: v for k, v in results.items() if k.startswith("rl_") and "safety" not in k}
    rl_safety_results = {k: v for k, v in results.items() if k.startswith("rl_safety_")}

    # 选择对比维度
    comparison_type = st.radio(
        "选择对比维度",
        ["按密度对比", "按种子对比", "总体对比"],
        horizontal=True
    )

    if comparison_type == "按密度对比":
        density = st.selectbox("选择密度", ["low", "medium", "high"], index=1)

        # 筛选指定密度的结果
        baseline_data = [v for k, v in baseline_results.items() if f"_{density}_" in k]
        rl_data = [v for k, v in rl_results.items() if f"_{density}_" in k]
        rl_safety_data = [v for k, v in rl_safety_results.items() if f"_{density}_" in k]

        # 计算平均值
        def avg_metrics(data_list):
            if not data_list:
                return {}
            return {
                "success_rate": np.mean([d['success_rate'] for d in data_list]),
                "collision_rate": np.mean([d['collision_rate'] for d in data_list]),
                "violation_rate": np.mean([d['violation_rate'] for d in data_list]),
                "avg_reward": np.mean([d['avg_reward'] for d in data_list]),
            }

        baseline_avg = avg_metrics(baseline_data)
        rl_avg = avg_metrics(rl_data)
        rl_safety_avg = avg_metrics(rl_safety_data)

        # 创建对比图表
        metrics = ["success_rate", "collision_rate", "violation_rate"]
        metric_names = ["成功率 (%)", "碰撞率 (%)", "违规率 (%)"]

        fig = go.Figure()

        methods = []
        if baseline_avg:
            methods.append(("规则基线", baseline_avg))
        if rl_avg:
            methods.append(("RL (PPO)", rl_avg))
        if rl_safety_avg:
            methods.append(("RL + Safety", rl_safety_avg))

        for metric, name in zip(metrics, metric_names):
            values = [data[metric] for _, data in methods]
            fig.add_trace(go.Bar(
                name=name,
                x=[m[0] for m in methods],
                y=values,
                text=[f"{v:.2f}" for v in values],
                textposition='outside'
            ))

        fig.update_layout(
            title=f"{density.upper()}密度 - 多方法对比",
            xaxis_title="方法",
            yaxis_title="百分比 (%)",
            barmode='group',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    elif comparison_type == "总体对比":
        # 所有结果的总体统计
        all_methods = {
            "规则基线": list(baseline_results.values()),
            "RL (PPO)": list(rl_results.values()),
            "RL + Safety": list(rl_safety_results.values())
        }

        comparison_data = []

        for method_name, method_results in all_methods.items():
            if method_results:
                comparison_data.append({
                    "方法": method_name,
                    "成功率 (%)": np.mean([r['success_rate'] for r in method_results]),
                    "碰撞率 (%)": np.mean([r['collision_rate'] for r in method_results]),
                    "违规率 (%)": np.mean([r['violation_rate'] for r in method_results]),
                    "平均奖励": np.mean([r['avg_reward'] for r in method_results]),
                })

        df = pd.DataFrame(comparison_data)

        st.dataframe(df.style.format({
            "成功率 (%)": "{:.2f}",
            "碰撞率 (%)": "{:.2f}",
            "违规率 (%)": "{:.2f}",
            "平均奖励": "{:.2f}"
        }), use_container_width=True)

        # 雷达图对比
        fig = go.Figure()

        for _, row in df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row['成功率 (%)'], 100-row['碰撞率 (%)'], 100-row['违规率 (%)'], (row['平均奖励']+200)/2],
                theta=['成功率', '安全性(低碰撞)', '合规性(低违规)', '奖励'],
                fill='toself',
                name=row['方法']
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="总体性能雷达图",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)


def show_figures():
    """查看生成的图表"""
    st.header("🖼️ 论文图表")

    figures_dir = Path("outputs/outputs/figures")

    if not figures_dir.exists():
        st.warning("图表目录不存在，请先生成图表。")
        return

    # 查找所有PNG文件
    png_files = list(figures_dir.glob("*.png"))

    if not png_files:
        st.info("暂无生成的图表，运行可视化脚本生成图表：")
        st.code("python -m src.utils.visualize --results-dir outputs/outputs/results --output-dir outputs/outputs/figures")

        if st.button("🎨 立即生成图表"):
            with st.spinner("正在生成图表..."):
                try:
                    result = subprocess.run(
                        ["python", "-m", "src.utils.visualize",
                         "--results-dir", "outputs/outputs/results",
                         "--output-dir", "outputs/outputs/figures"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        st.success("✅ 图表生成完成！")
                        st.rerun()
                    else:
                        st.error(f"生成失败: {result.stderr}")
                except Exception as e:
                    st.error(f"生成过程中出错: {e}")
    else:
        # 显示图表
        for png_file in sorted(png_files):
            st.subheader(png_file.stem)
            st.image(str(png_file), use_column_width=True)

            # 下载按钮
            with open(png_file, 'rb') as f:
                st.download_button(
                    label=f"📥 下载 {png_file.name}",
                    data=f,
                    file_name=png_file.name,
                    mime="image/png"
                )


def main():
    """主函数"""
    # 侧边栏导航
    st.sidebar.title("📚 导航菜单")

    page = st.sidebar.radio(
        "选择页面",
        [
            "🏠 项目Dashboard",
            "🔬 交互式评测",
            "📈 查看结果",
            "📊 多方法对比",
            "🖼️ 论文图表"
        ]
    )

    # 侧边栏信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 使用说明")
    st.sidebar.markdown("""
    1. **项目Dashboard**: 查看项目整体状态
    2. **交互式评测**: 运行新的评测实验
    3. **查看结果**: 查看已有评测结果
    4. **多方法对比**: 对比不同方法性能
    5. **论文图表**: 查看生成的可视化图表
    """)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ 项目信息")
    st.sidebar.info("""
    **项目**: 高速公路超车强化学习系统

    **版本**: 1.0.0
    """)

    # 路由到不同页面
    if page == "🏠 项目Dashboard":
        show_dashboard()
    elif page == "🔬 交互式评测":
        show_evaluation()
    elif page == "📈 查看结果":
        show_results()
    elif page == "📊 多方法对比":
        show_comparison()
    elif page == "🖼️ 论文图表":
        show_figures()


if __name__ == "__main__":
    main()
