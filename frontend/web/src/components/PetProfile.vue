<template>
  <base-page>
    <div class="pet-center">
      <div class="page-header">
        <div class="header-left">
          <h2>🐾 我的宠物档案</h2>
          <p class="sub-text">记录您毛茸茸伙伴的专属信息</p>
        </div>
        <el-button type="primary" :icon="Plus" @click="openDialog()" round>
          添加新宠物
        </el-button>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="!loading && pets.length === 0" description="还没有添加宠物哦，快来建档吧~" :image-size="160">
        <el-button type="primary" @click="openDialog()">立即添加</el-button>
      </el-empty>

      <!-- 宠物卡片列表 -->
      <el-row :gutter="24" v-loading="loading">
        <el-col :xs="24" :sm="12" :md="8" v-for="pet in pets" :key="pet.id" style="margin-bottom: 24px;">
          <div class="pet-card" :class="petTypeClass(pet.pet_type)">
            <div class="card-header">
              <span class="pet-avatar">{{ petEmoji(pet.pet_type) }}</span>
              <div class="card-actions">
                <el-button :icon="Edit" circle size="small" @click="openDialog(pet)" />
                <el-button :icon="Delete" circle size="small" type="danger" @click="handleDelete(pet)" />
              </div>
            </div>
            <div class="card-body">
              <h3 class="pet-name">{{ pet.pet_name }}</h3>
              <el-tag size="small" :type="genderTagType(pet.gender)" effect="light" round class="gender-tag">
                {{ genderLabel(pet.gender) }}
              </el-tag>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">物种</span>
                  <span class="info-value">{{ pet.pet_type }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">品种</span>
                  <span class="info-value">{{ pet.breed || '未登记' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">生日</span>
                  <span class="info-value">{{ pet.birthday || '未登记' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">建档日</span>
                  <span class="info-value">{{ formatDate(pet.create_time) }}</span>
                </div>
              </div>
            </div>
            <div class="card-footer">
              <span class="age-text" v-if="pet.birthday">🎂 {{ calcAge(pet.birthday) }}</span>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 新增/编辑弹窗 -->
      <el-dialog v-model="dialogVisible" :title="isEdit ? '✏️ 编辑宠物档案' : '🌟 添加新宠物'" width="520px" destroy-on-close>
        <el-form :model="form" label-width="90px" :rules="rules" ref="formRef">
          <el-form-item label="宠物昵称" prop="pet_name">
            <el-input v-model="form.pet_name" placeholder="给你的毛孩子起个名字" maxlength="50" show-word-limit />
          </el-form-item>
          <el-form-item label="物种类别" prop="pet_type">
            <el-select v-model="form.pet_type" placeholder="请选择物种" style="width: 100%" allow-create filterable>
              <el-option label="🐶 狗狗" value="狗狗" />
              <el-option label="🐱 猫咪" value="猫咪" />
              <el-option label="🐹 仓鼠" value="仓鼠" />
              <el-option label="🐰 兔子" value="兔子" />
              <el-option label="🐦 鸟类" value="鸟类" />
              <el-option label="🐟 鱼类" value="鱼类" />
              <el-option label="🐢 龟类" value="龟类" />
              <el-option label="🦎 爬行类" value="爬行类" />
            </el-select>
          </el-form-item>
          <el-form-item label="细分品种">
            <el-input v-model="form.breed" placeholder="如：金毛、布偶、英短蓝猫…" />
          </el-form-item>
          <el-form-item label="性别">
            <el-radio-group v-model="form.gender">
              <el-radio-button :label="1">♂ 公</el-radio-button>
              <el-radio-button :label="2">♀ 母</el-radio-button>
              <el-radio-button :label="0">未知</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="出生日期">
            <el-date-picker
              v-model="form.birthday"
              type="date"
              placeholder="选择宠物的破壳日"
              value-format="YYYY-MM-DD"
              :disabled-date="(d) => d > new Date()"
              style="width: 100%"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitForm" :loading="submitting">
              {{ isEdit ? '保存修改' : '确认添加' }}
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </base-page>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import axios from '@/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'PetProfilePage',
  setup() {
    const pets = ref([])
    const loading = ref(false)
    const dialogVisible = ref(false)
    const isEdit = ref(false)
    const editId = ref(null)
    const submitting = ref(false)
    const formRef = ref(null)

    const defaultForm = { pet_name: '', pet_type: '', breed: '', gender: 0, birthday: '' }
    const form = ref({ ...defaultForm })

    const rules = {
      pet_name: [{ required: true, message: '请输入宠物昵称', trigger: 'blur' }],
      pet_type: [{ required: true, message: '请选择物种类别', trigger: 'change' }],
    }

    // ---- 数据读取 ----
    const fetchPets = async () => {
      loading.value = true
      try {
        const res = await axios.get('/api/shopper/pets/')
        pets.value = res.data.results || res.data
      } catch {
        ElMessage.error('加载宠物档案失败')
      } finally {
        loading.value = false
      }
    }

    // ---- 打开弹窗 ----
    const openDialog = (pet) => {
      if (pet) {
        isEdit.value = true
        editId.value = pet.id
        form.value = {
          pet_name: pet.pet_name,
          pet_type: pet.pet_type,
          breed: pet.breed || '',
          gender: pet.gender,
          birthday: pet.birthday || '',
        }
      } else {
        isEdit.value = false
        editId.value = null
        form.value = { ...defaultForm }
      }
      dialogVisible.value = true
    }

    // ---- 提交表单 ----
    const submitForm = async () => {
      if (formRef.value) {
        try {
          await formRef.value.validate()
        } catch {
          return
        }
      }
      submitting.value = true
      try {
        const data = { ...form.value }
        if (!data.birthday) delete data.birthday
        if (!data.breed) delete data.breed

        if (isEdit.value) {
          await axios.put(`/api/shopper/pets/${editId.value}/`, data)
          ElMessage.success('档案更新成功 🎉')
        } else {
          await axios.post('/api/shopper/pets/', data)
          ElMessage.success('新宠物建档成功 🐾')
        }
        dialogVisible.value = false
        fetchPets()
      } catch {
        ElMessage.error('操作失败，请稍后重试')
      } finally {
        submitting.value = false
      }
    }

    // ---- 删除 ----
    const handleDelete = (pet) => {
      ElMessageBox.confirm(
        `确定要删除「${pet.pet_name}」的档案吗？此操作不可撤销。`,
        '删除确认',
        { confirmButtonText: '确认删除', cancelButtonText: '再想想', type: 'warning' }
      ).then(async () => {
        try {
          await axios.delete(`/api/shopper/pets/${pet.id}/`)
          ElMessage.success('已删除该宠物档案')
          fetchPets()
        } catch {
          ElMessage.error('删除失败')
        }
      }).catch(() => {})
    }

    // ---- 辅助函数 ----
    const petEmoji = (type) => {
      const map = { '狗狗': '🐶', '猫咪': '🐱', '仓鼠': '🐹', '兔子': '🐰', '鸟类': '🐦', '鱼类': '🐟', '龟类': '🐢', '爬行类': '🦎' }
      return map[type] || '🐾'
    }
    const petTypeClass = (type) => {
      const map = { '狗狗': 'type-dog', '猫咪': 'type-cat', '仓鼠': 'type-hamster', '兔子': 'type-rabbit' }
      return map[type] || 'type-other'
    }
    const genderLabel = (g) => g === 1 ? '♂ 公' : g === 2 ? '♀ 母' : '未知'
    const genderTagType = (g) => g === 1 ? '' : g === 2 ? 'danger' : 'info'

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('zh-CN')
    }

    const calcAge = (birthday) => {
      const birth = new Date(birthday)
      const now = new Date()
      let years = now.getFullYear() - birth.getFullYear()
      let months = now.getMonth() - birth.getMonth()
      if (months < 0) { years--; months += 12 }
      if (years > 0) return `${years}岁${months > 0 ? months + '个月' : ''}`
      if (months > 0) return `${months}个月`
      const days = Math.floor((now - birth) / 86400000)
      return `${days}天`
    }

    onMounted(fetchPets)

    return {
      pets, loading, dialogVisible, isEdit, form, rules, formRef, submitting,
      Plus, Edit, Delete,
      openDialog, submitForm, handleDelete, fetchPets,
      petEmoji, petTypeClass, genderLabel, genderTagType, formatDate, calcAge
    }
  }
}
</script>

<style scoped>
.pet-center {
  min-height: 600px;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  background: white;
  padding: 28px 36px;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(255, 168, 186, 0.1);
}
.header-left h2 {
  margin: 0;
  font-size: 22px;
  color: var(--text-main, #1d2129);
}
.sub-text {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--text-light, #86909c);
}

/* ---- 宠物卡片 ---- */
.pet-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(255, 168, 186, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
}
.pet-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 32px rgba(255, 168, 186, 0.2);
}

/* 卡片顶部色条 - 不同物种不同色 */
.pet-card::before {
  content: '';
  display: block;
  height: 8px;
  background: linear-gradient(135deg, #FFA8BA 0%, #FFB6C1 100%);
}
.pet-card.type-dog::before { background: linear-gradient(135deg, #FFB6C1 0%, #FF69B4 100%); }
.pet-card.type-cat::before { background: linear-gradient(135deg, #A0E8D7 0%, #4facfe 100%); }
.pet-card.type-hamster::before { background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%); }
.pet-card.type-rabbit::before { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
.pet-card.type-other::before { background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); }

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 8px;
}
.pet-avatar {
  font-size: 48px;
  line-height: 1;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.1));
}
.card-actions {
  opacity: 0;
  transition: opacity 0.25s ease;
}
.pet-card:hover .card-actions {
  opacity: 1;
}

.card-body {
  padding: 4px 20px 16px;
}
.pet-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text-main, #1d2129);
}
.gender-tag {
  margin-bottom: 16px;
}
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 16px;
}
.info-item {
  display: flex;
  flex-direction: column;
}
.info-label {
  font-size: 11px;
  color: var(--text-light, #86909c);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 3px;
}
.info-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-main, #1d2129);
}

.card-footer {
  padding: 0 20px 18px;
  min-height: 24px;
}
.age-text {
  font-size: 13px;
  color: var(--primary-color, #e87e7e);
  font-weight: 600;
}
</style>
