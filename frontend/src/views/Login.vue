<template>
  <div class="login-page">
    <div class="login-card">
      <!-- 左：产品定位 -->
      <div class="brand">
        <div class="brand-mark">
          <span class="brand-mark-text">问</span>
        </div>
        <h1 class="brand-title">把学习资料<br />变成你的 AI 问答库</h1>
        <p class="brand-sub">上传资料 · 语义检索 · 精准回答</p>

        <ul class="feature-list">
          <li>
            <span class="feature-dot"></span>
            <div>
              <strong>自动建库</strong>
              <span>上传 PDF / TXT / Markdown，自动提取、切分、入库</span>
            </div>
          </li>
          <li>
            <span class="feature-dot"></span>
            <div>
              <strong>检索作答</strong>
              <span>基于资料内容的语义检索，回答附引用出处</span>
            </div>
          </li>
          <li>
            <span class="feature-dot"></span>
            <div>
              <strong>记忆对话</strong>
              <span>多会话管理，对话上下文自然延续</span>
            </div>
          </li>
        </ul>
      </div>

      <!-- 右：登录 / 注册表单 -->
      <div class="form-panel">
        <h2 class="form-title">{{ isLogin ? '登录' : '注册' }}</h2>
        <p class="form-sub">{{ isLogin ? '使用你的账号继续' : '创建一个新账号' }}</p>

        <div class="form-body">
          <div class="form-item">
            <label>用户名</label>
            <el-input v-model="username" placeholder="请输入用户名" size="large" />
          </div>
          <div class="form-item">
            <label>密码</label>
            <el-input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
              @keyup.enter="submit"
            />
          </div>

          <el-button type="primary" size="large" class="submit-btn" @click="submit">
            {{ isLogin ? '登录' : '注册' }}
          </el-button>

          <div class="switch-line">
            <span>{{ isLogin ? '还没有账号？' : '已有账号？' }}</span>
            <a class="switch-link" @click="isLogin = !isLogin">{{ isLogin ? '去注册' : '去登录' }}</a>
          </div>

          <el-alert
            v-if="errorMsg"
            :title="errorMsg"
            :type="errorMsg.includes('成功') ? 'success' : 'error'"
            show-icon
            :closable="false"
            class="error-alert"
          />
        </div>
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
        await chatStore.loadUserData()
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
.login-page {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 40px 24px;
}

.login-card {
  width: 920px;
  max-width: 100%;
  display: flex;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

/* 左栏：产品定位 */
.brand {
  flex: 1.15;
  background: #f0f6ff;
  border-right: 1px solid #e4e7ed;
  padding: 48px 44px;
  display: flex;
  flex-direction: column;
}

.brand-mark {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 28px;
}

.brand-mark-text {
  color: #fff;
  font-size: 20px;
  font-weight: 600;
}

.brand-title {
  font-size: 28px;
  line-height: 1.4;
  font-weight: 600;
  color: #1f2329;
  margin: 0 0 10px;
}

.brand-sub {
  font-size: 14px;
  color: #909399;
  margin: 0 0 36px;
  letter-spacing: 0.02em;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.feature-list li {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.feature-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  margin-top: 6px;
  flex-shrink: 0;
}

.feature-list strong {
  display: block;
  font-size: 15px;
  color: #1f2329;
  margin-bottom: 3px;
  font-weight: 600;
}

.feature-list span {
  font-size: 13px;
  color: #5e6370;
  line-height: 1.6;
}

/* 右栏：表单 */
.form-panel {
  flex: 1;
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2329;
  margin: 0 0 6px;
}

.form-sub {
  font-size: 14px;
  color: #909399;
  margin: 0 0 28px;
}

.form-item {
  margin-bottom: 18px;
}

.form-item label {
  display: block;
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
  font-weight: 500;
}

.submit-btn {
  width: 100%;
  margin-top: 6px;
  border-radius: 8px;
  font-weight: 500;
}

.switch-line {
  margin-top: 18px;
  font-size: 13px;
  color: #909399;
  text-align: center;
}

.switch-link {
  color: #409eff;
  cursor: pointer;
  margin-left: 4px;
}

.switch-link:hover {
  text-decoration: underline;
}

.error-alert {
  margin-top: 16px;
}

/* 窄屏：只显示表单，隐藏品牌区 */
@media (max-width: 768px) {
  .login-card {
    width: 420px;
  }
  .brand {
    display: none;
  }
}
</style>
