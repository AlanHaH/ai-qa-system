<script setup>
import { onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './stores/user'
import { useChatStore } from './stores/chat'
import ChatSidebar from './components/ChatSidebar.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const chatStore = useChatStore()

onMounted(async () => {
  if (userStore.isLoggedIn()) {
    await userStore.fetchUserInfo()
    chatStore.loadUserData()
  }
})

// 监听用户变化，加载对应的聊天数据
watch(() => userStore.userId, (newUserId) => {
  if (newUserId) {
    chatStore.loadUserData()
  }
})

function logout() {
  chatStore.saveCurrentSession()
  userStore.logout()
  chatStore.clearMessages()
  router.push('/login')
}
</script>

<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <nav>
      <div class="nav-left">
        <div class="logo">🤖 AI QA</div>
        <div class="nav-links">
          <router-link to="/">聊天</router-link>
          <router-link to="/docs">知识库</router-link>
          <router-link to="/vectordb">向量库</router-link>
        </div>
      </div>
      <div class="nav-right">
        <span v-if="userStore.username" class="user-info">
          <span class="user-avatar">👤</span>
          <span class="user-name">{{ userStore.username }}</span>
          <a @click="logout" class="logout">退出</a>
        </span>
        <router-link v-else to="/login" class="login-btn">登录</router-link>
      </div>
    </nav>

    <!-- 主体区域 -->
    <div class="main-content">
      <!-- 聊天页面显示侧边栏 -->
      <ChatSidebar v-if="route.path === '/' && userStore.isLoggedIn()" />
      
      <!-- 路由出口 -->
      <router-view class="router-view" />
    </div>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #f5f7fa;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e5e5e5;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-links a {
  text-decoration: none;
  color: #666;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-links a:hover {
  background: #f5f5f5;
  color: #333;
}

.nav-links a.router-link-active {
  color: #409eff;
  background: #ecf5ff;
  font-weight: 500;
}

.nav-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.user-avatar {
  font-size: 18px;
}

.user-name {
  color: #333;
  font-weight: 500;
}

.logout {
  color: #f56c6c !important;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.logout:hover {
  background: #fef0f0;
}

.login-btn {
  text-decoration: none;
  color: #409eff !important;
  font-size: 14px;
  padding: 8px 16px;
  border: 1px solid #409eff;
  border-radius: 6px;
  transition: all 0.2s;
}

.login-btn:hover {
  background: #409eff;
  color: #fff !important;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.router-view {
  flex: 1;
  overflow-y: auto;
}
</style>
