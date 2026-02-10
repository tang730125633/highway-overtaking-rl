# Streamlit Cloud 部署问题排查指南

> 📝 本文档记录了将 highway-overtaking-rl 项目部署到 Streamlit Cloud 时遇到的所有问题及解决方案。
>
> **目标读者**: 未来的 AI 助手和开发者
>
> **创建日期**: 2026-02-10
>
> **部署成功地址**: https://highway-overtaking-rl-nqix5tw3ry3vbxkymfjnj5.streamlit.app

---

## 📋 快速检查清单

在部署到 Streamlit Cloud 之前，请务必完成以下检查：

- [ ] **Python 版本**: requirements.txt 中指定 Python 3.10-3.13（避免 3.14 的 pygame 兼容性问题）
- [ ] **包结构完整性**:
  - [ ] 所有目录都有 `__init__.py` 文件
  - [ ] 所有 `__init__.py` 文件已被 git 跟踪（`git ls-files | grep __init__.py`）
- [ ] **导入语句一致性**:
  - [ ] 使用完整导入路径（如 `from src.env.overtaking_env import create_overtaking_env`）
  - [ ] 避免简写导入（如 `from src.env import create_overtaking_env`）
- [ ] **文件 git 跟踪状态**:
  - [ ] 核心文件未被 .gitignore 排除
  - [ ] 使用 `git ls-files` 验证所有必要文件已提交
  - [ ] 在 GitHub 上验证文件存在（使用浏览器或 curl）
- [ ] **大文件处理**:
  - [ ] 模型文件（>.50MB）已排除或使用 Git LFS
  - [ ] 应用代码包含优雅的文件缺失处理逻辑
- [ ] **Streamlit 配置**:
  - [ ] Repository、Branch、Main file path 配置正确
  - [ ] requirements.txt 包含所有依赖

---

## 🐛 问题 #1: ImportError - 函数名错误

### 错误信息
```
ImportError: cannot import name 'OvertakingEnv' from 'src.env.overtaking_env'
ImportError: cannot import name 'load_config' from 'src.utils.config_loader'
```

### 根本原因
- `app.py` 中使用了错误的函数/类名
- 实际存在的是 `create_overtaking_env` 函数（而不是 `OvertakingEnv` 类）
- 实际存在的是 `load_yaml` 函数（而不是 `load_config` 函数）

### 解决方案
1. 检查源文件实际导出的函数/类名
```bash
grep "^def\|^class" src/env/overtaking_env.py
grep "^def\|^class" src/utils/config_loader.py
```

2. 修正 `app.py` 中的导入语句
```python
# 修改前
from src.env.overtaking_env import OvertakingEnv
from src.utils.config_loader import load_config

# 修改后
from src.env.overtaking_env import create_overtaking_env
from src.utils.config_loader import load_yaml
```

### 预防措施
- 在本地先运行 `streamlit run app.py` 测试
- 使用 IDE 的自动导入功能
- 保持导入语句与源文件定义一致

---

## 🐛 问题 #2: ModuleNotFoundError - 缺少包初始化文件

### 错误信息
```
ModuleNotFoundError: No module named 'src.env'
```

### 根本原因
- Python 包必须包含 `__init__.py` 文件才能被识别为模块
- `src/__init__.py` 文件缺失，导致 Python 无法将 `src` 识别为包

### 解决方案
1. 创建所有必要的 `__init__.py` 文件
```bash
# 创建顶层包初始化文件
echo "# src package" > src/__init__.py

# 创建子包初始化文件
echo '"""环境模块"""

from .overtaking_env import create_overtaking_env

__all__ = ["create_overtaking_env"]' > src/env/__init__.py
```

2. 验证所有包目录都有 `__init__.py`
```bash
find src -type d -exec test -f {}/__init__.py \; -print
```

### 预防措施
- 在创建新的 Python 包时，**第一步就是创建 `__init__.py`**
- 定期检查 `git ls-files | grep __init__.py` 确保所有初始化文件已提交

---

## 🐛 问题 #3: 导入路径不一致

