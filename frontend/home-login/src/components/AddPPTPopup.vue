<template>
  <div class="add-ppt-popup" @click.self="$emit('close')">
    <div class="popup-content">
      <!-- 弹窗标题 -->
      <div class="popup-header">
        <h2 class="popup-title">添加PPT</h2>
        <button class="close-button" @click="$emit('close')">
          <svg class="close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      
      <!-- 导航栏 -->
      <div class="nav-tabs">
        <button 
          class="nav-tab" 
          :class="{ active: activeTab === 'cloud' }"
          @click="activeTab = 'cloud'"
        >
          网盘导入
        </button>
        <button 
          class="nav-tab" 
          :class="{ active: activeTab === 'local' }"
          @click="activeTab = 'local'"
        >
          本地导入
        </button>
      </div>
      
      <!-- 内容区域 -->
      <div class="tab-content">
        <!-- 网盘导入 -->
        <div v-if="activeTab === 'cloud'" class="cloud-import">
          <!-- 搜索功能 -->
          <div class="search-section">
            <div class="search-box">
              <span class="search-label">搜索</span>
              <input 
                v-model="searchKeyword" 
                type="text" 
                class="search-input"
                placeholder="搜索文件名"
                @input="handleSearch"
              />
              <button class="search-button">
                <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              </button>
            </div>
            
            <!-- 文件统计信息 -->
            <div class="file-stats">
              已选 {{ selectedFiles.length }}个，共 {{ filteredFiles.length }}个
            </div>
          </div>
          
          <!-- 文件列表 -->
          <div class="file-list">
            <div class="file-list-header">
              <div class="list-header-item checkbox-column">
                <input 
                  type="checkbox" 
                  v-model="selectAll"
                  @change="handleSelectAll"
                />
              </div>
              <div class="list-header-item name-column">文件名</div>
              <div class="list-header-item size-column">大小</div>
              <div class="list-header-item time-column">创建时间</div>
            </div>
            
            <div class="file-list-body">
              <div 
                v-for="file in filteredFiles" 
                :key="file.id"
                class="file-item"
              >
                <div class="file-item-cell checkbox-column">
                  <input 
                    type="checkbox" 
                    :checked="selectedFiles.includes(file.id)"
                    @change="handleCloudFileSelect(file.id)"
                  />
                </div>
                <div class="file-item-cell name-column">{{ file.name }}</div>
                <div class="file-item-cell size-column">{{ file.size }}</div>
                <div class="file-item-cell time-column">{{ file.createTime }}</div>
              </div>
              
              <div v-if="filteredFiles.length === 0" class="empty-state">
                暂无文件
              </div>
            </div>
          </div>
        </div>
        
        <!-- 本地导入 -->
        <div v-else-if="activeTab === 'local'" class="local-import">
          <!-- 文件上传区域 -->
          <div 
            class="upload-area"
            @click="triggerFileInput"
            @dragover.prevent
            @drop.prevent="handleFileDrop"
          >
            <input 
              ref="fileInput" 
              type="file" 
              class="file-input"
              accept=".pptx,.pdf,.jpg"
              @change="handleLocalFileSelect"
            >
            <div class="upload-content">
              <div class="upload-icon">+</div>
              <p class="upload-text">点击或拖拽文件到此处</p>
            </div>
          </div>
          
          <!-- 上传规则 -->
          <div class="upload-rules">
            <h3 class="rules-title">上传规则</h3>
            <ul class="rules-list">
              <li class="rule-item">单次限制：单次只能上传1个文件</li>
              <li class="rule-item">大小限制：文件大小不超过1024M（1GB）</li>
              <li class="rule-item">支持格式：pptx、pdf、jpg</li>
            </ul>
          </div>
          
          <!-- 已选择文件 -->
          <div v-if="localFile" class="selected-file">
            <h3 class="selected-title">已选择文件</h3>
            <div class="file-info">
              <span class="file-name">{{ localFile.name }}</span>
              <span class="file-size">{{ formatFileSize(localFile.size) }}</span>
              <button class="remove-file" @click="removeLocalFile">
                <svg class="remove-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 底部操作区 -->
      <div class="popup-footer">
        <button class="cancel-button" @click="$emit('close')">
          取消
        </button>
        <button 
          class="confirm-button"
          :disabled="!canConfirm"
          @click="handleConfirm"
        >
          确定
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 状态
const activeTab = ref('cloud')
const searchKeyword = ref('')
const selectedFiles = ref([])
const selectAll = ref(false)
const localFile = ref(null)
const fileInput = ref(null)

