<template>
  <div class="sidebar" :class="{ open: open }">
    <div class="sidebar-header">
      <el-button type="primary" @click="newChat" class="new-chat-btn">
        + 新对话
      </el-button>
    </div>

    <div class="session-list">
      <div
        v-for="session in chatStore.sessions"
        :key="session.id"
        :class="['session-item', { active: session.id === chatStore.currentSessionId }]"
        @click="onSelectSession(session.id)"
      >
        <div class="session-title">{{ session.title }}</div>
        <el-button
          type="danger"
          size="small"
          @click.stop="chatStore.deleteSession(session.id)"
          class="delete-btn"
        >
          ×
        </el-button>
      </div>

      <div v-if="chatStore.sessions.length === 0" class="empty">
        暂无对话记录
      </div>
    </div>
  </div>

  <!-- 移动端抽屉遮罩（桌面隐藏） -->
  <div class="sidebar-mask" :class="{ open: open }" @click="$emit('close')"></div>
</template>

<script setup>
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()

defineProps({
  open: Boolean
})
const emit = defineEmits(['close'])

async function newChat() {
  await chatStore.createSession()
  emit('close')
}

async function onSelectSession(id) {
  await chatStore.switchSession(id)
  emit('close')
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100%;
  background: #fafafa;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #eee;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.new-chat-btn {
  width: 100%;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.session-item:hover {
  background: #f0f0f0;
}

.session-item.active {
  background: #ecf5ff;
}

.session-title {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
  padding: 4px 8px;
  font-size: 12px;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.empty {
  text-align: center;
  color: #999;
  font-size: 13px;
  padding: 20px;
}

/* 抽屉遮罩：桌面隐藏 */
.sidebar-mask {
  display: none;
}

/* ===== 移动端（<768px）：侧边栏变抽屉 ===== */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    z-index: 120;
    width: 260px;
    max-width: 80vw;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-mask {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 110;
    background: rgba(0, 0, 0, 0.45);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s ease;
  }

  .sidebar-mask.open {
    opacity: 1;
    pointer-events: auto;
  }

  /* 移动端没有 hover，删除按钮常显 */
  .delete-btn {
    opacity: 1;
  }
}
</style>
