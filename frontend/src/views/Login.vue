<template>
  <div class="login-container">
    <div class="form-box">
      <h2>{{ isLogin ? '登录' : '注册' }}</h2>

      <div class="form-item">
        <input v-model="username" placeholder="用户名" />
      </div>
      <div class="form-item">
        <input v-model="password" type="password" placeholder="密码" @keyup.enter="submit" />
      </div>

      <button @click="submit">{{ isLogin ? '登录' : '注册' }}</button>

      <p class="switch" @click="isLogin = !isLogin">
        {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
      </p>

      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 如果已登录，直接跳转到首页
onMounted(() => {
  if (localStorage.getItem('token')) {
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

  const url = isLogin.value
    ? 'http://127.0.0.1:8000/user/login'
    : 'http://127.0.0.1:8000/user/register'

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })
    const data = await res.json()

    if (data.error) {
      errorMsg.value = data.error
    } else {
      if (isLogin.value) {
        // 登录成功，保存 token 和用户信息
        localStorage.setItem('token', data.token)
        localStorage.setItem('username', data.username)
        localStorage.setItem('user_id', data.user_id)
        router.push('/')
      } else {
        // 注册成功，切换到登录
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
  height: 80vh;
  font-family: sans-serif;
}

.form-box {
  width: 320px;
  padding: 30px;
  border: 1px solid #ddd;
  border-radius: 12px;
  text-align: center;
}

h2 {
  margin-bottom: 20px;
}

.form-item {
  margin-bottom: 12px;
}

.form-item input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  margin-top: 8px;
}

button:hover {
  background: #337ecc;
}

.switch {
  margin-top: 12px;
  color: #409eff;
  cursor: pointer;
  font-size: 13px;
}

.error {
  color: #f56c6c;
  font-size: 13px;
  margin-top: 8px;
}
</style>
