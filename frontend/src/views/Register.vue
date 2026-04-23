<template>
  <div class="auth-layout">
    <div class="auth-card">
      <h2>用户注册</h2>
      
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="success" class="success-message">{{ success }}</div>
      
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名</label>
          <input type="text" v-model="form.username" placeholder="请输入用户名" required />
        </div>
        
        <div class="form-group">
          <label>邮箱</label>
          <input type="email" v-model="form.email" placeholder="请输入邮箱" required />
        </div>
        
        <div class="form-group">
          <label>密码</label>
          <input type="password" v-model="form.password" placeholder="请输入密码" required />
        </div>
        
        <div class="form-group">
          <label>确认密码</label>
          <input type="password" v-model="form.confirmPassword" placeholder="请确认密码" required />
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="footer-link">
        已有账号？<router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const form = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    
    const handleRegister = async () => {
      if (form.value.password !== form.value.confirmPassword) {
        error.value = '两次输入的密码不一致'
        return
      }
      
      loading.value = true
      error.value = ''
      success.value = ''
      
      try {
        await authApi.register({
          username: form.value.username,
          email: form.value.email,
          password: form.value.password
        })
        
        success.value = '注册成功！正在跳转到登录页...'
        setTimeout(() => {
          router.push('/login')
        }, 1500)
      } catch (err) {
        error.value = err.response?.data?.error || '注册失败，请重试'
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      loading,
      error,
      success,
      handleRegister
    }
  }
}
</script>
