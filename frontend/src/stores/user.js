import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const userId = ref(localStorage.getItem('user_id') || '')

  // 登录
  function login(tokenVal, usernameVal, userIdVal) {
    token.value = tokenVal
    username.value = usernameVal
    userId.value = userIdVal
    localStorage.setItem('token', tokenVal)
    localStorage.setItem('username', usernameVal)
    localStorage.setItem('user_id', userIdVal)
  }

  // 退出
  function logout() {
    token.value = ''
    username.value = ''
    userId.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('user_id')
  }

  // 是否已登录
  const isLoggedIn = () => !!token.value

  // 获取当前用户信息
  async function fetchUserInfo() {
    if (!token.value) return null
    try {
      const res = await api.get('/user/me')
      if (res.data.user_id) {
        username.value = res.data.username
        userId.value = res.data.user_id
        localStorage.setItem('username', res.data.username)
        localStorage.setItem('user_id', res.data.user_id)
        return res.data
      }
      return null
    } catch {
      return null
    }
  }

  return { token, username, userId, login, logout, isLoggedIn, fetchUserInfo }
})