// 模拟文件数据
const mockFiles = ref([
  { id: 1, name: 'PPT模板1.pptx', size: '10MB', createTime: '2026-03-01 10:00' },
  { id: 2, name: '产品演示.mp4', size: '150MB', createTime: '2026-03-02 14:30' },
  { id: 3, name: '会议记录.pptx', size: '5MB', createTime: '2026-03-03 09:15' },
  { id: 4, name: '培训视频.avi', size: '200MB', createTime: '2026-03-04 16:45' }
])

// 过滤后的文件列表
const filteredFiles = computed(() => {
  let files = mockFiles.value
  
  // 过滤文件格式
  files = files.filter(file => {
    const ext = file.name.toLowerCase().split('.').pop()
    return ['pptx', 'pdf', 'jpg'].includes(ext)
  })
  
  // 搜索过滤
  if (searchKeyword.value) {
    files = files.filter(file => 
      file.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  
  return files
})

// 是否可以确认
const canConfirm = computed(() => {
  if (activeTab.value === 'cloud') {
    return selectedFiles.value.length > 0
  } else {
    return localFile.value !== null
  }
})

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已通过 computed 实现
}

// 全选/取消全选
const handleSelectAll = () => {
  if (selectAll.value) {
    selectedFiles.value = filteredFiles.value.map(file => file.id)
  } else {
    selectedFiles.value = []
  }
}

// 选择单个文件
const handleCloudFileSelect = (fileId) => {
  const index = selectedFiles.value.indexOf(fileId)
  if (index > -1) {
    selectedFiles.value.splice(index, 1)
  } else {
    selectedFiles.value.push(fileId)
  }
  
  // 更新全选状态
  selectAll.value = selectedFiles.value.length === filteredFiles.value.length && filteredFiles.value.length > 0
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click()
}

// 处理文件选择
const handleLocalFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 检查文件大小
    if (file.size > 1024 * 1024 * 1024) {
      alert('文件大小不能超过1GB')
      return
    }
    
    // 检查文件格式
    const ext = file.name.toLowerCase().split('.').pop()
    if (!['pptx', 'pdf', 'jpg'].includes(ext)) {
      alert('只支持.pptx、.pdf和.jpg格式的文件')
      return
    }
    
    localFile.value = file
  }
}

// 处理文件拖拽
const handleFileDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file) {
    // 检查文件大小
    if (file.size > 1024 * 1024 * 1024) {
      alert('文件大小不能超过1GB')
      return
    }
    
    // 检查文件格式
    const ext = file.name.toLowerCase().split('.').pop()
    if (!['pptx', 'pdf', 'jpg'].includes(ext)) {
      alert('只支持.pptx、.pdf和.jpg格式的文件')
      return
    }
    
    localFile.value = file
  }
}

// 移除本地文件
const removeLocalFile = () => {
  localFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 确认处理
const handleConfirm = () => {
  if (activeTab.value === 'cloud') {
    // 处理网盘文件选择
    const selectedFileList = mockFiles.value.filter(file => selectedFiles.value.includes(file.id))
    console.log('选择的网盘文件:', selectedFileList)
    // 这里可以添加实际的文件处理逻辑
  } else {
    // 处理本地文件选择
    console.log('选择的本地文件:', localFile.value)
    // 这里可以添加实际的文件上传逻辑
  }
  
  // 关闭弹窗
  emit('close')
  // 触发成功事件
  emit('success')
}

// 事件
const emit = defineEmits(['close', 'success'])

// 监听Escape键

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})

const handleEscape = (event) => {
  if (event.key === 'Escape') {
    emit('close')
  }
}
</script>

<style scoped>
/* 弹窗容器 */
.add-ppt-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 弹窗内容 */
.popup-content {
  position: relative;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(24px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.5);
  overflow: hidden;
  animation: slideIn 0.3s ease;
  display: flex;
  flex-direction: column;
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

/* 弹窗头部 */
.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.popup-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.close-button {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 50%;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.1);
  transform: scale(1.1);
}

.close-icon {
  width: 16px;
  height: 16px;
}

