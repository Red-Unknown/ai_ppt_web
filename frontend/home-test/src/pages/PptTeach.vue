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

      <div class="navbar-user">
        <div class="user-avatar"></div>
      </div>
    </nav>
    
    <!-- 主内容区 -->
    <div class="main-content">
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
        </div>
        
        <!-- 滑块 -->
        <div class="resizer" @mousedown="startResize" :class="{ dragging: isResizing }" 
             @touchstart="startResizeTouch" 
             :style="{ cursor: isResizing ? 'grabbing' : 'grab' }"
             unselectable="on"
             onselectstart="return false;"
             onmousedown="return false;">
          <div class="resizer-handle"></div>
          <div class="resizer-tooltip" v-if="isResizing">{{ Math.round(lessonWidth) }}% | {{ Math.round(pptWidth) }}%</div>
        </div>
        
        <!-- PPT区 -->
        <div class="ppt-panel" :class="{ collapsed: pptCollapsed }" :style="{ width: pptWidth + '%' }">
          <div class="panel-header">
            <div class="header-content">
              <div class="header-top">
                <h2>PPT展示</h2>
                <div class="header-buttons">
                  <button class="zoom-toggle-button" @click="toggleZoom" :class="{ 'active': zoomLevel > 1 }">
                    <span class="zoom-text">{{ zoomLevel }}x</span>
                  </button>
                  <button class="state-toggle-button" @click="toggleLessonPanelState" :class="{ active: lessonPanelState }">
                    <svg v-if="lessonPanelState" class="state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                      <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    </svg>
                    <svg v-else class="state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                      <line x1="23" y1="9" x2="17" y2="15"></line>
                      <line x1="17" y1="9" x2="23" y2="15"></line>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="progress-container" v-if="!pptCollapsed">
                <div class="progress-info">
                  <span class="slide-info">{{ currentSlide + 1 }} / {{ totalSlides }}</span>
                  <span class="progress-percentage">{{ progressPercentage }}%</span>
                </div>
                <div class="progress-bar" @click="seekToSlide">
                  <div class="progress-filled" :style="{ width: progressPercentage + '%' }"></div>
                  <div class="progress-handle" :style="{ left: progressPercentage + '%' }" @mousedown="startDrag" @touchstart="startDragTouch"></div>
                </div>
              </div>
            </div>
            <button class="collapse-button" @click="togglePptPanel">
              <svg class="collapse-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
          </div>
          <div class="panel-content">
            <div class="ppt-content">
              <!-- 移除占位图片 -->
            </div>
            
            <!-- 悬浮提问框 -->
            <div class="question-box" @click="showPresets">
              <div class="input-container">
                <input type="text" placeholder="输入你的问题..." class="question-input" v-model="questionText">
                <button class="voice-button" @click.stop="toggleVoiceInput" :class="{ 'active': isVoiceInputActive }">
                  <svg class="voice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                    <line x1="8" y1="23" x2="16" y2="23"></line>
                  </svg>
                </button>
              </div>
              <button class="send-button" @click.stop="sendQuestion">发送</button>
              <!-- 预设问题区域 -->
              <div class="preset-questions" v-if="showPresetQuestions">
                <div 
                  v-for="(question, index) in presetQuestions" 
                  :key="index"
                  class="preset-question-item"
                  @click.stop="selectPresetQuestion(question)"
                >
                  {{ question }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧侧边栏 -->
      <div class="sidebar" :class="{ expanded: sidebarExpanded }">
        <button class="sidebar-toggle" @click="toggleSidebar">
          <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 12h18M3 6h18M3 18h18"></path>
          </svg>
        </button>
        <div class="sidebar-content">
          <button class="sidebar-button" @click="openAnserPopup">
            <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span>答疑集</span>
          </button>
          <!-- 方案1: 钢笔图标 -->
          <button class="sidebar-button" @click="handleSidebarAction('note')">
            <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"></path>
              <path d="m15 5 4 4"></path>
            </svg>
            <span>写笔记</span>
          </button>
          
          <!-- 方案2: 铅笔图标 -->
          <!-- <button class="sidebar-button" @click="handleSidebarAction('note')">
            <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
            <span>写笔记</span>
          </button> -->
          
          <!-- 方案3: 毛笔图标 -->
          <!-- <button class="sidebar-button" @click="handleSidebarAction('note')">
            <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 3a2.85 2.83 0 1 1 4 4L7 19l-4 1 1-4L17 3z"></path>
              <path d="M15 5 9 11"></path>
              <path d="M13 7 9 11"></path>
            </svg>
            <span>写笔记</span>
          </button> -->
          <button class="sidebar-button" @click="handleSidebarAction('export')">
            <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            <span>导出分享</span>
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
    </div>
    
    <!-- 答疑集弹窗 -->
    <AnserPopup 
      :is-visible="anserPopupVisible"
      :conversations="conversations"
      @close="closeAnserPopup"
    />
    
    <!-- PPT概括弹窗 -->
    <IntroductPopup 
      :is-visible="introductPopupVisible"
      :ppt-introduction="pptIntroduction"
      :mindmap-data="mindmapData"
      @close="closeIntroductPopup"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import AnserPopup from '../components/AnserPopup.vue'
import IntroductPopup from '../components/IntroductPopup.vue'

// 状态
const activeTab = ref('lesson')
const sidebarExpanded = ref(false)
const pptCollapsed = ref(false)
const lessonWidth = ref(50)
const pptWidth = ref(50)
const isResizing = ref(false)
const questionText = ref('')
const showPresetQuestions = ref(false)
const zoomLevel = ref(1)
// 语音输入状态
const isVoiceInputActive = ref(false)
let recognition = null
// PPT进度条状态
const currentSlide = ref(0)
const totalSlides = ref(5)
const progressPercentage = ref(0)
const isDragging = ref(false)
// 答疑集弹窗状态
const anserPopupVisible = ref(false)
const conversations = ref([])
// PPT概括弹窗状态
const introductPopupVisible = ref(false)
// 教案区状态切换按钮
const lessonPanelState = ref(localStorage.getItem('lessonPanelState') === 'true')
// PPT简介数据
const pptIntroduction = ref('本PPT主要讲解三角形的基本性质和面积计算方法，包括三角形的定义、分类、基本性质，以及面积计算公式的推导和应用。通过实际例题和练习，帮助学生掌握三角形面积计算的核心概念和解题技巧。')
// 思维导图数据
const mindmapData = ref({
  text: '三角形面积计算',
  children: [
    {
      text: '基本概念',
      children: [
        { text: '三角形定义' },
        { text: '三角形分类' },
        { text: '三角形基本性质' }
      ]
    },
    {
      text: '面积计算公式',
      children: [
        { text: '基本公式: S = 1/2 × 底 × 高' },
        { text: '公式推导' },
        { text: '单位换算' }
      ]
    },
    {
      text: '实际应用',
      children: [
        { text: '例题解析' },
        { text: '练习题' },
        { text: '生活中的应用' }
      ]
    },
    {
      text: '常见问题',
      children: [
        { text: '高的确定' },
        { text: '面积单位' },
        { text: '复杂三角形计算' }
      ]
    }
  ]
})

// 切换教案区状态
const toggleLessonPanelState = () => {
  lessonPanelState.value = !lessonPanelState.value
  // 保存状态到localStorage
  localStorage.setItem('lessonPanelState', lessonPanelState.value.toString())
}

// 切换倍率
const toggleZoom = () => {
  if (zoomLevel.value === 1) {
    zoomLevel.value = 2
  } else if (zoomLevel.value === 2) {
    zoomLevel.value = 3
  } else {
    zoomLevel.value = 1
  }
}

// 初始化语音识别
const initVoiceRecognition = () => {
  if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'zh-CN'
    
    recognition.onstart = () => {
      isVoiceInputActive.value = true
    }
    
    recognition.onresult = (event) => {
      let transcript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript
      }
      questionText.value = transcript
    }
    
    recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error)
    }
    
    recognition.onend = () => {
      // 保持isVoiceInputActive状态，只有手动停止时才设为false
    }
  }
}

