# SegStudio

> A lightweight desktop application for medical image segmentation based on deep learning.

## 📖 Introduction

SegStudio 是一个基于 Python 开发的医学图像分割桌面应用，面向红细胞图像智能分割场景，实现了图像加载、模型推理、结果可视化以及模型管理等功能。

项目采用模块化设计，可作为医学图像分割算法验证平台，也可作为深度学习模型部署的基础框架。

---

## ✨ Features

* 🖼️ 图像加载与预览
* 🤖 深度学习模型推理
* 🎯 红细胞智能分割
* 📊 分割结果可视化
* 🔐 管理员模式
* ⚙️ 模型管理
* 🧪 模型训练入口
* 🔑 管理员密码修改

---

## 📂 Project Structure

```text
SegStudio
│
├── app/                # GUI 与业务逻辑
├── models/             # 深度学习模型
├── tests/              # 测试代码
├── requirements.txt    # 项目依赖
├── README.md
└── .gitignore
```

---

## 🛠️ Technology Stack

* Python 3.10+
* PySide6
* PyTorch
* OpenCV
* NumPy

---

## 🚀 Quick Start

### Clone

```bash
git clone https://github.com/lanlanyangyang/SegStudio.git
cd SegStudio
```

### Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
python app/main.py
```

---

## 🎯 Future Work

* 支持更多医学图像类型
* 增加批量预测
* GPU 推理加速
* 导出分割结果
* 多模型切换

---

## 📄 License

This project is for learning and academic research only.
