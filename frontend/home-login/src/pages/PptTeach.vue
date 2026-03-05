<template>
  <div class="ppt-teach-page">
    <!-- 背景 -->
    <div class="bg-gradient"></div>
    
    <!-- 顶部导航 -->
    <nav class="navbar">
      <button class="navbar-back-button" @click="handleBack">
        <svg class="back-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"></path>
        </svg>
      </button>
      <div class="navbar-logo">AI智教</div>
      <div class="navbar-tabs">
        <button class="tab-button active" @click="activeTab = 'lesson'">教案区</button>
        <button class="tab-button" :class="{ active: activeTab === 'ppt' }" @click="togglePptPanel">PPT区</button>
      </div>
      <div class="navbar-user">
        <div class="user-avatar"></div>
        <span class="user-greeting">你好，同学</span>
      </div>
    </nav>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧侧边栏 -->
      <div class="sidebar" :class="{ expanded: sidebarExpanded }">
        <button class="sidebar-toggle" @click="toggleSidebar">
          <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 12h18M3 6h18M3 18h18"></path>
          </svg>
        </button>
        <div class="sidebar-content">
          <button class="sidebar-button" @click="handleSidebarAction('qa')">
            <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span>答疑集</span>
          </button>
          <button class="sidebar-button" @click="handleSidebarAction('note')">
            <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <span>写笔记</span>
          </button>
          <button class="sidebar-button" @click="handleSidebarAction('mindmap')">
            <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="18" cy="5" r="3"></circle>
              <circle cx="6" cy="12" r="3"></circle>
              <circle cx="18" cy="19" r="3"></circle>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
            </svg>
            <span>思维导图</span>
          </button>
          <button class="sidebar-button" @click="handleSidebarAction('summary')">
            <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <span>PPT概括</span>
          </button>
        </div>
      </div>
      
      <!-- 内容区域 -->
      <div class="content-area" :class="{ 'ppt-collapsed': pptCollapsed }">
        <!-- 教案区 -->
        <div class="lesson-panel" :style="{ width: lessonWidth + '%' }">
          <div class="panel-header">
            <h2>教案内容</h2>
          </div>
          <div class="panel-content">
            <div class="lesson-content">
              <h3>课程目标</h3>
              <p>1. 理解<span class="highlight">三角形的基本性质</span></p>
              <p>2. 掌握<span class="highlight">三角形面积计算</span>方法</p>
              <p>3. 能够应用三角形知识解决实际问题</p>
              
              <h3>课程重点</h3>
              <p>三角形的面积计算公式：S = 1/2 × 底 × 高</p>
              
              <h3>教学步骤</h3>
              <p>1. 导入：通过生活中的三角形实例引入课题</p>
              <p>2. 讲解：详细解释三角形的基本概念和性质</p>
              <p>3. 演示：通过PPT展示三角形面积计算的具体步骤</p>
              <p>4. 练习：让学生完成相关练习题</p>
              <p>5. 总结：回顾本节课的重点内容</p>
              
              <h3>课堂练习</h3>
              <p>1. 计算底为10cm，高为8cm的三角形面积</p>
              <p>2. 已知三角形面积为24cm²，底为8cm，求高</p>
              <p>3. 应用三角形知识解决实际问题</p>
            </div>
          </div>
          
          <!-- 悬浮提问框 -->
          <div class="question-box">
            <input type="text" placeholder="输入你的问题..." class="question-input" v-model="questionText">
            <button class="send-button" @click="sendQuestion">发送</button>
          </div>
        </div>
        
        <!-- 滑块 -->
        <div class="resizer" @mousedown="startResize" :class="{ dragging: isResizing }"></div>
        
        <!-- PPT区 -->
        <div class="ppt-panel" :class="{ collapsed: pptCollapsed }" :style="{ width: pptWidth + '%' }">
          <div class="panel-header">
            <h2>PPT展示</h2>
            <button class="collapse-button" @click="togglePptPanel">
              <svg class="collapse-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
          </div>
          <div class="panel-content">
            <div class="ppt-content">
              <img src="https://via.placeholder.com/800x450/FFD700/333?text=三角形面积计算" alt="PPT内容" class="ppt-image">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 状态
