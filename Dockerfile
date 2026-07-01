FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制项目代码
COPY . .

# 暴露 Chainlit 默认端口
EXPOSE 8000

# 启动应用
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
