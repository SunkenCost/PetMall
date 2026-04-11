<template>
  <div class="dashboard-v2">
    <!-- 顶部四项基础指标 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6" v-for="item in topStats" :key="item.label">
        <el-card shadow="hover" :body-style="{ padding: '20px' }">
          <div class="stat-card-inner">
            <div class="stat-icon-box" :class="item.type">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">{{ item.label }}</div>
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-footer">
                <span :class="item.trend >= 0 ? 'text-success' : 'text-danger'">
                  {{ item.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(item.trend) }}%
                </span>
                <span class="text-secondary ml-4">较上周</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 中间核心区域：左侧趋势图 (2/3)，右侧紧急处理 (1/3) -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="font-bold">近30天订单趋势</span>
              <el-radio-group v-model="chartTimeRange" size="small">
                <el-radio-button label="30">近30天</el-radio-button>
                <el-radio-button label="7">近7天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div v-if="trendData.length === 0" class="empty-placeholder">
            <el-empty description="暂无交易数据" :image-size="100" />
          </div>
          <div v-else class="business-chart">
            <div class="chart-axis-y">
              <span>{{ maxTrendValue }}</span>
              <span>{{ Math.round(maxTrendValue / 2) }}</span>
              <span>0</span>
            </div>
            <div class="chart-main">
              <div
                v-for="day in filteredTrendData"
                :key="day.date"
                class="chart-bar-item"
              >
                <el-tooltip
                  effect="dark"
                  :content="`${day.date}: ${day.count} 单 (¥${formatMoney(day.revenue)})`"
                  placement="top"
                >
                  <div
                    class="bar-fill"
                    :style="{ height: getBarHeight(day.count) + '%' }"
                  ></div>
                </el-tooltip>
                <div class="bar-date">{{ day.date.slice(-5) }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="alert-card">
          <template #header>
            <div class="card-header">
              <span class="font-bold">紧急处理事项</span>
              <el-tag type="danger" effect="dark" size="small" v-if="totalAlerts > 0">{{ totalAlerts }}</el-tag>
            </div>
          </template>
          
          <div class="alert-list">
            <div class="alert-item" @click="$router.push('/admin-panel/orders?status=PAID')">
              <div class="alert-left">
                <el-icon class="icon-warning"><Truck /></el-icon>
                <span>待发货订单</span>
              </div>
              <div class="alert-right">
                <span class="alert-count" :class="{ 'has-val': stats.orders.pending_ship > 0 }">{{ stats.orders.pending_ship }}</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>

            <div class="alert-item" @click="$router.push('/admin-panel/inventory?low=1')">
              <div class="alert-left">
                <el-icon class="icon-danger"><Warning /></el-icon>
                <span>库存预警商品</span>
              </div>
              <div class="alert-right">
                <span class="alert-count" :class="{ 'has-val': stats.products.low_stock > 0 }">{{ stats.products.low_stock }}</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>

            <div class="alert-item" @click="$router.push('/admin-panel/aftersales?status=APPLYING')">
              <div class="alert-left">
                <el-icon class="icon-info"><Refresh /></el-icon>
                <span>待处理售后</span>
              </div>
              <div class="alert-right">
                <span class="alert-count" :class="{ 'has-val': stats.aftersales.pending > 0 }">{{ stats.aftersales.pending }}</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>

          <div class="quick-entry-grid mt-20">
            <div class="entry-btn" @click="$router.push('/admin-panel/products')">
              <el-icon><Plus /></el-icon>
              <span>上架商品</span>
            </div>
            <div class="entry-btn" @click="$router.push('/admin-panel/orders')">
              <el-icon><List /></el-icon>
              <span>订单中心</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部分析区域 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card shadow="hover" class="rank-card">
          <template #header>
            <div class="card-header"><span class="font-bold">爆款商品 Top 5</span></div>
          </template>
          <div v-if="topProducts.length === 0" class="empty-placeholder-small">
            <el-empty description="暂无售出商品" :image-size="60" />
          </div>
          <div class="rank-list" v-else>
            <div v-for="(item, index) in topProducts" :key="item.id" class="rank-item">
              <div class="rank-index" :class="'top-' + (index + 1)">{{ index + 1 }}</div>
              <div class="rank-name">{{ item.name }}</div>
              <div class="rank-sales">{{ item.sales }} 件</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover" class="rank-card">
          <template #header>
            <div class="card-header"><span class="font-bold">总体订单状态分布</span></div>
          </template>
          <div v-if="statusDistribution.length === 0" class="empty-placeholder-small">
            <el-empty description="暂无订单" :image-size="60" />
          </div>
          <div class="status-list" v-else>
            <div v-for="st in statusDistribution" :key="st.status" class="status-item">
              <div class="status-name">{{ statusMap[st.status] || st.status }}</div>
              <div class="status-bar-wrap">
                 <div class="status-bar" :style="{ width: (st.count / totalOrderStatusCount * 100) + '%' }"></div>
              </div>
              <div class="status-count">{{ st.count }} 单</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from '@/axios'
import { 
  ShoppingCart, Money, Goods, Box, 
  Truck, Warning, Refresh, ArrowRight,
  Plus, List 
} from '@element-plus/icons-vue'

export default {
  name: 'AdminDashboard',
  components: {
    ShoppingCart, Money, Goods, Box,
    Truck, Warning, Refresh, ArrowRight,
    Plus, List
  },
  setup() {
    const stats = ref({
      orders: { total: 0, today: 0, pending_ship: 0 },
      revenue: { total: 0, monthly: 0 },
      products: { total: 0, on_shelf: 0, low_stock: 0 },
      aftersales: { pending: 0 },
    })
    const trendData = ref([])
    const topProducts = ref([])
    const statusDistribution = ref([])
    const chartTimeRange = ref('30')

    const statusMap = {
      'PENDING': '待支付',
      'PAID': '待发货',
      'SHIPPED': '已发货',
      'COMPLETED': '已完成',
      'CLOSED': '已关闭'
    }

    const formatMoney = (val) => Number(val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

    const loadDashboard = async () => {
      try {
        const userInfo = JSON.parse(localStorage.getItem('pet_user') || '{}')
        const res = await axios.get('/api/merchant/dashboard/', {
          headers: { 'X-Admin-Username': userInfo.username || '' }
        })
        stats.value = res.data
        trendData.value = res.data.trend || []
        topProducts.value = res.data.top_products || []
        statusDistribution.value = res.data.status_distribution || []
      } catch (e) {
        console.error('看板数据加载失败', e)
      }
    }

    const filteredTrendData = computed(() => {
      const days = parseInt(chartTimeRange.value)
      return trendData.value.slice(-days)
    })

    const maxTrendValue = computed(() => {
      if (filteredTrendData.value.length === 0) return 100
      return Math.max(...filteredTrendData.value.map(d => d.count), 10)
    })

    const getBarHeight = (count) => {
      return (count / maxTrendValue.value) * 100
    }

    const totalAlerts = computed(() => {
      return stats.value.orders.pending_ship + stats.value.products.low_stock + stats.value.aftersales.pending
    })

    const topStats = computed(() => [
      { label: '累计订单', value: stats.value.orders.total, icon: 'ShoppingCart', type: 'primary', trend: 12.5 },
      { label: '当月销售额', value: '¥' + formatMoney(stats.value.revenue.monthly), icon: 'Money', type: 'success', trend: 8.2 },
      { label: '在售商品', value: stats.value.products.on_shelf, icon: 'Goods', type: 'warning', trend: -2.1 },
      { label: '商品总数', value: stats.value.products.total, icon: 'Box', type: 'info', trend: 0.5 },
    ])

    const totalOrderStatusCount = computed(() => {
      return statusDistribution.value.reduce((acc, curr) => acc + curr.count, 0) || 1
    })

    onMounted(loadDashboard)

    return { 
      stats, trendData, chartTimeRange, filteredTrendData,
      topProducts, statusDistribution, statusMap, totalOrderStatusCount,
      formatMoney, getBarHeight, maxTrendValue,
      topStats, totalAlerts 
    }
  }
}
</script>

<style scoped>
.dashboard-v2 {
  animation: fadeIn 0.4s ease-out;
  color: #303133;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.mb-20 { margin-bottom: 20px; }
.mt-20 { margin-top: 20px; }
.ml-4 { margin-left: 4px; }
.font-bold { font-weight: 600; }

.stat-card-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.stat-icon-box.primary { background: #ecf5ff; color: #409eff; }
.stat-icon-box.success { background: #f0f9eb; color: #67c23a; }
.stat-icon-box.warning { background: #fdf6ec; color: #e6a23c; }
.stat-icon-box.info    { background: #f4f4f5; color: #909399; }

.stat-content { flex: 1; }
.stat-label { font-size: 13px; color: #909399; margin-bottom: 4px; }
.stat-value { font-size: 20px; font-weight: 700; color: #303133; }
.stat-footer { font-size: 11px; margin-top: 4px; display: flex; align-items: center; }

.text-success { color: #67c23a; }
.text-danger  { color: #f56c6c; }
.text-secondary { color: #909399; }

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 图标区域样式 */
.chart-card { height: 400px; }
.business-chart {
  display: flex;
  height: 280px;
  padding-top: 20px;
}
.chart-axis-y {
  width: 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 11px;
  color: #909399;
  padding-bottom: 24px;
}
.chart-main {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 8px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 4px;
}
.chart-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
}
.bar-fill {
  width: 100%;
  max-width: 30px;
  background: #409eff;
  border-radius: 4px 4px 0 0;
  transition: height 0.5s cubic-bezier(0.18, 0.89, 0.32, 1.28);
}
.bar-fill:hover { background: #66b1ff; }
.bar-date {
  font-size: 10px;
  color: #c0c4cc;
  margin-top: 8px;
  white-space: nowrap;
}

/* 预警区域样式 */
.alert-card { height: 400px; }
.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.alert-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.alert-item:hover { background: #f0f2f5; transform: translateX(4px); }
.alert-left { display: flex; align-items: center; gap: 10px; font-size: 14px; }
.alert-right { display: flex; align-items: center; gap: 8px; color: #c0c4cc; }
.alert-count { font-size: 16px; font-weight: 700; color: #909399; }
.alert-count.has-val { color: #f56c6c; }

.icon-warning { color: #e6a23c; }
.icon-danger  { color: #f56c6c; }
.icon-info    { color: #409eff; }

.quick-entry-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.entry-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 80px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  color: #606266;
  transition: all 0.2s;
}
.entry-btn:hover {
  color: #409eff;
  border-color: #409eff;
  background: #ecf5ff;
}
.entry-btn .el-icon { font-size: 20px; }
.entry-btn span { font-size: 12px; }

.empty-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 280px;
}
.empty-placeholder-small {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 180px;
}

/* 底部排名卡片 */
.rank-card { height: 260px; }
.rank-list, .status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 8px;
}
.rank-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}
.rank-index {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f4f4f5;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  margin-right: 12px;
}
.rank-index.top-1 { background: #fef0f0; color: #f56c6c; }
.rank-index.top-2 { background: #fdf6ec; color: #e6a23c; }
.rank-index.top-3 { background: #ecf5ff; color: #409eff; }
.rank-name {
  flex: 1;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rank-sales { color: #909399; font-weight: 500; }

.status-item {
  display: flex;
  align-items: center;
  font-size: 13px;
}
.status-name { width: 60px; color: #606266; }
.status-bar-wrap {
  flex: 1;
  height: 8px;
  background: #ebeef5;
  border-radius: 4px;
  margin: 0 12px;
  overflow: hidden;
}
.status-bar {
  height: 100%;
  background: #67c23a;
  border-radius: 4px;
  transition: width 0.5s ease;
}
.status-count { width: 40px; text-align: right; color: #909399; }
</style>
