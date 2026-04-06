<template>
  <div class="admin-users-refinement">
    <!-- 页头统计 -->
    <el-row :gutter="16" class="mb-20">
      <el-col :span="4" v-for="s in userStats" :key="s.label">
        <el-card shadow="never" class="compact-stat-card">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-value" :style="{ color: s.color }">{{ s.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索与操作栏 -->
    <el-card shadow="never" class="filter-card mb-16">
      <div class="filter-flex">
        <div class="filter-left">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索用户名/姓名/邮箱/手机号"
            class="search-input"
            clearable
            @keyup.enter="fetchUsers"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          
          <el-select v-model="filters.status" placeholder="账户状态" clearable @change="fetchUsers" style="width: 140px">
            <el-option label="正常" value="active" />
            <el-option label="已冻结" value="frozen" />
          </el-select>

          <el-select v-model="filters.role" placeholder="用户角色" clearable @change="fetchUsers" style="width: 140px">
            <el-option label="超级管理员" value="superuser" />
            <el-option label="商家运营" value="staff" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </div>
        <div class="filter-right">
          <el-button type="primary" :icon="Search" @click="fetchUsers">查询</el-button>
          <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never" class="table-card">
      <el-table
        v-loading="loading"
        :data="users"
        style="width: 100%"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="用户信息" min-width="200">
          <template #default="{ row }">
            <div class="user-info-cell">
              <el-avatar :size="32" :src="row.avatar || ''">{{ row.username[0].toUpperCase() }}</el-avatar>
              <div class="ml-10">
                <div class="username-text">{{ row.username }}</div>
                <div class="realname-text">{{ row.real_name || '未实名' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="联系方式" min-width="180">
          <template #default="{ row }">
            <div class="contact-cell">
              <div v-if="row.email"><el-icon><Message /></el-icon> {{ row.email }}</div>
              <div v-if="row.phone"><el-icon><Iphone /></el-icon> {{ row.phone }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="140">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row)" size="small" effect="plain">
              {{ getRoleLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常' : '已冻结' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="180" sortable />
        <el-table-column label="操作" min-width="260" fixed="right">
          <template #default="{ row }">
            <template v-if="!row.is_superuser">
              <el-button 
                size="small"
                :type="row.is_active ? 'danger' : 'success'" 
                @click="toggleStatus(row)"
              >
                {{ row.is_active ? '冻结' : '解封' }}
              </el-button>
              <el-button 
                size="small"
                :type="row.is_staff ? 'warning' : 'primary'" 
                @click="grantStaff(row)"
              >
                {{ row.is_staff ? '移除商家权限' : '设为商家' }}
              </el-button>
            </template>
            <span v-else class="text-secondary">系统管理员</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页栏 -->
      <div class="pagination-footer">
        <el-pagination
          background
          layout="total, prev, pager, next, jumper"
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Message, Iphone } from '@element-plus/icons-vue'

export default {
  name: 'AdminUsers',
  setup() {
    const loading = ref(false)
    const users = ref([])
    const totalCount = ref(0)
    const currentPage = ref(1)
    const pageSize = 15
    const stats = ref({ total: 0, active: 0, frozen: 0, staff: 0, superuser: 0 })
    const filters = ref({ keyword: '', status: '', role: '' })

    const userStats = computed(() => [
      { label: '总用户数', value: stats.value.total, color: '#303133' },
      { label: '正常', value: stats.value.active, color: '#67C23A' },
      { label: '已冻结', value: stats.value.frozen, color: '#F56C6C' },
      { label: '商家总额', value: stats.value.staff, color: '#409EFF' },
      { label: '管理层', value: stats.value.superuser, color: '#E6A23C' }
    ])

    const fetchStats = async () => {
      try {
        const res = await axios.get('/api/accounts/admin/stats/')
        stats.value = res.data.users
      } catch (e) { console.error(e) }
    }

    const _loadPage = async (page) => {
      loading.value = true
      try {
        const res = await axios.get('/api/accounts/admin/users/', {
          params: { page, page_size: pageSize, ...filters.value }
        })
        users.value = res.data.results
        totalCount.value = res.data.count
      } catch (e) {
        ElMessage.error('加载列表失败')
      } finally {
        loading.value = false
      }
    }

    const fetchUsers = () => {
      currentPage.value = 1
      _loadPage(1)
    }

    const resetFilters = () => {
      filters.value = { keyword: '', status: '', role: '' }
      fetchUsers()
    }

    const toggleStatus = async (user) => {
      const action = user.is_active ? '冻结' : '解封'
      try {
        await ElMessageBox.confirm(`确定要${action}用户「${user.username}」吗？`, '安全警告', { type: 'warning' })
        const res = await axios.post(`/api/accounts/admin/users/${user.id}/toggle-status/`)
        ElMessage.success(res.data.detail)
        _loadPage(currentPage.value)
        fetchStats()
      } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
    }

    const grantStaff = async (user) => {
      const action = user.is_staff ? '撤销商家权限' : '设为商家管理员'
      try {
        await ElMessageBox.confirm(`确定要将「${user.username}」${action}吗？`, '权限变更', { type: 'info' })
        const res = await axios.post(`/api/accounts/admin/users/${user.id}/grant-staff/`)
        ElMessage.success(res.data.detail)
        _loadPage(currentPage.value)
        fetchStats()
      } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
    }

    const getRoleLabel = (user) => {
      if (user.is_superuser) return '超级管理员'
      if (user.is_staff) return '商家运营'
      return '普通用户'
    }

    const getRoleTagType = (user) => {
      if (user.is_superuser) return 'warning'
      if (user.is_staff) return 'primary'
      return 'info'
    }

    onMounted(() => {
      fetchStats()
      fetchUsers()
    })

    return {
      loading, users, totalCount, currentPage, pageSize,
      userStats, filters, fetchUsers, resetFilters, _loadPage,
      getRoleLabel, getRoleTagType, toggleStatus, grantStaff,
      Search, Refresh, Message, Iphone
    }
  }
}
</script>

<style scoped>
.admin-users-refinement {
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.mb-20 { margin-bottom: 20px; }
.mb-16 { margin-bottom: 16px; }
.ml-10 { margin-left: 10px; }

.compact-stat-card {
  border: 1px solid #ebeef5;
}
.stat-label { font-size: 12px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 20px; font-weight: bold; }

.filter-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.filter-left { display: flex; gap: 12px; }
.search-input { width: 280px; }

.user-info-cell { display: flex; align-items: center; }
.username-text { font-size: 14px; font-weight: 600; color: #303133; }
.realname-text { font-size: 12px; color: #909399; margin-top: 2px; }

.contact-cell { font-size: 12px; color: #606266; line-height: 1.6; }
.contact-cell .el-icon { font-size: 13px; vertical-align: -2px; margin-right: 4px; }

.text-secondary { color: #c0c4cc; font-size: 13px; }

.pagination-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-card__body) { padding: 16px; }
</style>
