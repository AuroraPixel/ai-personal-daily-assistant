# AI 个人日常助手项目 (AI Personal Daily Assistant)

一个基于 Python 后端的人工智能个人日常助手项目，旨在帮助用户管理日常任务和提供智能化服务。

## 项目结构 (Project Structure)

```
ai-personal-daily-assistant/
├── backend/                    # Python 后端服务 (Python backend service)
│   ├── agent/                 # AI 代理模块 (AI agent modules)
│   ├── api/                   # API 接口 (API endpoints)
│   ├── core/                  # 核心功能模块 (Core functionality)
│   ├── remote_api/            # 远程 API 客户端 (Remote API clients)
│   ├── service/               # 业务服务层 (Business service layer)
│   └── main.py                # 主入口文件 (Main entry point)
├── ui/                        # 前端界面 (Frontend UI)
└── README.md                  # 项目说明文档 (Project documentation)
```

## 后端环境配置 (Backend Environment Setup)

### 前置要求 (Prerequisites)

- Python 3.8+ 
- pip (Python 包管理器)

### 1. 创建虚拟环境 (Create Virtual Environment)

在项目根目录下执行以下命令：

```bash
# 创建虚拟环境 (Create virtual environment)
python -m venv venv

# 或者使用 python3 (Or use python3)
python3 -m venv venv
```

### 2. 激活虚拟环境 (Activate Virtual Environment)

**在 macOS/Linux 系统：**
```bash
source venv/bin/activate
```

**在 Windows 系统：**
```bash
# PowerShell
venv\Scripts\Activate.ps1

# 命令提示符 (Command Prompt)
venv\Scripts\activate.bat
```

激活成功后，终端提示符前会显示 `(venv)` 标识。

### 3. 安装依赖包 (Install Dependencies)

```bash
# 进入后端目录 (Navigate to backend directory)
cd backend

# 安装依赖包 (Install required packages)
# 注意：如果有 requirements.txt 文件，使用以下命令
# pip install -r requirements.txt
```

### 4. 环境变量配置 (Environment Variables)

在 `backend` 目录下创建 `.env` 文件来配置环境变量：

```bash
# 在 backend 目录下创建 .env 文件 (Create .env file in backend directory)
touch backend/.env
```

在 `.env` 文件中添加必要的环境变量：
```env
# API 配置 (API Configuration)
API_HOST=localhost
API_PORT=8000

# 数据库配置 (Database Configuration)
DATABASE_URL=sqlite:///./app.db

# 外部 API 密钥 (External API Keys)
WEATHER_API_KEY=your_weather_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

### 5. 运行后端服务 (Run Backend Service)

```bash
# 确保在 backend 目录下 (Make sure you are in the backend directory)
cd backend

# 运行主程序 (Run the main application)
python main.py

# 或者如果使用 FastAPI 和 uvicorn (Or if using FastAPI with uvicorn)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```