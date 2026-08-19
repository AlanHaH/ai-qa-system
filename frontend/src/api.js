import axios from 'axios'

// 部署时通过 VITE_API_BASE 注入（.env.production 设 '/' 走同域反代），本地默认直连后端
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：token 缺失/无效/过期（401）时，清除本地登录信息并跳转登录页
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('user_id')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
