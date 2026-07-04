FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制项目代码
COPY . .

# 设置 HuggingFace 模型缓存目录（挂载到宿主机 data/hf_cache）
ENV HF_HOME=/app/data/hf_cache
# 使用国内镜像下载模型（解决 huggingface.co 访问受限问题）
ENV HF_ENDPOINT=https://hf-mirror.com

# 预下载 Embedding 模型（利用 Docker 层缓存，避免运行时重复下载）
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# 暴露 Chainlit 默认端口
EXPOSE 8000

# 启动应用
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
