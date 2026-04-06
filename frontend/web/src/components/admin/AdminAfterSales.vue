<template>
  <div class="admin-aftersales">
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
      </button>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <el-table :data="aftersales" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="order_no" label="关联订单号" min-width="180" show-overflow-tooltip />
        <el-table-column prop="username" label="申请用户" width="120" />
        <el-table-column prop="sales_type_display" label="类型" width="90">
          <template #default="{ row }">
            <el-tag :type="row.sales_type === 'REFUND' ? 'danger' : 'warning'" size="small">
              {{ row.sales_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="申请原因" min-width="180" show-overflow-tooltip />
        <el-table-column prop="refund_amount" label="退款金额" width="100">
          <template #default="{ row }">
            <span v-if="Number(row.refund_amount) > 0">¥{{ row.refund_amount }}</span>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="asStatusStyle[row.status]" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handle_result" label="处理结果" min-width="140" show-overflow-tooltip />
        <el-table-column prop="handler_name" label="处理人" width="100">
          <template #default="{ row }">{{ row.handler_name || '—' }}</template>
        </el-table-column>
        <el-table-column prop="create_time" label="申请时间" width="160">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'APPLYING' || row.status === 'PROCESSING'">
              <el-button type="success" size="small" @click="openHandleDialog(row, 'approve')">通过</el-button>
              <el-button type="danger" size="small" @click="openHandleDialog(row, 'reject')">拒绝</el-button>
            </template>
            <span v-else class="handled-text">已处理</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadAfterSales"
        />
      </div>
    </div>

    <!-- 处理对话框 -->
    <el-dialog
      v-model="handleVisible"
      :title="handleAction === 'approve' ? '✅ 通过售后申请' : '❌ 拒绝售后申请'"
      width="480px"
    >
      <div class="dialog-info" v-if="handlingItem">
        <p>订单号：<strong>{{ handlingItem.order_no }}</strong></p>
        <p>申请用户：<strong>{{ handlingItem.username }}</strong></p>
        <p>类型：<strong>{{ handlingItem.sales_type_display }}</strong></p>
        <p>原因：{{ handlingItem.reason || '—' }}</p>
      </div>
      <el-form style="margin-top: 16px">
        <el-form-item label="处理说明" label-width="80px">
          <el-input
            v-model="handleResult"
            type="textarea"
            :rows="3"
            :placeholder="handleAction === 'approve' ? '填写通过说明（可选）' : '请填写拒绝原因'"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleVisible = false">取消</el-button>
        <el-button
          :type="handleAction === 'approve' ? 'success' : 'danger'"
          @click="confirmHandle"
          :loading="submitting"
        >
          {{ handleAction === 'approve' ? '确认通过' : '确认拒绝' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '@/axios'

export default {
  name: 'AdminAfterSales',
  setup() {
    const aftersales = ref([])
    const loading = ref(false)
    const submitting = ref(false)
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const filterStatus = ref('')

    const handleVisible = ref(false)
    const handlingItem = ref(null)
    const handleAction = ref('approve')
    const handleResult = ref('')

    const statusTabs = [
      { label: '全部', value: '' },
      { label: '申请中', value: 'APPLYING' },
      { label: '处理中', value: 'PROCESSING' },
      { label: '已完成', value: 'COMPLETED' },
      { label: '已拒绝', value: 'REJECTED' },
    ]

    const asStatusStyle = {
      APPLYING: 'warning',
      PROCESSING: 'primary',
      COMPLETED: 'success',
      REJECTED: 'danger',
    }

    const getAdminHeaders = () => {
      const u = JSON.parse(localStorage.getItem('pet_user') || '{}')
      return { 'X-Admin-Username': u.username || '' }
    }

    const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : '—'

    const loadAfterSales = async () => {
      loading.value = true
      try {
        const params = { page: currentPage.value }
        if (filterStatus.value) params.status = filterStatus.value
        const res = await axios.get('/api/merchant/aftersales/', { params, headers: getAdminHeaders() })
        aftersales.value = res.data.results || res.data
        total.value = res.data.count || 0
      } catch (e) {
        ElMessage.error('加载售后列表失败')
      } finally {
        loading.value = false
      }
    }

    const switchStatus = (val) => {
      filterStatus.value = val
      currentPage.value = 1
      loadAfterSales()
    }

    const openHandleDialog = (item, action) => {
      handlingItem.value = item
      handleAction.value = action
      handleResult.value = ''
      handleVisible.value = true
    }

    const confirmHandle = async () => {
      if (handleAction.value === 'reject' && !handleResult.value.trim()) {
        ElMessage.warning('拒绝时请填写拒绝原因')
        return
      }
      submitting.value = true
      try {
        await axios.post(
          `/api/merchant/aftersales/${handlingItem.value.id}/handle/`,
          { action: handleAction.value, handle_result: handleResult.value },
          { headers: getAdminHeaders() }
        )
        ElMessage.success(handleAction.value === 'approve' ? '售后申请已通过' : '售后申请已拒绝')
        handleVisible.value = false
        loadAfterSales()
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || '处理失败')
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadAfterSales)

    return {
      aftersales, loading, submitting, total, currentPage, pageSize, filterStatus,
      statusTabs, asStatusStyle,
      handleVisible, handlingItem, handleAction, handleResult,
      loadAfterSales, switchStatus, openHandleDialog, confirmHandle, formatTime,
    }
  }
}
</script>

<style scoped>
.admin-aftersales { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }

.status-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.status-tab {
  padding: 8px 18px;
  border-radius: 20px;
  border: 1.5px solid #e4e7ed;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  transition: all 0.2s;
}
.status-tab:hover { border-color: #6366f1; color: #6366f1; }
.status-tab.active { background: #6366f1; border-color: #6366f1; color: #fff; }

.table-card {
  background: #fff;
  border-radius: 6px;
  padding: 20px;
  border: 1px solid #e8e8e8;
}
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
.handled-text { color: #c0c4cc; font-size: 13px; }
.dialog-info { background: #f8f9fa; border-radius: 8px; padding: 12px 16px; }
.dialog-info p { margin: 6px 0; color: #606266; font-size: 14px; }
</style>
