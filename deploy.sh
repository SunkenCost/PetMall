#!/bin/bash

# --- PetMall Deployment Script ---
# 服务器一键部署脚本，支持代码拉取、数据库迁移、数据初始化

set -e  # 任何错误都退出

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "========== PetMall Server Deployment Started =========="

# 1. Pull latest code
log_info "Step 1/5: Pulling latest code from GitHub..."
git fetch --all
git reset --hard origin/main
log_info "✓ Code pulled successfully"

# 2. Rebuild and start containers
log_info "Step 2/5: Rebuilding and starting Docker containers..."
docker-compose up -d --build
log_info "✓ Containers started"

# 3. Wait for database
log_info "Step 3/5: Waiting for database to be ready..."
sleep 15
log_info "✓ Database ready"

# 4. Apply migrations
log_info "Step 4/5: Applying database migrations..."
docker-compose exec -T backend python manage.py migrate
log_info "✓ Migrations completed"

# 5. Initialize data
log_info "Step 5/5: Initializing test data..."
if [ -f "backup_local_data.sql" ]; then
    log_info "Found backup_local_data.sql, importing data..."
    docker exec -T petmall_db mysql -uroot -p123456xqy e < backup_local_data.sql
    log_info "✓ Backup data imported"
else
    log_warn "backup_local_data.sql not found, generating test data with Python script..."
    docker exec -T petmall_backend python test/backend_scripts/test_init_data.py
    log_info "✓ Test data generated"
fi

log_info "========== Deployment Completed Successfully =========="
log_info ""
log_info "🌐 Service URLs:"
log_info "  Frontend:   http://$(hostname -I | awk '{print $1}'):80"
log_info "  Backend:    http://$(hostname -I | awk '{print $1}'):8000"
log_info "  Admin:      http://$(hostname -I | awk '{print $1}'):80/admin"
log_info ""
log_info "📝 Test Accounts:"
log_info "  Admin:      admin / password123"
log_info "  Test User:  test1 / password123"
log_info ""
