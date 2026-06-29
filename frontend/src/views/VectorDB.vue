<template>
  <div class="vector-container">
    <div class="page-header">
      <h1>向量库管理</h1>
      <p class="subtitle">查看已存储的文档片段，用于 RAG 知识库问答</p>
    </div>

    <div class="stats-card">
      <div class="stat-item">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ total }}</div>
          <div class="stat-label">文档片段</div>
        </div>
      </div>
      <el-button @click="loadChunks" :icon="Refresh">刷新</el-button>
    </div>

    <div class="chunk-list">
      <div class="list-header">
        <h3>片段列表</h3>
      </div>

      <el-empty v-if="chunks.length === 0" description="向量库为空，上传文档后自动生成" />

      <div v-else class="chunk-items">
        <div v-for="(chunk, index) in chunks" :key="chunk.id" class="chunk-item">
          <div class="chunk-header">
            <el-tag size="small" type="primary">#{{ index + 1 }}</el-tag>
            <span class="chunk-id">{{ chunk.id }}</span>
          </div>
          <div class="chunk-content">{{ chunk.content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import api from '../api'

const chunks = ref([])
const total = ref(0)

async function loadChunks() {
  const res = await api.get('/rag/chunks')
  total.value = res.data.total
  chunks.value = res.data.chunks
}

onMounted(() => loadChunks())
</script>

<style scoped>
.vector-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 14px;
  color: #888;
  margin: 0;
}

.stats-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 24px;
  color: white;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  font-size: 32px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
}

.stat-label {
  font-size: 13px;
  opacity: 0.9;
}

.refresh-btn {
  padding: 10px 20px;
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: rgba(255,255,255,0.3);
}

.chunk-list {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e5e5;
  overflow: hidden;
}

.list-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e5e5;
}

.list-header h3 {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.empty {
  text-align: center;
  padding: 40px 20px;
  color: #888;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty p {
  font-size: 14px;
  margin: 0;
}

.chunk-items {
  padding: 12px;
  max-height: 600px;
  overflow-y: auto;
}

.chunk-item {
  padding: 16px;
  margin-bottom: 8px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.2s;
}

.chunk-item:last-child {
  margin-bottom: 0;
}

.chunk-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.chunk-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.chunk-index {
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  background: #ecf5ff;
  padding: 2px 8px;
  border-radius: 4px;
}

.chunk-id {
  font-size: 11px;
  color: #888;
  font-family: monospace;
}

.chunk-content {
  font-size: 13px;
  line-height: 1.6;
  color: #555;
  word-break: break-word;
  white-space: pre-wrap;
}
</style>
