# 如何上传到 GitHub

## 方法一：命令行（推荐）

### 1. 配置 Git 用户信息（首次使用）

```bash
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱"
```

### 2. 初始化并提交（如果还没做）

```bash
cd D:\PyCharm_AI
git init
git add .
git commit -m "Initial commit: AI Journal Dashboard"
```

### 3. 在 GitHub 创建仓库

1. 打开 https://github.com/new
2. 仓库名：`ai-journal-dashboard`
3. 描述：`Desktop widget for monitoring MCP Agent work logs`
4. 选择 **Public** 或 **Private**
5. **不要**勾选 "Add a README file"（我们已经有了）
6. 点击 **Create repository**

### 4. 关联远程仓库并推送

```bash
# 关联远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/ai-journal-dashboard.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 5. 后续更新

```bash
# 添加修改
git add .

# 提交
git commit -m "描述你的修改"

# 推送
git push
```

---

## 方法二：GitHub Desktop（图形界面）

### 1. 下载并安装 GitHub Desktop

https://desktop.github.com/

### 2. 登录 GitHub 账号

打开 GitHub Desktop → File → Options → Accounts → Sign in

### 3. 添加本地仓库

1. File → Add local repository
2. 选择 `D:\PyCharm_AI`
3. 如果提示"不是 Git 仓库"，点击 **Create a repository**

### 4. 发布到 GitHub

1. 点击顶部 **Publish repository**
2. 填写仓库名：`ai-journal-dashboard`
3. 描述：`Desktop widget for monitoring MCP Agent work logs`
4. 取消勾选 **Keep this code private**（如果想公开）
5. 点击 **Publish repository**

### 5. 后续更新

1. 在左侧看到修改的文件
2. 填写 Commit message
3. 点击 **Commit to main**
4. 点击 **Push origin**

---

## 方法三：VS Code（如果你用 VS Code）

### 1. 打开项目

```bash
code D:\PyCharm_AI
```

### 2. 初始化 Git（如果还没做）

1. 点击左侧 **Source Control** 图标
2. 点击 **Initialize Repository**

### 3. 提交

1. 在 Source Control 面板输入提交信息
2. 点击 ✓ 提交

### 4. 发布到 GitHub

1. 点击 **Publish to GitHub**
2. 选择 Public 或 Private
3. 确认

---

## 推送前检查清单

### ✅ 确认 .gitignore 正确

```bash
cat .gitignore
```

应该包含：
```
Dai_journalstore/
__pycache__/
*.pyc
.idea/
```

### ✅ 确认敏感信息已移除

检查 `config.json` 是否包含敏感路径：
```bash
cat config.json
```

如果有敏感信息，可以创建 `config.example.json`：
```json
{
  "store_path": "./Dai_journalstore",
  "window_opacity": 0.95,
  "auto_refresh": true,
  "refresh_interval": 2
}
```

然后把 `config.json` 加入 `.gitignore`：
```bash
echo "config.json" >> .gitignore
```

### ✅ 测试运行

```bash
python app.py
```

确保没有报错。

---

## 推送后优化

### 1. 添加 GitHub Topics

在仓库页面点击 ⚙️ Settings → 在 About 区域添加 Topics：
- `pyside6`
- `desktop-app`
- `python`
- `mcp`
- `dashboard`
- `log-viewer`

### 2. 添加 License

在仓库页面：
1. Add file → Create new file
2. 文件名输入 `LICENSE`
3. 右侧会出现 **Choose a license template**
4. 选择 **MIT License**
5. Commit

### 3. 添加 GitHub Actions（可选）

创建 `.github/workflows/test.yml`：
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python -m py_compile app.py
```

---

## 常见问题

### Q: 推送时要求输入用户名密码？

A: GitHub 已不支持密码认证，需要使用 Personal Access Token：

1. 访问 https://github.com/settings/tokens
2. Generate new token (classic)
3. 勾选 `repo` 权限
4. 生成后复制 token
5. 推送时用 token 代替密码

或者配置 SSH：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# 复制公钥到 https://github.com/settings/keys
git remote set-url origin git@github.com:YOUR_USERNAME/ai-journal-dashboard.git
```

### Q: 推送失败，提示 "rejected"？

A: 远程仓库有你本地没有的提交，先拉取：
```bash
git pull origin main --rebase
git push
```

### Q: 想修改提交历史？

A: 修改最后一次提交：
```bash
git commit --amend -m "新的提交信息"
git push --force
```

⚠️ 注意：`--force` 会覆盖远程历史，谨慎使用。

---

## 推荐的 README.md 结构

你的 `README.md` 已经很好，可以再加上：

```markdown
## Screenshots

![Main Widget](screenshots/main.png)
![Detail Dialog](screenshots/detail.png)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_USERNAME/ai-journal-dashboard&type=Date)](https://star-history.com/#YOUR_USERNAME/ai-journal-dashboard&Date)
```

记得截图放到 `screenshots/` 目录。

---

## 完整命令速查

```bash
# 首次推送
cd D:\PyCharm_AI
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱"
git init
git add .
git commit -m "Initial commit: AI Journal Dashboard"
git remote add origin https://github.com/YOUR_USERNAME/ai-journal-dashboard.git
git branch -M main
git push -u origin main

# 后续更新
git add .
git commit -m "Update: 描述修改内容"
git push
```

---

完成后，你的仓库地址是：
`https://github.com/YOUR_USERNAME/ai-journal-dashboard`
