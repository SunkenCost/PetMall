<template>
  <div class="super-layout">
    <!-- 企业级深色侧边栏 -->
    <aside class="super-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-brand">
        <div class="brand-logo">
          <el-icon><Management /></el-icon>
        </div>
        <div class="brand-text" v-if="!sidebarCollapsed">系统管理中心</div>
      </div>

      <nav class="super-nav">
        <div class="nav-group-title" v-if="!sidebarCollapsed">平台监控</div>
        <router-link
          v-for="item in overviewMenu"
          :key="item.path"
          :to="item.path"
          class="super-menu-item"
          :class="{ active: isActive(item.path) }"
        >
          <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
          <span class="menu-label" v-if="!sidebarCollapsed">{{ item.label }}</span>
        </router-link>

        <div class="nav-group-title" v-if="!sidebarCollapsed">安全与日志</div>
        <div class="nav-divider" v-else></div>
        
        <router-link
          v-for="item in adminMenu"
          :key="item.path"
          :to="item.path"
          class="super-menu-item"
          :class="{ active: isActive(item.path) }"
        >
          <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
          <span class="menu-label" v-if="!sidebarCollapsed">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="footer-btn" @click="$router.push('/admin-panel')">
          <el-icon><Shop /></el-icon>
          <span v-if="!sidebarCollapsed">商家后台</span>
        </div>
        <div class="footer-btn collapse-toggle" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><Expand v-if="sidebarCollapsed" /><Fold v-else /></el-icon>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="super-main">
      <header class="super-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>系统管理员</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <div class="header-time">{{ currentTime }}</div>
          <el-divider direction="vertical" />
          <el-dropdown trigger="click">
            <div class="admin-user">
              <el-avatar :size="28" style="background-color: #1677ff;">{{ adminInitial }}</el-avatar>
              <span class="admin-name">{{ adminName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :icon="Shop" @click="$router.push('/admin-panel')">进入商家后台</el-dropdown-item>
                  <el-dropdown-item divided :icon="SwitchButton" @click="logout">安全退出</el-dropdown-item>
                </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="super-body">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Management, DataAnalysis, User, 
  DocumentCopy, Shop, Fold, 
  Expand, ArrowDown, SwitchButton
} from '@element-plus/icons-vue'

export default {
  name: 'SuperAdminLayout',
  components: {
    Management, DataAnalysis, User,
    DocumentCopy, Shop, Fold,
    Expand, ArrowDown, SwitchButton
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const sidebarCollapsed = ref(false)
    const currentTime = ref('')

    const userInfo = JSON.parse(localStorage.getItem('pet_user') || '{}')
    const adminName = userInfo.realName || userInfo.username || '系统管理员'
    const adminInitial = computed(() => (adminName[0] || 'A').toUpperCase())

    const updateTime = () => {
      const now = new Date()
      currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }
    let timer = null
    onMounted(() => { updateTime(); timer = setInterval(updateTime, 60000) })
    onUnmounted(() => clearInterval(timer))

    const overviewMenu = [
      { path: '/super-admin/dashboard', label: '平台总览', icon: 'DataAnalysis' },
    ]
    const adminMenu = [
      { path: '/super-admin/users', label: '用户安全', icon: 'User' },
      { path: '/super-admin/system-logs', label: '系统日志', icon: 'DocumentCopy' },
    ]

    const pageTitleMap = {
      '/super-admin/dashboard': '平台总览',
      '/super-admin/users': '用户管理',
      '/super-admin/system-logs': '系统日志',
    }

    const currentPageTitle = computed(() => pageTitleMap[route.path] || '管理控制台')
    const isActive = (path) => route.path === path || route.path.startsWith(path + '/')

    const logout = () => {
      localStorage.removeItem('pet_user')
      router.push('/login')
    }

    return {
      sidebarCollapsed, overviewMenu, adminMenu,
      currentPageTitle, isActive,
      adminName, adminInitial, logout, currentTime
    }
  }
}
</script>

<style scoped>
.super-layout {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
  color: #334155;
  font-family: 'Inter', system-ui, sans-serif;
}

/* ===== 侧边栏 (深色方案) ===== */
.super-sidebar {
  width: 240px;
  background: #001529; /* 标准企业级深蓝 */
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100vh;
  position: sticky;
  top: 0;
  z-index: 100;
  color: #fff;
}
.super-sidebar.collapsed { width: 64px; }

.sidebar-brand {
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  overflow: hidden;
}
.brand-logo {
  width: 32px; height: 32px;
  background: #1677ff;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
}
.brand-text {
  font-size: 15px; font-weight: 700; color: #fff;
  white-space: nowrap; letter-spacing: 0.5px;
}

.super-nav {
  flex: 1;
  padding: 16px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.nav-group-title {
  font-size: 11px;
  color: #64748b;
  padding: 12px 12px 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}
.nav-divider {
  border-top: 1px solid rgba(255,255,255,0.05);
  margin: 12px 10px;
}

.super-menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
  overflow: hidden;
}
.super-menu-item:hover {
  background: rgba(255,255,255,0.05);
  color: #fff;
}
.super-menu-item.active {
  background: #1677ff; /* 强调蓝 */
  color: #fff;
  font-weight: 600;
}
.menu-icon { font-size: 18px; margin-right: 12px; flex-shrink: 0; }
.super-sidebar.collapsed .menu-icon { margin-right: 0; }

.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.footer-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; border-radius: 8px;
  color: #64748b; cursor: pointer; font-size: 13px;
  transition: all 0.2s;
}
.footer-btn:hover { background: rgba(255,255,255,0.05); color: #fff; }
.collapse-toggle { justify-content: center; padding: 10px; }

/* ===== 主内容区 ===== */
.super-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.super-header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky; top: 0; z-index: 90;
}
.header-right { display: flex; align-items: center; gap: 12px; }
.header-time { font-size: 13px; color: #94a3b8; font-variant-numeric: tabular-nums; }

.admin-user {
  display: flex; align-items: center; gap: 10px;
  cursor: pointer; padding: 4px 8px; border-radius: 6px;
}
.admin-user:hover { background: #f8fafc; }
.admin-name { font-size: 14px; font-weight: 600; color: #1e293b; }

.super-body {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}
</style>
