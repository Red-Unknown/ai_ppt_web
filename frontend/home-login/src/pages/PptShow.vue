<template>
  <div class="ppt-show-page">
    <!-- 背景渐变 -->
    <div class="bg-gradient"></div>
    
    <!-- 动态气泡 -->
    <div class="bubbles">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div>
    </div>
    
    <!-- 导航栏 -->
    <nav class="navbar">
      <button class="navbar-back-button" @click="handleBack">
        <svg class="back-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"></path>
        </svg>
      </button>
      <div class="navbar-logo"></div>
      <div class="navbar-actions">
        <button class="add-ppt-button" @click="showAddPPTPopup = true">
          添加PPT
        </button>
      </div>
      <div class="navbar-avatar">
        <div class="avatar-placeholder"></div>
      </div>
    </nav>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- PPT封面展示区域 -->
      <div class="ppt-cover-container">
        <div class="ppt-cover">
          <div class="ppt-cover-content">
            <h1 class="ppt-title">PPT 封面标题</h1>
            <p class="ppt-subtitle">PPT 副标题内容</p>
            <div class="ppt-meta">
              <span class="ppt-author">作者：用户名</span>
              <span class="ppt-date">日期：2026-03-04</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加PPT弹窗 -->
    <AddPPTPopup 
      v-if="showAddPPTPopup" 
      @close="showAddPPTPopup = false"
      @success="handleAddPPTSuccess"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AddPPTPopup from '../components/AddPPTPopup.vue'

// 状态
const showAddPPTPopup = ref(false)

// 返回
const handleBack = () => {
  window.history.back()
}

// 处理添加PPT成功
const handleAddPPTSuccess = () => {
  console.log('添加PPT成功')
  // 这里可以添加成功后的处理逻辑
}
</script>

<style scoped>
/* PPT展示页面容器 */
.ppt-show-page {
  min-height: 100vh;
  width: 100%;
  position: relative;
  overflow: hidden;
  padding: 0;
  box-sizing: border-box;
}

/* 背景渐变 */
.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #ff6b6b, #ffd93d, #ff6b6b);
  background-size: 400% 400%;
  animation: gradientFlow 8s ease infinite;
  z-index: 1;
}

/* 背景流动动画 */
@keyframes gradientFlow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* 气泡容器 */
.bubbles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
  pointer-events: none;
}

/* 气泡样式 */
.bubble {
  position: absolute;
  border-radius: 50%;
  backdrop-filter: blur(50px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: float 10s ease-in-out infinite;
  filter: blur(5px);
}

.bubble-1 {
  width: 200px;
  height: 200px;
  top: 20%;
  left: 25%;
  background: rgba(255, 255, 255, 0.3);
  animation-delay: 0s;
}

.bubble-2 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 20%;
  background: rgba(255, 255, 255, 0.3);
  animation-delay: 3s;
}

.bubble-3 {
  width: 120px;
  height: 120px;
  bottom: 20%;
  left: 20%;
  background: rgba(255, 255, 255, 0.3);
  animation-delay: 6s;
}

/* 气泡浮动动画 */
@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(20px, -20px) scale(1.1);
  }
  50% {
    transform: translate(0, 20px) scale(1);
  }
  75% {
    transform: translate(-20px, 10px) scale(0.9);
  }
}

/* 导航栏 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  z-index: 100;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.navbar-back-button {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.navbar-back-button:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateX(-2px);
}

.back-icon {
  width: 20px;
  height: 20px;
}

.navbar-logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
}

.navbar-actions {
  display: flex;
  align-items: center;
}

.add-ppt-button {
  padding: 0.5rem 1rem;
  background: #f5622b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-right: 1rem;
  box-shadow: 0 2px 8px rgba(245, 98, 43, 0.3);
}

.add-ppt-button:hover {
  background: #e65a27;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 98, 43, 0.4);
}

.navbar-avatar {
  display: flex;
  align-items: center;
}

.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  border: 2px solid rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 主内容区 */
.main-content {
  position: relative;
  z-index: 3;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 2rem 2rem;
  box-sizing: border-box;
}

/* PPT封面展示区域 */
.ppt-cover-container {
  margin-bottom: 3rem;
  position: relative;
  z-index: 4;
}

.ppt-cover {
  position: relative;
  width: 800px;
  height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 0 40px rgba(255, 107, 107, 0.6);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ppt-cover-content {
  text-align: center;
  padding: 2rem;
  max-width: 90%;
}

.ppt-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 1.5rem;
  line-height: 1.3;
}

.ppt-subtitle {
  font-size: 1.25rem;
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.ppt-meta {
  display: flex;
  justify-content: center;
  gap: 2rem;
  font-size: 0.875rem;
  color: #999;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .ppt-cover {
    width: 100%;
    max-width: 800px;
    height: auto;
    aspect-ratio: 1.6;
  }
  
  .ppt-title {
    font-size: 2rem;
  }
  
  .ppt-subtitle {
    font-size: 1.125rem;
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 0 1rem;
  }
  
  .main-content {
    padding: 80px 1rem 1rem;
  }
  
  .ppt-cover {
    padding: 1.5rem;
  }
  
  .ppt-title {
    font-size: 1.75rem;
  }
  
  .ppt-subtitle {
    font-size: 1rem;
  }
  
  .ppt-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .ppt-title {
    font-size: 1.5rem;
  }
  
  .ppt-subtitle {
    font-size: 0.875rem;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .bubble,
  .bg-gradient {
    animation: none;
  }
  
  .navbar-back-button {
    transition: none;
  }
}
</style>
