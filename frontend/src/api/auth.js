import api from './index'

export const authApi = {
  register(data) {
    return api.post('/auth/register', data)
  },
  
  login(data) {
    return api.post('/auth/login', data)
  },
  
  getCurrentUser() {
    return api.get('/auth/me')
  }
}

export default authApi
