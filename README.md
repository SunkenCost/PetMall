# PetMall 宠物商城系统

本项目是一个基于 **Vue 3** 和 **Django 4** 构建的前后端分离电商平台，旨在提供一个功能完整、界面美观且易于扩展的在线宠物用品销售系统。

## 🌟 系统架构

本系统采用经典的前后端分离架构，通过 RESTful API 进行数据交互，确保了前端的高性能展现与后端逻辑的稳健运行。

### 技术栈

- **前端 (Frontend):**
  - 核心框架：Vue 3.x
  - 路由管理：Vue Router
  - 状态管理：Vuex
  - UI 组件库：Element Plus / Element UI
  - 请求处理：Axios
- **后端 (Backend):**
  - 开发框架：Python 3.x / Django 4.1
  - API 开发：Django REST Framework (DRF)
  - 数据库支持：MySQL 5.7/8.0
  - 跨域处理：django-cors-headers
- **中间层与环境:**
  - Nginx (生产部署)
  - Git (版本控制)

## 📦 核心功能

- **用户管理中心**: 用户注册、登录、个人资料修改、收货地址管理。
- **商品分类浏览**: 多级商品分类展示，搜索及详情查看。
- **购物车与订单**: 加入并管理购物车，提交并处理支付订单。
- **商家管理后台**:
  - **商品管理**: 快捷上下架、库存动态监控与补货。
  - **订单流水**: 实时查看待支付、待发货及已完成订单状态。
  - **数据统计**: 可视化当日收入、订单走势及热卖排行。
- **系统安全**: 基于 Token 的登录校验与角色管理，确保管理权限的严谨闭环。

## 🚀 部署指南

本项目推荐使用 **Docker** 进行快速部署，同时也支持传统的本地原生开发模式。

### 方式一：Docker 一键部署 (推荐)
适合快速预览或生产部署，无需手动安装数据库和环境。
1. **启动服务**：`docker-compose up -d --build`
2. **初始化数据**：
   ```bash
   docker exec petmall_backend python manage.py migrate
   docker exec petmall_backend python test/backend_scripts/test_init_data.py
   ```
3. **访问地址**：前台 `http://localhost`，后台管理 `http://localhost/admin`

### 方式二：本地开发
不依赖 Docker，所有组件均运行在本地实机环境中。

1. **数据库准备**：
   - 确保本地已安装运行 **MySQL** (推荐 5.7+ 或 8.0+)。
   - 创建名为 `e` 的数据库：`CREATE DATABASE e DEFAULT CHARACTER SET utf8mb4;`。
   - 执行数据库同步：`python backend/server/manage.py migrate`。
   - 初始数据灌入：`python backend/server/test/backend_scripts/test_init_data.py`。

2. **启动后端 (Django)**：
   - 进入目录：`cd backend/server`
   - 安装依赖：`pip install -r requirements.txt`
   - 启动：`python manage.py runserver` (默认连接本地 3306 端口)

3. **启动前端 (Vue)**：
   - 进入目录：`cd frontend/web`
   - 安装依赖：`npm install`
   - 启动：`npm run dev`


## 📜 项目申明

本系统包含了完整的业务逻辑链条，适合中小型宠物电商场景的二次开发与参考学习。
