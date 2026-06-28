<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const username = ref(localStorage.getItem('username') || '')

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('user_id')
  username.value = ''
  router.push('/login')
}

// 监听路由变化，每次跳转页面时重新读取 localStorage
watch(() => route.path, () => {
  username.value = localStorage.getItem('username') || ''
})
</script>

<template>
  <nav>
    <div class="nav-left">
      <router-link to="/">聊天</router-link>
      <router-link to="/docs">知识库</router-link>
      <router-link to="/vectordb">向量库</router-link>
    </div>
    <div class="nav-right">
      <span v-if="username">
        {{ username }}
        <a @click="logout" class="logout">退出</a>
      </span>
      <router-link v-else to="/login">登录</router-link>
    </div>
  </nav>
  <router-view />
</template>

<style>
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.nav-left {
  display: flex;
  gap: 16px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

nav a {
  text-decoration: none;
  color: #409eff;
  font-size: 14px;
  cursor: pointer;
}

nav a.router-link-active {
  font-weight: bold;
  color: #337ecc;
}

.logout {
  color: #f56c6c !important;
  font-size: 13px;
}
</style>
