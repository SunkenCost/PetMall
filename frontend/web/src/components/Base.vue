<template>
  <div class="base-layout">
    <!-- 吸顶高斯模糊导航栏 -->
    <el-menu mode="horizontal" :ellipsis="false" class="glass-nav" :router="true" :default-active="activeIndex">
      <div class="logo" @click="$router.push('/commodity')">
        <img src="/favicon.ico" alt="PetMall" class="logo-icon" />
        PETMALL <span class="logo-sub">宠爱之家</span>
      </div>
      <div class="flex-grow" />
      <!-- 全局搜索框 -->
      <div class="search-wrap">
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索您想要的宠物好物..." 
          class="nav-search"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-menu-item index="/commodity">
        <el-icon><Shop /></el-icon> 挑选好物
      </el-menu-item>
      
      <!-- 触发抽屉购物车的按钮 -->
      <el-menu-item @click="drawerVisible = true" style="overflow: visible;">
        <el-badge :value="cartCount" :hidden="cartCount === 0" type="danger" class="cart-badge">
          <span style="display: flex; align-items: center;"><el-icon style="margin-right: 4px;"><ShoppingCart /></el-icon>购物车</span>
        </el-badge>
      </el-menu-item>

      <el-sub-menu index="user" v-if="userInfo">
        <template #title>
          <el-avatar size="small" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
          <span style="margin-left: 8px;">{{ userInfo.realName || userInfo.username }}</span>
        </template>
        <el-menu-item index="/shopper">我的收货地址</el-menu-item>
        <el-menu-item index="/orders">我的订单</el-menu-item>
        <el-menu-item index="/pets">我的宠物档案</el-menu-item>
        <el-menu-item v-if="userInfo.is_superuser" index="/super-admin" style="font-weight: 600;">
          <el-icon style="color: #7C3AED;"><Management /></el-icon>
          <span style="color: #7C3AED;">系统管理控制台</span>
        </el-menu-item>
        <el-menu-item v-if="userInfo.is_staff || userInfo.is_superuser" index="/admin-panel" style="font-weight: 600;">
          <el-icon style="color: #6366f1;"><Shop /></el-icon>
          <span style="color: #6366f1;">商家管理后台</span>
        </el-menu-item>
        <el-menu-item @click="logout" style="color: #f56c6c;">退出登录</el-menu-item>
      </el-sub-menu>

      <el-menu-item index="/login" v-else>
        <el-button type="primary" round>去登录</el-button>
      </el-menu-item>
    </el-menu>

    <!-- 主体区域 -->
    <main class="main-content">
      <slot></slot>
    </main>

    <!-- 购物车右侧边栏抽屉 Drawer -->
    <el-drawer
      title="我的购物车"
      v-model="drawerVisible"
      size="400px"
      custom-class="cart-drawer"
    >
      <template #header>
        <div class="drawer-header">
          <el-icon class="mr-8"><ShoppingCart /></el-icon>
          <span>我的购物车</span>
        </div>
      </template>
      <Shopcart @close="drawerVisible = false" />
    </el-drawer>

    <!-- 美观通用的底边栏 -->
    <footer-page />
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, Shop, ShoppingCart, Management } from '@element-plus/icons-vue'
import Shopcart from './Shopcart.vue'
import axios from '@/axios'

export default {
  name: 'BasePage',
  components: {
    Search, Shop, ShoppingCart, Management, Shopcart
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const activeIndex = ref(route.path)
    const searchKeyword = ref('')
    const drawerVisible = ref(false)
    const cartCount = ref(0)
    const userInfo = ref(null)

    watch(() => route.path, (val) => {
      activeIndex.value = val
    })

    const handleSearch = () => {
      if (searchKeyword.value) {
        router.push({ path: '/commodity', query: { search: searchKeyword.value } })
      }
    }

    // 实时读取购物车角标数量
    const loadCartCount = () => {
      if (!userInfo.value) return;
      axios.get('/api/shopper/cart/my_cart/').then(res => {
        cartCount.value = res.data.items ? res.data.items.length : 0
      }).catch(() => {})
    }

    const loadUser = () => {
      const u = localStorage.getItem('pet_user')
      if (u) userInfo.value = JSON.parse(u)
    }

    const logout = () => {
      localStorage.removeItem('pet_user')
      userInfo.value = null
      window.location.reload()
    }

    onMounted(() => {
      loadUser()
      loadCartCount()
    })

    return {
      activeIndex, searchKeyword, handleSearch, drawerVisible, cartCount, userInfo, logout
    }
  }
}
</script>

<style scoped>
.base-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.glass-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 40px;
  align-items: center;
}
.logo {
  font-size: 20px;
  font-weight: 900;
  color: #1a1a1a;
  margin-right: 40px;
  cursor: pointer;
  letter-spacing: 0.5px;
  font-family: 'Inter', sans-serif;
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}
.logo-sub {
  font-size: 14px;
  font-weight: 500;
  color: #909399;
}
.flex-grow {
  flex-grow: 1;
}
.search-wrap {
  margin-right: 40px;
  width: 300px;
}
:deep(.nav-search .el-input__wrapper) {
  border-radius: 20px;
  background-color: var(--bg-color);
  box-shadow: none !important;
  border: 1px solid #ebeef5;
}
.main-content {
  flex: 1;
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
:deep(.cart-drawer .el-drawer__body) {
  padding: 0;
}
.cart-badge {
  display: flex !important;
  align-items: center !important;
}
:deep(.cart-badge .el-badge__content.is-fixed) {
  top: 18px !important;
  right: 6px !important;
}
.drawer-header {
  display: flex;
  align-items: center;
  font-weight: 700;
  color: #303133;
}
.mr-8 { margin-right: 8px; }
</style>
