<template>
  <div class="start-learning-popup" :class="{ 'visible': isVisible }" @click.self="closePopup">
    <div class="popup-content">
      <!-- 弹窗头部 -->
      <div class="popup-header">
        <h3 class="popup-title">{{ title }}</h3>
        <button class="close-button" @click="closePopup">
          <svg class="close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      
      <!-- 内容区域 -->
      <div class="popup-body">
        <!-- 空白图片区域 -->
        <div class="image-placeholder">
          <div class="placeholder-content">
            <svg class="placeholder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <circle cx="8.5" cy="8.5" r="1.5"></circle>
              <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <p>图片区域</p>
          </div>
        </div>
        
        <!-- 开始学习按钮 -->
        <button class="start-button" :class="{ 'teacher-button': isTeacher }" @click="startLearning">
          {{ isTeacher ? '开始修改' : '开始学习' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Props
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '开始学习'
  },
  isTeacher: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'start'])

// 关闭弹窗
const closePopup = () => {
  emit('close')
}

// 开始学习
const startLearning = () => {
  emit('start')
  closePopup()
}
</script>

<style scoped>
.start-learning-popup {
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
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
}

.start-learning-popup.visible {
  opacity: 1;
  visibility: visible;
}

.popup-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 400px;
  max-width: 90%;
  overflow: hidden;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.popup-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #666;
  transition: color 0.2s ease;
}

.close-button:hover {
  color: #333;
}

.close-icon {
  width: 20px;
  height: 20px;
}

.popup-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.image-placeholder {
  width: 100%;
  height: 200px;
  border: 2px dashed #d0d0d0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #666;
}

.placeholder-icon {
  width: 48px;
  height: 48px;
  opacity: 0.5;
}

.placeholder-content p {
  margin: 0;
  font-size: 14px;
}

.start-button {
  width: 100%;
  padding: 12px;
  background: #FF8A3D;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.start-button:hover {
  background: #ff731d;
}

/* 教师端按钮样式 */
.start-button.teacher-button {
  background: #3283FD;
}

.start-button.teacher-button:hover {
  background: #1a6efd;
}

.start-button:active {
  transform: translateY(1px);
}
</style>