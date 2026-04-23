<template>
  <div class="container">
    <div class="page-header">
      <h1>确认订单</h1>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else class="checkout-layout">
      <div>
        <div class="card">
          <div class="section-title">收货地址</div>
          
          <div class="form-group">
            <label>收货人姓名</label>
            <input type="text" v-model="form.address.name" placeholder="请输入收货人姓名" />
          </div>
          
          <div class="form-group">
            <label>联系电话</label>
            <input type="tel" v-model="form.address.phone" placeholder="请输入联系电话" />
          </div>
          
          <div class="form-group">
            <label>详细地址</label>
            <textarea 
              v-model="form.address.address" 
              placeholder="请输入详细地址"
              rows="3"
            ></textarea>
          </div>
        </div>
        
        <div class="card">
          <div class="section-title">支付方式</div>
          
          <div class="payment-options">
            <div 
              class="payment-option" 
              :class="{ selected: form.payment_method === '微信' }"
              @click="form.payment_method = '微信'"
            >
              <div class="icon">💬</div>
              <div class="name">微信支付</div>
            </div>
            <div 
              class="payment-option" 
              :class="{ selected: form.payment_method === '支付宝' }"
              @click="form.payment_method = '支付宝'"
            >
              <div class="icon">💰</div>
              <div class="name">支付宝</div>
            </div>
          </div>
        </div>
        
        <div class="card">
          <div class="section-title">商品清单</div>
          
          <div v-for="item in cartItems" :key="item.id" class="order-item">
            <div class="order-item-info">
              <div class="order-item-name">{{ item.product?.name }}</div>
              <div class="order-item-price">
                ¥{{ item.product?.price?.toFixed(2) }} × {{ item.quantity }}
              </div>
            </div>
            <div class="order-item-subtotal">
              ¥{{ (item.product?.price * item.quantity).toFixed(2) }}
            </div>
          </div>
        </div>
      </div>
      
      <div>
        <div class="cart-summary" style="position: sticky; top: 20px;">
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
            <span>应付金额</span>
            <span class="value">¥{{ totalAmount.toFixed(2) }}</span>
          </div>
          
          <button 
            class="btn btn-success" 
            style="width: 100%; padding: 14px; font-size: 16px; margin-top: 16px;"
            @click="submitOrder"
            :disabled="submitting"
          >
            {{ submitting ? '提交中...' : '提交订单' }}
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
import { orderApi } from '../api/order'

export default {
  name: 'Checkout',
  setup() {
    const router = useRouter()
    const cartItems = ref([])
    const loading = ref(false)
    const error = ref('')
    const submitting = ref(false)
    
    const form = ref({
      address: {
        name: '',
        phone: '',
        address: ''
      },
      payment_method: '微信'
    })
    
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
        
        if (cartItems.value.length === 0) {
          router.push('/cart')
        }
      } catch (err) {
        if (err.response?.status === 401) {
          router.push('/login')
        } else {
          error.value = '加载购物车失败，请重试'
        }
      } finally {
        loading.value = false
      }
    }
    
    const validateForm = () => {
      const { name, phone, address } = form.value.address
      
      if (!name.trim()) {
        error.value = '请输入收货人姓名'
        return false
      }
      
      if (!phone.trim()) {
        error.value = '请输入联系电话'
        return false
      }
      
      if (!/^1[3-9]\d{9}$/.test(phone.trim())) {
        error.value = '请输入正确的手机号码'
        return false
      }
      
      if (!address.trim()) {
        error.value = '请输入详细地址'
        return false
      }
      
      return true
    }
    
    const submitOrder = async () => {
      error.value = ''
      
      if (!validateForm()) {
        return
      }
      
      submitting.value = true
      
      try {
        const response = await orderApi.createOrder({
          address: form.value.address,
          payment_method: form.value.payment_method
        })
        
        alert('订单创建成功！')
        router.push('/orders')
      } catch (err) {
        error.value = err.response?.data?.error || '提交订单失败，请重试'
      } finally {
        submitting.value = false
      }
    }
    
    onMounted(() => {
      fetchCart()
    })
    
    return {
      cartItems,
      loading,
      error,
      submitting,
      form,
      totalAmount,
      totalCount,
      submitOrder
    }
  }
}
</script>
