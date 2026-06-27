import { createRouter, createWebHistory } from 'vue-router'
import Chat from '../views/Chat.vue'
import Docs from '../views/Docs.vue'
import VectorDB from '../views/VectorDB.vue'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: Chat
  },
  {
    path: '/docs',
    name: 'Docs',
    component: Docs
  },
  {
    path: '/vectordb',
    name: 'VectorDB',
    component: VectorDB
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
