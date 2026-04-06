<template>
  <div class="admin-orders">
    <!-- 状态过滤标签栏 -->
    <div class="status-tabs">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        class="status-tab"
        :class="{ active: filterStatus === tab.value }"
        @click="switchStatus(tab.value)"
      >
        {{ tab.label }}
        <span class="tab-count" v-if="tab.count">{{ tab.count }}</span>
      </button>
    </div>

    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索订单号 / 收件人 / 手机号..."
        clearable
        style="width: 300px"
        @input="handleSearch"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <!-- 订单列表 -->
    <div class="order-list" v-loading="loading">
      <div v-if="orders.length === 0 && !loading" class="empty-tip">
        暂无符合条件的订单
      </div>

      <div
        v-for="order in orders"
        :key="order.id"
        class="order-card"
      >
        <div class="order-header">
          <div class="order-no">
            <span class="label">订单号：</span>
            <span class="value">{{ order.order_no }}</span>
          </div>
          <div class="order-meta">
            <span class="meta-item">买家：{{ order.username }}</span>
            <span class="meta-item">下单：{{ formatTime(order.create_time) }}</span>
          </div>
          <el-tag :type="statusStyle[order.status]" size="small">
            {{ order.status_display }}
          </el-tag>
        </div>

        <!-- 订单商品 -->
        <div class="order-items">
          <div v-for="item in order.items" :key="item.id" class="order-item">
            <span class="item-name">{{ item.product_name }}</span>
            <span class="item-price">¥{{ item.product_price }} × {{ item.quantity }}</span>
            <span class="item-sub">= ¥{{ item.subtotal }}</span>
          </div>
        </div>

        <!-- 收货信息 + 操作 -->
        <div class="order-footer">
          <div class="receiver-info">
            <el-icon class="mr-4"><Location /></el-icon> {{ order.receiver_name }} {{ order.receiver_phone }}
            | {{ order.receiver_address }}
            <span v-if="order.logistics_no" class="logistics">
              | <el-icon class="mr-4"><Van /></el-icon> 物流：{{ order.logistics_no }}
            </span>
          </div>
          <div class="order-total">
            合计：<strong>¥{{ order.total_amount }}</strong>
          </div>
          <div class="order-actions">
            <el-button
              v-if="order.status === 'PAID'"
              type="primary"
              size="small"
              plain
              @click="openShipDialog(order)"
            >
              <el-icon class="mr-4"><Van /></el-icon> 发货
            </el-button>
            <el-button
              v-if="order.status === 'SHIPPED'"
              type="success"
              size="small"
              plain
              @click="markComplete(order)"
            >
              <el-icon class="mr-4"><CircleCheck /></el-icon> 标记完成
            </el-button>
            <el-button
              v-if="order.status === 'PENDING'"
              type="danger"
              size="small"
              plain
              @click="closeOrder(order)"
            >
              <el-icon class="mr-4"><Close /></el-icon> 关闭订单
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadOrders"
      />
    </div>

    <!-- 发货对话框 -->
    <el-dialog v-model="shipVisible" title="订单发货" width="450px" destroy-on-close>
      <div class="dialog-info" v-if="shippingOrder">
        <p>订单号：<strong>{{ shippingOrder.order_no }}</strong></p>
        <p>收件人：<strong>{{ shippingOrder.receiver_name }} {{ shippingOrder.receiver_phone }}</strong></p>
        <p>地址：{{ shippingOrder.receiver_address }}</p>
      </div>
      <el-form style="margin-top: 20px">
        <el-form-item label="物流单号" label-width="80px">
          <el-input v-model="logisticsNo" placeholder="请输入物流单号（如顺丰/京东快递单号）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmShip" :loading="submitting">确认发货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Location, Van, CircleCheck, Close } from '@element-plus/icons-vue'
import axios from '@/axios'