### 错误信息
```
ModuleNotFoundError: No module named 'src.env'
```
（即使 `src/env/__init__.py` 存在，仍然报错）

### 根本原因
- 项目中存在两种导入风格：
  - `from src.env import create_overtaking_env` （依赖 __init__.py 的重导出）
  - `from src.env.overtaking_env import create_overtaking_env` （直接导入）
- 当 `__init__.py` 未正确配置时，第一种方式会失败

### 解决方案
1. **推荐做法**：统一使用完整路径导入
```bash
# 批量替换所有文件中的导入语句
sed -i '' 's/from src\.env import create_overtaking_env/from src.env.overtaking_env import create_overtaking_env/g' \
  src/baseline/evaluate_baseline.py \
  src/rl/train.py \
  src/rl/evaluate.py
```

2. **替代做法**：确保 `__init__.py` 正确导出
```python
# src/env/__init__.py
from .overtaking_env import create_overtaking_env

__all__ = ['create_overtaking_env']
```

### 预防措施
- 在项目开始时确定导入风格规范
- 使用 linter 检查导入一致性
- 优先使用完整路径导入（更明确、更可靠）

---

## 🐛 问题 #4: 文件存在本地但未被 git 跟踪

### 错误信息
```
ModuleNotFoundError: No module named 'src.env.overtaking_env'
```

### 根本原因
- 关键文件（如 `src/env/overtaking_env.py`、`src/env/__init__.py`）存在于本地
- 但这些文件未被 git 跟踪，因此未推送到 GitHub
- Streamlit Cloud 从 GitHub 拉取代码，导致文件缺失

### 诊断方法
1. 检查文件是否被 git 跟踪
```bash
git ls-files | grep "src/env/"
```

2. 在 GitHub 上验证文件存在
```bash
# 使用 curl 检查文件是否在 GitHub 上
curl -s https://raw.githubusercontent.com/tang730125633/highway-overtaking-rl/main/src/env/__init__.py | head -n 5
```

3. 检查 .gitignore 是否误排除了文件
```bash
git check-ignore -v src/env/overtaking_env.py
```

### 解决方案
1. 强制添加被忽略的文件
```bash
git add -f src/env/__init__.py
git add -f src/env/overtaking_env.py
```

2. 提交并推送
```bash
git commit -m "Fix: 添加缺失的环境模块文件"
git push origin main
```

3. **关键验证步骤**：在 GitHub 网页上确认文件已上传
- 访问 `https://github.com/你的用户名/你的仓库/blob/main/src/env/overtaking_env.py`
- 确保文件内容正确显示

### 预防措施
- 在每次推送后，**必须在 GitHub 上验证关键文件已上传**
- 谨慎配置 .gitignore，避免误排除源代码文件
- 使用 `git status` 和 `git ls-files` 交叉验证

---

## 🐛 问题 #5: 大文件导致的模型加载失败

### 错误信息
```
FileNotFoundError: [Errno 2] No such file or directory: 'outputs/outputs/models/best/best_model.zip'
```

### 根本原因
- 训练好的模型文件通常很大（~100MB）
- Git 仓库有文件大小限制（单文件 <100MB，推荐 <50MB）
- .gitignore 排除了模型文件，导致 Streamlit Cloud 上无法加载模型

### 解决方案 #1: 优雅降级（推荐用于演示型项目）
修改 `app.py` 检测模型文件是否存在，并提供不同的用户体验：

```python
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
        """)
        return  # 不显示评测界面

    # 正常的评测逻辑...
```

在 Dashboard 中显示部署状态：
```python
# 检测是否有模型文件
model_available = Path("outputs/outputs/models/best/best_model.zip").exists()
deployment_mode = "💻 本地完整版" if model_available else "☁️ 在线演示版"

st.sidebar.success(f"**部署状态**: {deployment_mode}")
```

