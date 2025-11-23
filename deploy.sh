#!/bin/bash

echo "🚀 Starting deployment..."

# 1. 拉取最新代码
echo "📥 Pulling latest code..."
git pull origin main

# 2. 重建并启动容器
echo "🐳 Rebuilding and restarting containers..."
docker compose up -d --build

# 3. 清理未使用的镜像 (可选，防止磁盘爆满)
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "✅ Deployment finished!"
docker compose logs -f --tail=20
