<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="admin-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-brand">
        <div class="brand-logo">
          <el-icon><Shop /></el-icon>
        </div>
        <div class="brand-text" v-if="!sidebarCollapsed">商家管理后台</div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-menu-item"
          :class="{ active: isActive(item.path) }"
        >
          <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
          <span class="menu-label" v-if="!sidebarCollapsed">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="footer-action" @click="$router.push('/commodity')">
          <el-icon><Back /></el-icon>
          <span v-if="!sidebarCollapsed">返回商城</span>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="admin-main">
      <!-- 顶栏 -->
      <header class="admin-header">
        <div class="header-left">
          <div class="toggle-btn" @click="sidebarCollapsed = !sidebarCollapsed">
            <el-icon><Expand v-if="sidebarCollapsed" /><Fold v-else /></el-icon>
          </div>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>管理中心</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click">
            <div class="user-info-box">
              <el-avatar :size="32" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
              <span class="username" v-if="!isMobile">{{ adminName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :icon="HomeFilled" @click="$router.push('/commodity')">返回商城主页</el-dropdown-item>
                  <el-dropdown-item divided :icon="SwitchButton" @click="logout">安全退出</el-dropdown-item>
                </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容区 -->
      <main class="admin-body">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Shop, DataLine, Goods, Box, List, 
  Refresh, Back, Fold, Expand, ArrowDown, HomeFilled, SwitchButton
} from '@element-plus/icons-vue'

export default {
  name: 'AdminLayout',
  components: {
    Shop, DataLine, Goods, Box, List,
    Refresh, Back, Fold, Expand, ArrowDown, HomeFilled, SwitchButton
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const sidebarCollapsed = ref(false)
    const isMobile = ref(window.innerWidth < 768)

    const userInfo = JSON.parse(localStorage.getItem('pet_user') || '{}')
    const adminName = userInfo.realName || userInfo.username || '管理员'

    const menuItems = ref([
      { path: '/admin-panel/dashboard', icon: 'DataLine', label: '主要看板' },
      { path: '/admin-panel/products', icon: 'Goods', label: '商品管理' },
      { path: '/admin-panel/inventory', icon: 'Box', label: '库存监控' },
      { path: '/admin-panel/orders', icon: 'List', label: '订单中心' },
      { path: '/admin-panel/aftersales', icon: 'Refresh', label: '售后服务' },
    ])

    const pageTitleMap = {
      '/admin-panel/dashboard': '主要看板',
      '/admin-panel/products': '商品管理',
      '/admin-panel/inventory': '库存监控',
      '/admin-panel/orders': '订单中心',
      '/admin-panel/aftersales': '售后服务',
    }

    const currentPageTitle = computed(() => pageTitleMap[route.path] || '管理后台')
    const isActive = (path) => route.path === path || route.path.startsWith(path + '/')

    const handleResize = () => {
      isMobile.value = window.innerWidth < 768
      if (isMobile.value) sidebarCollapsed.value = true
    }

    onMounted(() => window.addEventListener('resize', handleResize))
    onUnmounted(() => window.removeEventListener('resize', handleResize))

    const logout = () => {
      localStorage.removeItem('pet_user')
      router.push('/login')
    }

    return { 
      sidebarCollapsed, menuItems, 
      currentPageTitle, isActive, 
      adminName, logout, isMobile 
    }
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
  color: #303133;
}

/* ===== 侧边栏 ===== */
.admin-sidebar {
  width: 220px;
  background: #ffffff;
  border-right: 1px solid #e6e8eb;
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: 100;
}
.admin-sidebar.collapsed { width: 64px; }

.sidebar-brand {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 12px;
  border-bottom: 1px solid #f0f2f5;
  overflow: hidden;
}
.brand-logo {
  width: 32px;
  height: 32px;
  background: #409eff;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
}
.brand-text {
  font-weight: 700;
  font-size: 15px;
  color: #1f2d3d;
  white-space: nowrap;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.nav-menu-item {
  display: flex;
  align-items: center;
  padding: 12px 12px;
  border-radius: 8px;
  color: #606266;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
  overflow: hidden;
}
.nav-menu-item:hover {
  background: #f5f7fa;
  color: #409eff;
}
.nav-menu-item.active {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}
.menu-icon {
  font-size: 18px;
  margin-right: 12px;
  flex-shrink: 0;
}
.admin-sidebar.collapsed .menu-icon { margin-right: 0; }

.sidebar-footer {
  padding: 16px 8px;
  border-top: 1px solid #f0f2f5;
}
.footer-action {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  color: #909399;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.footer-action:hover {
  background: #fef0f0;
  color: #f56c6c;
}

/* ===== 主内容区 ===== */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.admin-header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e6e8eb;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 90;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}
.toggle-btn {
  font-size: 20px;
  color: #606266;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.toggle-btn:hover { color: #409eff; }

.header-right {
  display: flex;
  align-items: center;
}
.user-info-box {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}
.user-info-box:hover { background: #f5f7fa; }
.username { font-size: 14px; font-weight: 500; }

.admin-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