### 解决方案 #2: 使用 Git LFS（适用于需要在云端加载模型的场景）
```bash
# 安装 Git LFS
brew install git-lfs  # macOS
git lfs install

# 跟踪大文件
git lfs track "*.zip"
git lfs track "outputs/outputs/models/**/*.zip"

# 提交 .gitattributes
git add .gitattributes
git commit -m "Add Git LFS tracking for model files"

# 正常提交模型文件
git add outputs/outputs/models/best/best_model.zip
git commit -m "Add trained model with Git LFS"
git push origin main
```

**注意**: Streamlit Cloud 的 Git LFS 配额有限，免费版可能不够用。

### 解决方案 #3: 外部存储（生产环境推荐）
将模型文件上传到外部存储（如 AWS S3、Google Cloud Storage），在应用启动时下载：

```python
import requests
from pathlib import Path

def download_model():
    model_path = Path("outputs/outputs/models/best/best_model.zip")
    if not model_path.exists():
        url = "https://your-storage.com/best_model.zip"
        response = requests.get(url)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_path.write_bytes(response.content)
```

### 预防措施
- 在设计应用时，考虑大文件的处理策略
- 为不同部署环境（本地/云端）设计不同的功能集
- 使用功能开关（feature flags）控制功能可用性

---

## ⚙️ Streamlit Cloud 配置检查清单

### 部署配置
在 Streamlit Cloud 部署页面，确保以下配置正确：

| 配置项 | 正确值 | 说明 |
|--------|--------|------|
| **Repository** | `tang730125633/highway-overtaking-rl` | GitHub 仓库完整路径 |
| **Branch** | `main` | 主分支 |
| **Main file path** | `app.py` | Streamlit 应用入口文件 |
| **Python version** | `3.10` | 在 .streamlit/config.toml 或环境变量中指定 |

### requirements.txt 必备依赖
```txt
streamlit==1.54.0
stable-baselines3==2.7.1
gymnasium==1.2.3
highway-env==1.10.2
torch==2.10.0
pygame==2.6.1
matplotlib==3.10.8
seaborn==0.13.2
pandas==2.3.3
pyyaml==6.0.3
```

### Python 版本问题
⚠️ **避免使用 Python 3.14**：
- pygame 2.6.1 在 Python 3.14 上有已知的 circular import 问题
- 推荐使用 Python 3.10-3.13

在 `.streamlit/config.toml` 中指定 Python 版本（如果支持）：
```toml
[server]
pythonVersion = "3.10"
```

---

## 🔍 调试技巧

### 1. 查看 Streamlit Cloud 日志
- 进入 Streamlit Cloud 应用管理页面
- 点击右下角的 "Manage app" > "Logs"
- 下载日志文件进行详细分析

### 2. 本地模拟 Streamlit Cloud 环境
```bash
# 创建干净的虚拟环境
python3.10 -m venv test_env
source test_env/bin/activate

# 仅使用 requirements.txt 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

### 3. 验证 GitHub 文件完整性
```bash
# 列出所有被跟踪的 Python 文件
git ls-files | grep ".py$"

# 检查特定目录
git ls-files | grep "src/env/"

# 使用 curl 验证 GitHub 上的文件
curl -s https://raw.githubusercontent.com/你的用户名/你的仓库/main/src/env/__init__.py
```

### 4. 对比本地和 GitHub 的文件
```bash
# 获取 GitHub 上的文件
curl -s https://raw.githubusercontent.com/tang730125633/highway-overtaking-rl/main/src/env/overtaking_env.py > /tmp/github_version.py

# 对比本地文件
diff src/env/overtaking_env.py /tmp/github_version.py
```

---

## 📝 完整部署流程（推荐顺序）

### 步骤 1: 本地验证
```bash
# 1. 检查所有 __init__.py 文件
find src -type d -exec test -f {}/__init__.py \; -print

# 2. 验证导入语句
python -c "from src.env.overtaking_env import create_overtaking_env; print('✓ Import OK')"

# 3. 本地运行测试
streamlit run app.py
```

### 步骤 2: Git 提交前检查
```bash
# 1. 查看所有将被提交的文件
git status

# 2. 验证关键文件已被跟踪
git ls-files | grep -E "(src/.*\.py$|app.py|requirements.txt)"

