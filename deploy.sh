#!/bin/bash

# --- PetMall 自动化部署脚本 ---
echo "开始自动化部署流程..."

# 1. 拉取最新代码
echo "正在从 GitHub 拉取代码..."
git fetch --all
git reset --hard origin/main

# 2. 重新构建并启动容器
echo "正在重启容器服务..."
docker-compose up -d --build

# 3. 执行数据库迁移
echo "正在更新数据库结构..."
docker exec petmall_backend python manage.py migrate

# 4. 同步媒体文件 (可选)
# 如果你手动加了图片，这里可以保留

echo "部署完成"
