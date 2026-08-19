<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './stores/user'
import { useChatStore } from './stores/chat'
import { Menu } from '@element-plus/icons-vue'
import ChatSidebar from './components/ChatSidebar.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const chatStore = useChatStore()

onMounted(async () => {
  if (userStore.isLoggedIn()) {
    await userStore.fetchUserInfo()
    await chatStore.loadUserData()
  }
})

// 监听用户变化，加载对应的聊天数据
watch(() => userStore.userId, async (newUserId) => {
  if (newUserId) {
    await chatStore.loadUserData()
  }
})

// 移动端侧边栏抽屉开关
const sidebarOpen = ref(false)

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

// 路由切换时关闭抽屉，避免从 /docs 返回 / 后抽屉自动弹开
watch(() => route.path, () => {
  sidebarOpen.value = false
})

// 抽屉打开时锁定背景滚动（移动端）
watch(sidebarOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

async function logout() {
  await chatStore.saveCurrentSession()
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
        <button
          v-if="route.path === '/' && userStore.isLoggedIn()"
          class="hamburger"
          @click="toggleSidebar"
          aria-label="打开菜单"
        >
          <el-icon :size="20"><Menu /></el-icon>
        </button>
        <div class="logo">
          <span class="logo-mark">问</span>
          <span class="logo-text">学习问答</span>
        </div>
        <div class="nav-links">
          <router-link to="/">聊天</router-link>
          <router-link to="/docs">知识库</router-link>
          <router-link to="/vectordb">向量库</router-link>
        </div>
      </div>
      <div class="nav-right">
        <span v-if="userStore.username" class="user-info">
          <span class="user-avatar">{{ userStore.username.charAt(0).toUpperCase() }}</span>
          <span class="user-name">{{ userStore.username }}</span>
          <a @click="logout" class="logout">退出</a>
        </span>
        <router-link v-else to="/login" class="login-btn">登录</router-link>
      </div>
    </nav>

    <!-- 主体区域 -->
    <div class="main-content">
      <!-- 聊天页面显示侧边栏 -->
      <ChatSidebar
        v-if="route.path === '/' && userStore.isLoggedIn()"
        :open="sidebarOpen"
        @close="sidebarOpen = false"
      />
      
      <!-- 路由出口 -->
      <router-view class="router-view" />
    </div>

    <!-- 移动端底部 Tab 栏（桌面隐藏） -->
    <nav v-if="userStore.isLoggedIn()" class="bottom-nav">
      <router-link to="/">聊天</router-link>
      <router-link to="/docs">知识库</router-link>
      <router-link to="/vectordb">向量库</router-link>
    </nav>
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-mark {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: #409eff;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 17px;
  font-weight: 600;
  color: #1f2329;
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
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
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

/* 汉堡按钮：桌面隐藏，移动端显示 */
.hamburger {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  color: #333;
  line-height: 1;
}

.hamburger:hover {
  background: #f5f5f5;
}

/* 底部 Tab 栏：桌面隐藏 */
.bottom-nav {
  display: none;
}

/* ===== 移动端（<768px） ===== */
@media (max-width: 768px) {
  /* 动态视口高度：跟随移动端 URL 栏/键盘（桌面 100dvh 等于 100vh，无副作用） */
  @supports (height: 100dvh) {
    .app-container {
      height: 100dvh;
    }
  }

  nav {
    padding: 0 12px;
  }

  .nav-left {
    gap: 12px;
  }

  /* 汉堡按钮出现 */
  .hamburger {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  /* 隐藏文字导航与用户名，只留 logo / 头像 */
  .nav-links {
    display: none;
  }

  .user-name {
    display: none;
  }

  .user-info {
    gap: 4px;
  }

  .logout {
    padding: 4px 6px;
  }

  .login-btn {
    padding: 6px 12px;
  }

  /* 给底部 Tab 栏让出空间 */
  .main-content {
    padding-bottom: calc(56px + env(safe-area-inset-bottom));
  }

  /* 底部 Tab 栏 */
  .bottom-nav {
    display: flex;
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 90;
    height: calc(56px + env(safe-area-inset-bottom));
    padding-bottom: env(safe-area-inset-bottom);
    background: #fff;
    border-top: 1px solid #e5e5e5;
  }

  .bottom-nav a {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    color: #666;
    font-size: 13px;
  }

  .bottom-nav a.router-link-active {
    color: #409eff;
    font-weight: 500;
  }
}
</style>