# 3. 如果文件缺失，强制添加
git add -f src/env/__init__.py
git add -f src/env/overtaking_env.py

# 4. 提交
git commit -m "Deploy: 完整的 Streamlit 应用（包含所有模块）"
```

### 步骤 3: GitHub 验证
```bash
# 推送到 GitHub
git push origin main

# 验证关键文件已上传
curl -s https://raw.githubusercontent.com/你的用户名/你的仓库/main/src/env/__init__.py | head -n 5
curl -s https://raw.githubusercontent.com/你的用户名/你的仓库/main/src/env/overtaking_env.py | head -n 5
```

### 步骤 4: Streamlit Cloud 配置
1. 访问 https://share.streamlit.io
2. 点击 "New app"
3. 填写配置：
   - Repository: `你的用户名/你的仓库`
   - Branch: `main`
   - Main file path: `app.py`
4. 点击 "Deploy"

### 步骤 5: 部署后验证
1. 等待部署完成（通常 2-5 分钟）
2. 查看日志，确认无错误
3. 访问应用 URL，测试所有功能
4. 如果有错误：
   - 下载日志文件
   - 根据错误信息查阅本文档
   - 修复后重新推送代码（Streamlit Cloud 会自动重新部署）

---

## 🎯 常见错误速查表

| 错误信息 | 可能原因 | 解决方案编号 |
|---------|---------|-------------|
| `ImportError: cannot import name 'XXX'` | 函数/类名错误 | 问题 #1 |
| `ModuleNotFoundError: No module named 'src.env'` | 缺少 `__init__.py` | 问题 #2 |
| `ModuleNotFoundError` 且 `__init__.py` 存在 | 文件未被 git 跟踪 | 问题 #4 |
| 导入在本地正常但云端失败 | 导入路径不一致 | 问题 #3 |
| `FileNotFoundError: ... best_model.zip` | 大文件未上传 | 问题 #5 |
| pygame circular import | Python 版本太新 | 使用 Python 3.10-3.13 |

---

## 🚀 成功部署的完整案例

**项目**: highway-overtaking-rl
**部署地址**: https://highway-overtaking-rl-nqix5tw3ry3vbxkymfjnj5.streamlit.app
**部署时间**: 2026-02-10
**遇到的问题**: 问题 #1, #2, #3, #4, #5（全部）
**解决时间**: 约 2 小时

**关键成功因素**:
1. 使用完整的导入路径（`from src.env.overtaking_env import`）
2. 强制添加所有 `__init__.py` 文件到 git
3. 在 GitHub 上验证文件完整性后再部署
4. 优雅处理缺失的模型文件（功能降级）
5. 使用 Python 3.10（避免 pygame 兼容性问题）

---

## 📚 参考资源

- [Streamlit Cloud 官方文档](https://docs.streamlit.io/streamlit-community-cloud)
- [Git LFS 文档](https://git-lfs.github.com/)
- [Python 包管理最佳实践](https://docs.python.org/3/tutorial/modules.html)
- [Streamlit Community Forum](https://discuss.streamlit.io/)

---

## ✅ 最终检查清单（部署前必查）

打印此清单，逐项检查：

- [ ] Python 版本: 3.10-3.13 ✓
- [ ] 所有目录有 `__init__.py` ✓
- [ ] `git ls-files` 显示所有关键文件 ✓
- [ ] GitHub 上验证文件存在 ✓
- [ ] 导入语句使用完整路径 ✓
- [ ] requirements.txt 包含所有依赖 ✓
- [ ] 本地 `streamlit run app.py` 正常运行 ✓
- [ ] .gitignore 未误排除源代码 ✓
- [ ] 大文件有优雅降级逻辑 ✓
- [ ] Streamlit Cloud 配置正确 ✓

---

**文档维护者**: Claude Code
**最后更新**: 2026-02-10
**版本**: 1.0

如果您在部署过程中遇到本文档未覆盖的问题，请将错误信息和解决方案补充到此文档中，造福后来者。🙏
