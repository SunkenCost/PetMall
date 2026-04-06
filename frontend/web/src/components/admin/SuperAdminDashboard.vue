<template>
  <div class="super-dashboard-v2">
    <!-- 页头 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="title">平台概览</h1>
        <p class="subtitle">实时监控 PetMall 平台的运行状态与用户增长</p>
      </div>
      <div class="header-extra">
        <el-tag type="info" effect="plain" class="time-tag">
          <el-icon><Calendar /></el-icon> {{ todayStr }}
        </el-tag>
      </div>
    </div>

    <!-- 用户数据摘要 (Top Stats) -->
    <el-row :gutter="20" class="mb-24">
      <el-col :span="6" v-for="card in topSummary" :key="card.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-inner">
            <div class="stat-info">
              <span class="stat-label">{{ card.label }}</span>
              <div class="stat-value">{{ card.value }}</div>
            </div>
            <div class="stat-icon" :style="{ color: card.color, background: card.bgColor }">
              <el-icon><component :is="card.icon" /></el-icon>
            </div>
          </div>
          <div class="stat-footer">
            <span :class="card.trend >= 0 ? 'up' : 'down'">
              {{ card.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(card.trend) }}%
            </span>
            <span class="footer-desc">较上月同期</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 核心区域：用户增长趋势 (16/24) + 系统健康度 (8/24) -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="hover" class="main-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">用户分布与增长</span>
              <el-button-group size="small">
                <el-button>周视图</el-button>
                <el-button type="primary">月视图</el-button>
              </el-button-group>
            </div>
          </template>
          
          <div class="user-chart-section">
            <div class="user-stats-bar">
              <div class="user-stat-item">
                <span class="u-label">活跃账户</span>
                <span class="u-val">{{ stats.users.active }}</span>
                <el-progress :percentage="activePct" :color="customColors" :show-text="false" />
              </div>
              <div class="user-stat-item">
                <span class="u-label">商家账户</span>
                <span class="u-val">{{ stats.users.staff }}</span>
                <el-progress :percentage="staffPct" color="#409eff" :show-text="false" />
              </div>
              <div class="user-stat-item">
                <span class="u-label">冻结账户</span>
                <span class="u-val">{{ stats.users.frozen }}</span>
                <el-progress :percentage="frozenPct" color="#f56c6c" :show-text="false" />
              </div>
            </div>
            
            <!-- 模拟增长趋势占位图 (商用感) -->
            <div class="mock-growth-chart">
              <div class="chart-y-axis">
                <span>{{ Math.round(stats.users.total * 1.2) }}</span>
                <span>{{ Math.round(stats.users.total * 0.6) }}</span>
                <span>0</span>
              </div>
              <div class="chart-area">
                <div 
                  v-for="(h, i) in mockTrendHeights" 
                  :key="i"
                  class="chart-line-point"
                  :style="{ height: h + '%', left: (i * 10) + '%' }"
                >
                  <div class="point-dot"></div>
                </div>
                <svg class="chart-svg-line" viewBox="0 0 100 100" preserveAspectRatio="none">
                  <path :d="svgPath" fill="none" stroke="#409eff" stroke-width="2" />
                </svg>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="side-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">系统健康监控</span>
              <el-icon class="status-pulse"><Monitor /></el-icon>
            </div>
          </template>
          
          <div class="health-monitor">
            <div class="monitor-item" :class="{ 'warning': stats.system_logs.pending > 0 }">
              <div class="m-top">
                <span class="m-label">异常日志 (待处理)</span>
                <span class="m-status">{{ stats.system_logs.pending > 0 ? '需要关注' : '运行正常' }}</span>
              </div>
              <div class="m-val">{{ stats.system_logs.pending }}</div>
              <router-link to="/super-admin/system-logs" class="m-link">查看详情 <el-icon><ArrowRight /></el-icon></router-link>
            </div>

            <div class="monitor-item mt-16 secondary">
              <div class="m-top">
                <span class="m-label">全平台用户规模</span>
                <span class="m-status">稳步增长</span>
              </div>
              <div class="m-val">{{ stats.users.total }}</div>
              <router-link to="/super-admin/users" class="m-link">用户中心 <el-icon><ArrowRight /></el-icon></router-link>
            </div>

            <div class="platform-entry mt-24">
              <div class="entry-row" @click="$router.push('/admin-panel/dashboard')">
                <el-icon><Shop /></el-icon>
                <span>跳转至商家管理后台</span>
                <el-icon class="ml-auto"><Right /></el-icon>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <div v-if="loading" class="loading-overlay">
      <el-skeleton :rows="10" animated />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from '@/axios'
import { 
  User, UserFilled, Warning, Management,
  Monitor, Calendar, ArrowRight, Shop, Right
} from '@element-plus/icons-vue'

