<template>
  <div class="vector-container">
    <h1>向量库管理</h1>

    <div class="stats">
      <span>共 <strong>{{ total }}</strong> 个文档片段</span>
      <button @click="loadChunks">刷新</button>
    </div>

    <div class="chunk-list">
      <div v-for="chunk in chunks" :key="chunk.id" class="chunk-item">
        <div class="chunk-id">{{ chunk.id }}</div>
        <div class="chunk-content">{{ chunk.content }}</div>
      </div>
      <p v-if="chunks.length === 0" class="empty">暂无数据</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const chunks = ref([])
const total = ref(0)

async function loadChunks() {
  const res = await fetch('http://127.0.0.1:8000/rag/chunks')
  const data = await res.json()
  total.value = data.total
  chunks.value = data.chunks
}

onMounted(() => loadChunks())
</script>

<style scoped>
.vector-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: sans-serif;
}

h1 {
  text-align: center;
}

.stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
}

.stats button {
  padding: 6px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chunk-list {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  max-height: 600px;
  overflow-y: auto;
}

.chunk-item {
  padding: 12px;
  margin-bottom: 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  background: #fafafa;
}

.chunk-item:last-child {
  margin-bottom: 0;
}

.chunk-id {
  font-size: 12px;
  color: #409eff;
  margin-bottom: 8px;
  font-family: monospace;
}

.chunk-content {
  font-size: 13px;
  line-height: 1.6;
  color: #333;
  word-break: break-all;
}

.empty {
  text-align: center;
  color: #999;
}
</style>
