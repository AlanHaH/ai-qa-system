<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1>AI 学习助手</h1>
      <p class="subtitle">基于大模型与 RAG 的智能问答系统</p>
    </div>

    <div class="chat-box" ref="chatBox">
      <div class="welcome" v-if="chatStore.messages.length === 0">
        <div class="welcome-icon">问</div>
        <h2>你好，我是 AI 学习助手</h2>
        <p>有什么问题可以问我，或者开启知识库问答获取更精准的回答</p>
      </div>

      <div
        v-for="(msg, index) in chatStore.messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="avatar">{{ msg.role === 'user' ? userInitial : '问' }}</div>
        <div class="bubble-wrapper">
          <!-- 引用片段 -->
          <div v-if="msg.refs && msg.refs.length > 0" class="references">
            <div class="refs-header" @click="chatStore.toggleRefs(index)">
              引用了 {{ msg.refs.length }} 个文档片段
              <span class="toggle-icon">{{ msg.showRefs ? '▼' : '▶' }}</span>
            </div>
            <div v-show="msg.showRefs" class="refs-list">
              <div v-for="(ref, i) in msg.refs" :key="i" class="ref-item">
                <span class="ref-index">#{{ i + 1 }}</span>
                <div class="ref-text">
                  <div v-if="typeof ref === 'object' && ref.filename" class="ref-filename">
                    来自《{{ ref.filename }}》
                  </div>
                  <div class="ref-content">{{ typeof ref === 'string' ? ref : ref.content }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="bubble">
            <!-- 用户消息：纯文本 -->
            <template v-if="msg.role === 'user'">{{ msg.content }}</template>
            <!-- 正在流式生成的 AI 消息：纯文本，避免 markdown 符号闪烁 -->
            <template v-else-if="chatStore.streaming && index === chatStore.messages.length - 1">
              <template v-if="msg.content">{{ msg.content }}</template>
              <div v-else class="typing-indicator" aria-label="正在输入">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </template>
            <!-- 已完成的 AI 消息：渲染 markdown -->
            <div v-else class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </div>
      </div>

      <div v-if="webSearchStatus" class="searching-tip">{{ webSearchStatus }}</div>
    </div>

    <div class="input-area">
      <div class="option-row">
        <el-checkbox v-model="useRAG" @change="v => { if (v) useWebSearch = false }">知识库问答</el-checkbox>
        <el-switch
          v-model="useWebSearch"
          active-text="联网搜索"
          @change="v => { if (v) useRAG = false }"
        />
      </div>
      <div class="input-wrapper">
        <el-input
          v-model="question"
          @keyup.enter="send"
          :placeholder="useRAG ? '基于知识库回答...' : useWebSearch ? '联网搜索回答...' : '输入你的问题...'"
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useChatStore } from '../stores/chat'
import { useUserStore } from '../stores/user'
import { renderMarkdown } from '../utils/markdown'

const question = ref('')
const useRAG = ref(false)
const useWebSearch = ref(false)
const webSearchStatus = ref('')

// 后端地址（部署时由 VITE_API_BASE 注入，本地默认直连）
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const chatBox = ref(null)
const chatStore = useChatStore()
const userStore = useUserStore()

// 用户头像首字母
const userInitial = computed(() => {
  const name = userStore.username || '我'
  return name.charAt(0).toUpperCase()
})

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatBox.value) {
      chatBox.value.scrollTop = chatBox.value.scrollHeight
    }
  })
}

// 页面加载时：等待会话初始化完成
onMounted(async () => {
  await chatStore.ensureLoaded()

  // 如果已有消息，不重新加载
  if (chatStore.messages.length > 0) {
    scrollToBottom()
    return
  }

  // 如果没有当前会话，创建新会话
  if (!chatStore.currentSessionId) {
    await chatStore.createSession()
  }
  scrollToBottom()
})

