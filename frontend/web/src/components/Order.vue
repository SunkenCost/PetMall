<template>
  <base-page>
    <div class="orders-center">
      <h2>📦 我的宠物粮饷流转单</h2>
      <el-empty v-if="orders.length === 0" description="您还没有下过单，赶紧去给主子挑点好东西吧！" />

      <div v-else class="order-list" v-loading="loading">
        <el-card v-for="order in orders" :key="order.id" class="order-card" shadow="never">
          <template #header>
            <div class="order-header">
              <span class="order-no">订单号：{{ order.order_no }}</span>
              <span class="order-time">系统流转时间：{{ new Date(order.create_time).toLocaleString() }}</span>
              <el-tag :type="getStatusTag(order.status)" class="status-tag">
                {{ statusMap[order.status] }}
              </el-tag>
            </div>
          </template>
          
          <div class="order-body">
            <div class="products-snapshot">
               <div v-for="item in order.items" :key="item.id" class="item-line">
                 <span class="item-name">{{ item.product_name }}</span>
                 <span class="item-meta">x{{ item.quantity }} = ¥{{ item.subtotal }}</span>
               </div>
            </div>
            
            <div class="address-snapshot">
              <strong>快照收件信息：</strong><br/>
              {{ order.receiver_name }} ({{ order.receiver_phone }})<br/>
              {{ order.receiver_address }}
            </div>
          </div>
          
          <div class="order-footer">
            <span>实付款：<strong style="color:var(--primary-color); font-size: 20px;">¥{{ order.total_amount }}</strong></span>
            <el-button type="primary" v-if="order.status === 'PENDING'" round>立即支付 (Demo)</el-button>
          </div>
        </el-card>
      </div>
    </div>
  </base-page>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'OrdersPage',
  setup() {
    const orders = ref([])
    const loading = ref(false)
    const statusMap = {
      'PENDING': '待支付',
      'PAID': '已脱单待出库',
      'SHIPPED': '在路上啦',
      'COMPLETED': '喵星人已签收',
      'CLOSED': '已关闭'
    }

    const fetchOrders = async () => {
      loading.value = true
      try {
        const res = await axios.get('/api/shopper/orders/')
        orders.value = res.data.results || res.data
      } catch (err) {
        ElMessage.error('无法读取流转信息')
      } finally {
        loading.value = false
      }
    }

    const getStatusTag = (status) => {
      if (status === 'PENDING') return 'warning'
      if (status === 'COMPLETED') return 'success'
      if (status === 'PAID') return 'info'
      return ''
    }

    onMounted(() => fetchOrders())

    return { orders, loading, statusMap, getStatusTag }
  }
}
</script>

<style scoped>
.orders-center {
  max-width: 1000px;
  margin: 0 auto;
}
h2 {
  margin-bottom: 30px;
}
.order-card {
  margin-bottom: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(255, 168, 186, 0.1) !important;
}
.order-header {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 14px;
}
.order-no {
  font-weight: 600;
}
.order-time {
  color: var(--text-light);
  flex: 1;
}
.order-body {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
}
.products-snapshot {
  flex: 2;
}
.item-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: var(--text-main);
}
.address-snapshot {
  flex: 1;
  background: var(--bg-color);
  padding: 15px;
  border-radius: 8px;
  font-size: 13px;
  color: #5a5e66;
  line-height: 1.5;
  margin-left: 20px;
}
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #ebeef5;
}
</style>
