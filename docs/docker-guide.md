# Docker 容器化指南

## 什么是 Docker

Docker 是一个开源的容器化平台，允许开发者将应用程序及其依赖打包到一个轻量级、可移植的容器中。容器可以在任何支持 Docker 的环境中运行，确保应用在不同环境中的一致性。

## 核心概念

### 镜像 (Image)

镜像是一个只读的模板，包含创建容器所需的所有文件和配置。镜像可以基于其他镜像构建。

### 容器 (Container)

容器是镜像的运行实例。可以创建、启动、停止、移动或删除容器。容器之间相互隔离。

### Dockerfile

Dockerfile 是一个文本文件，包含构建 Docker 镜像的指令。

### Docker Hub

Docker Hub 是一个公共的镜像仓库，可以分享和获取 Docker 镜像。

## 安装 Docker

### macOS

下载 Docker Desktop：https://www.docker.com/products/docker-desktop

### Ubuntu

```bash
# 更新包索引
sudo apt update

# 安装依赖
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
```

## 常用命令

### 镜像操作

```bash
# 拉取镜像
docker pull nginx

# 列出本地镜像
docker images

# 删除镜像
docker rmi nginx

# 构建镜像
docker build -t myapp:1.0 .
```

### 容器操作

```bash
# 运行容器
docker run nginx

# 后台运行
docker run -d nginx

# 端口映射
docker run -d -p 8080:80 nginx

# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 停止容器
docker stop container_id

# 启动已停止的容器
docker start container_id

# 删除容器
docker rm container_id

# 进入容器
docker exec -it container_id /bin/bash
```

## Dockerfile 示例

```dockerfile
# 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app.py"]
```

## Docker Compose

Docker Compose 用于定义和运行多容器应用。

### docker-compose.yml 示例

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Compose 命令

```bash
# 启动服务
docker-compose up

# 后台启动
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs

# 重建镜像
docker-compose build
```

## 最佳实践

1. **使用官方基础镜像**
2. **最小化镜像层数**
3. **使用 .dockerignore 排除不需要的文件**
4. **不要在镜像中存储敏感信息**
5. **使用多阶段构建减小镜像大小**
6. **为容器设置资源限制**