export default {
  name: 'SuperAdminDashboard',
  components: {
    User, UserFilled, Warning, Management,
    Monitor, Calendar, ArrowRight, Shop, Right
  },
  setup() {
    const loading = ref(true)
    const stats = ref({
      users: { total: 0, today_registered: 0, monthly_registered: 0, active: 0, frozen: 0, staff: 0, superuser: 0 },
      system_logs: { total: 0, pending: 0 },
    })

    const today = new Date()
    const todayStr = today.toLocaleDateString('zh-CN', { 
      year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' 
    })

    const activePct = computed(() => stats.value.users.total ? Math.round((stats.value.users.active / stats.value.users.total) * 100) : 0)
    const staffPct = computed(() => stats.value.users.total ? Math.round((stats.value.users.staff / stats.value.users.total) * 100) : 0)
    const frozenPct = computed(() => stats.value.users.total ? Math.round((stats.value.users.frozen / stats.value.users.total) * 100) : 0)

    const topSummary = computed(() => [
      { label: '用户总额', value: stats.value.users.total, icon: 'User', color: '#409eff', bgColor: '#ecf5ff', trend: 5.2 },
      { label: '本月新增', value: stats.value.users.monthly_registered, icon: 'UserFilled', color: '#67c23a', bgColor: '#f0f9eb', trend: 12.8 },
      { label: '异常告警', value: stats.value.system_logs.pending, icon: 'Warning', color: '#f56c6c', bgColor: '#fef0f0', trend: -15.4 },
      { label: '特权账户', value: stats.value.users.staff + stats.value.users.superuser, icon: 'Management', color: '#e6a23c', bgColor: '#fdf6ec', trend: 2.1 }
    ])

    // 模拟趋势数据点 (商用展示用)
    const mockTrendHeights = [30, 45, 40, 60, 55, 75, 70, 85, 80, 95]
    const svgPath = computed(() => {
      return "M" + mockTrendHeights.map((h, i) => `${i * 10},${100 - h}`).join(" L")
    })

    const loadStats = async () => {
      loading.value = true
      try {
        const res = await axios.get('/api/accounts/admin/stats/')
        stats.value = res.data
      } catch (e) {
        console.error('获取系统统计失败', e)
      } finally {
        loading.value = false
      }
    }

    onMounted(loadStats)

    return { 
      loading, stats, todayStr, topSummary, 
      activePct, staffPct, frozenPct,
      mockTrendHeights, svgPath,
      customColors: [
        { color: '#f56c6c', percentage: 20 },
        { color: '#e6a23c', percentage: 40 },
        { color: '#5cb87a', percentage: 60 },
        { color: '#1989fa', percentage: 80 },
        { color: '#6f7ad3', percentage: 100 },
      ]
    }
  }
}
</script>

<style scoped>
.super-dashboard-v2 {
  max-width: 1300px;
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.mb-24 { margin-bottom: 24px; }
.mt-16 { margin-top: 16px; }
.mt-24 { margin-top: 24px; }
.ml-auto { margin-left: auto; }

/* 页头 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}
.title { font-size: 22px; font-weight: 700; color: #1f2937; margin: 0 0 8px 0; }
.subtitle { font-size: 14px; color: #6b7280; margin: 0; }
.time-tag { display: flex; align-items: center; gap: 6px; padding: 12px 16px; }

/* 统计卡片 */
.stat-card { border: none; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.stat-inner { display: flex; justify-content: space-between; margin-bottom: 12px; }
.stat-label { font-size: 13px; color: #6b7280; display: block; margin-bottom: 4px; }
.stat-value { font-size: 24px; font-weight: 700; color: #111827; }
.stat-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.stat-footer { font-size: 12px; display: flex; align-items: center; gap: 6px; }
.up { color: #10b981; font-weight: 600; }
.down { color: #ef4444; font-weight: 600; }
.footer-desc { color: #9ca3af; }

/* 主区域卡片 */
.main-card, .side-card { height: 450px; border: none; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-size: 15px; font-weight: 600; color: #374151; }

.user-chart-section { padding: 10px 0; }
.user-stats-bar { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin-bottom: 40px; }
.user-stat-item { display: flex; flex-direction: column; gap: 6px; }
.u-label { font-size: 12px; color: #6b7280; }
.u-val { font-size: 18px; font-weight: 700; color: #111827; }

/* 趋势图伪实现 */
.mock-growth-chart {
  height: 220px; position: relative; display: flex;
}
.chart-y-axis {
  width: 40px; display: flex; flex-direction: column; 
  justify-content: space-between; font-size: 11px; color: #9ca3af;
  padding-bottom: 20px;
}
.chart-area {
  flex: 1; border-bottom: 1px solid #e5e7eb; position: relative;
  margin-left: 10px;
}
.chart-line-point {
  position: absolute; bottom: 0; width: 0; overflow: visible;
}
.point-dot {
  width: 6px; height: 6px; background: #409eff; border-radius: 50%;
  position: absolute; top: -3px; left: -3px;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}
.chart-svg-line {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
}

/* 侧边监控栏 */
.monitor-item {
  padding: 18px; border-radius: 12px;
  background: #fffafa; border: 1px solid #fee2e2;
}
.monitor-item.secondary { background: #f0f9ff; border-color: #e0f2fe; }
.monitor-item.warning .m-status { color: #ef4444; }
.m-top { display: flex; justify-content: space-between; margin-bottom: 8px; }
.m-label { font-size: 12px; color: #6b7280; }
.m-status { font-size: 11px; color: #10b981; font-weight: 600; }
.m-val { font-size: 26px; font-weight: 800; color: #111827; margin-bottom: 12px; }
.m-link { font-size: 12px; color: #3b82f6; text-decoration: none; display: flex; align-items: center; gap: 4px; }

.platform-entry { padding-top: 10px; }
.entry-row {
  display: flex; align-items: center; gap: 12px; padding: 16px;
  background: #f9fafb; border-radius: 10px; cursor: pointer;
  transition: all 0.2s; color: #4b5563; font-size: 13.5px;
}
.entry-row:hover { background: #f3f4f6; color: #1e293b; }

.status-pulse { color: #10b981; animation: pulse 2s infinite; }
@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  70% { transform: scale(1); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}

.loading-overlay { padding: 40px; background: #fff; border-radius: 12px; }
</style>
