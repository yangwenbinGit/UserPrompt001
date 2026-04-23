import api from './index'

export const productApi = {
  getProducts(params = {}) {
    return api.get('/products', { params })
  },
  
  getProduct(id) {
    return api.get(`/products/${id}`)
  }
}

export default productApi
