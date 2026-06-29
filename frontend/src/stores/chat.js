import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'

export const useChatStore = defineStore('chat', () => {
  const userStore = useUserStore()
  
  // 获取用户专属的存储 key
  function getStorageKey(key) {
    const userId = userStore.userId || 'guest'
    return `${key}_${userId}`
  }

  // 所有对话会话
  const sessions = ref([])
  const currentSessionId = ref('')
  const messages = ref([])

  // 加载用户数据
  function loadUserData() {
    const userId = userStore.userId || 'guest'
    sessions.value = JSON.parse(localStorage.getItem(getStorageKey('chat_sessions')) || '[]')
    currentSessionId.value = localStorage.getItem(getStorageKey('current_session_id')) || ''
    
    // 加载当前会话的消息
    if (currentSessionId.value) {
      const session = sessions.value.find(s => s.id === currentSessionId.value)
      messages.value = session ? [...session.messages] : []
    } else {
      messages.value = []
    }
  }

  // 保存到 localStorage
  function saveSessions() {
    localStorage.setItem(getStorageKey('chat_sessions'), JSON.stringify(sessions.value))
    localStorage.setItem(getStorageKey('current_session_id'), currentSessionId.value)
  }

  // 创建新会话
  function createSession() {
    if (currentSessionId.value && messages.value.length > 0) {
      saveCurrentSession()
    }
    
    const id = Date.now().toString()
    const session = {
      id,
      title: '新对话',
      messages: [],
      createdAt: new Date().toISOString()
    }
    sessions.value.unshift(session)
    currentSessionId.value = id
    messages.value = []
    saveSessions()
    return id
  }

  // 保存当前会话
  function saveCurrentSession() {
    if (!currentSessionId.value) return
    
    const index = sessions.value.findIndex(s => s.id === currentSessionId.value)
    if (index !== -1) {
      const firstUserMsg = messages.value.find(m => m.role === 'user')
      sessions.value[index].title = firstUserMsg 
        ? firstUserMsg.content.substring(0, 30) + (firstUserMsg.content.length > 30 ? '...' : '')
        : '新对话'
      sessions.value[index].messages = [...messages.value]
      saveSessions()
    }
  }

  // 切换会话
  function switchSession(sessionId) {
    if (currentSessionId.value && messages.value.length > 0) {
      saveCurrentSession()
    }
    
    currentSessionId.value = sessionId
    const session = sessions.value.find(s => s.id === sessionId)
    messages.value = session ? [...session.messages] : []
    saveSessions()
  }

  // 删除会话
  function deleteSession(sessionId) {
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
    
    if (currentSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        switchSession(sessions.value[0].id)
      } else {
        currentSessionId.value = ''
        messages.value = []
      }
    }
    saveSessions()
  }

  // 添加用户消息
  function addUserMessage(content) {
    messages.value.push({ role: 'user', content })
  }

  // 添加 AI 消息
  function addAiMessage() {
    const index = messages.value.length
    messages.value.push({ role: 'ai', content: '', refs: [], showRefs: true })
    return index
  }

  // 更新 AI 消息内容
  function updateAiContent(index, content) {
    if (messages.value[index]) {
      messages.value[index].content += content
    }
  }

  // 设置引用片段
  function setRefs(index, chunks) {
    if (messages.value[index]) {
      messages.value[index].refs = chunks
    }
  }

  // 切换引用片段显示
  function toggleRefs(index) {
    if (messages.value[index]) {
      messages.value[index].showRefs = !messages.value[index].showRefs
    }
  }

  // 加载历史记录
  function loadHistory(historyList) {
    messages.value = []
    historyList.forEach(record => {
      messages.value.push({ role: 'user', content: record.question })
      messages.value.push({ role: 'ai', content: record.answer, refs: [], showRefs: true })
    })
  }

  // 清空消息
  function clearMessages() {
    messages.value = []
  }

  // 当前会话标题
  const currentSessionTitle = computed(() => {
    const session = sessions.value.find(s => s.id === currentSessionId.value)
    return session ? session.title : '新对话'
  })

  return {
    sessions,
    currentSessionId,
    messages,
    currentSessionTitle,
    loadUserData,
    createSession,
    saveCurrentSession,
    switchSession,
    deleteSession,
    addUserMessage,
    addAiMessage,
    updateAiContent,
    setRefs,
    toggleRefs,
    loadHistory,
    clearMessages
  }
})
