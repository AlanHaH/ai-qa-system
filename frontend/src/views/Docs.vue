<template>
  <div class="docs-container">
    <h1>知识库管理</h1>

    <div class="upload-area">
      <input type="file" @change="handleFile" accept=".pdf,.txt,.md" />
      <button @click="upload" :disabled="!selectedFile">上传</button>
    </div>

    <div class="doc-list">
      <div v-for="doc in docs" :key="doc.id" class="doc-item">
        <span class="doc-name">{{ doc.filename }}</span>
        <span class="doc-time">{{ doc.created_at }}</span>
        <button class="delete-btn" @click="remove(doc.id)">删除</button>
      </div>
      <p v-if="docs.length === 0" class="empty">暂无文档</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const docs = ref([])
const selectedFile = ref(null)

// 加载文档列表
async function loadDocs() {
  const res = await fetch('http://127.0.0.1:8000/doc/list')
  docs.value = await res.json()
}

// 选择文件
function handleFile(e) {
  selectedFile.value = e.target.files[0]
}

// 上传文件
async function upload() {
  if (!selectedFile.value) return
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  const res = await fetch('http://127.0.0.1:8000/doc/upload', {
    method: 'POST',
    body: formData
  })
  const data = await res.json()
  if (data.error) {
    alert(data.error)
  } else {
    alert(data.message)
    selectedFile.value = null
    loadDocs()
  }
}

// 删除文档
async function remove(id) {
  if (!confirm('确定删除？')) return
  const res = await fetch(`http://127.0.0.1:8000/doc/${id}`, { method: 'DELETE' })
  const data = await res.json()
  alert(data.message)
  loadDocs()
}

onMounted(() => loadDocs())
</script>

<style scoped>
.docs-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
  font-family: sans-serif;
}

h1 {
  text-align: center;
}

.upload-area {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.upload-area button {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.upload-area button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.doc-list {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
}

.doc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.doc-item:last-child {
  border-bottom: none;
}

.doc-name {
  flex: 1;
}

.doc-time {
  color: #999;
  margin: 0 12px;
  font-size: 13px;
}

.delete-btn {
  padding: 4px 12px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty {
  text-align: center;
  color: #999;
}
</style>