// 切换语音输入
const toggleVoiceInput = () => {
  if (!recognition) {
    initVoiceRecognition()
  }
  
  if (isVoiceInputActive.value) {
    recognition.stop()
    isVoiceInputActive.value = false
  } else {
    if (recognition) {
      recognition.start()
    } else {
      alert('您的浏览器不支持语音识别功能')
    }
  }
}

// 计算进度百分比
const calculateProgress = () => {
  if (totalSlides.value > 0) {
    progressPercentage.value = Math.round((currentSlide.value / (totalSlides.value - 1)) * 100 * 100) / 100
  } else {
    progressPercentage.value = 0
  }
}

// 切换到下一张幻灯片
const nextSlide = () => {
  if (currentSlide.value < totalSlides.value - 1) {
    currentSlide.value++
    calculateProgress()
  }
}

// 切换到上一张幻灯片
const prevSlide = () => {
  if (currentSlide.value > 0) {
    currentSlide.value--
    calculateProgress()
  }
}

// 跳转到指定幻灯片
const seekToSlide = (event) => {
  const progressBar = event.currentTarget
  const rect = progressBar.getBoundingClientRect()
  const clickPosition = (event.clientX - rect.left) / rect.width
  const slideIndex = Math.round(clickPosition * (totalSlides.value - 1))
  currentSlide.value = Math.max(0, Math.min(totalSlides.value - 1, slideIndex))
  calculateProgress()
}

