<template>
  <div class="introduct-popup-overlay" v-if="isVisible">
    <div class="introduct-popup" ref="popupRef">
      <!-- 弹窗头部 -->
      <div class="popup-header">
        <h3 class="popup-title">PPT概括</h3>
        <button class="close-button" @click="closePopup">
          <svg class="close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      
      <!-- 双栏内容区域 -->
      <div class="content-container">
        <!-- PPT内容简介区域 -->
        <div class="intro-section">
          <h4 class="section-title">内容简介</h4>
          <div class="intro-content" v-if="pptIntroduction">
            <p>{{ pptIntroduction }}</p>
          </div>
          <div class="empty-state" v-else>
            <p>暂无PPT简介数据</p>
          </div>
        </div>
        
        <!-- 思维导图区域 -->
        <div class="mindmap-section">
          <h4 class="section-title">思维导图</h4>
          <div class="mindmap-container" ref="mindmapContainer">
            <div class="mindmap-placeholder" v-if="!mindmapData">
              <p>加载思维导图中...</p>
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
  pptIntroduction: {
    type: String,
    default: ''
  },
  mindmapData: {
    type: Object,
    default: () => null
  }
})

// 状态
const popupRef = ref(null)
const mindmapContainer = ref(null)
let mindmapInstance = null

// 监听isVisible变化，初始化思维导图并更新位置
watch(() => props.isVisible, (newVal) => {
  if (newVal) {
    nextTick(() => {
      updatePopupPosition()
      if (props.mindmapData) {
        initMindmap()
      }
    })
  } else {
    destroyMindmap()
  }
})

// 监听思维导图数据变化
watch(() => props.mindmapData, (newData) => {
  if (newData && props.isVisible) {
    nextTick(() => {
      initMindmap()
    })
  }
}, { deep: true })

// 初始化思维导图
const initMindmap = () => {
  if (!mindmapContainer.value || !props.mindmapData) return
  
  // 清除之前的实例
  destroyMindmap()
  
  // 这里使用简单的思维导图实现，实际项目中可以集成专业的思维导图库
  renderMindmap(props.mindmapData)
}

// 渲染思维导图
const renderMindmap = (data) => {
  if (!mindmapContainer.value) return
  
  // 清空容器
  mindmapContainer.value.innerHTML = ''
  
  // 创建思维导图容器
  const mindmapElement = document.createElement('div')
  mindmapElement.className = 'mindmap'
  mindmapContainer.value.appendChild(mindmapElement)
  
  // 递归渲染节点
  const renderNode = (node, parentElement) => {
    const nodeElement = document.createElement('div')
    nodeElement.className = 'mindmap-node'
    nodeElement.textContent = node.text
    
    // 添加点击事件处理折叠/展开
    nodeElement.addEventListener('click', (e) => {
      e.stopPropagation()
      const childrenContainer = nodeElement.querySelector('.mindmap-children')
      if (childrenContainer) {
        childrenContainer.classList.toggle('collapsed')
      }
    })
    
    parentElement.appendChild(nodeElement)
    
    if (node.children && node.children.length > 0) {
      const childrenContainer = document.createElement('div')
      childrenContainer.className = 'mindmap-children'
      nodeElement.appendChild(childrenContainer)
      
      node.children.forEach(child => {
        renderNode(child, childrenContainer)
      })
    }
  }
  
  // 渲染根节点
  renderNode(data, mindmapElement)
}

// 销毁思维导图
const destroyMindmap = () => {
  if (mindmapContainer.value) {
    mindmapContainer.value.innerHTML = ''
  }
  mindmapInstance = null
}

