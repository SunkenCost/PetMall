<template>
  <div class="admin-inventory">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-switch
          v-model="showLowOnly"
          active-text="仅显示库存预警"
          inactive-text="全部库存"
          @change="loadInventory"
        />
      </div>
    </div>

    <!-- 预警提示 -->
    <el-alert
      v-if="lowStockCount > 0"
      :title="`共有 ${lowStockCount} 件商品库存不足（≤10件），请及时补货！`"
      type="warning"
      show-icon
      :closable="false"
      style="margin-bottom: 20px; border-radius: 12px"
    />

    <!-- 库存表格 -->
    <div class="table-card">
      <el-table :data="inventory" v-loading="loading" stripe>
        <el-table-column prop="product_name" label="商品名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="product_price" label="售价" width="100">
          <template #default="{ row }">¥{{ row.product_price }}</template>
        </el-table-column>
        <el-table-column prop="product_status" label="上架状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.product_status ? 'success' : 'info'" size="small">
              {{ row.product_status ? '已上架' : '已下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_quantity" label="当前库存" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.current_quantity <= row.warning_threshold }">
              <el-tag :type="row.current_quantity <= row.warning_threshold ? 'danger' : 'success'" size="small">
                {{ row.current_quantity }}
              </el-tag>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="warning_threshold" label="预警阈值" width="100">
          <template #default="{ row }">{{ row.warning_threshold }} 件</template>
        </el-table-column>
        <el-table-column prop="update_time" label="最后更新" width="160">
          <template #default="{ row }">{{ formatTime(row.update_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="openRestockDialog(row)">补货</el-button>
            <el-button size="small" type="primary" @click="openAdjustDialog(row)">直接调整</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadInventory"
        />
      </div>
    </div>

    <!-- 补货对话框 -->
    <el-dialog v-model="restockVisible" title="补货操作" width="400px">
      <div class="dialog-info">
        <p>商品：<strong>{{ currentItem?.product_name }}</strong></p>
        <p>当前库存：<strong>{{ currentItem?.current_quantity }}</strong> 件</p>
      </div>
      <el-form label-width="80px" style="margin-top: 20px">
        <el-form-item label="补货数量">
          <el-input-number v-model="restockQty" :min="1" :step="10" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="restockVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRestock" :loading="submitting">确认补货</el-button>
      </template>
    </el-dialog>

    <!-- 直接调整对话框 -->
    <el-dialog v-model="adjustVisible" title="直接调整库存" width="400px">
      <div class="dialog-info">
        <p>商品：<strong>{{ currentItem?.product_name }}</strong></p>
        <p>当前库存：<strong>{{ currentItem?.current_quantity }}</strong> 件</p>
      </div>
      <el-form label-width="80px" style="margin-top: 20px">
        <el-form-item label="目标库存">
          <el-input-number v-model="adjustQty" :min="0" :step="10" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustVisible = false">取消</el-button>
        <el-button type="warning" @click="confirmAdjust" :loading="submitting">确认调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '@/axios'

export default {
  name: 'AdminInventory',
  setup() {
    const inventory = ref([])
    const loading = ref(false)
    const submitting = ref(false)
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const showLowOnly = ref(false)

    const restockVisible = ref(false)
    const adjustVisible = ref(false)
    const currentItem = ref(null)
    const restockQty = ref(10)
    const adjustQty = ref(0)

    const lowStockCount = computed(() => inventory.value.filter(i => i.current_quantity <= i.warning_threshold).length)

    const getAdminHeaders = () => {
      const u = JSON.parse(localStorage.getItem('pet_user') || '{}')
      return { 'X-Admin-Username': u.username || '' }
    }

    const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : '—'

    const loadInventory = async () => {
      loading.value = true
      try {
        const params = { page: currentPage.value }
        if (showLowOnly.value) params.low = '1'
        const res = await axios.get('/api/merchant/inventory/', { params, headers: getAdminHeaders() })
        inventory.value = res.data.results || res.data
        total.value = res.data.count || 0
      } catch (e) {
        ElMessage.error('加载库存失败')
      } finally {
        loading.value = false
      }
    }

    const openRestockDialog = (row) => {
      currentItem.value = row
      restockQty.value = 10
      restockVisible.value = true
    }

    const openAdjustDialog = (row) => {
      currentItem.value = row
      adjustQty.value = row.current_quantity
      adjustVisible.value = true
    }

    const confirmRestock = async () => {
      submitting.value = true
      try {
        const res = await axios.post(
          `/api/merchant/inventory/${currentItem.value.id}/restock/`,
          { quantity: restockQty.value },
          { headers: getAdminHeaders() }
        )
        ElMessage.success(res.data.detail)
        restockVisible.value = false
        loadInventory()
      } catch (e) {
        ElMessage.error('补货失败')
      } finally {
        submitting.value = false
      }
    }

    const confirmAdjust = async () => {
      submitting.value = true
      try {
        const res = await axios.post(
          `/api/merchant/inventory/${currentItem.value.id}/adjust/`,
          { quantity: adjustQty.value },
          { headers: getAdminHeaders() }
        )
        ElMessage.success(res.data.detail)
        adjustVisible.value = false
        loadInventory()
      } catch (e) {
        ElMessage.error('调整失败')
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadInventory)

    return {
      inventory, loading, submitting, total, currentPage, pageSize, showLowOnly, lowStockCount,
      restockVisible, adjustVisible, currentItem, restockQty, adjustQty,
      loadInventory, formatTime,
      openRestockDialog, openAdjustDialog, confirmRestock, confirmAdjust,
    }
  }
}
</script>

<style scoped>
.admin-inventory { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.toolbar-left { display: flex; gap: 12px; align-items: center; }
.table-card {
  background: #fff;
  border-radius: 6px;
  padding: 20px;
  border: 1px solid #e8e8e8;
}
.text-danger { color: #ef4444; font-weight: 600; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 20px; }
.dialog-info { background: #f8f9fa; border-radius: 8px; padding: 12px 16px; }
.dialog-info p { margin: 4px 0; color: #606266; font-size: 14px; }
</style>
