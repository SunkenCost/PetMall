<template>
  <div class="admin-products">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索商品名称..."
          clearable
          style="width: 220px"
          @input="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterCategory" placeholder="全部分类" clearable style="width: 140px" @change="loadProducts">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="全部状态" clearable style="width: 120px" @change="loadProducts">
          <el-option label="已上架" value="on" />
          <el-option label="已下架" value="off" />
        </el-select>
      </div>
      <el-button type="primary" @click="openCreateDialog" :icon="Plus">新增商品</el-button>
    </div>

    <!-- 商品表格 -->
    <div class="table-card">
      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column label="图片" width="80">
          <template #default="{ row }">
            <img
              v-if="row.main_image_url"
              :src="row.main_image_url"
              class="product-thumb"
              @error="handleImgError"
            />
            <div v-else class="no-img">暂无</div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="price" label="售价" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="old_price" label="原价" width="100">
          <template #default="{ row }">
            <span v-if="row.old_price" style="color:#999;text-decoration:line-through">¥{{ row.old_price }}</span>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="inventory_qty" label="库存" width="80">
          <template #default="{ row }">
            <el-tag :type="row.inventory_qty <= 10 ? 'danger' : 'success'" size="small">
              {{ row.inventory_qty }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sales" label="销量" width="80" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'info'" size="small">
              {{ row.status ? '已上架' : '已下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              size="small"
              :type="row.status ? 'warning' : 'success'"
              @click="toggleStatus(row)"
            >
              {{ row.status ? '下架' : '上架' }}
            </el-button>
            <el-popconfirm
              title="确认删除该商品？此操作不可逆"
              @confirm="deleteProduct(row)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadProducts"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingProduct ? '编辑商品' : '新增商品'"
      width="600px"
      destroy-on-close
    >
      <el-form :model="form" label-width="90px" :rules="rules" ref="formRef">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="所属分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="售卖价格" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" :step="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="原价">
          <el-input-number v-model="form.old_price" :min="0" :precision="2" :step="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="初始库存" v-if="!editingProduct">
          <el-input-number v-model="form.initial_qty" :min="0" :step="10" style="width:100%" />
        </el-form-item>
        <el-form-item label="上架状态">
          <el-switch v-model="form.status" active-text="上架" inactive-text="下架" />
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入商品详情描述..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ editingProduct ? '保存修改' : '创建商品' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import axios from '@/axios'

export default {
  name: 'AdminProducts',
  components: { Search },
  setup() {
    const products = ref([])
    const categories = ref([])
    const loading = ref(false)
    const submitting = ref(false)
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const searchKeyword = ref('')
    const filterCategory = ref(null)
    const filterStatus = ref(null)

    const dialogVisible = ref(false)
    const editingProduct = ref(null)
    const formRef = ref(null)
    const form = ref({
      name: '', category: null, price: 0, old_price: null,
      status: true, description: '', initial_qty: 0
    })
    const rules = {
      name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
      category: [{ required: true, message: '请选择分类', trigger: 'change' }],
      price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
    }

    const getAdminHeaders = () => {
      const u = JSON.parse(localStorage.getItem('pet_user') || '{}')
      return { 'X-Admin-Username': u.username || '' }
    }

    const loadCategories = async () => {
      try {
        const res = await axios.get('/api/merchant/categories/', { headers: getAdminHeaders() })
        categories.value = res.data
      } catch (e) {
        // 分类加载失败时静默处理，不影响主功能
        console.warn('分类加载失败', e)
      }
    }

    const loadProducts = async () => {
      loading.value = true
      try {
        const params = { page: currentPage.value }
        if (searchKeyword.value) params.search = searchKeyword.value
        if (filterCategory.value) params.category = filterCategory.value
        if (filterStatus.value) params.status = filterStatus.value
        const res = await axios.get('/api/merchant/products/', { params, headers: getAdminHeaders() })
        products.value = res.data.results || res.data
        total.value = res.data.count || (res.data.results?.length || 0)
      } catch (e) {
        ElMessage.error('加载商品列表失败')
      } finally {
        loading.value = false
      }
    }

    let searchTimer = null
    const handleSearch = () => {
      clearTimeout(searchTimer)
      searchTimer = setTimeout(() => {
        currentPage.value = 1
        loadProducts()
      }, 400)
    }

    const openCreateDialog = () => {
      editingProduct.value = null
      form.value = { name: '', category: null, price: 0, old_price: null, status: true, description: '', initial_qty: 0 }
      dialogVisible.value = true
    }

    const openEditDialog = (row) => {
      editingProduct.value = row
      form.value = {
        name: row.name,
        category: row.category,
        price: Number(row.price),
        old_price: row.old_price ? Number(row.old_price) : null,
        status: row.status,
        description: row.description || '',
      }
      dialogVisible.value = true
    }

    const submitForm = async () => {
      await formRef.value.validate()
      submitting.value = true
      try {
        const payload = { ...form.value }
        if (editingProduct.value) {
          await axios.patch(`/api/merchant/products/${editingProduct.value.id}/`, payload, { headers: getAdminHeaders() })
          ElMessage.success('商品信息已更新')
        } else {
          await axios.post('/api/merchant/products/', payload, { headers: getAdminHeaders() })
          ElMessage.success('商品创建成功')
        }
        dialogVisible.value = false
        loadProducts()
      } catch (e) {
        ElMessage.error('操作失败，请重试')
      } finally {
        submitting.value = false
      }
    }

    const toggleStatus = async (row) => {
      try {
        await axios.post(`/api/merchant/products/${row.id}/toggle_status/`, {}, { headers: getAdminHeaders() })
        row.status = !row.status
        ElMessage.success(row.status ? '商品已上架' : '商品已下架')
      } catch (e) {
        ElMessage.error('操作失败')
      }
    }

    const deleteProduct = async (row) => {
      try {
        await axios.delete(`/api/merchant/products/${row.id}/`, { headers: getAdminHeaders() })
        ElMessage.success('商品已删除')
        loadProducts()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    }

    const handleImgError = (e) => { e.target.style.display = 'none' }

    onMounted(() => {
      loadCategories()
      loadProducts()
    })

    return {
      products, categories, loading, submitting, total, currentPage, pageSize,
      searchKeyword, filterCategory, filterStatus,
      dialogVisible, editingProduct, formRef, form, rules,
      Plus,
      loadProducts, handleSearch, openCreateDialog, openEditDialog,
      submitForm, toggleStatus, deleteProduct, handleImgError,
    }
  }
}
</script>

<style scoped>
.admin-products { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
}
.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.table-card {
  background: #fff;
  border-radius: 6px;
  padding: 20px;
  border: 1px solid #e8e8e8;
}
.product-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 8px;
}
.no-img {
  width: 48px;
  height: 48px;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #ccc;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
