<template>
  <div class="about-us-popup-overlay" @click="close">
    <div class="about-us-popup" @click.stop :class="themeClass">
      <!-- 弹窗头部 -->
      <div class="popup-header">
        <h3 class="popup-title">关于我们</h3>
        <button class="close-button" @click="close">×</button>
      </div>
      
      <!-- 内容区域 -->
      <div class="popup-content">
        <div class="status-message">
          <div class="status-text">暂未上线</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// 定义props
const props = defineProps({
  theme: {
    type: String,
    default: 'orange',
    validator: (value) => ['orange', 'blue'].includes(value)
  }
})

// 计算主题类
const themeClass = computed(() => {
  return props.theme === 'blue' ? 'theme-blue' : ''
})

// 定义事件
const emit = defineEmits(['close'])

// 关闭弹窗
const close = () => {
  emit('close')
}
</script>

<style scoped>
.about-us-popup-overlay {
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
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.about-us-popup {
  background: #FFFFFF;
  border-radius: 12px;
  width: 320px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
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

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #F0F0F0;
}

.popup-title {
  font-size: 18px;
  font-weight: bold;
  color: #C96030;
  margin: 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.close-button {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #F0F0F0;
  color: #333;
}

.popup-content {
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
}

.status-message {
  text-align: center;
}

.status-text {
  font-size: 16px;
  color: #666;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

/* 蓝色主题样式 */
.theme-blue .popup-title {
  color: #008AC5;
}

.theme-blue .close-button:hover {
  background: #E6F4FB;
  color: #008AC5;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .about-us-popup {
    width: 280px;
  }
  
  .popup-content {
    padding: 30px 16px;
  }
  
  .status-text {
    font-size: 14px;
  }
}
</style>