async function send() {
  if (!question.value.trim()) return
  chatStore.streaming = true

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
    const res = await fetch(`${API_BASE}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      body: JSON.stringify({ question: q, history: history, use_web_search: useWebSearch.value })
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

          // 检查是否是引用片段 / 联网搜索状态 / 降级提示
          try {
            const data = JSON.parse(content)
            if (data.type === 'references') {
              chatStore.setRefs(aiIndex, data.chunks)
              scrollToBottom()
              continue
            }
            // 联网搜索状态事件
            if (data.type === 'web_search') {
              if (data.phase === 'thinking') {
                webSearchStatus.value = '正在分析是否需要联网搜索...'
              } else if (data.phase === 'searching') {
                webSearchStatus.value = `正在联网搜索：${data.query}...`
              }
              scrollToBottom()
              continue
            }
            // 降级提示事件
            if (data.type === 'notice') {
              ElMessage.warning(data.message)
              continue
            }
          } catch {
            // 不是 JSON，正常文本
          }

          if (content) {
            webSearchStatus.value = ''
            chatStore.updateAiContent(aiIndex, content)
            scrollToBottom()
          }
        }
      }
    }
  } catch (err) {
    chatStore.updateAiContent(aiIndex, '请求失败：' + err.message)
  } finally {
    webSearchStatus.value = ''
    // 保存会话
    await chatStore.saveCurrentSession()
    chatStore.streaming = false
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px;
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
  border-radius: 12px;
  padding: 16px;
  overflow-y: auto;
  background: #f5f7fa;
  margin-bottom: 16px;
  /* 滚动条：固定在右侧、细窄美观、预留空间防内容抖动 */
  scrollbar-width: thin;
  scrollbar-color: #c1c7d0 transparent;
  scrollbar-gutter: stable;
}

.chat-box::-webkit-scrollbar {
  width: 6px;
}

.chat-box::-webkit-scrollbar-track {
  background: transparent;
}

.chat-box::-webkit-scrollbar-thumb {
  background: #c1c7d0;
  border-radius: 3px;
}

.chat-box::-webkit-scrollbar-thumb:hover {
  background: #a8b0bd;
}

.welcome {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.welcome-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 16px;
  border-radius: 14px;
  background: #409eff;
  color: #fff;
  font-size: 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
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
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 600;
  flex-shrink: 0;
}

.message.user .avatar {
  background: #409eff;
  color: #fff;
}

.message.ai .avatar {
  background: #ecf5ff;
  color: #409eff;
}

.bubble-wrapper {
  max-width: 85%;
}

.message.user .bubble-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 16px;
  line-height: 1.7;
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
  border-top-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* 等待大模型回复的加载动画 */
.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #409eff;
  animation: typing-bounce 1.2s infinite ease-in-out;
}

.typing-indicator .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-bounce {
  0%, 80%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  40% {
    transform: translateY(-5px);
    opacity: 1;
  }
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

.ref-text {
  flex: 1;
  min-width: 0;
}

.ref-filename {
  font-size: 12px;
  color: #409eff;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.option-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 4px;
}

.searching-tip {
  padding: 8px 12px;
  font-size: 13px;
  color: #909399;
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

.input-wrapper :deep(.el-input) {
  flex: 1;
}

.input-wrapper button:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}
</style>

<!-- Markdown 渲染样式（非 scoped：v-html 注入的内容不受 scoped 影响） -->
<style>
.markdown-body {
  font-size: 16px;
  line-height: 1.7;
  word-break: break-word;
}

.markdown-body > *:first-child { margin-top: 0 !important; }
.markdown-body > *:last-child { margin-bottom: 0 !important; }

.markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 {
  font-weight: 600;
  color: #1a1a1a;
  margin: 12px 0 6px;
  line-height: 1.4;
}
.markdown-body h1 { font-size: 19px; }
.markdown-body h2 { font-size: 18px; }

.markdown-body p { margin: 6px 0; }

.markdown-body ul, .markdown-body ol { margin: 6px 0; padding-left: 22px; }
.markdown-body li { margin: 3px 0; }

.markdown-body strong { font-weight: 600; }
.markdown-body em { font-style: italic; }

.markdown-body a { color: #409eff; text-decoration: none; }
.markdown-body a:hover { text-decoration: underline; }

.markdown-body hr { border: none; border-top: 1px solid #e5e5e5; margin: 12px 0; }

.markdown-body blockquote {
  margin: 8px 0;
  padding: 4px 12px;
  border-left: 3px solid #409eff;
  background: #f5f7fa;
  color: #666;
}

.markdown-body code {
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
  background: #f5f5f5;
  padding: 1px 5px;
  border-radius: 4px;
  color: #d14;
}

.markdown-body pre {
  background: #f8f9fa;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
}
.markdown-body pre code {
  background: transparent;
  padding: 0;
  color: inherit;
  font-size: 14px;
  line-height: 1.5;
}

.markdown-body table { border-collapse: collapse; margin: 8px 0; font-size: 14px; width: 100%; }
.markdown-body th, .markdown-body td { border: 1px solid #e5e5e5; padding: 6px 10px; text-align: left; }
.markdown-body th { background: #f5f7fa; font-weight: 600; }
</style>
