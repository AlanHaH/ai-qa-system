import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from './user'
import api from '../api'

export const useChatStore = defineStore('chat', () => {
  const userStore = useUserStore()

  // 所有对话会话（轻量列表，来自后端）
  const sessions = ref([])
  const currentSessionId = ref('')
  const messages = ref([])
  const loading = ref(false)
  const ready = ref(false)      // 数据是否已从后端加载完成
  const streaming = ref(false)  // 是否正在流式生成

  // 并发去重：避免 loadUserData / migrate 被多处同时触发
  let loadPromise = null
  let migratePromise = null

  // 用户专属的存储 key（仅用于旧数据迁移检测）
  function getStorageKey(key) {
    const userId = userStore.userId || 'guest'
    return `${key}_${userId}`
  }

  // 从未登录兜底：保留旧 localStorage 行为
  function loadFromLocalStorage() {
    sessions.value = JSON.parse(localStorage.getItem(getStorageKey('chat_sessions')) || '[]')
    currentSessionId.value = localStorage.getItem(getStorageKey('current_session_id')) || ''
    if (currentSessionId.value) {
      const session = sessions.value.find(s => s.id === currentSessionId.value)
      messages.value = session ? [...session.messages] : []
    } else {
      messages.value = []
    }
  }

  // 拉取单个会话的消息
  async function fetchMessages(sessionId) {
    const res = await api.get(`/session/${sessionId}`)
    messages.value = (res.data.messages || []).map(m => ({
      role: m.role,
      content: m.content,
      refs: m.refs || [],
      showRefs: true
    }))
  }

  // 初始化：迁移旧数据 + 拉取会话列表 + 恢复当前会话
  async function loadUserData() {
    if (loadPromise) return loadPromise
    loading.value = true
    loadPromise = (async () => {
      try {
        const userId = userStore.userId
        if (!userId) {
          loadFromLocalStorage()
          return
        }

        // 1) 迁移 localStorage 旧数据（失败不阻塞）
        await migrateLegacyData()

        // 2) 拉取会话列表
        const res = await api.get('/session/list')
        sessions.value = res.data || []

        // 3) 恢复当前会话：优先迁移后 localStorage 记录的 id，否则选最近一个
        const savedCurrent = localStorage.getItem(getStorageKey('current_session_id'))
        let target = null
        if (savedCurrent) {
          target = sessions.value.find(s => String(s.id) === String(savedCurrent))
        }
        if (!target && sessions.value.length > 0) target = sessions.value[0]

        if (target) {
          currentSessionId.value = target.id
          await fetchMessages(target.id)
        } else {
          currentSessionId.value = ''
          messages.value = []
        }
      } finally {
        loading.value = false
        ready.value = true
        loadPromise = null
      }
    })()
    return loadPromise
  }

  // 供页面 onMounted 等待初始化完成（子组件 onMounted 先于 App.vue 执行）
  function ensureLoaded() {
    if (ready.value) return Promise.resolve()
    if (loadPromise) return loadPromise
    return loadUserData()
  }

  // 创建新会话
  async function createSession() {
    if (streaming.value) { ElMessage.warning('回答生成中，请稍候'); return null }
    if (currentSessionId.value && messages.value.length > 0) {
      await saveCurrentSession()
    }

    const res = await api.post('/session', { title: '新对话', messages: [] })
    const session = res.data
    sessions.value.unshift(session)
    currentSessionId.value = session.id
    messages.value = []
    return session.id
  }

  // 保存当前会话（全量覆盖）
  async function saveCurrentSession() {
    if (!currentSessionId.value) return

    const index = sessions.value.findIndex(s => s.id === currentSessionId.value)
    const firstUserMsg = messages.value.find(m => m.role === 'user')
    const title = firstUserMsg
      ? firstUserMsg.content.substring(0, 30) + (firstUserMsg.content.length > 30 ? '...' : '')
      : '新对话'

    const payload = {
      title,
      messages: messages.value.map(m => ({
        role: m.role,
        content: m.content,
        refs: Array.isArray(m.refs) ? m.refs : []
      }))
    }

    try {
      const res = await api.put(`/session/${currentSessionId.value}`, payload)
      if (index !== -1) {
        sessions.value[index].title = res.data.title
        sessions.value[index].updated_at = res.data.updated_at
      }
    } catch (e) {
      console.error('保存会话失败：', e)
    }
  }

  // 切换会话
  async function switchSession(sessionId) {
    if (streaming.value) { ElMessage.warning('回答生成中，请稍候'); return }
    if (currentSessionId.value && currentSessionId.value !== sessionId && messages.value.length > 0) {
      await saveCurrentSession()
    }
    currentSessionId.value = sessionId
    messages.value = []
    await fetchMessages(sessionId)
  }

  // 删除会话
  async function deleteSession(sessionId) {
    if (streaming.value) { ElMessage.warning('回答生成中，请稍候'); return }
    await api.delete(`/session/${sessionId}`)
    sessions.value = sessions.value.filter(s => s.id !== sessionId)

    if (currentSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        await switchSession(sessions.value[0].id)
      } else {
        currentSessionId.value = ''
        messages.value = []
      }
    }
  }

  // 迁移 localStorage 旧数据（按 old_id 幂等）
  async function migrateLegacyData() {
    const key = getStorageKey('chat_sessions')
    const raw = localStorage.getItem(key)
    if (!raw) return null
    if (migratePromise) return migratePromise

    let legacy = []
    try {
      legacy = JSON.parse(raw)
    } catch {
      return null
    }
    if (!Array.isArray(legacy) || legacy.length === 0) {
      localStorage.removeItem(key)
      return null
    }

    migratePromise = (async () => {
      const payload = legacy.map(s => ({
        old_id: String(s.id),
        title: s.title || '新对话',
        messages: (s.messages || []).map(m => ({
          role: m.role,
          content: m.content,
          refs: Array.isArray(m.refs) ? m.refs : []
        }))
      }))
      try {
        const res = await api.post('/session/migrate', { sessions: payload })
        const mapping = res.data.mapping || {}

        // 把当前会话 id 映射到新 id，再清理旧数据
        const oldCurrent = localStorage.getItem(getStorageKey('current_session_id'))
        if (oldCurrent && mapping[oldCurrent]) {
          localStorage.setItem(getStorageKey('current_session_id'), String(mapping[oldCurrent]))
        }
        localStorage.removeItem(key)
        return mapping
      } catch (e) {
        console.error('迁移失败，保留 localStorage 数据待重试', e)
        return null
      } finally {
        migratePromise = null
      }
    })()
    return migratePromise
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

  // 更新 AI 消息内容（流式追加）
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
    loading,
    ready,
    streaming,
    currentSessionTitle,
    loadUserData,
    ensureLoaded,
    createSession,
    saveCurrentSession,
    switchSession,
    deleteSession,
    migrateLegacyData,
    addUserMessage,
    addAiMessage,
    updateAiContent,
    setRefs,
    toggleRefs,
    clearMessages
  }
})
