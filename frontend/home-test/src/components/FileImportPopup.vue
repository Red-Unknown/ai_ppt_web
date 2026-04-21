<template>
  <div class="file-import-popup-overlay" @click.self="$emit('close')">
    <div class="popup-content">
      <h3 class="popup-title">{{ title }}</h3>
      
      <div class="file-upload-area" 
           :class="{ 'has-file': selectedFile, 'drag-over': isDragOver }"
           @dragover.prevent="handleDragOver"
           @dragleave="handleDragLeave"
           @drop.prevent="handleDrop"
           @click="triggerFileInput"
      >
        <input 
          type="file" 
          class="file-input" 
          ref="fileInput"
          @change="handleFileChange"
          :accept="acceptTypes"
          :multiple="multiple"
        />
        
        <div class="upload-hint" v-if="!selectedFile">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          <p>点击或拖拽文件到此处</p>
          <p class="hint-text">{{ hintText }}</p>
        </div>
        
        <div class="file-preview" v-else>
          <div class="file-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
          </div>
          <div class="file-details">
            <span class="file-name">{{ selectedFile.name }}</span>
            <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
          </div>
          <button class="remove-file-btn" @click.stop="removeFile">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 上传进度 -->
      <div class="upload-progress" v-if="uploadProgress > 0 && uploadProgress < 100">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <span class="progress-text">{{ uploadProgress }}%</span>
      </div>
      
      <!-- 错误提示 -->
      <div class="error-message" v-if="errorMessage">
        {{ errorMessage }}
      </div>
      
      <div class="popup-actions">
        <button class="btn-cancel" @click="$emit('close')">取消</button>
        <button 
          class="btn-confirm" 
          @click="handleImport"
          :disabled="!selectedFile || isUploading"
        >
          {{ isUploading ? '导入中...' : '导入' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    default: '导入文件'
  },
  acceptTypes: {
    type: String,
    default: '.ppt,.pptx,.pdf,.jpg,.jpeg,.png'
  },
  multiple: {
    type: Boolean,
    default: false
  },
  hintText: {
    type: String,
    default: '支持 PPT、PDF、图片文件'
  },
  maxFileSize: {
    type: Number,
    default: 100 * 1024 * 1024 // 100MB
  }
})

// Emits
const emit = defineEmits(['close', 'select', 'import', 'error'])

// 状态
const fileInput = ref(null)
const selectedFile = ref(null)
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')

// 方法
const triggerFileInput = () => {
  fileInput.value.click()
}

const handleDragOver = (event) => {
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  const files = event.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const handleFileChange = (event) => {
  const files = event.target.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const processFile = (file) => {
  // 清除错误
  errorMessage.value = ''
  
  // 检查文件类型
  const acceptTypesArray = props.acceptTypes.split(',').map(t => t.trim())
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
  const isValidType = acceptTypesArray.some(type => {
    const ext = type.toLowerCase()
    return fileExtension === ext || file.name.toLowerCase().endsWith(ext)
  })
  
  if (!isValidType) {
    errorMessage.value = `不支持的文件类型：${fileExtension}。请上传 ${props.hintText}`
    emit('error', { type: 'invalid_type', message: errorMessage.value })
    return
  }
  
  // 检查文件大小
  if (file.size > props.maxFileSize) {
    errorMessage.value = `文件过大。最大支持 ${formatFileSize(props.maxFileSize)}`
    emit('error', { type: 'file_too_large', message: errorMessage.value })
    return
  }
  
  selectedFile.value = file
  emit('select', file)
}

const removeFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  errorMessage.value = ''
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const handleImport = async () => {
  if (!selectedFile.value) return
  
  isUploading.value = true
  uploadProgress.value = 0
  errorMessage.value = ''
  
  try {
    // 创建FormData
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('course_id', 'course_mechanics_001')
    formData.append('school_id', 'SCH001')
    
    // 使用XMLHttpRequest监听上传进度
    const response = await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100)
          uploadProgress.value = percentComplete
        }
      })
      
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText)
            resolve({ ok: true, data })
          } catch (error) {
            reject(new Error('响应格式错误'))
          }
        } else {
          try {
            const errorData = JSON.parse(xhr.responseText)
            reject(new Error(errorData.detail || `上传失败: ${xhr.status}`))
          } catch (error) {
            reject(new Error(`上传失败: ${xhr.status}`))
          }
        }
      })
      
      xhr.addEventListener('error', () => {
        reject(new Error('网络错误，请检查网络连接'))
      })
      
      xhr.addEventListener('abort', () => {
        reject(new Error('上传被取消'))
      })
      
      xhr.open('POST', 'http://127.0.0.1:8001/api/v1/lesson/upload')
      xhr.send(formData)
    })
    
    emit('import', {
      file: selectedFile.value,
      response: response.data
    })
    
    // 关闭弹窗
    emit('close')
  } catch (error) {
    errorMessage.value = error.message || '导入失败，请重试'
    emit('error', { type: 'upload_error', message: errorMessage.value })
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.file-import-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.popup-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 480px;
  padding: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.popup-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 20px 0;
  text-align: center;
}

.file-upload-area {
  position: relative;
  border: 2px dashed #E0E0E0;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
}

.file-upload-area:hover {
  border-color: #3285FA;
  background: #f0f7ff;
}

.file-upload-area.drag-over {
  border-color: #3285FA;
  background: #e6f0ff;
  transform: scale(1.02);
}

.file-upload-area.has-file {
  border-style: solid;
  border-color: #3285FA;
  background: #f0f7ff;
  padding: 20px;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 1;
}

.upload-hint {
  pointer-events: none;
}

.upload-hint svg {
  width: 48px;
  height: 48px;
  color: #999;
  margin-bottom: 12px;
}

.upload-hint p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.upload-hint .hint-text {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.file-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 2;
}

.file-icon {
  width: 48px;
  height: 48px;
  background: #3285FA;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.file-details {
  flex: 1;
  text-align: left;
  overflow: hidden;
}

.file-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.remove-file-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #ff4757;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.remove-file-btn:hover {
  background: #ff3344;
  transform: scale(1.1);
}

.remove-file-btn svg {
  width: 16px;
  height: 16px;
}

.upload-progress {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3285FA, #5da3ff);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #666;
  font-weight: 500;
  min-width: 40px;
  text-align: right;
}

.error-message {
  margin-top: 12px;
  padding: 10px 12px;
  background: #fff3f3;
  border: 1px solid #ffcdd9;
  border-radius: 8px;
  color: #d32f2f;
  font-size: 13px;
}

.popup-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: white;
  color: #666;
  border: 1px solid #ddd;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

.btn-confirm {
  background: #3285FA;
  color: white;
  border: none;
}

.btn-confirm:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(50, 133, 250, 0.3);
}

.btn-confirm:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>