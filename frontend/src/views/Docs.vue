<template>
  <div class="docs-container">
    <div class="page-header">
      <h1>知识库管理</h1>
      <p class="subtitle">上传学习资料，AI 可以基于这些资料回答问题</p>
    </div>

    <div class="upload-card">
      <div class="upload-icon">📄</div>
      <div class="upload-info">
        <h3>上传文档</h3>
        <p>支持 PDF、TXT、MD 格式，最大 10MB</p>
      </div>
      <div class="upload-actions">
        <el-upload
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFile"
          accept=".pdf,.txt,.md"
        >
          <el-button :disabled="uploading">选择文件</el-button>
        </el-upload>
        <el-button type="primary" @click="upload" :disabled="!selectedFile" :loading="uploading">
          {{ uploading ? '上传中...' : (selectedFile ? '上传 ' + selectedFile.name : '上传') }}
        </el-button>
      </div>
    </div>

    <div class="doc-list">
      <div class="list-header">
        <h3>已上传文档</h3>
        <el-tag type="info">{{ docs.length }} 个文档</el-tag>
      </div>

      <el-empty v-if="docs.length === 0" description="暂无文档，上传一个试试" />

      <div v-else class="doc-items">
        <div v-for="doc in docs" :key="doc.id" class="doc-item">
          <div class="doc-icon">📎</div>
          <div class="doc-info">
            <div class="doc-name">{{ doc.filename }}</div>
            <div class="doc-time">{{ doc.created_at }}</div>
          </div>
          <el-button type="danger" size="small" @click="remove(doc.id)">删除</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const docs = ref([])
const selectedFile = ref(null)
const uploading = ref(false)

// 加载文档列表
async function loadDocs() {
  const res = await api.get('/doc/list')
  docs.value = res.data
}

// 选择文件
function handleFile(e) {
  selectedFile.value = e.raw
}

// 上传文件
async function upload() {
  if (!selectedFile.value) return
  uploading.value = true

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await api.post('/doc/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000
    })
    const data = res.data
    if (data.error) {
      ElMessage.error(data.error)
    } else {
      ElMessage.success(data.message)
      selectedFile.value = null
      loadDocs()
    }
  } catch (err) {
    ElMessage.error('上传失败：' + err.message)
  } finally {
    uploading.value = false
  }
}

// 删除文档
async function remove(id) {
  try {
    await ElMessageBox.confirm('确定删除该文档？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const res = await api.delete(`/doc/${id}`)
    ElMessage.success(res.data.message)
    loadDocs()
  } catch {
    // 用户点了取消
  }
}

onMounted(() => loadDocs())
</script>

<style scoped>
.docs-container {
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

.upload-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border: 2px dashed #e5e5e5;
  border-radius: 12px;
  margin-bottom: 24px;
  transition: border-color 0.2s;
}

.upload-card:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 36px;
}

.upload-info {
  flex: 1;
}

.upload-info h3 {
  font-size: 16px;
  color: #333;
  margin: 0 0 4px 0;
}

.upload-info p {
  font-size: 13px;
  color: #888;
  margin: 0;
}

.upload-actions {
  display: flex;
  gap: 8px;
}

.doc-list {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e5e5;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e5e5;
}

.list-header h3 {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.doc-items {
  padding: 8px;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.doc-item:hover {
  background: #f5f7fa;
}

.doc-icon {
  font-size: 24px;
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-time {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
}
</style>
