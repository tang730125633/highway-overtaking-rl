# 部署指南 - Streamlit Cloud免费部署

本文档提供两种使用方式：本地运行和云端部署。

## 方式一：本地运行（推荐用于开发测试）

### Windows用户

**双击运行**：
```
start_app.bat
```

**或命令行运行**：
```cmd
python -m streamlit run app.py
```

### Mac用户

**双击运行**：
```
start_app.command
```

**或命令行运行**：
```bash
python3 -m streamlit run app.py
```

浏览器会自动打开：`http://localhost:8501`

---

## 方式二：Streamlit Cloud免费部署（推荐用于分享）

### 为什么选择Streamlit Cloud？

✅ **完全免费** - 无需信用卡
✅ **自动部署** - 推送代码即自动更新
✅ **快速分享** - 一个链接，全球访问
✅ **无需服务器** - 零运维成本

### 部署步骤

#### 1. 准备GitHub仓库

**方式A：使用现有仓库**（如果已有）
- 确保项目代码已推送到GitHub

**方式B：创建新仓库**
```bash
# 1. 在GitHub上创建新仓库（不要初始化README）
# 仓库名建议：highway-overtaking-rl

# 2. 在本地项目目录执行
cd /Users/tang/Desktop/highway_overtaking_rl

# 3. 初始化git（如果还没有）
git init
git add .
git commit -m "Initial commit: Highway Overtaking RL System"

# 4. 关联远程仓库（替换为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/highway-overtaking-rl.git
git branch -M main
git push -u origin main
```

#### 2. 在Streamlit Cloud部署

**步骤详解**：

1. **访问Streamlit Cloud**
   - 打开：https://share.streamlit.io/
   - 点击 "Sign up" 或 "Sign in with GitHub"

2. **授权GitHub**
   - 使用GitHub账号登录
   - 授权Streamlit访问你的仓库

3. **新建应用**
   - 点击 "New app"
   - 选择你的仓库：`YOUR_USERNAME/highway-overtaking-rl`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL（可选）：自定义域名前缀

4. **高级设置（可选）**
   - Python version: 3.10
   - Secrets: 如果有API密钥等敏感信息

5. **部署**
   - 点击 "Deploy!"
   - 等待3-5分钟（首次部署会安装依赖）

6. **完成！**
   - 获得永久链接，例如：
     ```
     https://YOUR-APP-NAME.streamlit.app
     ```
   - 分享给客户即可访问

#### 3. 自动更新

**非常简单**：推送代码，自动部署！

```bash
# 修改代码后
git add .
git commit -m "Update features"
git push

# Streamlit会自动检测并重新部署（约2-3分钟）
```

---

## 部署配置文件

### `.streamlit/config.toml`（可选优化）

创建配置文件以自定义应用：

```bash
mkdir -p .streamlit
cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
EOF
```

### `packages.txt`（可选系统依赖）

如果需要额外的系统包：

```bash
cat > packages.txt << 'EOF'
# 添加系统级依赖（如果需要）
# 例如：
# libgl1-mesa-glx
# libglib2.0-0
EOF
```

---

## 常见问题

### Q1: 部署后显示"Module not found"

**原因**：requirements.txt未包含所有依赖

**解决**：
```bash
# 更新requirements.txt
pip freeze > requirements.txt

# 提交并推送
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Q2: 应用启动慢

**原因**：首次加载需安装大量依赖

**解决**：
- 首次启动需3-5分钟，之后只需10-20秒
- 优化：使用`@st.cache_data`和`@st.cache_resource`装饰器

### Q3: 免费版限制

**Streamlit Cloud免费版**：
- ✅ 无限公开应用
- ✅ 1 GB RAM per app
- ✅ 1 CPU core
- ✅ GitHub集成
- ⚠️ 应用7天无访问会休眠（首次访问会唤醒）

**如果需要更多资源**：
- 升级到团队版（$20/月，3个私有应用）
- 或部署到Heroku/AWS/Azure等

### Q4: 如何设置密码保护？

在应用中添加密码验证：

```python
# 在app.py顶部添加
def check_password():
    """密码验证"""
    def password_entered():
        if st.session_state["password"] == "your_password_here":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("请输入密码", type="password",
                     on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("请输入密码", type="password",
                     on_change=password_entered, key="password")
        st.error("密码错误")
        return False
    else:
        return True

if not check_password():
    st.stop()
```

---

## 性能优化建议

### 1. 缓存优化

```python
@st.cache_data
def load_results():
    # 缓存数据加载
    pass

@st.cache_resource
def load_model():
    # 缓存模型加载（不可序列化对象）
    pass
```

### 2. 懒加载

```python
# 只在需要时加载重量级依赖
if page == "运行评测":
    from src.rl.train import train_ppo
```

### 3. 异步操作

```python
import asyncio

async def run_evaluation():
    # 长时间运行的任务
    pass
```

---

## 分享给客户

**推荐做法**：

1. **短链接**（使用bit.ly等）
   ```
   原链接：https://highway-overtaking-rl.streamlit.app
   短链接：https://bit.ly/highway-rl
   ```

2. **添加说明文档**
   - 在应用首页添加使用说明
   - 提供操作视频或GIF演示

3. **收集反馈**
   ```python
   # 在侧边栏添加反馈入口
   st.sidebar.markdown("---")
   feedback = st.sidebar.text_area("💬 反馈建议")
   if st.sidebar.button("提交反馈"):
       # 保存到文件或发送邮件
       pass
   ```

---

## 监控和维护

### 查看应用日志

1. 登录Streamlit Cloud
2. 进入你的应用
3. 点击右下角的三点菜单
4. 选择 "Logs" 查看实时日志

### 应用管理

- **暂停应用**：Settings → Pause app
- **删除应用**：Settings → Delete app
- **更新配置**：修改GitHub代码自动同步

---

## 成本对比

| 方案 | 成本 | 优点 | 缺点 |
|------|------|------|------|
| **Streamlit Cloud** | 免费 | 简单快速，自动部署 | 7天无访问会休眠 |
| **Heroku** | $7/月起 | 不休眠，自定义域名 | 需要信用卡 |
| **AWS/GCP** | $5-20/月 | 高性能，可扩展 | 配置复杂 |
| **本地运行** | 免费 | 完全控制 | 无法远程访问 |

**推荐**：对于这个项目，**Streamlit Cloud免费版**完全够用！

---

## 快速部署检查清单

- [ ] 代码已推送到GitHub
- [ ] requirements.txt包含所有依赖
- [ ] app.py在项目根目录
- [ ] 已注册Streamlit Cloud账号
- [ ] 已授权GitHub仓库访问
- [ ] 应用部署成功（绿色对勾）
- [ ] 测试所有功能正常
- [ ] 分享链接给客户

---

## 技术支持

如有问题，查阅：
- Streamlit文档：https://docs.streamlit.io
- Streamlit社区：https://discuss.streamlit.io
- GitHub Issues：https://github.com/streamlit/streamlit/issues

---

**祝部署顺利！🚀**
