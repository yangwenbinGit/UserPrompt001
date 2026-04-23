import api from './index'

export const cartApi = {
  getCart() {
    return api.get('/cart')
  },
  
  addToCart(productId, quantity = 1) {
    return api.post('/cart', { product_id: productId, quantity })
  },
  
  updateCart(productId, quantity) {
    return api.put(`/cart/${productId}`, { quantity })
  },
  
  removeFromCart(productId) {
    return api.delete(`/cart/${productId}`)
  }
}

export default cartApi
