<template>
  <div class="container">
    <div class="page-header">
      <h1>我的订单</h1>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="orders.length === 0" class="empty-state">
      <h3>暂无订单</h3>
      <p>快去选购喜欢的商品吧</p>
      <router-link to="/" class="btn btn-primary">去逛逛</router-link>
    </div>
    
    <div v-else>
      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <div class="order-id">订单号: {{ order.id }}</div>
          <div class="order-status" :class="getStatusClass(order.status)">
            {{ order.status }}
          </div>
        </div>
        
        <div class="order-body">
          <div style="margin-bottom: 12px; font-size: 14px; color: #666;">
            下单时间: {{ formatDate(order.created_at) }}
          </div>
          
          <div v-if="expandedOrderId === order.id" style="margin-top: 16px;">
            <div class="section-title" style="font-size: 14px; margin-bottom: 12px;">订单详情</div>
            
            <div v-for="item in order.items" :key="item.id" class="order-item">
              <div class="order-item-info">
                <div class="order-item-name">{{ item.product?.name || `商品 ${item.product_id}` }}</div>
                <div class="order-item-price">
                  ¥{{ item.price?.toFixed(2) }} × {{ item.quantity }}
                </div>
              </div>
              <div class="order-item-subtotal">
                ¥{{ (item.price * item.quantity).toFixed(2) }}
              </div>
            </div>
            
            <div style="margin-top: 16px; padding: 12px; background: #fafafa; border-radius: 4px;">
              <div style="font-size: 13px; color: #666;">
                <div style="margin-bottom: 4px;">
                  <strong>收货人:</strong> {{ orderAddress.name }}
                </div>
                <div style="margin-bottom: 4px;">
                  <strong>电话:</strong> {{ orderAddress.phone }}
                </div>
                <div>
                  <strong>地址:</strong> {{ orderAddress.address }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="order-footer">
          <div class="order-total">
            订单金额: <span class="amount">¥{{ order.total_amount?.toFixed(2) }}</span>
          </div>
          <div style="display: flex; gap: 8px;">
            <button 
              class="btn btn-primary" 
              style="padding: 6px 16px; font-size: 13px;"
              @click="toggleOrderDetail(order)"
            >
              {{ expandedOrderId === order.id ? '收起' : '查看详情' }}
            </button>
            
            <button 
              v-if="order.status === '待支付'"
              class="btn btn-success" 
              style="padding: 6px 16px; font-size: 13px;"
              @click="simulatePayment(order)"
              :disabled="payingOrderId === order.id"
            >
              {{ payingOrderId === order.id ? '处理中...' : '去支付' }}
            </button>
            
            <button 
              v-if="order.status === '待支付'"
              class="btn btn-danger" 
              style="padding: 6px 16px; font-size: 13px;"
              @click="cancelOrder(order)"
            >
              取消订单
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="pagination.pages > 1" class="pagination">
        <button @click="goToPage(pagination.current_page - 1)" :disabled="pagination.current_page <= 1">
          上一页
        </button>
        <button 
          v-for="page in pagination.pages" 
          :key="page"
          :class="{ active: page === pagination.current_page }"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
        <button @click="goToPage(pagination.current_page + 1)" :disabled="pagination.current_page >= pagination.pages">
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { orderApi } from '../api/order'

export default {
  name: 'Orders',
  setup() {
    const router = useRouter()
    const orders = ref([])
    const pagination = ref({
      current_page: 1,
      pages: 1,
      total: 0
    })
    const loading = ref(false)
    const error = ref('')
    const expandedOrderId = ref(null)
    const payingOrderId = ref(null)
    const orderDetails = ref({})
    
    const getStatusClass = (status) => {
      switch (status) {
        case '待支付': return 'pending'
        case '已支付': return 'paid'
        case '已取消': return 'cancelled'
        default: return ''
      }
    }
    
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    const parseAddress = (addressJson) => {
      try {
        return JSON.parse(addressJson)
      } catch {
        return { name: '-', phone: '-', address: '-' }
      }
    }
    
    const orderAddress = computed(() => {
      if (!expandedOrderId.value) return {}
      const order = orders.value.find(o => o.id === expandedOrderId.value)
      if (!order) return {}
      return parseAddress(order.address_json)
    })
    
    const fetchOrders = async (page = 1) => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await orderApi.getOrders({ page, per_page: 10 })
        orders.value = response.data.items || []
        pagination.value = {
          current_page: response.data.current_page,
          pages: response.data.pages,
          total: response.data.total
        }
      } catch (err) {
        if (err.response?.status === 401) {
          router.push('/login')
        } else {
          error.value = '加载订单失败，请重试'
        }
      } finally {
        loading.value = false
      }
    }
    
    const fetchOrderDetail = async (orderId) => {
      try {
        const response = await orderApi.getOrder(orderId)
        orderDetails.value[orderId] = response.data
        
        const index = orders.value.findIndex(o => o.id === orderId)
        if (index !== -1) {
          orders.value[index] = { ...orders.value[index], ...response.data }
        }
      } catch (err) {
        console.error('获取订单详情失败:', err)
      }
    }
    
    const toggleOrderDetail = async (order) => {
      if (expandedOrderId.value === order.id) {
        expandedOrderId.value = null
      } else {
        expandedOrderId.value = order.id
        if (!order.items) {
          await fetchOrderDetail(order.id)
        }
      }
    }
    
    const simulatePayment = async (order) => {
      if (!confirm('确认支付该订单？')) return
      
      payingOrderId.value = order.id
      
      try {
        await orderApi.updateOrderStatus(order.id, '已支付')
        alert('支付成功！')
        
        const index = orders.value.findIndex(o => o.id === order.id)
        if (index !== -1) {
          orders.value[index].status = '已支付'
        }
      } catch (err) {
        alert(err.response?.data?.error || '支付失败')
      } finally {
        payingOrderId.value = null
      }
    }
    
    const cancelOrder = async (order) => {
      if (!confirm('确认取消该订单？')) return
      
      try {
        await orderApi.updateOrderStatus(order.id, '已取消')
        alert('订单已取消')
        
        const index = orders.value.findIndex(o => o.id === order.id)
        if (index !== -1) {
          orders.value[index].status = '已取消'
        }
      } catch (err) {
        alert(err.response?.data?.error || '取消失败')
      }
    }
    
    const goToPage = (page) => {
      if (page >= 1 && page <= pagination.value.pages) {
        fetchOrders(page)
      }
    }
    
    onMounted(() => {
      fetchOrders()
    })
    
    return {
      orders,
      pagination,
      loading,
      error,
      expandedOrderId,
      payingOrderId,
      orderAddress,
      getStatusClass,
      formatDate,
      fetchOrders,
      toggleOrderDetail,
      simulatePayment,
      cancelOrder,
      goToPage
    }
  }
}
</script>