// 开始拖拽进度条
const startDrag = (event) => {
  isDragging.value = true
  document.addEventListener('mousemove', dragProgress)
  document.addEventListener('mouseup', stopDrag)
  event.preventDefault()
}

// 开始触摸拖拽
const startDragTouch = (event) => {
  isDragging.value = true
  document.addEventListener('touchmove', dragProgressTouch)
  document.addEventListener('touchend', stopDrag)
  event.preventDefault()
}

// 拖拽进度条
const dragProgress = (event) => {
  if (!isDragging.value) return
  const progressBar = document.querySelector('.progress-bar')
  if (progressBar) {
    const rect = progressBar.getBoundingClientRect()
    const dragPosition = (event.clientX - rect.left) / rect.width
    const slideIndex = Math.round(dragPosition * (totalSlides.value - 1))
    currentSlide.value = Math.max(0, Math.min(totalSlides.value - 1, slideIndex))
    calculateProgress()
  }
}

// 触摸拖拽进度条
const dragProgressTouch = (event) => {
  if (!isDragging.value) return
  const progressBar = document.querySelector('.progress-bar')
  if (progressBar && event.touches.length > 0) {
    const rect = progressBar.getBoundingClientRect()
    const dragPosition = (event.touches[0].clientX - rect.left) / rect.width
    const slideIndex = Math.round(dragPosition * (totalSlides.value - 1))
    currentSlide.value = Math.max(0, Math.min(totalSlides.value - 1, slideIndex))
    calculateProgress()
  }
}

// 停止拖拽
const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', dragProgress)
  document.removeEventListener('touchmove', dragProgressTouch)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchend', stopDrag)
}

// 预设问题数据
const presetQuestions = [
  '三角形面积公式是什么？',
  '如何计算三角形的高？',
  '三角形的基本性质有哪些？',
  '如何应用三角形知识解决实际问题？',
  '三角形和其他几何图形的关系是什么？'
]

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
  if (action === 'summary') {
    openIntroductPopup()
  }
  // 这里可以添加其他操作逻辑
}

// 打开PPT概括弹窗
const openIntroductPopup = () => {
  introductPopupVisible.value = true
}

