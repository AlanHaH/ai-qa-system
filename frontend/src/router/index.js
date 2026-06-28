import { createRouter, createWebHistory } from 'vue-router'
import Chat from '../views/Chat.vue'
import Docs from '../views/Docs.vue'
import VectorDB from '../views/VectorDB.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: Chat,
    meta: { requiresAuth: true }
  },
  {
    path: '/docs',
    name: 'Docs',
    component: Docs,
    meta: { requiresAuth: true }
  },
  {
    path: '/vectordb',
    name: 'VectorDB',
    component: VectorDB,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：检查是否登录
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 如果访问需要登录的页面，但没有 token，跳转到登录页
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