/* 导航栏 */
.nav-tabs {
  display: flex;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.nav-tab {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
}

.nav-tab:hover {
  color: #f5622b;
}

.nav-tab.active {
  color: #f5622b;
  border-bottom-color: #f5622b;
}

/* 内容区域 */
.tab-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

/* 网盘导入 */
.cloud-import {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 搜索区域 */
.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  padding: 0.5rem 1rem;
}

.search-label {
  margin-right: 0.75rem;
  color: #666;
  font-size: 0.875rem;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.875rem;
  color: #333;
}

.search-input::placeholder {
  color: #999;
}

.search-button {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.search-button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.search-icon {
  width: 16px;
  height: 16px;
}

.file-stats {
  font-size: 0.875rem;
  color: #666;
  white-space: nowrap;
}

/* 文件列表 */
.file-list {
  flex: 1;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

.file-list-header {
  display: grid;
  grid-template-columns: 40px 1fr 100px 150px;
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.02);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  font-weight: 600;
  font-size: 0.875rem;
  color: #333;
}

.list-header-item {
  display: flex;
  align-items: center;
}

.checkbox-column {
  padding-right: 0.5rem;
}

.file-list-body {
  max-height: 300px;
  overflow-y: auto;
}

.file-item {
  display: grid;
  grid-template-columns: 40px 1fr 100px 150px;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background-color 0.2s ease;
}

.file-item:hover {
  background: rgba(0, 0, 0, 0.02);
}

.file-item-cell {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  color: #333;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #999;
  font-size: 0.875rem;
}

/* 本地导入 */
.local-import {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 上传区域 */
.upload-area {
  position: relative;
  border: 2px dashed #f5622b;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(245, 98, 43, 0.05);
}

.upload-area:hover {
  border-color: #e65a27;
  background: rgba(245, 98, 43, 0.1);
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  font-size: 3rem;
  font-weight: 300;
  color: #f5622b;
}

.upload-text {
  font-size: 1rem;
  color: #666;
  margin: 0;
}

/* 上传规则 */
.upload-rules {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
  padding: 1.5rem;
}

.rules-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.rules-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.rule-item {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.rule-item.indent {
  margin-left: 1.5rem;
}

/* 已选择文件 */
.selected-file {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
  padding: 1.5rem;
}

.selected-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.file-name {
  flex: 1;
  font-size: 0.875rem;
  color: #333;
}

.file-size {
  font-size: 0.75rem;
  color: #666;
  white-space: nowrap;
}

.remove-file {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.remove-file:hover {
  color: #f5622b;
  background: rgba(245, 98, 43, 0.1);
}

.remove-icon {
  width: 16px;
  height: 16px;
}

/* 底部操作区 */
.popup-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
}

.cancel-button {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #f5622b;
  border: 2px solid #f5622b;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-button:hover {
  background: rgba(245, 98, 43, 0.05);
  transform: translateY(-1px);
}

.confirm-button {
  padding: 0.75rem 1.5rem;
  background: #f5622b;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(245, 98, 43, 0.3);
}

.confirm-button:hover:not(:disabled) {
  background: #e65a27;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 98, 43, 0.4);
}

.confirm-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .popup-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .popup-header,
  .popup-footer {
    padding: 1rem 1.5rem;
  }
  
  .tab-content {
    padding: 1.5rem;
  }
  
  .search-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .file-list-header {
    grid-template-columns: 40px 1fr 80px 120px;
    font-size: 0.75rem;
  }
  
  .file-item {
    grid-template-columns: 40px 1fr 80px 120px;
    font-size: 0.75rem;
  }
  
  .upload-area {
    padding: 2rem;
  }
  
  .upload-icon {
    font-size: 2rem;
  }
  
  .upload-text {
    font-size: 0.875rem;
  }
}

@media (max-width: 480px) {
  .file-list-header {
    grid-template-columns: 40px 1fr 60px 100px;
  }
  
  .file-item {
    grid-template-columns: 40px 1fr 60px 100px;
  }
  
  .popup-footer {
    flex-direction: column;
  }
  
  .cancel-button,
  .confirm-button {
    width: 100%;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .add-ppt-popup,
  .popup-content,
  .close-button,
  .nav-tab,
  .upload-area,
  .cancel-button,
  .confirm-button {
    animation: none;
    transition: none;
  }
}
</style>