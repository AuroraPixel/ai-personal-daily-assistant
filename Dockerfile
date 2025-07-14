# 多阶段构建 Dockerfile
# 阶段1: 构建前端
FROM node:20-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app/ui

# 安装必要的系统依赖
RUN apk add --no-cache python3 make g++

# 复制前端依赖文件
COPY ui/package*.json ./

# 清理 npm 缓存并安装所有依赖
RUN npm cache clean --force && \
    npm ci --no-audit --no-fund

# 复制前端源代码
COPY ui/ .

# 构建前端应用
RUN npm run build

# 验证构建结果
RUN ls -la dist/

# 阶段2: 构建后端
FROM python:3.11-slim AS backend

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装Python依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/ui/dist ./static

# 创建必要的目录
RUN mkdir -p logs data

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# 启动命令
CMD ["python", "main.py"] 