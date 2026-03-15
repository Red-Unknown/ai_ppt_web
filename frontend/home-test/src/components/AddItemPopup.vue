<template>
  <div class="add-item-popup" @click.self="$emit('close')">
    <div class="popup-content">
      <!-- 弹窗标题 - 通过props传入 -->
      <div class="popup-header">
        <h2 class="popup-title">{{ title }}</h2>
        <button class="close-button" @click="$emit('close')">
          <svg class="close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      
      <!-- 内容区域 -->
      <div class="popup-body">
        <!-- 输入区域 - 通过props传入标签和占位符 -->
        <div class="form-group">
          <label class="form-label" :for="inputId">{{ inputLabel }}</label>
          <input 
            :id="inputId"
            v-model="itemName" 
            type="text" 
            class="form-input"
            :placeholder="inputPlaceholder"
            @input="clearError"
            @keyup.enter="handleConfirm"
          />
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        </div>
      </div>
      
      <!-- 底部操作区 -->
      <div class="popup-footer">
        <button class="cancel-button" @click="$emit('close')">
          取消
        </button>
        <button 
          class="confirm-button"
          @click="handleConfirm"
          :disabled="isLoading"
        >
          {{ isLoading ? loadingText : '确认' }}
        </button>
      </div>
      
      <!-- 确认对话框 - 通过props传入文本 -->
      <div v-if="showConfirmDialog" class="confirm-dialog-overlay">
        <div class="confirm-dialog">
          <h3 class="confirm-title">{{ confirmTitle }}</h3>
          <p class="confirm-message">{{ confirmMessage }}</p>
          <div class="confirm-actions">
            <button class="confirm-cancel" @click="cancelCreateItem">取消</button>
            <button class="confirm-confirm" @click="confirmCreateItem">确定</button>
          </div>
        </div>
      </div>
      
      <!-- 状态提示 - 通过props传入消息 -->
      <div v-if="operationStatus" :class="['status-toast', operationStatus]">
        <div class="status-content">
          <svg v-if="operationStatus === 'success'" class="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <svg v-else class="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <span class="status-text">{{ statusMessage }}</span>
        </div>
      </div>
      
      <!-- 加载遮罩 - 通过props传入文本 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">{{ loadingText }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  // 弹窗标题
  title: {
    type: String,
    default: '添加项目'
  },
  // 输入字段标签
  inputLabel: {
    type: String,
    default: '名称'
  },
  // 输入字段占位符
  inputPlaceholder: {
    type: String,
    default: '请输入名称'
  },
  // 确认对话框标题
  confirmTitle: {
    type: String,
    default: '确认添加'
  },
  // 加载文本
  loadingText: {
    type: String,
    default: '添加中...'
  },
  // 成功消息
  successMessage: {
    type: String,
    default: '添加成功！'
  },
  // 错误消息
  errorMessageDefault: {
    type: String,
    default: '添加失败，请重试'
  },
  // 输入字段ID
  inputId: {
    type: String,
    default: 'itemName'
  }
})

// 状态
const itemName = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const showConfirmDialog = ref(false)
const operationStatus = ref('') // 'success' or 'error'
const statusMessage = ref('')

// 计算属性 - 确认消息
const confirmMessage = computed(() => {
  return `确定要创建${props.title.replace('添加', '')} "${itemName.value}" 吗？`
})

// 方法
// 清除错误信息
const clearError = () => {
  errorMessage.value = ''
}

// 验证表单
const validateForm = () => {
  if (!itemName.value.trim()) {
    errorMessage.value = `${props.inputLabel}不能为空`
    return false
  }
  return true
}

// 确认处理
const handleConfirm = () => {
  if (validateForm()) {
    showConfirmDialog.value = true
  }
}

// 确认创建
const confirmCreateItem = async () => {
  showConfirmDialog.value = false
  isLoading.value = true
  operationStatus.value = ''
  statusMessage.value = ''
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟API成功响应
    console.log(`${props.title}:`, itemName.value)
    
    // 显示成功状态
    operationStatus.value = 'success'
    statusMessage.value = props.successMessage
    
    // 延迟后关闭弹窗并触发成功事件
    setTimeout(() => {
      isLoading.value = false
      emit('close')
      emit('success', itemName.value)
    }, 1500)
  } catch (error) {
    // 显示错误状态
    operationStatus.value = 'error'
    statusMessage.value = props.errorMessageDefault
    console.error(`${props.title}失败:`, error)
    isLoading.value = false
    
    // 3秒后清除错误状态
    setTimeout(() => {
      operationStatus.value = ''
      statusMessage.value = ''
    }, 3000)
  }
}

// 取消创建
const cancelCreateItem = () => {
  showConfirmDialog.value = false
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
.add-item-popup {
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
  max-width: 500px;
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
  background: #3285FA;
}

.popup-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.close-button {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.close-icon {
  width: 16px;
  height: 16px;
}

/* 内容区域 */
.popup-body {
  padding: 2rem;
}

/* 表单组 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #E0E8FF;
  border-radius: 12px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #3285FA;
  box-shadow: 0 0 0 3px rgba(50, 133, 250, 0.1);
}

.form-input::placeholder {
  color: #999;
}

/* 错误信息 */
.error-message {
  font-size: 0.75rem;
  color: #ff4757;
  margin-top: 0.5rem;
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
  color: #3285FA;
  border: 2px solid #3285FA;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-button:hover {
  background: rgba(50, 133, 250, 0.05);
  transform: translateY(-1px);
}

.confirm-button {
  padding: 0.75rem 1.5rem;
  background: #3285FA;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(50, 133, 250, 0.3);
}

.confirm-button:hover {
  background: #2563EB;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(50, 133, 250, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .popup-content {
    width: 95%;
  }
  
  .popup-header,
  .popup-body,
  .popup-footer {
    padding: 1rem 1.5rem;
  }
  
  .popup-footer {
    flex-direction: column;
  }
  
  .cancel-button,
  .confirm-button {
    width: 100%;
  }
}

/* 确认对话框 */
.confirm-dialog-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  animation: fadeIn 0.3s ease;
}

.confirm-dialog {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
}

.confirm-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 1rem 0;
}

.confirm-message {
  font-size: 0.875rem;
  color: #666;
  margin: 0 0 1.5rem 0;
  line-height: 1.4;
}

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.confirm-cancel {
  padding: 0.5rem 1rem;
  background: white;
  color: #666;
  border: 1px solid #E0E8FF;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.confirm-cancel:hover {
  background: #f5f5f5;
}

.confirm-confirm {
  padding: 0.5rem 1rem;
  background: #3285FA;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.confirm-confirm:hover {
  background: #2563EB;
}

/* 状态提示 */
.status-toast {
  position: fixed;
  top: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideInRight 0.3s ease;
  z-index: 10000;
}

.status-toast.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-toast.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
}

/* 加载遮罩 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3285FA;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-text {
  font-size: 0.875rem;
  color: #666;
}

/* 动画 */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .add-item-popup,
  .popup-content,
  .close-button,
  .form-input,
  .cancel-button,
  .confirm-button,
  .confirm-dialog-overlay,
  .confirm-dialog,
  .status-toast,
  .loading-spinner {
    animation: none;
    transition: none;
  }
}
</style>