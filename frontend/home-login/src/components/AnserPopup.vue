<template>
  <div class="anser-popup-overlay" v-if="isVisible">
    <div class="anser-popup" ref="popupRef">
      <!-- 弹窗头部 -->
      <div class="popup-header">
        <h3 class="popup-title">答疑集</h3>
        <button class="close-button" @click="closePopup">
          <svg class="close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      
      <!-- 对话内容区域 -->
      <div class="conversation-container" ref="conversationContainer">
        <div v-if="conversations.length === 0" class="empty-state">
          <p>暂无对话记录</p>
        </div>
        <div v-else class="conversation-list">
          <!-- 对话项 -->
          <div v-for="(msg, index) in conversations" :key="index" class="message-item" :class="{ 'user-message': msg.isUser, 'ai-message': !msg.isUser }">
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
            </div>
          </div>
        </div>
      </div>
      

    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

// 事件
const emit = defineEmits(['close'])

// 接收props
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  conversations: {
    type: Array,
    default: () => []
  }
})

// 状态
const conversationContainer = ref(null)
const popupRef = ref(null)

// 监听isVisible变化，滚动到底部并更新位置
watch(() => props.isVisible, (newVal) => {
  if (newVal) {
    nextTick(() => {
      scrollToBottom()
      updatePopupPosition()
    })
  }
})

// 滚动到底部
const scrollToBottom = () => {
  if (conversationContainer.value) {
    conversationContainer.value.scrollTop = conversationContainer.value.scrollHeight
  }
}

// 更新弹窗位置
const updatePopupPosition = () => {
  if (!popupRef.value) return
  
  // 找到问题输入框
  const questionBox = document.querySelector('.question-box')
  if (!questionBox) return
  
  // 获取问题输入框的位置和尺寸
  const questionBoxRect = questionBox.getBoundingClientRect()
  
  // 获取弹窗的尺寸
  const popupRect = popupRef.value.getBoundingClientRect()
  
  // 计算弹窗的位置：垂直方向上与问题输入框中心点对齐，底部与问题输入框顶部保持12px间距
  const popupTop = questionBoxRect.top - popupRect.height - 12
  const popupLeft = questionBoxRect.left + (questionBoxRect.width - popupRect.width) / 2
  
  // 设置弹窗位置
  popupRef.value.style.position = 'fixed'
  popupRef.value.style.top = `${popupTop}px`
  popupRef.value.style.left = `${popupLeft}px`
  popupRef.value.style.transform = 'none'
}

// 关闭弹窗
const closePopup = () => {
  emit('close')
}

// 键盘事件处理
const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.isVisible) {
    closePopup()
  }
}

// 监听窗口大小变化和滚动，更新弹窗位置
const handleResize = () => {
  if (props.isVisible) {
    updatePopupPosition()
  }
}

const handleScroll = () => {
  if (props.isVisible) {
    updatePopupPosition()
  }
}

// 挂载时添加事件监听器
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  window.addEventListener('resize', handleResize)
  window.addEventListener('scroll', handleScroll, true)
  
  // 初始更新位置
  if (props.isVisible) {
    nextTick(() => {
      updatePopupPosition()
    })
  }
})

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('scroll', handleScroll, true)
})
</script>

<style scoped>
/* 弹窗遮罩 */
.anser-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 900;
  animation: fadeIn 0.3s ease;
  pointer-events: none;
}

/* 弹窗容器 */
.anser-popup {
  width: 730px;
  height: 730px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 900;
  pointer-events: auto;
}

/* 弹窗头部 */
.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: rgb(255, 138, 61);
  height: auto;
}

.popup-title {
  font-size: 20px;
  font-family: 'Microsoft YaHei', 'Source Han Sans', sans-serif;
  font-weight: bold;
  color: white;
  margin: 0;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  text-align: left;
}

/* 关闭按钮 */
.close-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s ease;
  color: white;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.close-icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* 对话容器 */
.conversation-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background: #fafafa;
}

/* 空状态 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #94a3b8;
  font-size: 1rem;
}

/* 对话列表 */
.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 消息项 */
.message-item {
  display: flex;
  align-items: flex-start;
  max-width: 80%;
  animation: messageFadeIn 0.3s ease;
}

/* 用户消息 */
.message-item.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

/* AI消息 */
.message-item.ai-message {
  align-self: flex-start;
}



/* 消息内容 */
.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.message-text {
  padding: 1rem 1.25rem;
  border-radius: 20px;
  line-height: 1.5;
  font-size: 0.9375rem;
  word-wrap: break-word;
}

.message-item.user-message .message-text {
  background: #f5622b;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-item.ai-message .message-text {
  background: white;
  color: #1e293b;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}





/* 滚动条样式 */
.conversation-container::-webkit-scrollbar {
  width: 6px;
}

.conversation-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.conversation-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.conversation-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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

@keyframes messageFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .anser-popup {
    width: 90vw;
    height: 80vh;
    max-width: 500px;
    max-height: 600px;
  }
  
  .popup-header {
    padding: 1.25rem;
  }
  
  .conversation-container {
    padding: 1.25rem;
  }
  
  .input-container {
    padding: 1.25rem;
  }
  
  .message-item {
    max-width: 85%;
  }
  
  .message-text {
    padding: 0.875rem 1.125rem;
    font-size: 0.875rem;
  }
}

@media (max-width: 480px) {
  .anser-popup {
    width: 95vw;
    height: 85vh;
  }
  
  .popup-title {
    font-size: 1.125rem;
  }
  
  .message-avatar {
    width: 2rem;
    height: 2rem;
  }
  
  .avatar-icon {
    width: 1.25rem;
    height: 1.25rem;
  }
  
  .message-text {
    padding: 0.75rem 1rem;
    font-size: 0.8125rem;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .anser-popup-overlay,
  .anser-popup,
  .message-item {
    animation: none;
  }
}
</style>