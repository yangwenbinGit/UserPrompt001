<template>
  <div class="auth-layout">
    <div class="auth-card">
      <h2>用户登录</h2>
      
      <div v-if="error" class="error-message">{{ error }}</div>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名</label>
          <input type="text" v-model="form.username" placeholder="请输入用户名" required />
        </div>
        
        <div class="form-group">
          <label>密码</label>
          <input type="password" v-model="form.password" placeholder="请输入密码" required />
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <div class="footer-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const form = ref({
      username: '',
      password: ''
    })
    const loading = ref(false)
    const error = ref('')
    
    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await authApi.login(form.value)
        const { access_token, user } = response.data
        
        localStorage.setItem('token', access_token)
        localStorage.setItem('user', JSON.stringify(user))
        
        window.dispatchEvent(new Event('storage'))
        router.push('/')
      } catch (err) {
        error.value = err.response?.data?.error || '登录失败，请重试'
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      loading,
      error,
      handleLogin
    }
  }
}
</script>
