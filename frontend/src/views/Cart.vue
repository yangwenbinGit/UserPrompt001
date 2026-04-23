<template>
  <div class="container">
    <div class="page-header">
      <h1>我的购物车</h1>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="cartItems.length === 0" class="empty-state">
      <h3>购物车是空的</h3>
      <p>快去选购喜欢的商品吧</p>
      <router-link to="/" class="btn btn-primary">去逛逛</router-link>
    </div>
    
    <div v-else class="checkout-layout">
      <div>
        <div class="card">
          <div class="section-title">商品清单</div>
          
          <div v-for="item in cartItems" :key="item.id" class="cart-item">
            <div class="cart-item-image">
              {{ item.product?.name?.charAt(0) || '商品' }}
            </div>
            <div class="cart-item-info">
              <div class="cart-item-name">{{ item.product?.name }}</div>
              <div class="cart-item-price">¥{{ item.product?.price?.toFixed(2) }}</div>
              <div class="cart-item-quantity">
                <button @click="updateQuantity(item, item.quantity - 1)" :disabled="item.quantity <= 1">-</button>
                <span>{{ item.quantity }}</span>
                <button @click="updateQuantity(item, item.quantity + 1)">+</button>
              </div>
            </div>
            <div class="cart-item-actions">
              <div class="cart-item-price" style="font-size: 18px;">
                ¥{{ (item.product?.price * item.quantity).toFixed(2) }}
              </div>
              <button class="btn btn-danger" style="padding: 4px 12px; font-size: 12px;" @click="removeItem(item)">
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div>
        <div class="cart-summary">
          <div class="section-title">订单摘要</div>
          
          <div class="cart-summary-row">
            <span>商品数量</span>
            <span>{{ totalCount }} 件</span>
          </div>
          
          <div class="cart-summary-row">
            <span>商品总价</span>
            <span>¥{{ totalAmount.toFixed(2) }}</span>
          </div>
          
          <div class="cart-summary-row">
            <span>运费</span>
            <span>¥0.00</span>
          </div>
          
          <div class="cart-summary-row total">
            <span>合计</span>
            <span class="value">¥{{ totalAmount.toFixed(2) }}</span>
          </div>
          
          <button class="btn btn-primary" style="width: 100%; padding: 14px; font-size: 16px;" @click="goToCheckout">
            去结算
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { cartApi } from '../api/cart'

export default {
  name: 'Cart',
  setup() {
    const router = useRouter()
    const cartItems = ref([])
    const loading = ref(false)
    const error = ref('')
    
    const totalAmount = computed(() => {
      return cartItems.value.reduce((sum, item) => {
        return sum + (item.product?.price || 0) * item.quantity
      }, 0)
    })
    
    const totalCount = computed(() => {
      return cartItems.value.reduce((sum, item) => sum + item.quantity, 0)
    })
    
    const fetchCart = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await cartApi.getCart()
        cartItems.value = response.data.items || []
      } catch (err) {
        if (err.response?.status === 401) {
          router.push('/login')
        } else {
          const errMsg = err.response?.data?.error || err.message || '加载购物车失败'
          console.error('Cart error:', err.response?.data, err)
          error.value = errMsg
        }
      } finally {
        loading.value = false
      }
    }
    
    const updateQuantity = async (item, newQuantity) => {
      if (newQuantity <= 0) return
      
      try {
        await cartApi.updateCart(item.product_id, newQuantity)
        item.quantity = newQuantity
      } catch (err) {
        alert(err.response?.data?.error || '更新失败')
      }
    }
    
    const removeItem = async (item) => {
      if (!confirm('确定要删除该商品吗？')) return
      
      try {
        await cartApi.removeFromCart(item.product_id)
        cartItems.value = cartItems.value.filter(i => i.id !== item.id)
      } catch (err) {
        alert(err.response?.data?.error || '删除失败')
      }
    }
    
    const goToCheckout = () => {
      if (cartItems.value.length === 0) {
        alert('购物车为空')
        return
      }
      router.push('/checkout')
    }
    
    onMounted(() => {
      fetchCart()
    })
    
    return {
      cartItems,
      loading,
      error,
      totalAmount,
      totalCount,
      fetchCart,
      updateQuantity,
      removeItem,
      goToCheckout
    }
  }
}
</script>
