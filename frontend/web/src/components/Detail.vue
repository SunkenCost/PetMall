<template>
  <base-page>
    <div class="detail-container" v-loading="loading">
      <el-button @click="$router.back()" class="back-btn" :icon="Back" text>返回商品大厅</el-button>
      
      <div v-if="product" class="product-layout">
        <div class="image-section">
          <el-card :body-style="{ padding: '0px' }" class="main-img-card" shadow="never">
            <img :src="product.main_image || 'https://via.placeholder.com/600x600?text=Pet+Product'" class="main-image" />
          </el-card>
        </div>
        
        <div class="info-section">
          <div class="tag">{{ product.category_name }}</div>
          <h1 class="product-title">{{ product.name }}</h1>
          
          <div class="price-box">
            <span class="currency">¥</span>
            <span class="current-price">{{ product.price }}</span>
            <span class="old-price" v-if="product.old_price">¥{{ product.old_price }}</span>
            
            <el-tag type="danger" effect="dark" class="stock-tag" v-if="product.inventory <= 10 && product.inventory > 0">
              仅剩 {{ product.inventory }} 件，欲购从速
            </el-tag>
            <el-tag type="info" effect="dark" class="stock-tag" v-if="product.inventory === 0">
              正在补货中
            </el-tag>
          </div>
          
          <div class="stats-row">
            <span>全部销量：<strong style="color:var(--text-main)">{{ product.sales }}件</strong></span>
            <span>上架时间：{{ new Date(product.create_time).toLocaleDateString() }}</span>
          </div>
          
          <el-divider />
          
          <div class="action-box">
            <el-input-number v-model="buyCount" :min="1" :max="product.inventory" :disabled="product.inventory === 0" size="large" />
            <span style="margin: 0 20px; color: var(--text-light)">件 (库存: {{product.inventory}})</span>
            
            <el-button 
              type="primary" 
              class="add-to-cart-btn" 
              size="large" 
              :icon="ShoppingCart" 
              :disabled="product.inventory === 0"
              @click="addToCart"
            >
              {{ product.inventory === 0 ? '暂无库存' : '加入购物车' }}
            </el-button>
          </div>
          
          <div class="product-desc-box">
            <h3>商品图文详情</h3>
            <p class="desc-text">{{ product.description || '主人很懒，什么都没写~' }}</p>
          </div>
        </div>
      </div>
    </div>
  </base-page>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back, ShoppingCart } from '@element-plus/icons-vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'ProductDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const product = ref(null)
    const loading = ref(true)
    const buyCount = ref(1)

    const fetchDetail = async () => {
      try {
        const res = await axios.get(`/api/commodity/products/${route.params.id}/`)
        product.value = res.data
      } catch (err) {
        ElMessage.error('无法读取商品库')
        router.push('/commodity')
      } finally {
        loading.value = false
      }
    }

    const addToCart = async () => {
      try {
        await axios.post('/api/shopper/cart-items/', {
          product: product.value.id,
          quantity: buyCount.value
        })
        ElMessage.success({ message: `成功将 ${buyCount.value} 件商品加入购物车`, type: 'success' })
        // 这时因为App使用的是Base包裹，想要刷新右上角购物车数字可以走 Vuex 或简单重刷
        setTimeout(() => {
            window.location.reload()
        }, 800)
      } catch (err) {
        ElMessage.error('加入失败，请检查网络')
      }
    }

    onMounted(() => {
      fetchDetail()
    })

    return { product, loading, buyCount, Back, ShoppingCart, addToCart }
  }
}
</script>

<style scoped>
.back-btn {
  margin-bottom: 30px;
  font-size: 16px;
}
.product-layout {
  display: flex;
  gap: 60px;
  margin-top: 10px;
}
.image-section {
  flex: 0 0 500px;
}
.main-img-card {
  border-radius: var(--border-radius);
  overflow: hidden;
  border: 1px solid #ebeef5 !important;
}
.main-image {
  width: 100%;
  height: 500px;
  object-fit: cover;
  display: block;
}
.info-section {
  flex-grow: 1;
  padding-top: 20px;
}
.tag {
  color: var(--primary-color);
  font-weight: 700;
  letter-spacing: 2px;
  margin-bottom: 10px;
}
.product-title {
  font-size: 32px;
  line-height: 1.3;
  margin: 0 0 20px 0;
  color: var(--text-main);
}
.price-box {
  background: rgba(255, 168, 186, 0.08);
  padding: 24px;
  border-radius: 20px;
  display: flex;
  align-items: baseline;
  margin-bottom: 20px;
}
.currency {
  font-size: 24px;
  color: var(--primary-color);
  font-weight: 600;
}
.current-price {
  font-size: 48px;
  color: var(--primary-color);
  font-weight: 800;
  margin-right: 20px;
}
.old-price {
  font-size: 18px;
  color: var(--text-light);
  text-decoration: line-through;
  margin-right: 20px;
}
.stock-tag {
  transform: translateY(-5px);
}
.stats-row {
  display: flex;
  gap: 40px;
  font-size: 14px;
  color: var(--text-light);
  margin-bottom: 20px;
}
.action-box {
  display: flex;
  align-items: center;
  margin-top: 30px;
}
.add-to-cart-btn {
  width: 200px;
  height: 50px;
  font-size: 18px;
  border-radius: 25px !important;
}
.product-desc-box {
  margin-top: 60px;
}
.product-desc-box h3 {
  font-size: 20px;
  margin-bottom: 20px;
}
.desc-text {
  line-height: 1.8;
  color: #5a5e66;
  font-size: 16px;
  white-space: pre-wrap;
}
</style>
