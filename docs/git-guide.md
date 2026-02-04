# Git 版本控制指南

## 什么是 Git

Git 是一个分布式版本控制系统，用于跟踪文件的更改并协调多人之间的工作。它由 Linus Torvalds 于 2005 年创建，最初用于 Linux 内核开发。

## 安装 Git

### Windows

下载 Git for Windows：https://git-scm.com/download/win

### macOS

```bash
brew install git
```

### Linux

```bash
sudo apt install git  # Ubuntu/Debian
sudo yum install git  # CentOS/RHEL
```

## 基本配置

安装完成后，需要配置用户信息：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 常用命令

### 初始化仓库

```bash
# 在当前目录初始化新仓库
git init

# 克隆远程仓库
git clone https://github.com/user/repo.git
```

### 基本操作

```bash
# 查看状态
git status

# 添加文件到暂存区
git add filename
git add .  # 添加所有更改

# 提交更改
git commit -m "提交信息"

# 查看提交历史
git log
git log --oneline  # 简洁模式
```

### 分支操作

```bash
# 查看分支
git branch

# 创建新分支
git branch feature-name

# 切换分支
git checkout feature-name
git switch feature-name  # Git 2.23+

# 创建并切换分支
git checkout -b feature-name

# 合并分支
git merge feature-name

# 删除分支
git branch -d feature-name
```

### 远程操作

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin https://github.com/user/repo.git

# 推送到远程
git push origin main

# 拉取远程更改
git pull origin main

# 获取远程更改（不合并）
git fetch origin
```

## 工作流程

### Git Flow

1. **main/master**: 主分支，存放稳定版本
2. **develop**: 开发分支，日常开发在此进行
3. **feature/***: 功能分支，开发新功能
4. **release/***: 发布分支，准备新版本发布
5. **hotfix/***: 热修复分支，修复生产环境问题

### GitHub Flow

1. 从 main 创建功能分支
2. 在功能分支上开发
3. 创建 Pull Request
4. 代码审查
5. 合并到 main

## 常见问题

### 撤销更改

```bash
# 撤销工作区更改
git checkout -- filename

# 撤销暂存区更改
git reset HEAD filename

# 撤销最近一次提交（保留更改）
git reset --soft HEAD~1

# 撤销最近一次提交（丢弃更改）
git reset --hard HEAD~1
```

### 解决冲突

当合并分支时发生冲突：

1. 打开冲突文件，找到冲突标记
2. 手动编辑解决冲突
3. 删除冲突标记
4. 添加并提交解决后的文件