export default {
  name: 'AdminOrders',
  components: { Search, Location, Van, CircleCheck, Close },
  setup() {
    const orders = ref([])
    const loading = ref(false)
    const submitting = ref(false)
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const searchKeyword = ref('')
    const filterStatus = ref('')

    const shipVisible = ref(false)
    const shippingOrder = ref(null)
    const logisticsNo = ref('')

    const statusTabs = ref([
      { label: '全部', value: '' },
      { label: '待支付', value: 'PENDING' },
      { label: '待发货', value: 'PAID', count: 0 },
      { label: '已发货', value: 'SHIPPED' },
      { label: '已完成', value: 'COMPLETED' },
      { label: '已关闭', value: 'CLOSED' },
    ])

    const statusStyle = {
      PENDING: 'info',
      PAID: 'warning',
      SHIPPED: 'primary',
      COMPLETED: 'success',
      CLOSED: 'danger',
    }

    const getAdminHeaders = () => {
      const u = JSON.parse(localStorage.getItem('pet_user') || '{}')
      return { 'X-Admin-Username': u.username || '' }
    }

    const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : '—'

    const loadOrders = async () => {
      loading.value = true
      try {
        const params = { page: currentPage.value }
        if (filterStatus.value) params.status = filterStatus.value
        if (searchKeyword.value) params.search = searchKeyword.value
        const res = await axios.get('/api/merchant/orders/', { params, headers: getAdminHeaders() })
        orders.value = res.data.results || res.data
        total.value = res.data.count || 0
      } catch (e) {
        ElMessage.error('加载订单失败')
      } finally {
        loading.value = false
      }
    }

    const switchStatus = (val) => {
      filterStatus.value = val
      currentPage.value = 1
      loadOrders()
    }

    let searchTimer = null
    const handleSearch = () => {
      clearTimeout(searchTimer)
      searchTimer = setTimeout(() => {
        currentPage.value = 1
        loadOrders()
      }, 400)
    }

    const openShipDialog = (order) => {
      shippingOrder.value = order
      logisticsNo.value = ''
      shipVisible.value = true
    }

    const confirmShip = async () => {
      if (!logisticsNo.value.trim()) {
        ElMessage.warning('请输入物流单号')
        return
      }
      submitting.value = true
      try {
        await axios.post(
          `/api/merchant/orders/${shippingOrder.value.id}/ship/`,
          { logistics_no: logisticsNo.value },
          { headers: getAdminHeaders() }
        )
        ElMessage.success('发货成功！')
        shipVisible.value = false
        loadOrders()
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || '发货失败')
      } finally {
        submitting.value = false
      }
    }

    const markComplete = async (order) => {
      try {
        await ElMessageBox.confirm(`确认将订单 ${order.order_no} 标记为已完成？`, '确认', { type: 'warning' })
        await axios.post(`/api/merchant/orders/${order.id}/complete/`, {}, { headers: getAdminHeaders() })
        ElMessage.success('订单已标记完成')
        loadOrders()
      } catch (e) {
        if (e !== 'cancel') ElMessage.error('操作失败')
      }
    }

    const closeOrder = async (order) => {
      try {
        await ElMessageBox.confirm(`确认关闭订单 ${order.order_no}？`, '确认关闭', { type: 'warning' })
        await axios.post(`/api/merchant/orders/${order.id}/close/`, {}, { headers: getAdminHeaders() })
        ElMessage.success('订单已关闭')
        loadOrders()
      } catch (e) {
        if (e !== 'cancel') ElMessage.error('操作失败')
      }
    }

    onMounted(loadOrders)

    return {
      orders, loading, submitting, total, currentPage, pageSize,
      searchKeyword, filterStatus, statusTabs, statusStyle,
      shipVisible, shippingOrder, logisticsNo,
      loadOrders, switchStatus, handleSearch,
      openShipDialog, confirmShip, markComplete, closeOrder,
      formatTime,
    }
  }
}
</script>

<style scoped>
.admin-orders { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }

.status-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.status-tab {
  padding: 8px 18px;
  border-radius: 4px;
  border: 1px solid #d9d9d9;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.status-tab:hover { border-color: #1677FF; color: #1677FF; }
.status-tab.active { background: #1677FF; border-color: #1677FF; color: #fff; }
.tab-count {
  background: rgba(255,255,255,0.3);
  border-radius: 10px;
  padding: 0 6px;
  font-size: 11px;
}
.status-tab.active .tab-count { background: rgba(255,255,255,0.3); }

.toolbar { margin-bottom: 16px; }

.order-list { display: flex; flex-direction: column; gap: 16px; }
.order-card {
  background: #fff;
  border-radius: 6px;
  padding: 20px;
  border: 1px solid #e8e8e8;
  transition: all 0.3s;
}
.order-card:hover { border-color: #1677FF; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

.order-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.order-no .label { color: #909399; font-size: 13px; }
.order-no .value { font-weight: 700; color: #1a1f3a; font-size: 14px; }
.order-meta { display: flex; gap: 16px; flex: 1; }
.meta-item { font-size: 13px; color: #909399; }

.order-items {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}
.item-name { flex: 1; color: #303133; }
.item-price { color: #909399; }
.item-sub { font-weight: 600; color: #1a1f3a; min-width: 80px; text-align: right; }

.order-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.receiver-info {
  flex: 1;
  font-size: 13px;
  color: #606266;
}
.logistics { color: #1677FF; font-weight: 500; }
.order-total { font-size: 14px; color: #606266; }
.order-total strong { font-size: 18px; color: #ef4444; }
.order-actions { display: flex; gap: 8px; }

.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 24px; }
.empty-tip { text-align: center; color: #c0c4cc; padding: 60px; font-size: 16px; }
.dialog-info { background: #f8f9fa; border-radius: 8px; padding: 12px 16px; }
.dialog-info p { margin: 6px 0; color: #606266; font-size: 14px; }
.mr-4 { margin-right: 4px; }
</style>
