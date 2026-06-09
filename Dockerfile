# 基础镜像，带有 Python 3.11 和基础 Linux 环境
FROM python:3.11-slim

# 设置工作目录 相当于 cd /app
WORKDIR /app

# 复制依赖文件进镜像
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目所有代码到容器内
COPY . .

# 运行时暴露 8000 端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]