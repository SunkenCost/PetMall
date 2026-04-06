<template>
  <base-page>
    <div class="commodity-container">
      <!-- 动态分类导航 -->
      <aside class="sidebar">
        <h3 class="sidebar-title">全部分类</h3>
        <el-menu :default-active="activeCategory" class="category-menu" @select="handleCategorySelect">
          <el-menu-item index="">全部商品</el-menu-item>
          <el-menu-item v-for="cat in categories" :key="cat.id" :index="String(cat.id)">
            {{ cat.name }}
          </el-menu-item>
        </el-menu>
        
      </aside>

      <!-- 商品展示瀑布墙 -->
      <section class="products-grid" v-loading="loading">
        <div class="top-toolbar">
          <span class="toolbar-label">智能排序：</span>
          <el-radio-group v-model="sortOrder" @change="fetchProducts">
            <el-radio-button label="">默认推荐</el-radio-button>
            <el-radio-button label="-sales">销量最高</el-radio-button>
            <el-radio-button label="price">价格最低</el-radio-button>
          </el-radio-group>
        </div>

        <el-empty v-if="products.length === 0" description="很抱歉，没有找到相关商品哦~" />
        
        <el-row :gutter="24">
          <el-col :span="8" v-for="item in products" :key="item.id" style="margin-bottom: 24px;">
            <el-card class="product-card" @click="goToDetail(item.id)" shadow="hover" :body-style="{ padding: '0px' }">
              <div class="image-wrapper">
                <img :src="item.main_image || 'https://via.placeholder.com/600x400?text=Pet+Product'" class="product-img" />
                <div class="sales-badge">已售 {{ item.sales }} 件</div>
              </div>
              <div class="product-info">
                <div class="cat-tag">{{ item.category_name }}</div>
                <h2 class="title">{{ item.name }}</h2>
                <div class="price-row">
                  <span class="price">¥{{ item.price }}</span>
                  <span v-if="item.old_price" class="old-price">¥{{ item.old_price }}</span>
                  <el-button type="primary" circle :icon="ShoppingCart" class="add-btn" @click.stop="addToCart(item)" />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- Vue3 分页器 -->
        <div class="pagination-wrap" v-if="total > 0">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="total"
            :page-size="12"
            v-model:current-page="currentPage"
            @current-change="fetchProducts"
          />
        </div>
      </section>
    </div>
  </base-page>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ShoppingCart } from '@element-plus/icons-vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'CommodityList',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const categories = ref([])
    const products = ref([])
    const loading = ref(false)
    const activeCategory = ref('')
    const sortOrder = ref('')
    const currentPage = ref(1)
    const total = ref(0)
    const searchQuery = ref(route.query.search || '')

    const fetchCategories = async () => {
      try {
        const res = await axios.get('/api/commodity/categories/')
        categories.value = res.data
      } catch (err) {
        ElMessage.error('无法加载分类库')
      }
    }

    const fetchProducts = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          search: searchQuery.value,
          ordering: sortOrder.value,
        }
        if (activeCategory.value) {
          params.category = activeCategory.value
        }
        const res = await axios.get('/api/commodity/products/', { params })
        products.value = res.data.results
        total.value = res.data.count
      } catch (err) {
        ElMessage.error('加载商品失败')
      } finally {
        loading.value = false
      }
    }

    const handleCategorySelect = (index) => {
      activeCategory.value = index
      currentPage.value = 1
      fetchProducts()
    }

    const goToDetail = (id) => {
      router.push(`/commodity/detail/${id}`)
    }

    const addToCart = async (item) => {
      try {
        await axios.post('/api/shopper/cart-items/', {
          product: item.id,
          quantity: 1
        })
        ElMessage.success({ message: `成功将 ${item.name} 加入购物车🐾`, type: 'success' })
      } catch (err) {
        ElMessage.error('加入购物车失败')
      }
    }

    watch(() => route.query.search, (newSearch) => {
      searchQuery.value = newSearch || ''
      currentPage.value = 1
      fetchProducts()
    })

    onMounted(() => {
      fetchCategories()
      fetchProducts()
    })

    return {
      ShoppingCart, categories, products, loading, activeCategory, sortOrder,
      currentPage, total, handleCategorySelect, goToDetail, fetchProducts, addToCart
    }
  }
}
</script>

<style scoped>
.commodity-container {
  display: flex;
  gap: 40px;
}
.sidebar {
  width: 240px;
  flex-shrink: 0;
}
.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text-main);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.category-menu {
  border-right: none;
  background: transparent;
}
.products-grid {
  flex-grow: 1;
}
.top-toolbar {
  display: flex;
  align-items: center;
  background: var(--bg-color);
  padding: 15px 25px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
}
.toolbar-label {
  font-weight: 600;
  color: var(--text-main);
  margin-right: 20px;
}
.product-card {
  cursor: pointer;
  position: relative;
}
.image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 100%; /* 1:1 Aspect ratio */
  overflow: hidden;
}
.product-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}
.product-card:hover .product-img {
  transform: scale(1.08); /* 轻微放大交互 */
}
.sales-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(0,0,0,0.6);
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  backdrop-filter: blur(4px);
}
.product-info {
  padding: 20px;
}
.cat-tag {
  font-size: 11px;
  color: var(--primary-color);
  background: rgba(255, 168, 186, 0.15);
  font-weight: 600;
  margin-bottom: 8px;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}
.title {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  margin: 0 0 16px;
  height: 44px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}
.price-row {
  display: flex;
  align-items: center;
  margin-top: 10px;
}
.price {
  font-size: 22px;
  font-weight: 800;
  color: var(--primary-color);
}
.old-price {
  font-size: 14px;
  color: var(--text-light);
  text-decoration: line-through;
  margin-left: 10px;
}
.add-btn {
  margin-left: auto;
}
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}
</style>
