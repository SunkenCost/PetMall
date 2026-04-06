<template>
  <base-page>
    <div class="user-center">
      <h2>🐾 我的收货地址档</h2>
      
      <el-button type="primary" :icon="Plus" @click="dialogVisible = true" style="margin-bottom: 20px;">
        新增收货地址
      </el-button>

      <el-table :data="addresses" style="width: 100%" border v-loading="loading">
        <el-table-column prop="receiver_name" label="收件人" width="120" />
        <el-table-column prop="receiver_phone" label="联系电话" width="150" />
        <el-table-column label="地址详情">
          <template #default="scope">
            {{ scope.row.province }} {{ scope.row.city }} {{ scope.row.district }} {{ scope.row.detail_address }}
          </template>
        </el-table-column>
        <el-table-column label="默认" width="80" align="center">
          <template #default="scope">
            <div class="default-toggle" @click="toggleDefault(scope.row)">
              <el-icon v-if="scope.row.is_default" class="icon-active"><CircleCheckFilled /></el-icon>
              <el-icon v-else class="icon-inactive"><CircleCheck /></el-icon>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 新增地址弹窗 -->
      <el-dialog v-model="dialogVisible" title="🌟 登记新地址" width="500px">
        <el-form :model="form" label-width="100px">
          <el-form-item label="收件人姓名">
            <el-input v-model="form.receiver_name" />
          </el-form-item>
          <el-form-item label="联系电话">
            <el-input v-model="form.receiver_phone" placeholder="请输入11位手机号" />
          </el-form-item>
          <el-form-item label="省市区">
            <el-cascader
              size="large"
              :options="regionData"
              v-model="selectedRegion"
              placeholder="请选择省/市/区"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="详细街道">
            <el-input v-model="form.detail_address" type="textarea" />
          </el-form-item>
          <el-form-item label="设为默认">
            <el-checkbox v-model="form.is_default">设置为默认收货地址</el-checkbox>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitAddress">保存档位</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </base-page>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Plus, CircleCheck, CircleCheckFilled } from '@element-plus/icons-vue'
import axios from '@/axios'
import { ElMessage } from 'element-plus'
import { regionData, codeToText } from 'element-china-area-data'

export default {
  name: 'ShopperPage',
  setup() {
    const addresses = ref([])
    const loading = ref(false)
    const dialogVisible = ref(false)
    const selectedRegion = ref([])
    const form = ref({
      receiver_name: '', receiver_phone: '', province: '', city: '', district: '', detail_address: '', is_default: false
    })

    const fetchAddresses = async () => {
      loading.value = true
      try {
        const res = await axios.get('/api/shopper/addresses/')
        // DRF 可能会包裹在 results 里
        addresses.value = res.data.results || res.data
      } finally {
        loading.value = false
      }
    }

    const toggleDefault = async (row) => {
      if (row.is_default) return // 已经是默认，无需重复操作
      
      loading.value = true
      try {
        await axios.post(`/api/shopper/addresses/${row.id}/set_default/`)
        ElMessage.success(`已设置 ${row.receiver_name} 为默认地址`)
        await fetchAddresses() 
      } catch (err) {
        console.error('设置默认地址失败:', err)
        ElMessage.error('设置默认地址失败，请刷新重试')
      } finally {
        loading.value = false
      }
    }

    const submitAddress = async () => {
      try {
        if (!form.value.receiver_name || !form.value.receiver_phone || selectedRegion.value.length !== 3) {
           return ElMessage.warning('请将收件人、联系电话及省市区信息填写完整');
        }
        
        // 将地区编码转换为中文省市区 (v6+ 统一使用小写 codeToText)
        form.value.province = codeToText[selectedRegion.value[0]]
        form.value.city = codeToText[selectedRegion.value[1]]
        form.value.district = codeToText[selectedRegion.value[2]]

        await axios.post('/api/shopper/addresses/', form.value)
        ElMessage.success('收货地址添加成功！')
        dialogVisible.value = false
        // 重置表单
        form.value = {
          receiver_name: '', 
          receiver_phone: '', 
          province: '', 
          city: '', 
          district: '', 
          detail_address: '',
          is_default: false
        }
        selectedRegion.value = []
        fetchAddresses()
      } catch(err) {
        console.error('地址添加失败:', err)
        const msg = err.response?.data?.detail || '添加失败，请检查填写内容'
        ElMessage.error(msg)
      }
    }

    onMounted(() => {
      fetchAddresses()
    })

    return { 
      addresses, loading, dialogVisible, form, 
      selectedRegion, regionData, Plus, 
      submitAddress, toggleDefault,
      CircleCheck, CircleCheckFilled 
    }
  }
}
</script>

<style scoped>
.user-center {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(255, 168, 186, 0.1);
  min-height: 600px;
}
h2 {
  color: var(--text-main);
  margin-bottom: 30px;
}
.default-toggle {
  cursor: pointer;
  font-size: 22px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 0.2s;
}
.default-toggle:hover {
  transform: scale(1.1);
}
.icon-active {
  color: #67c23a;
}
.icon-inactive {
  color: #dcdfe6;
}
.icon-inactive:hover {
  color: #c0c4cc;
}
</style>