const activeTab = ref('lesson')
const sidebarExpanded = ref(false)
const pptCollapsed = ref(false)
const lessonWidth = ref(50)
const pptWidth = ref(50)
const isResizing = ref(false)
const questionText = ref('')

// 处理返回
const handleBack = () => {
  window.history.back()
}

// 切换侧边栏
const toggleSidebar = () => {
  sidebarExpanded.value = !sidebarExpanded.value
}

// 处理侧边栏动作
const handleSidebarAction = (action) => {
  console.log(`执行${action}操作`)
  // 这里可以添加实际的操作逻辑
}

// 切换PPT面板
const togglePptPanel = () => {
  pptCollapsed.value = !pptCollapsed.value
  if (pptCollapsed.value) {
    lessonWidth.value = 100
    pptWidth.value = 0
  } else {
    lessonWidth.value = 50
    pptWidth.value = 50
  }
}

// 开始调整大小
const startResize = (e) => {
  isResizing.value = true
  document.addEventListener('mousemove', resize)
  document.addEventListener('mouseup', stopResize)
}

// 调整大小
const resize = (e) => {
  if (!isResizing.value) return
  
  const contentArea = document.querySelector('.content-area')
  const rect = contentArea.getBoundingClientRect()
  const width = e.clientX - rect.left
  const percentage = (width / rect.width) * 100
  
  // 磁吸效果
  let newWidth = percentage
  if (Math.abs(newWidth - 50) < 5) {
    newWidth = 50
  } else if (newWidth < 10) {
    newWidth = 0
    pptCollapsed.value = true
  } else if (newWidth > 90) {
    newWidth = 100
    pptCollapsed.value = true
  } else {
    pptCollapsed.value = false
  }
  
  lessonWidth.value = newWidth
  pptWidth.value = 100 - newWidth
}

// 停止调整大小
const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
}

// 发送问题
const sendQuestion = () => {
  if (questionText.value.trim()) {
    console.log('发送问题:', questionText.value)
    questionText.value = ''
  }
}

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
})
</script>

<style scoped>
/* PPT教学页面容器 */
.ppt-teach-page {
  min-height: 100vh;
  width: 100%;
  position: relative;
  overflow: hidden;
  padding: 0;
  box-sizing: border-box;
  background: #FFFBF5;
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
  opacity: 0.1;
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

/* 导航栏 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #F0E0D0;
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

.navbar-tabs {
  display: flex;
  gap: 16px;
}

.tab-button {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
}

.tab-button:hover {
  color: #FF8A3D;
}

.tab-button.active {
  color: #FF8A3D;
  border-bottom: 2px solid #FF8A3D;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  cursor: pointer;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  border: 2px solid rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.user-avatar:hover {
  transform: scale(1.1);
}

.user-greeting {
  font-size: 0.875rem;
  color: #333333;
  font-weight: 500;
}

/* 主内容区 */
.main-content {
  position: relative;
  z-index: 3;
  min-height: 100vh;
  padding-top: 64px;
  box-sizing: border-box;
  display: flex;
}

/* 左侧侧边栏 */
.sidebar {
  width: 60px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-right: 1px solid #F0E0D0;
  transition: width 0.3s ease;
  position: relative;
  z-index: 10;
}

.sidebar.expanded {
  width: 200px;
}

.sidebar-toggle {
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
  margin: 12px auto;
  transition: all 0.3s ease;
}

.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: scale(1.1);
}

.toggle-icon {
  width: 20px;
  height: 20px;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 0;
}

.sidebar-button {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
  gap: 12px;
  width: 100%;
  text-align: left;
}

.sidebar-button:hover {
  background: rgba(255, 138, 61, 0.1);
  color: #FF8A3D;
}

.sidebar-button:active {
  transform: scale(0.99);
}

.sidebar-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-left: 8px;
}

