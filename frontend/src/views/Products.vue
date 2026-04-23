<template>
  <div class="container">
    <div class="page-header">
      <h1>商品列表</h1>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else>
      <div class="product-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          <div class="product-image">
            {{ product.name.charAt(0) }}
          </div>
          <div class="product-info">
            <div class="product-name">{{ product.name }}</div>
            <div class="product-price">¥{{ product.price.toFixed(2) }}</div>
            <div class="product-stock">库存: {{ product.stock }}</div>
          </div>
          <div class="product-actions">
            <button 
              class="btn btn-primary" 
              @click="addToCart(product)"
              :disabled="product.stock <= 0 || addingCart === product.id"
            >
              {{ addingCart === product.id ? '添加中...' : '加入购物车' }}
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { productApi } from '../api/product'
import { cartApi } from '../api/cart'

export default {
  name: 'Products',
  setup() {
    const router = useRouter()
    const products = ref([])
    const pagination = ref({
      current_page: 1,
      pages: 1,
      total: 0
    })
    const loading = ref(false)
    const error = ref('')
    const addingCart = ref(null)
    
    const fetchProducts = async (page = 1) => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await productApi.getProducts({ page, per_page: 10 })
        products.value = response.data.items
        pagination.value = {
          current_page: response.data.current_page,
          pages: response.data.pages,
          total: response.data.total
        }
      } catch (err) {
        error.value = '加载商品失败，请重试'
      } finally {
        loading.value = false
      }
    }
    
    const addToCart = async (product) => {
      if (!localStorage.getItem('token')) {
        router.push('/login')
        return
      }
      
      addingCart.value = product.id
      
      try {
        await cartApi.addToCart(product.id, 1)
        alert('已加入购物车')
      } catch (err) {
        alert(err.response?.data?.error || '添加失败')
      } finally {
        addingCart.value = null
      }
    }
    
    const goToPage = (page) => {
      if (page >= 1 && page <= pagination.value.pages) {
        fetchProducts(page)
      }
    }
    
    onMounted(() => {
      fetchProducts()
    })
    
    return {
      products,
      pagination,
      loading,
      error,
      addingCart,
      fetchProducts,
      addToCart,
      goToPage
    }
  }
}
</script>
