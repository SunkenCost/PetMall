<template>
  <div class="shopcart-drawer-content" v-loading="loading">
    <el-empty v-if="cartItems.length === 0" description="你的购物车肚子空空如也，快去喂饱它喵~" />
    
    <div v-else class="cart-items-wrap">
      <div v-for="item in cartItems" :key="item.id" class="cart-item">
        <img :src="item.product_detail.main_image" class="item-img" />
        <div class="item-info">
          <div class="item-title">{{ item.product_detail.name }}</div>
          <div class="item-price">¥{{ item.product_detail.price }}</div>
          <div class="item-actions">
            <!-- 步进器，限制数量不能超过当前库存 -->
            <el-input-number 
               v-model="item.quantity" 
               :min="1" 
               :max="item.product_detail.inventory" 
               size="small"
               @change="(val) => updateQuantity(item, val)"
            />
            <el-button type="danger" text @click="removeItem(item.id)">移除</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部结算区 -->
    <div class="cart-footer" v-if="cartItems.length > 0">
      <div class="total-row">
        <span>合计:</span>
        <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
      </div>
      
      <!-- 结账时要选地址 -->
      <div class="checkout-actions">
        <el-select v-model="selectedAddress" placeholder="请选择收货地址飞奔过去🐾" class="address-select" placement="top">
          <el-option v-for="addr in addresses" :key="addr.id" :label="`${addr.receiver_name} - ${addr.detail_address}`" :value="addr.id" />
        </el-select>
        
        <el-button type="primary" size="large" class="checkout-btn" @click="handleCheckout" :loading="checkoutLoading">
          一键结账 🌟
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'ShopcartContent',
  emits: ['close'],
  setup(props, { emit }) {
    const loading = ref(true)
    const checkoutLoading = ref(false)
    const cartItems = ref([])
    const addresses = ref([])
    const selectedAddress = ref(null)

    const loadCart = async () => {
      try {
        const res = await axios.get('/api/shopper/cart/my_cart/')
        cartItems.value = res.data.items || []
      } catch (err) {
        ElMessage.error('读取购物车失败')
      } finally {
        loading.value = false
      }
    }

    const loadAddresses = async () => {
      try {
        const res = await axios.get('/api/shopper/addresses/')
        addresses.value = res.data.results || res.data
        if (addresses.value.length > 0) {
            // 挑默认地址，没有就挑第一个
            const def = addresses.value.find(c => c.is_default)
            selectedAddress.value = def ? def.id : addresses.value[0].id
        }
      } catch(e) {
          console.error(e)
      }
    }

    const updateQuantity = async (item, newVal) => {
      try {
          await axios.patch(`/api/shopper/cart-items/${item.id}/`, { quantity: newVal })
      } catch (error) {
          ElMessage.error('修改数量失败')
      }
    }

    const removeItem = async (itemId) => {
      try {
        await axios.delete(`/api/shopper/cart-items/${itemId}/`)
        loadCart() // 重新拉取
        ElMessage.success('移除成功')
      } catch(err) {
        ElMessage.error('移除失败')
      }
    }

    const totalPrice = computed(() => {
      return cartItems.value.reduce((sum, item) => sum + (item.product_detail.price * item.quantity), 0)
    })

    const handleCheckout = async () => {
      if (!selectedAddress.value) {
        return ElMessage.warning('主子别急，还没有添加收货地址呢！')
      }
      checkoutLoading.value = true
      try {
        const itemIds = cartItems.value.map(i => i.id)
        const res = await axios.post('/api/shopper/orders/checkout/', {
          address_id: selectedAddress.value,
          cart_item_ids: itemIds
        })
        ElMessage.success({ message: `结账成功啦！你的猫条在路上~ 订单号：${res.data.order_no}`, type: 'success' })
        emit('close')
        setTimeout(() => {
           window.location.reload() // 简单粗暴清空状态
        }, 1500)
      } catch (err) {
        ElMessage.error(err.response?.data?.detail || '结账失败，可能商品被抢光了')
      } finally {
        checkoutLoading.value = false
      }
    }

    onMounted(() => {
      loadCart()
      loadAddresses()
    })

    return { loading, checkoutLoading, cartItems, addresses, selectedAddress, updateQuantity, removeItem, totalPrice, handleCheckout }
  }
}
</script>

<style scoped>
.shopcart-drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-color);
}
.cart-items-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.cart-item {
  display: flex;
  background: #fff;
  padding: 16px;
  border-radius: 16px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(255, 168, 186, 0.15);
}
.item-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  margin-right: 16px;
}
.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.item-title {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.item-price {
  color: var(--primary-color);
  font-weight: bold;
  font-size: 16px;
  margin-top: 5px;
}
.item-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}
.cart-footer {
  background: #fff;
  padding: 24px;
  border-top: 1px solid #ebeef5;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.05);
}
.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
}
.total-price {
  color: var(--primary-color);
  font-size: 28px;
  font-weight: 800;
}
.checkout-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.checkout-btn {
  width: 100%;
  font-size: 18px;
  font-weight: bold;
  height: 50px;
  border-radius: 25px !important;
}
</style>