.sidebar-button span {
  font-size: 0.875rem;
  font-weight: 500;
  opacity: 0;
  transition: opacity 0.3s ease;
  white-space: nowrap;
}

.sidebar.expanded .sidebar-button span {
  opacity: 1;
}

/* 内容区域 */
.content-area {
  flex: 1;
  display: flex;
  height: calc(100vh - 64px);
  position: relative;
  transition: all 0.4s ease;
}

.content-area.ppt-collapsed {
  flex-direction: column;
}

/* 面板通用样式 */
.lesson-panel, .ppt-panel {
  background: #FFFFFF;
  border-radius: 8px;
  margin: 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #F0E0D0;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.lesson-panel {
  flex-shrink: 0;
  transition: width 0.3s ease;
}

.ppt-panel {
  flex-shrink: 0;
  transition: all 0.4s ease;
}

.ppt-panel.collapsed {
  width: 60px !important;
  margin-right: 0;
}

/* 面板头部 */
.panel-header {
  background: #FF8A3D;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: white;
}

.collapse-button {
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

.collapse-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.collapse-icon {
  width: 16px;
  height: 16px;
}

/* 面板内容 */
.panel-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 教案内容 */
.lesson-content {
  color: #333333;
  line-height: 1.6;
}

.lesson-content h3 {
  color: #FF8A3D;
  margin-top: 24px;
  margin-bottom: 12px;
  font-size: 1.1rem;
}

.lesson-content p {
  margin-bottom: 8px;
}

.highlight {
  color: #FF8A3D;
  font-weight: bold;
}

/* PPT内容 */
.ppt-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.ppt-image {
  max-width: 100%;
  max-height: 100%;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ppt-panel.collapsed .ppt-content {
  display: none;
}

/* 滑块 */
.resizer {
  width: 8px;
  background: rgba(255, 138, 61, 0.2);
  cursor: col-resize;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.resizer:hover {
  background: rgba(255, 138, 61, 0.4);
  box-shadow: 0 0 0 2px rgba(255, 138, 61, 0.6);
}

.resizer.dragging {
  background: rgba(255, 138, 61, 0.6);
  box-shadow: 0 0 0 2px rgba(255, 138, 61, 0.8);
}

/* 悬浮提问框 */
.question-box {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 24px;
  padding: 8px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  width: 80%;
  max-width: 600px;
  border: 1px solid #F0E0D0;
}

.question-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px 0;
  font-size: 0.875rem;
  color: #333;
}

.question-input::placeholder {
  color: #999;
}

.send-button {
  padding: 8px 16px;
  border: none;
  background: #FF8A3D;
  color: white;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.send-button:hover {
  background: #FF6B00;
  transform: scale(1.05);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    padding: 0 1rem;
  }
  
  .navbar-tabs {
    display: none;
  }
  
  .sidebar {
    position: fixed;
    bottom: 0;
    top: auto;
    width: 100%;
    height: 60px;
    flex-direction: row;
    border-right: none;
    border-top: 1px solid #F0E0D0;
  }
  
  .sidebar.expanded {
    height: 200px;
    width: 100%;
  }
  
  .sidebar-toggle {
    display: none;
  }
  
  .sidebar-content {
    flex-direction: row;
    padding: 8px;
    justify-content: space-around;
  }
  
  .sidebar-button {
    flex-direction: column;
    gap: 4px;
    padding: 8px;
  }
  
  .sidebar-button span {
    font-size: 0.75rem;
    opacity: 1;
  }
  
  .sidebar-icon {
    margin-left: 0;
  }
  
  .main-content {
    padding-top: 64px;
    padding-bottom: 60px;
  }
  
  .content-area {
    flex-direction: column;
    height: calc(100vh - 124px);
  }
  
  .lesson-panel, .ppt-panel {
    width: calc(100% - 32px) !important;
    margin: 16px;
  }
  
  .resizer {
    width: 100%;
    height: 8px;
    cursor: row-resize;
  }
  
  .question-box {
    width: calc(100% - 40px);
  }
}
</style>