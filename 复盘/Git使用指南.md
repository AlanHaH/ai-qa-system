# Git 使用指南

## 什么是 Git？

Git 是一个**版本管理工具**，用来记录代码的每一次修改，方便回退和多人协作。

**类比**：就像游戏的存档功能，你可以随时保存进度，出问题了可以回档。

---

## 核心概念

```
工作区（你写的代码）
    ↓ git add
暂存区（准备提交的代码）
    ↓ git commit
本地仓库（已保存的版本）
    ↓ git push
远程仓库（GitHub 上的备份）
```

- **工作区**：你正在编辑的文件
- **暂存区**：标记"这些文件我要提交"
- **本地仓库**：保存一个版本快照
- **远程仓库**：GitHub 上的备份，别人也能看到

---

## 常用命令

### 初始化（第一次用）

```powershell
git init                    # 在当前目录创建 Git 仓库
```

### 日常提交（每次改完代码）

```powershell
git add .                   # 把所有修改加入暂存区
git commit -m "改了什么"     # 提交到本地仓库
git push                    # 推送到 GitHub
```

### 查看状态

```powershell
git status                  # 查看哪些文件被修改了
git log                     # 查看提交历史
git log --oneline           # 简洁版提交历史
```

### 拉取代码（从 GitHub 下载最新代码）

```powershell
git pull                    # 拉取并合并
```

### 分支操作

```powershell
git branch                  # 查看当前分支
git branch dev              # 创建 dev 分支
git checkout dev            # 切换到 dev 分支
git checkout -b dev         # 创建并切换（上面两条合并）
git merge dev               # 把 dev 合并到当前分支
git branch -d dev           # 删除 dev 分支
```

---

## .gitignore 文件

告诉 Git 哪些文件**不要提交**。

**本项目的 .gitignore**：
```
# Python
backend/venv/          # 虚拟环境（太大，别人自己装）
__pycache__/           # Python 缓存文件
*.pyc                  # 编译后的 Python 文件

# 前端依赖
frontend/node_modules/ # 前端依赖（太大，别人 npm install 自己装）

# 环境变量
backend/.env           # 含 API Key，不能公开

# IDE
.idea/                 # PyCharm 配置
.vscode/               # VS Code 配置
```

---

## 配置代理（国内访问 GitHub）

```powershell
git config --global http.proxy http://127.0.0.1:10808
git config --global https.proxy http://127.0.0.1:10808
```

把 `10808` 换成你代理软件的实际端口。

取消代理：
```powershell
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

## 常见问题

### 提交时中文乱码

只是终端显示问题，不影响实际内容。Git 里存的还是中文。

### push 被拒绝（non-fast-forward）

远程有本地没有的提交，先拉取：
```powershell
git pull --rebase origin main
git push
```

### 撤销上次提交（还没 push）

```powershell
git reset --soft HEAD~1     # 撤销提交，保留修改
```

### 撤销某个文件的修改

```powershell
git checkout -- 文件名       # 恢复到上次提交的版本
```

### 查看某个文件改了什么

```powershell
git diff 文件名
```

---

## 本项目的 Git 工作流

```
1. 写代码 / 改代码
2. git add .                    # 添加到暂存区
3. git commit -m "改了什么"      # 提交到本地
4. git push                     # 推送到 GitHub
```

**注意**：
- `backend/.env` 不会被提交（在 .gitignore 里），所以 API Key 不会泄露
- `node_modules/` 和 `venv/` 也不会被提交，别人克隆后需要自己安装依赖

---

## 克隆仓库（别人怎么下载你的代码）

```powershell
git clone https://github.com/AlanHaH/ai-qa-system.git
cd ai-qa-system
```

然后分别安装依赖：
```powershell
# 后端
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 前端
cd frontend
npm install
```