// 关闭PPT概括弹窗
const closeIntroductPopup = () => {
  introductPopupVisible.value = false
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

// 滑动状态
const startX = ref(0)
const startWidth = ref(0)
const velocity = ref(0)
const lastX = ref(0)
const lastTime = ref(0)
const animationFrameId = ref(null)

// 开始调整大小（鼠标）
const startResize = (e) => {
  e.preventDefault()
  e.stopPropagation()
  
  // 禁止文本选择
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'grabbing'
  
  isResizing.value = true
  startX.value = e.clientX
  startWidth.value = lessonWidth.value
  lastX.value = e.clientX
  lastTime.value = performance.now()
  velocity.value = 0
  
  document.addEventListener('mousemove', resize)
  document.addEventListener('mouseup', stopResize)
  document.addEventListener('mouseleave', stopResize)
}

// 开始调整大小（触摸）
const startResizeTouch = (e) => {
  e.preventDefault()
  e.stopPropagation()
  
  // 禁止文本选择
  document.body.style.userSelect = 'none'
  
  isResizing.value = true
  const touch = e.touches[0]
  startX.value = touch.clientX
  startWidth.value = lessonWidth.value
  lastX.value = touch.clientX
  lastTime.value = performance.now()
  velocity.value = 0
  
  document.addEventListener('touchmove', resizeTouch)
  document.addEventListener('touchend', stopResizeTouch)
  document.addEventListener('touchcancel', stopResizeTouch)
}

// 调整大小（鼠标）
const resize = (e) => {
  if (!isResizing.value) return
  e.preventDefault()
  e.stopPropagation()
  
  const currentTime = performance.now()
  const deltaTime = currentTime - lastTime.value
  const deltaX = e.clientX - lastX.value
  
  // 计算速度
  if (deltaTime > 0) {
    velocity.value = deltaX / deltaTime
  }
  
  lastX.value = e.clientX
  lastTime.value = currentTime
  
  // 性能优化：使用requestAnimationFrame
  if (!animationFrameId.value) {
    animationFrameId.value = requestAnimationFrame(() => {
      const contentArea = document.querySelector('.content-area')
      const rect = contentArea.getBoundingClientRect()
      let width = e.clientX - rect.left
      let percentage = (width / rect.width) * 100
      
      // 设置最小和最大宽度阈值
      const minWidth = 20 // 最小宽度20%
      const maxWidth = 80 // 最大宽度80%
      
      // 平滑的边界限制效果
      if (percentage < minWidth) {
        // 接近最小边界时提供阻力
        const distance = minWidth - percentage
        const resistance = 1 + (distance / 10)
        percentage = minWidth - (distance / resistance)
      } else if (percentage > maxWidth) {
        // 接近最大边界时提供阻力
        const distance = percentage - maxWidth
        const resistance = 1 + (distance / 10)
        percentage = maxWidth + (distance / resistance)
      }
      
      // 确保不超出边界
      percentage = Math.max(minWidth, Math.min(maxWidth, percentage))
      
      // 磁吸效果
      let newWidth = percentage
      if (Math.abs(newWidth - 50) < 5) {
        newWidth = 50
      }
      
      lessonWidth.value = newWidth
      pptWidth.value = 100 - newWidth
      pptCollapsed.value = false
      
      animationFrameId.value = null
    })
  }
}

// 调整大小（触摸）
const resizeTouch = (e) => {
  if (!isResizing.value) return
  e.preventDefault()
  e.stopPropagation()
  
  const touch = e.touches[0]
  const currentTime = performance.now()
  const deltaTime = currentTime - lastTime.value
  const deltaX = touch.clientX - lastX.value
  
  // 计算速度
  if (deltaTime > 0) {
    velocity.value = deltaX / deltaTime
  }
  
  lastX.value = touch.clientX
  lastTime.value = currentTime
  
  // 性能优化：使用requestAnimationFrame
  if (!animationFrameId.value) {
    animationFrameId.value = requestAnimationFrame(() => {
      const contentArea = document.querySelector('.content-area')
      const rect = contentArea.getBoundingClientRect()
      let width = touch.clientX - rect.left
      let percentage = (width / rect.width) * 100
      
      // 设置最小和最大宽度阈值
      const minWidth = 20 // 最小宽度20%
      const maxWidth = 80 // 最大宽度80%
      
      // 平滑的边界限制效果
      if (percentage < minWidth) {
        // 接近最小边界时提供阻力
        const distance = minWidth - percentage
        const resistance = 1 + (distance / 10)
        percentage = minWidth - (distance / resistance)
      } else if (percentage > maxWidth) {
        // 接近最大边界时提供阻力
        const distance = percentage - maxWidth
        const resistance = 1 + (distance / 10)
        percentage = maxWidth + (distance / resistance)
      }
      
      // 确保不超出边界
      percentage = Math.max(minWidth, Math.min(maxWidth, percentage))
      
      // 磁吸效果
      let newWidth = percentage
      if (Math.abs(newWidth - 50) < 5) {
        newWidth = 50
      }
      
      lessonWidth.value = newWidth
      pptWidth.value = 100 - newWidth
      pptCollapsed.value = false
      
      animationFrameId.value = null
    })
  }
}

// 停止调整大小（鼠标）
const stopResize = () => {
  if (!isResizing.value) return
  
  isResizing.value = false
  document.body.style.userSelect = ''
  document.body.style.cursor = ''
  
  // 应用惯性效果
  applyInertia()
  
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
  document.removeEventListener('mouseleave', stopResize)
}

// 停止调整大小（触摸）
const stopResizeTouch = () => {
  if (!isResizing.value) return
  
  isResizing.value = false
  document.body.style.userSelect = ''
  
  // 应用惯性效果
  applyInertia()
  
  document.removeEventListener('touchmove', resizeTouch)
  document.removeEventListener('touchend', stopResizeTouch)
  document.removeEventListener('touchcancel', stopResizeTouch)
}

// 应用惯性效果
const applyInertia = () => {
  const contentArea = document.querySelector('.content-area')
  const rect = contentArea.getBoundingClientRect()
  let currentWidth = lessonWidth.value
  let currentVelocity = velocity.value * 10 // 放大速度影响
  const friction = 0.9
  const minVelocity = 0.1
  
  // 设置最小和最大宽度阈值
  const minWidth = 20 // 最小宽度20%
  const maxWidth = 80 // 最大宽度80%
  
  const animateInertia = () => {
    if (Math.abs(currentVelocity) < minVelocity) {
      // 磁吸效果
      if (Math.abs(currentWidth - 50) < 5) {
        currentWidth = 50
      }
      
      // 确保不超出边界
      currentWidth = Math.max(minWidth, Math.min(maxWidth, currentWidth))
      
      lessonWidth.value = currentWidth
      pptWidth.value = 100 - currentWidth
      pptCollapsed.value = false
      return
    }
    
    currentVelocity *= friction
    const deltaWidth = (currentVelocity / rect.width) * 100
    currentWidth += deltaWidth
    
    // 平滑的边界限制效果
    if (currentWidth < minWidth) {
      // 接近最小边界时提供阻力
      const distance = minWidth - currentWidth
      const resistance = 1 + (distance / 10)
      currentWidth = minWidth - (distance / resistance)
      currentVelocity *= 0.8 // 减小速度
    } else if (currentWidth > maxWidth) {
      // 接近最大边界时提供阻力
      const distance = currentWidth - maxWidth
      const resistance = 1 + (distance / 10)
      currentWidth = maxWidth + (distance / resistance)
      currentVelocity *= 0.8 // 减小速度
    }
    
    // 确保不超出边界
    currentWidth = Math.max(minWidth, Math.min(maxWidth, currentWidth))
    
    lessonWidth.value = currentWidth
    pptWidth.value = 100 - currentWidth
    pptCollapsed.value = false
    
    requestAnimationFrame(animateInertia)
  }
  
  if (Math.abs(currentVelocity) > minVelocity) {
    requestAnimationFrame(animateInertia)
  }
}

// 发送问题
const sendQuestion = () => {
  if (questionText.value.trim()) {
    console.log('发送问题:', questionText.value)
    // 发送到答疑集
    sendToAnser(questionText.value.trim())
    // 打开答疑集弹窗
    openAnserPopup()
    // 清空输入框
    questionText.value = ''
  }
}

// 显示预设问题
const showPresets = () => {
  showPresetQuestions.value = true
}

// 选择预设问题
const selectPresetQuestion = (question) => {
  questionText.value = question
  showPresetQuestions.value = false
}

// 打开答疑集弹窗
const openAnserPopup = () => {
  anserPopupVisible.value = true
}

// 关闭答疑集弹窗
const closeAnserPopup = () => {
  anserPopupVisible.value = false
}

// 发送消息到答疑集
const sendToAnser = (message) => {
  // 添加用户消息
  const userMessage = {
    id: Date.now(),
    content: message,
    isUser: true,
    timestamp: new Date().toLocaleTimeString()
  }
  conversations.value.push(userMessage)
  
  // 模拟AI回复
  setTimeout(() => {
    const aiMessage = {
      id: Date.now() + 1,
      content: `这是对"${message}"的AI回复`,
      isUser: false,
      timestamp: new Date().toLocaleTimeString()
    }
    conversations.value.push(aiMessage)
  }, 1000)
}

// 隐藏预设问题
const hidePresets = () => {
  // 延迟隐藏，以便可以点击预设问题
  setTimeout(() => {
    showPresetQuestions.value = false
  }, 200)
}

// 点击页面其他区域隐藏预设问题
const handleClickOutside = (e) => {
  const questionBox = document.querySelector('.question-box')
  if (questionBox && !questionBox.contains(e.target)) {
    showPresetQuestions.value = false
  }
}

// 挂载时添加全局点击事件监听器
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // 初始化进度条
  calculateProgress()
  // 初始化语音识别
  initVoiceRecognition()
})

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
  document.removeEventListener('click', handleClickOutside)
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
  animation: gradientFlow 15s ease infinite;
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
  flex-direction: row;
}

