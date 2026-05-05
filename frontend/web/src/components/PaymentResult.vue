<template>
  <base-page>
    <div class="payment-result-container">
      <el-card class="result-card" shadow="never" v-loading="loading">
        <div class="result-content">
          <!-- 支付成功 -->
          <div v-if="payStatus === 'success'" class="result-icon success">
            <el-icon :size="80" color="#67C23A"><SuccessFilled /></el-icon>
          </div>
          <!-- 支付失败/待确认 -->
          <div v-else-if="!queryError" class="result-icon pending">
            <el-icon :size="80" color="#E6A23C"><WarningFilled /></el-icon>
          </div>
          <!-- 查询出错 -->
          <div v-else class="result-icon error">
            <el-icon :size="80" color="#F56C6C"><CircleCloseFilled /></el-icon>
          </div>

          <h2 class="result-title">{{ payStatus === 'success' ? '支付成功！' : queryError ? '查询出错' : '支付结果确认中...' }}</h2>
          
          <div class="order-info" v-if="!queryError">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="订单号">{{ orderNo }}</el-descriptions-item>
              <el-descriptions-item label="支付宝流水号">{{ tradeNo || '暂无' }}</el-descriptions-item>
              <el-descriptions-item label="支付金额">
                <span class="amount">¥{{ totalAmount }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="订单状态">
                <el-tag :type="statusTagType">{{ statusText }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="actions">
            <el-button v-if="queryError" type="danger" size="large" round @click="retryQuery">重新查询</el-button>
            <el-button type="primary" size="large" round @click="goToOrders">查看我的订单</el-button>
            <el-button size="large" round @click="goHome">返回首页</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </base-page>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '@/axios'
import { ElMessage } from 'element-plus'
import { SuccessFilled, WarningFilled, CircleCloseFilled } from '@element-plus/icons-vue'

export default {
  name: 'PaymentResult',
  components: { SuccessFilled, WarningFilled, CircleCloseFilled },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const loading = ref(true)
    const orderStatus = ref('')
    const queryError = ref(false)

    const orderNo = computed(() => route.query.out_trade_no || '')
    const tradeNo = computed(() => route.query.trade_no || '')
    const totalAmount = computed(() => route.query.total_amount || '0.00')
    const payStatus = computed(() => {
      if (orderStatus.value === 'PAID') return 'success'
      return 'pending'
    })
    const statusText = computed(() => {
      const map = {
        'PAID': '已支付',
        'PENDING': '待支付',
        'SHIPPED': '已发货',
        'COMPLETED': '已完成'
      }
      return map[orderStatus.value] || '确认中'
    })
    const statusTagType = computed(() => {
      if (orderStatus.value === 'PAID') return 'success'
      return 'warning'
    })

    const queryPaymentStatus = async () => {
      if (!orderNo.value) return
      queryError.value = false
      try {
        const res = await axios.get('/api/shopper/pay/query/', {
          params: { order_no: orderNo.value }
        })
        orderStatus.value = res.data?.status || ''
      } catch (err) {
        queryError.value = true
        ElMessage.error('查询支付状态失败')
      } finally {
        loading.value = false
      }
    }

    const retryQuery = () => {
      loading.value = true
      queryPaymentStatus()
    }

    const goToOrders = () => router.push('/orders')
    const goHome = () => router.push('/commodity')

    onMounted(() => {
      queryPaymentStatus()
    })

    return { loading, orderNo, tradeNo, totalAmount, payStatus, queryError, statusText, statusTagType, retryQuery, goToOrders, goHome }
  }
}
</script>

<style scoped>
.payment-result-container {
  max-width: 600px;
  margin: 40px auto;
}
.result-card {
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(255, 168, 186, 0.1) !important;
}
.result-content {
  text-align: center;
  padding: 20px 0;
}
.result-icon {
  margin-bottom: 20px;
}
.result-title {
  font-size: 24px;
  margin-bottom: 30px;
  color: #303133;
}
.order-info {
  margin-bottom: 30px;
}
.amount {
  font-size: 20px;
  font-weight: bold;
  color: #E6A23C;
}
.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}
</style>
