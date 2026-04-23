import api from './index'

export const orderApi = {
  createOrder(data) {
    return api.post('/orders', data)
  },
  
  getOrders(params = {}) {
    return api.get('/orders', { params })
  },
  
  getOrder(orderId) {
    return api.get(`/orders/${orderId}`)
  },
  
  updateOrderStatus(orderId, status) {
    return api.put(`/orders/${orderId}/status`, { status })
  }
}

export default orderApi
