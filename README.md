# Smart Payment Checkout

基于12年支付经验打造的智能支付收银台系统，支持多渠道支付（信用卡/支付宝/微信），集成AI风控和3DS验证。

## 项目概述

这是一个完整的支付收银台系统，包含以下核心功能：

1. **Checkout页面**：用户输入支付信息，选择支付方式
2. **支付路由**：根据支付方式调用不同渠道（信用卡/支付宝/微信）
3. **风控校验**：3DS 2.0验证 + LLM增强风险分析
4. **支付结果**：成功/失败/需复核，展示给用户

## 技术栈

- **前端**：HTML + CSS + JavaScript
- **后端**：Python + FastAPI
- **风控**：规则引擎 + LLM分析
- **部署**：本地开发环境（可扩展至AWS Lambda + API Gateway + S3）

## 支付流程

1. 用户打开Checkout页面
2. 输入金额和支付方式
3. 前端调用后端API
4. 后端进行风控校验（规则+LLM）
5. 低风险直接支付，高风险触发3DS验证
6. 调用支付渠道（模拟）
7. 返回结果并展示给用户

## 快速开始

### 后端服务

1. 进入后端目录
2. 创建虚拟环境并安装依赖
3. 启动服务

```bash
cd backend
uv venv
uv pip install -r requirements.txt
.venv\Scripts\activate
uvicorn app:app --reload
```

或者使用 `uv sync` 自动安装依赖：

```bash
cd backend
uv sync
uv run uvicorn app:app --reload
```

### 前端页面

1. 进入前端目录
2. 使用浏览器打开 `index.html` 文件

## 测试场景

| 场景 | 输入 | 预期结果 | 展示能力 |
|------|------|----------|----------|
| 正常小额 | 100元，老用户，本地IP | 直接成功，低风险 | 流畅支付 |
| 大额新用户 | 8000元，新用户，异地 | 触发3DS，LLM解释风险 | 风控敏感 |
| 跨境交易 | 5000元，中国卡，美国IP | 高风险，建议人工复核 | 跨境风控 |
| 支付宝/微信 | 200元，扫码支付 | 路由到对应渠道 | 多渠道支持 |

## 项目结构

```
smart-payment-checkout/
├── backend/
│   ├── app.py          # 后端主应用
│   ├── pyproject.toml  # 项目配置和依赖管理 (uv)
│   └── requirements.txt # 依赖项 (兼容性)
├── frontend/
│   └── index.html      # 前端页面
├── README.md           # 项目说明
└── project-planning.md  # 项目规划
```

## 包管理

本项目使用 **uv** 进行包管理，这是比 pip 更快的 Python 包管理器。

### 安装 uv

```bash
# 使用 pip 安装
pip install uv

# 或者使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 常用命令

```bash
# 创建虚拟环境
uv venv

# 安装依赖
uv pip install -r requirements.txt

# 同步项目依赖（推荐）
uv sync

# 运行应用
uv run uvicorn app:app --reload

# 添加新依赖
uv add <package-name>
```


