<template>
  <div id="app">
    <nav class="nav">
      <div class="nav-inner">
        <router-link to="/" class="nav-brand">简易电商</router-link>
        <div class="nav-links">
          <router-link to="/">商品</router-link>
          <router-link to="/cart" v-if="isLoggedIn">购物车</router-link>
          <router-link to="/orders" v-if="isLoggedIn">我的订单</router-link>
          <template v-if="isLoggedIn">
            <span>{{ currentUser?.username }}</span>
            <a href="#" @click.prevent="logout">退出登录</a>
          </template>
          <template v-else>
            <router-link to="/login">登录</router-link>
            <router-link to="/register">注册</router-link>
          </template>
        </div>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const isLoggedInRef = ref(!!localStorage.getItem('token'))
const userRef = ref(null)

const updateAuthState = () => {
  const token = localStorage.getItem('token')
  const userData = localStorage.getItem('user')
  
  isLoggedInRef.value = !!token
  
  if (userData && token) {
    try {
      userRef.value = JSON.parse(userData)
    } catch {
      userRef.value = null
    }
  } else {
    userRef.value = null
  }
}

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    
    const isLoggedIn = computed(() => isLoggedInRef.value)
    const currentUser = computed(() => userRef.value)
    
    const logout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      updateAuthState()
      router.push('/login')
    }
    
    watch(() => router.currentRoute.value, () => {
      updateAuthState()
    }, { immediate: true })
    
    onMounted(() => {
      updateAuthState()
      
      window.addEventListener('storage', updateAuthState)
    })
    
    return {
      isLoggedIn,
      currentUser,
      logout
    }
  }
}
</script>