/* 右侧侧边栏 */
.sidebar {
  width: 60px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-left: 1px solid #F0E0D0;
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
  order: 1;
  /* 硬件加速 */
  transform: translateZ(0);
  will-change: transform;
}

/* 侧边栏顺序 */
.sidebar {
  order: 2;
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
  /* 硬件加速 */
  transform: translateZ(0);
  will-change: width;
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
  align-items: flex-start;
  gap: 16px;
}

.header-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.panel-header h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
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

/* PPT进度条 */
.progress-container {
  width: 100%;
  min-width: 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
}

.slide-info {
  font-weight: 500;
}

.progress-percentage {
  font-family: monospace;
}

.progress-bar {
  position: relative;
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  cursor: pointer;
  overflow: hidden;
}

.progress-filled {
  height: 100%;
  background: white;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-handle {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.progress-handle:hover {
  transform: translate(-50%, -50%) scale(1.2);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
}

.progress-bar:hover .progress-handle {
  opacity: 1;
}

/* 状态变换按钮 */
.state-toggle-button {
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

.state-toggle-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.state-toggle-button.active {
  background: #FF6B00;
  color: white;
}

/* 头部按钮容器 */
.header-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 倍率切换按钮 */
.zoom-toggle-button {
  width: 60px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 0.875rem;
  font-weight: 600;
}

.zoom-toggle-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.zoom-toggle-button.active {
  background: #FF6B00;
  color: white;
}

.zoom-text {
  transition: all 0.3s ease;
}

.state-icon {
  width: 16px;
  height: 16px;
  transition: all 0.3s ease;
}

/* 面板内容 */
.panel-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  position: relative;
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
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  -webkit-appearance: none;
  -webkit-tap-highlight-color: transparent;
  /* 硬件加速 */
  transform: translateZ(0);
  will-change: transform;
}

.resizer:hover {
  background: rgba(255, 138, 61, 0.4);
  box-shadow: 0 0 0 2px rgba(255, 138, 61, 0.6);
}

.resizer.dragging {
  background: rgba(255, 138, 61, 0.6);
  box-shadow: 0 0 0 2px rgba(255, 138, 61, 0.8);
}

/* 滑块手柄 */
.resizer-handle {
  width: 4px;
  height: 40px;
  background: #FF8A3D;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.resizer:hover .resizer-handle {
  height: 60px;
  background: #FF6B00;
}

.resizer.dragging .resizer-handle {
  height: 80px;
  background: #FF6B00;
  box-shadow: 0 0 0 2px rgba(255, 107, 0, 0.3);
}

/* 滑块提示框 */
.resizer-tooltip {
  position: absolute;
  top: -40px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 100;
  pointer-events: none;
  animation: fadeIn 0.2s ease;
}

.resizer-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 4px;
  border-style: solid;
  border-color: rgba(0, 0, 0, 0.8) transparent transparent transparent;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  cursor: text;
  z-index: 1100;
  transition: all 0.3s ease;
}

/* PPT面板中的提问框 */
.ppt-panel .question-box {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 40px);
  max-width: 500px;
}

/* 确保PPT内容区域相对定位，使提问框能正确定位 */
.ppt-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.input-container {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}

.question-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px 40px 8px 0;
  font-size: 0.875rem;
  color: #333;
}

.question-input::placeholder {
  color: #999;
}

.voice-button {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.voice-button:hover {
  background: rgba(255, 138, 61, 0.1);
  color: #FF8A3D;
}

.voice-button.active {
  background: rgba(255, 138, 61, 0.2);
  color: #FF8A3D;
  animation: pulse 1.5s infinite;
}

.voice-icon {
  width: 18px;
  height: 18px;
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

/* 语音按钮脉冲动画 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 138, 61, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 138, 61, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 138, 61, 0);
  }
}

.send-button:hover {
  background: #FF6B00;
  transform: scale(1.05);
}

/* 预设问题区域 */
.preset-questions {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 8px 8px 0 0;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  border: 1px solid #F0E0D0;
  border-bottom: none;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 8px;
  z-index: 1200;
}

.preset-question-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  color: #333;
  border-bottom: 1px solid #F0F0F0;
}

.preset-question-item:hover {
  background: rgba(255, 138, 61, 0.1);
  color: #FF8A3D;
}

.preset-question-item:last-child {
  border-bottom: none;
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