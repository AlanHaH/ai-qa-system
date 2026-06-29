<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1>AI 学习助手</h1>
      <p class="subtitle">基于大模型与 RAG 的智能问答系统</p>
    </div>

    <div class="chat-box" ref="chatBox">
      <div class="welcome" v-if="chatStore.messages.length === 0">
        <div class="welcome-icon">🤖</div>
        <h2>你好，我是 AI 学习助手</h2>
        <p>有什么问题可以问我，或者开启知识库问答获取更精准的回答</p>
      </div>

      <div
        v-for="(msg, index) in chatStore.messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="bubble-wrapper">
          <!-- 引用片段 -->
          <div v-if="msg.refs && msg.refs.length > 0" class="references">
            <div class="refs-header" @click="chatStore.toggleRefs(index)">
              📚 引用了 {{ msg.refs.length }} 个文档片段
              <span class="toggle-icon">{{ msg.showRefs ? '▼' : '▶' }}</span>
            </div>
            <div v-show="msg.showRefs" class="refs-list">
              <div v-for="(ref, i) in msg.refs" :key="i" class="ref-item">
                <span class="ref-index">#{{ i + 1 }}</span>
                <span class="ref-content">{{ ref }}</span>
              </div>
            </div>
          </div>
          <div class="bubble">{{ msg.content }}</div>
        </div>
      </div>
    </div>

    <div class="input-area">
      <el-checkbox v-model="useRAG">知识库问答</el-checkbox>
      <div class="input-wrapper">
        <el-input
          v-model="question"
          @keyup.enter="send"
          :placeholder="useRAG ? '基于知识库回答...' : '输入你的问题...'"
          size="large"
        />
        <el-button type="primary" @click="send" :disabled="!question.trim()" size="large">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useChatStore } from '../stores/chat'
import api from '../api'

const question = ref('')
const useRAG = ref(false)
const chatBox = ref(null)
const chatStore = useChatStore()

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatBox.value) {
      chatBox.value.scrollTop = chatBox.value.scrollHeight
    }
  })
}

// 页面加载时获取历史记录
onMounted(async () => {
  // 如果已有消息，不重新加载
  if (chatStore.messages.length > 0) {
    scrollToBottom()
    return
  }

  // 如果没有当前会话，创建新会话
  if (!chatStore.currentSessionId) {
    chatStore.createSession()
  }

  try {
    const res = await api.get('/chat/history')
    chatStore.loadHistory(res.data.reverse())
    scrollToBottom()
  } catch (err) {
    console.log('加载历史记录失败：', err)
  }
})

async function send() {
  if (!question.value.trim()) return

  const q = question.value
  chatStore.addUserMessage(q)
  question.value = ''
  scrollToBottom()

  const aiIndex = chatStore.addAiMessage()

  try {
    const url = useRAG.value ? '/rag/chat' : '/chat/stream'

    // 构建历史记录（最近10条）
    const history = chatStore.messages
      .slice(0, -1)
      .filter(msg => msg.content)
      .slice(-10)
      .map(msg => ({
        role: msg.role === 'ai' ? 'assistant' : msg.role,
        content: msg.content
      }))

    const token = localStorage.getItem('token')
    const res = await fetch(`http://127.0.0.1:8000${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      body: JSON.stringify({ question: q, history: history })
    })

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const content = line.slice(6).trim()
          if (content === '[DONE]') return

          // 检查是否是引用片段
          try {
            const data = JSON.parse(content)
            if (data.type === 'references') {
              chatStore.setRefs(aiIndex, data.chunks)
              scrollToBottom()
              continue
            }
          } catch {
            // 不是 JSON，正常文本
          }

          if (content) {
            chatStore.updateAiContent(aiIndex, content)
            scrollToBottom()
          }
        }
      }
    }
  } catch (err) {
    chatStore.updateAiContent(aiIndex, '请求失败：' + err.message)
  } finally {
    // 保存会话
    chatStore.saveCurrentSession()
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.chat-header {
  text-align: center;
  margin-bottom: 20px;
}

.chat-header h1 {
  font-size: 24px;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 13px;
  color: #888;
  margin: 0;
}

.chat-box {
  flex: 1;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 20px;
  overflow-y: auto;
  background: #f8f9fa;
  margin-bottom: 16px;
}

.welcome {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome h2 {
  font-size: 20px;
  color: #333;
  margin: 0 0 8px 0;
}

.welcome p {
  font-size: 14px;
  margin: 0;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  flex-shrink: 0;
}

.bubble-wrapper {
  max-width: 70%;
}

.message.user .bubble-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.message.user .bubble {
  background: #409eff;
  color: white;
  border-top-right-radius: 4px;
}

.message.ai .bubble {
  background: #fff;
  color: #333;
  border: 1px solid #e5e5e5;
  border-top-left-radius: 4px;
}

/* 引用片段样式 */
.references {
  margin-bottom: 8px;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  overflow: hidden;
}

.refs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  font-size: 12px;
  color: #666;
  background: #f5f7fa;
  cursor: pointer;
  user-select: none;
}

.refs-header:hover {
  background: #ecf5ff;
}

.toggle-icon {
  font-size: 10px;
}

.refs-list {
  padding: 8px;
}

.ref-item {
  display: flex;
  gap: 8px;
  padding: 6px 8px;
  margin-bottom: 4px;
  background: #fafafa;
  border-radius: 4px;
  font-size: 12px;
}

.ref-item:last-child {
  margin-bottom: 0;
}

.ref-index {
  color: #409eff;
  font-weight: 600;
  flex-shrink: 0;
}

.ref-content {
  color: #666;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  line-clamp: 3;
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-wrapper {
  display: flex;
  gap: 8px;
}

.input-wrapper button:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}
</style>
