<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="logo">🐾 PetMall</div>
      <!-- 动态标题 -->
      <h2 class="title">
        {{ mode === 'register' ? '欢迎新铲屎官，注册账号' : mode === 'forgot' ? '找回密码流程' : '登录您的账号' }}
      </h2>
      
      <el-form :model="form" class="login-form">
        <!-- 登录和注册需要账号，找回密码不需要用户名（用邮箱） -->
        <el-form-item v-if="mode !== 'forgot'">
          <el-input v-model="form.username" placeholder="请输入您的账号 (Username)" size="large" />
        </el-form-item>

        <!-- 邮箱：注册和找回密码都需要 -->
        <el-form-item v-if="mode === 'register' || mode === 'forgot'">
          <el-input v-model="form.email" :placeholder="mode === 'forgot' ? '请输入绑定的电子邮箱' : '请输入您的常用电子邮箱'" size="large" />
        </el-form-item>

        <!-- 密码字段：注册显示“设置密码”，登录显示“通行密码”，找回密码显示“设置新密码” -->
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            :placeholder="mode === 'register' ? '请设置通行密码' : mode === 'forgot' ? '请设置新密码 (不少于6位)' : '请输入通行密码'" 
            size="large" 
            show-password 
          />
        </el-form-item>

        <!-- 确认密码：注册和找回密码都需要 -->
        <el-form-item v-if="mode === 'register' || mode === 'forgot'">
          <el-input 
            v-model="form.confirm_password" 
            type="password" 
            :placeholder="mode === 'forgot' ? '请再次确认新密码' : '请再次输入密码以确认'" 
            size="large" 
            show-password 
          />
        </el-form-item>
        
        <template v-if="mode === 'register'">
          <el-form-item>
            <el-input v-model="form.real_name" placeholder="请输入真实姓名或昵称 (选填)" size="large" />
          </el-form-item>
        </template>

        <!-- 验证码：注册和找回密码都需要 -->
        <template v-if="mode === 'register' || mode === 'forgot'">
          <el-form-item>
            <div style="display: flex; gap: 10px; width: 100%;">
              <el-input v-model="form.code" placeholder="请输入验证码" size="large" style="flex: 1;" />
              <el-button type="info" plain size="large" @click="sendCode" :disabled="countdown > 0 || loadingCode">
                {{ countdown > 0 ? `${countdown}s 后重发` : '获取验证码' }}
              </el-button>
            </div>
          </el-form-item>
        </template>
        
        <!-- 人机验证 -->
        <el-form-item>
           <div style="display: flex; gap: 10px; width: 100%; align-items: center; justify-content: space-between;">
              <span style="color:#5a5e66; font-weight:bold; white-space:nowrap; width: 120px;">
                🤖 人机验证: <br> {{ mathA }} + {{ mathB }} = ?
              </span>
              <el-input v-model.number="form.math_answer" placeholder="算术结果" size="large" style="width: 100px;" />
           </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" class="submit-btn" :loading="loading" @click="handleSubmit">
            {{ mode === 'register' ? '确认注册 🚀' : mode === 'forgot' ? '重置密码 ✨' : '立即登录 🌟' }}
          </el-button>
        </el-form-item>
        
        <!-- 切换入口 -->
        <div class="toggle-text">
          <template v-if="mode === 'login'">
            <a @click.prevent="mode = 'register'">没有账号？赶快去注册一个吧！</a>
            <span class="sep">|</span>
            <a @click.prevent="mode = 'forgot'">忘记密码？</a>
          </template>
          <template v-else>
            <a @click.prevent="mode = 'login'">已有账号？返回登录</a>
          </template>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'LoginCenter',
  setup() {
    const router = useRouter()
    // 模式: login, register, forgot
    const mode = ref('login')
    const loading = ref(false)
    const loadingCode = ref(false)
    const countdown = ref(0)
    const form = ref({ 
      username: '', 
      password: '', 
      confirm_password: '', // 新增：确认密码
      real_name: '', 
      email: '', 
      code: '', 
      math_answer: null 
    })
    
    const mathA = ref(Math.floor(Math.random() * 20))
    const mathB = ref(Math.floor(Math.random() * 20))
    const resetMath = () => {
      mathA.value = Math.floor(Math.random() * 20);
      mathB.value = Math.floor(Math.random() * 20);
      form.value.math_answer = null;
    }

    const sendCode = async () => {
      if (!form.value.email) {
        return ElMessage.warning('请先填写邮箱地址哦');
      }
      if (form.value.math_answer !== (mathA.value + mathB.value)) {
        resetMath()
        return ElMessage.error('🤖 算术结果错误，证明您是人类后再试吧！');
      }
      
      loadingCode.value = true
      try {
         // 根据模式使用不同的发送接口
         const url = mode.value === 'forgot' ? '/api/accounts/send-reset-code/' : '/api/accounts/send-email-code/'
         await axios.post(url, { email: form.value.email })
         ElMessage.success('验证码已发送至您的邮箱，请查收！')
         
         countdown.value = 60
         const timer = setInterval(() => {
           countdown.value--
           if(countdown.value <= 0) clearInterval(timer)
         }, 1000)
      } catch (err) {
         ElMessage.error(err.response?.data?.detail || '发送失败，请检查配置或邮箱是否正确')
         resetMath()
      } finally {
         loadingCode.value = false
      }
    }

    const handleSubmit = async () => {
      // 通用人机验证校验
      if (form.value.math_answer !== (mathA.value + mathB.value)) {
        resetMath()
        return ElMessage.error('🤖 算术结果错误，证明您是人类后再试吧！');
      }

      // 1. 登录逻辑
      if (mode.value === 'login') {
        if (!form.value.username || !form.value.password) {
           return ElMessage.warning('账号或密码是必填项哦~')
        }
      } 
      // 2. 注册或找回密码校验
      else {
        if (!form.value.email || !form.value.code || !form.value.password || !form.value.confirm_password) {
          return ElMessage.warning('请填满所有必填项哦~')
        }
        if (form.value.password !== form.value.confirm_password) {
          return ElMessage.error('两次输入的密码不一致！')
        }
        if (form.value.password.length < 6) {
          return ElMessage.warning('密码长度不能少于6位')
        }
        if (mode.value === 'register' && !form.value.username) {
          return ElMessage.warning('注册需要填写用户名哦')
        }
      }

      loading.value = true
      try {
        if (mode.value === 'register') {
          await axios.post('/api/accounts/register/', form.value)
          ElMessage.success('注册成功！正在为您切换登录...')
          mode.value = 'login'
          form.value.password = ''
          form.value.confirm_password = ''
          form.value.code = ''
          resetMath()
        } 
        else if (mode.value === 'forgot') {
          await axios.post('/api/accounts/reset-password/', {
            email: form.value.email,
            code: form.value.code,
            new_password: form.value.password
          })
          ElMessage.success('密码重置成功！请使用新密码登录')
          mode.value = 'login'
          form.value.password = ''
          form.value.confirm_password = ''
          form.value.code = ''
          resetMath()
        }
        else {
          const res = await axios.post('/api/accounts/login/', {
            username: form.value.username,
            password: form.value.password
          })
          localStorage.setItem('pet_user', JSON.stringify(res.data))
          ElMessage.success(`欢迎回来，${res.data.realName || res.data.username}！`)
          router.push('/commodity')
        }
      } catch (err) {
        ElMessage.error(err.response?.data?.detail || '操作失败')
        resetMath()
      } finally {
        loading.value = false
      }
    }

    return { mode, form, loading, loadingCode, countdown, mathA, mathB, sendCode, handleSubmit }
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: linear-gradient(135deg, #FFF0F5 0%, #FDFBF8 100%);
}
.login-card {
  width: 440px; /* 略微调宽以适应更多输入 */
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 50px 40px;
  border-radius: 24px;
  box-shadow: 0 16px 40px rgba(255, 168, 186, 0.2);
  text-align: center;
}
.logo {
  font-size: 32px;
  font-weight: 900;
  color: var(--primary-color);
  margin-bottom: 10px;
}
.title {
  color: var(--text-main);
  font-size: 18px;
  margin-bottom: 30px;
  font-weight: 500;
}
.submit-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  border-radius: 25px !important;
  margin-top: 10px;
}
.toggle-text {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 12px;
  align-items: center;
}
.toggle-text a {
  color: var(--primary-color);
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}
.toggle-text a:hover {
  text-decoration: underline;
}
.sep {
  color: #dcdfe6;
}
</style>
