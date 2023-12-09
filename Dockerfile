# 使用官方Python运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录为/app
WORKDIR /app

# 将当前目录内容复制到位于/app中的容器中
COPY . /app

# 安装requirements.txt中指定的任何所需包
RUN pip install --no-cache-dir -r requirements.txt

# 使端口80可用于此容器外的通信
EXPOSE 80

# 定义环境变量
ENV NAME World
ENV PYTHONPATH "${PYTHONPATH}:/app"


# 在容器启动时运行python app.py
CMD ["python", "app/services/websocket_client.py"]