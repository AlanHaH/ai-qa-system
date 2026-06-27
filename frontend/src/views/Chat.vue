<template>
  <div class="chat-container">
    <h1>AI 学习助手</h1>

    <div class="chat-box">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="bubble">{{ msg.content }}</div>
      </div>
    </div>

    <div class="input-area">
      <input
        v-model="question"
        @keyup.enter="send"
        placeholder="输入你的问题..."
      />
      <button @click="send">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const question = ref('')
const messages = ref([])

// 页面加载时获取历史记录
onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/chat/history')
    const data = await res.json()
    // 数据库返回的是倒序（最新在前），需要反转成正序
    data.reverse().forEach(record => {
      messages.value.push({ role: 'user', content: record.question })
      messages.value.push({ role: 'ai', content: record.answer })
    })
  } catch (err) {
    console.log('加载历史记录失败：', err)
  }
})

async function send() {
  if (!question.value.trim()) return

  const q = question.value
  messages.value.push({ role: 'user', content: q })
  question.value = ''

  // 先添加一个空的 AI 消息，后续逐字填充
  const aiIndex = messages.value.length
  messages.value.push({ role: 'ai', content: '' })

  try {
    const res = await fetch('http://127.0.0.1:8000/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    })

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''  // 缓存未处理完的数据

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      // 按行分割处理
      const lines = buffer.split('\n')
      buffer = lines.pop()  // 最后一行可能不完整，留到下次处理

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const content = line.slice(6).trim()
          if (content === '[DONE]') return
          if (content) {
            messages.value[aiIndex].content += content
          }
        }
      }
    }
  } catch (err) {
    messages.value[aiIndex].content = '请求失败：' + err.message
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
  font-family: sans-serif;
}

h1 {
  text-align: center;
}

.chat-box {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  height: 400px;
  overflow-y: auto;
  margin-bottom: 16px;
  background: #fafafa;
}

.message {
  margin-bottom: 12px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.ai {
  justify-content: flex-start;
}

.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 12px;
}

.message.user .bubble {
  background: #409eff;
  color: white;
}

.message.ai .bubble {
  background: #e5e5ea;
  color: black;
}

.input-area {
  display: flex;
  gap: 8px;
}

.input-area input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.input-area button {
  padding: 10px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.input-area button:hover {
  background: #337ecc;
}
</style>
