<template>
  <div class="login-container">
    <div class="form-box">
      <div class="form-header">
        <div class="logo">🤖</div>
        <h2>{{ isLogin ? '欢迎回来' : '创建账号' }}</h2>
        <p class="subtitle">{{ isLogin ? '登录后开始使用 AI 学习助手' : '注册后开始你的学习之旅' }}</p>
      </div>

      <div class="form-body">
        <div class="form-item">
          <label>用户名</label>
          <el-input v-model="username" placeholder="请输入用户名" size="large" />
        </div>
        <div class="form-item">
          <label>密码</label>
          <el-input v-model="password" type="password" placeholder="请输入密码" @keyup.enter="submit" size="large" show-password />
        </div>

        <el-button type="primary" @click="submit" class="submit-btn" size="large">
          {{ isLogin ? '登录' : '注册' }}
        </el-button>

        <p class="switch" @click="isLogin = !isLogin">
          {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
        </p>

        <el-alert v-if="errorMsg" :title="errorMsg" :type="errorMsg.includes('成功') ? 'success' : 'error'" show-icon :closable="false" style="margin-top: 12px" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'
import { useChatStore } from '../stores/chat'
import api from '../api'

const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()

// 如果已登录，直接跳转到首页
onMounted(() => {
  if (userStore.isLoggedIn()) {
    router.push('/')
  }
})

const username = ref('')
const password = ref('')
const isLogin = ref(true)
const errorMsg = ref('')

async function submit() {
  errorMsg.value = ''
  if (!username.value || !password.value) {
    errorMsg.value = '请填写用户名和密码'
    return
  }

  const url = isLogin.value ? '/user/login' : '/user/register'

  try {
    const res = await api.post(url, {
      username: username.value,
      password: password.value
    })
    const data = res.data

    if (data.error) {
      errorMsg.value = data.error
    } else {
      if (isLogin.value) {
        // 用 Pinia 保存用户状态
        userStore.login(data.token, data.username, data.user_id)
        chatStore.loadUserData()
        ElMessage.success('登录成功')
        router.push('/')
      } else {
        isLogin.value = true
        errorMsg.value = '注册成功，请登录'
      }
    }
  } catch (err) {
    errorMsg.value = '请求失败：' + err.message
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 56px);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #0c0c1d 0%, #1a1a3e 50%, #2d1b69 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 70% 50%, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
  animation: float 15s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-20px, -20px); }
}

.form-box {
  width: 380px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 25px 80px rgba(0,0,0,0.3), 0 0 40px rgba(99, 102, 241, 0.1);
  overflow: hidden;
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.form-header {
  text-align: center;
  padding: 32px 32px 0;
}

.logo {
  font-size: 48px;
  margin-bottom: 16px;
}

.form-header h2 {
  font-size: 24px;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #888;
  margin: 0;
}

.form-body {
  padding: 24px 32px 32px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  font-weight: 500;
}

.submit-btn {
  width: 100%;
  margin-top: 8px;
}

.switch {
  text-align: center;
  margin-top: 16px;
  color: #6366f1;
  cursor: pointer;
  font-size: 13px;
}

.switch:hover {
  text-decoration: underline;
  color: #8b5cf6;
}
</style>