// 更新弹窗位置
const updatePopupPosition = () => {
  if (!popupRef.value) return
  
  // 获取窗口中心位置
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight
  const popupRect = popupRef.value.getBoundingClientRect()
  
  // 计算弹窗的位置：居中显示
  const popupTop = (windowHeight - popupRect.height) / 2
  const popupLeft = (windowWidth - popupRect.width) / 2
  
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

// 监听窗口大小变化，更新弹窗位置
const handleResize = () => {
  if (props.isVisible) {
    updatePopupPosition()
  }
}

// 挂载时添加事件监听器
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  window.addEventListener('resize', handleResize)
  
  // 初始更新位置
  if (props.isVisible) {
    nextTick(() => {
      updatePopupPosition()
      if (props.mindmapData) {
        initMindmap()
      }
    })
  }
})

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('resize', handleResize)
  destroyMindmap()
})
</script>

<style scoped>
/* 弹窗遮罩 */
.introduct-popup-overlay {
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
.introduct-popup {
  width: 900px;
  height: 700px;
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

/* 双栏内容容器 */
.content-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧简介区域 */
.intro-section {
  width: 40%;
  padding: 1.5rem;
  border-right: 1px solid #f0f0f0;
  overflow-y: auto;
  background: #fafafa;
}

/* 右侧思维导图区域 */
.mindmap-section {
  width: 60%;
  padding: 1.5rem;
  overflow: hidden;
  background: #ffffff;
}

/* 区域标题 */
.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

/* 简介内容 */
.intro-content {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: #333;
}

.intro-content p {
  margin: 0 0 1rem 0;
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

/* 思维导图容器 */
.mindmap-container {
  width: 100%;
  height: calc(100% - 2rem);
  overflow: auto;
  position: relative;
}

/* 思维导图占位符 */
.mindmap-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #94a3b8;
  font-size: 1rem;
}

/* 思维导图样式 */
.mindmap {
  padding: 1rem;
  min-width: 100%;
  min-height: 100%;
}

.mindmap-node {
  padding: 0.75rem 1rem;
  margin: 0.5rem 0;
  background: #f5f5f5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 4px solid #FF8A3D;
  font-size: 0.9375rem;
  font-weight: 500;
}

.mindmap-node:hover {
  background: #e8e8e8;
  transform: translateX(4px);
}

.mindmap-children {
  margin-left: 1.5rem;
  margin-top: 0.5rem;
  transition: all 0.3s ease;
}

.mindmap-children.collapsed {
  max-height: 0;
  overflow: hidden;
  margin-top: 0;
  margin-bottom: 0;
}

/* 滚动条样式 */
.intro-section::-webkit-scrollbar,
.mindmap-container::-webkit-scrollbar {
  width: 6px;
}

.intro-section::-webkit-scrollbar-track,
.mindmap-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.intro-section::-webkit-scrollbar-thumb,
.mindmap-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.intro-section::-webkit-scrollbar-thumb:hover,
.mindmap-container::-webkit-scrollbar-thumb:hover {
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

/* 响应式设计 */
@media (max-width: 1024px) {
  .introduct-popup {
    width: 80vw;
    height: 70vh;
    max-width: 800px;
    max-height: 600px;
  }
}

@media (max-width: 768px) {
  .introduct-popup {
    width: 90vw;
    height: 80vh;
    max-width: 600px;
    max-height: 500px;
  }
  
  .content-container {
    flex-direction: column;
  }
  
  .intro-section {
    width: 100%;
    height: 40%;
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .mindmap-section {
    width: 100%;
    height: 60%;
  }
  
  .popup-header {
    padding: 1.25rem;
  }
  
  .intro-section,
  .mindmap-section {
    padding: 1.25rem;
  }
}

@media (max-width: 480px) {
  .introduct-popup {
    width: 95vw;
    height: 85vh;
  }
  
  .popup-title {
    font-size: 1.125rem;
  }
  
  .section-title {
    font-size: 0.9375rem;
  }
  
  .intro-content {
    font-size: 0.875rem;
  }
  
  .mindmap-node {
    font-size: 0.875rem;
    padding: 0.625rem 0.875rem;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .introduct-popup-overlay,
  .introduct-popup {
    animation: none;
  }
  
  .mindmap-node {
    transition: none;
  }
  
  .mindmap-children {
    transition: none;
  }
}
</style>