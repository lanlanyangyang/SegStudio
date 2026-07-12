# SegStudio

SegStudio 是一个面向红细胞图像分割的轻量级桌面应用，包含普通模式查看结果、管理员模式训练与模型管理，以及管理员密码修改功能。

## 1. 环境要求

- Windows 10/11
- Python 3.10 或 3.11
- Git

## 2. 本地运行

在项目根目录执行：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

如果你使用的是当前工作区的虚拟环境，也可以直接运行：

```bash
D:\SegStudio\.venv\Scripts\python.exe app/main.py
```

## 3. 发布给别人

当前项目最稳妥的方式是把整个项目文件夹打包给别人，或者只发给别人下面这几个目录：

- app/
- models/
- data/
- requirements.txt

别人收到后可以直接在本机创建虚拟环境并运行：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

## 4. GitHub 发布流程

### 5.1 初始化 Git 仓库

```bash
git init
git add .
git commit -m "Initial commit"
```

### 5.2 创建 GitHub 仓库

1. 打开 GitHub
2. 点击 New repository
3. 输入仓库名，例如：SegStudio
4. 选择 Public 或 Private
5. 创建仓库

### 5.3 关联远程仓库

```bash
git remote add origin https://github.com/你的用户名/SegStudio.git
git branch -M main
git push -u origin main
```

### 5.4 后续更新

```bash
git add .
git commit -m "Update UI and password feature"
git push
```

## 6. 工作日志建议

建议把以下内容记录下来：

- 本次完成的功能
- 遇到的错误与解决方案
- 性能优化点
- 未来待办项

例如：

- 增加普通模式结果查看与过滤逻辑
- 增加管理员密码修改弹窗
- 优化启动时模型加载路径
- 解决 PySide6 与路径依赖问题

## 7. 说明

如果你想让别人更容易使用，建议把项目打包为一个单独的 exe，并附上简短使用说明。
