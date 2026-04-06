<template>
  <div class="admin-logs-refinement">
    <!-- 页头统计 -->
    <el-row :gutter="16" class="mb-20">
      <el-col :span="6" v-for="s in logStats" :key="s.label">
        <el-card shadow="never" class="compact-stat-card">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-value" :style="{ color: s.color }">{{ s.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选面板 -->
    <el-card shadow="never" class="filter-card mb-16">
      <div class="filter-flex">
        <div class="filter-left">
          <el-radio-group v-model="currentStatus" @change="fetchLogs" size="default">
            <el-radio-button label="">全部日志</el-radio-button>
            <el-radio-button label="pending">待修复</el-radio-button>
            <el-radio-button label="fixed">已修复</el-radio-button>
          </el-radio-group>
        </div>
        <div class="filter-right">
          <el-button :icon="Refresh" @click="fetchLogs" :loading="loading">刷新数据</el-button>
        </div>
      </div>
    </el-card>

    <!-- 日志列表 (使用 el-table 增强可读性) -->
    <el-card shadow="never" class="table-card">
      <el-table
        v-loading="loading"
        :data="logs"
        style="width: 100%"
        row-key="id"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
      >
        <!-- 展开行展示堆栈详情 -->
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="log-detail-expand">
              <div class="detail-section">
                <div class="section-title">完整错误堆栈</div>
                <pre class="stack-pre">{{ logDetails[row.id] || row.error_stack }}</pre>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="错误信息" min-width="300">
          <template #default="{ row }">
            <div class="log-info-main">
              <div class="log-url" v-if="row.request_url">
                <el-tag size="small" type="info" class="mr-8">URL</el-tag>
                <code>{{ row.request_url }}</code>
              </div>
              <div class="log-msg-preview">{{ truncateMsg(row.error_stack) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.process_status ? 'success' : 'danger'" effect="plain">
              {{ row.process_status ? '已修复' : '待处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="来源 IP" width="140" />
        <el-table-column prop="create_time" label="触发时间" width="180" sortable />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="!row.process_status"
              type="primary" 
              size="small"
              plain
              @click="markFixed(row)"
              :loading="fixingId === row.id"
            >
              标记已修复
            </el-button>
            <el-button 
              type="info" 
              size="small"
              plain
              @click="toggleExpand(row)"
            >
              详细堆栈
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页占位 (暂用计算分页) -->
      <div class="pagination-footer">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="totalCount"
          :page-size="pageSize"
          v-model:current-page="currentPage"
          @current-change="_loadPage"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

export default {
  name: 'AdminSystemLogs',
  setup() {
    const loading = ref(false)
    const logs = ref([])
    const totalCount = ref(0)
    const pendingCount = ref(0)
    const currentPage = ref(1)
    const pageSize = 15
    const currentStatus = ref('')
    const fixingId = ref(null)
    const logDetails = ref({})

    const logStats = computed(() => [
      { label: '待修复异常', value: pendingCount.value, color: '#F56C6C' },
      { label: '累计已修复', value: totalCount.value - pendingCount.value, color: '#67C23A' },
      { label: '系统日志总计', value: totalCount.value, color: '#909399' },
      { label: '活跃运行', value: 'Normal', color: '#409EFF' }
    ])

    const fetchPendingCount = async () => {
      try {
        const res = await axios.get('/api/accounts/admin/stats/')
        pendingCount.value = res.data.system_logs?.pending || 0
      } catch (e) { /* 静默 */ }
    }

    const _loadPage = async (page) => {
      loading.value = true
      try {
        const res = await axios.get('/api/accounts/admin/error-logs/', {
          params: { page, page_size: pageSize, status: currentStatus.value },
        })
        logs.value = res.data.results
        totalCount.value = res.data.count
        currentPage.value = page
      } catch (e) {
        ElMessage.error('加载日志失败')
      } finally {
        loading.value = false
      }
    }

    const fetchLogs = () => {
      currentPage.value = 1
      _loadPage(1)
      fetchPendingCount()
    }

    const markFixed = async (log) => {
      fixingId.value = log.id
      try {
        const res = await axios.post(`/api/accounts/admin/error-logs/${log.id}/mark-fixed/`)
        log.process_status = true
        pendingCount.value = Math.max(0, pendingCount.value - 1)
        ElMessage.success(res.data.detail)
      } catch (e) {
        ElMessage.error('操作失败')
      } finally {
        fixingId.value = null
      }
    }

    const truncateMsg = (str) => {
      if (!str) return '无详情'
      return str.split('\n')[0].substring(0, 100)
    }

    const toggleExpand = () => {
      // 预留展开详情逻辑 (table自带expand)
    }

    onMounted(fetchLogs)

    return {
      loading, logs, totalCount, pendingCount, currentPage, pageSize,
      currentStatus, fixingId, logDetails, logStats,
      fetchLogs, _loadPage, markFixed, truncateMsg, toggleExpand,
      Refresh
    }
  }
}
</script>

<style scoped>
.admin-logs-refinement {
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.mb-20 { margin-bottom: 20px; }
.mb-16 { margin-bottom: 16px; }
.mr-8 { margin-right: 8px; }

.compact-stat-card { border: 1px solid #ebeef5; }
.stat-label { font-size: 12px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 20px; font-weight: bold; }

.filter-flex { display: flex; justify-content: space-between; align-items: center; }

.log-info-main { display: flex; flex-direction: column; gap: 4px; }
.log-url { font-family: 'Courier New', monospace; font-size: 12px; color: #409eff; }
.log-msg-preview { font-size: 12px; color: #606266; }

.log-detail-expand { padding: 20px; background: #f8fafc; border-radius: 4px; }
.section-title { font-size: 13px; font-weight: bold; margin-bottom: 12px; color: #1e293b; }
.stack-pre {
  background: #1a1a2e;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
}

.pagination-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-card__body) { padding: 16px; }
</style>
