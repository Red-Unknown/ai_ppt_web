<template>
  <div class="fullscreen-viewer">
    <!-- Top Title Bar -->
    <div class="top-bar">
      <h1 class="course-title">{{ courseTitle }}</h1>
    </div>

    <!-- Main PPT Display Area -->
    <div class="ppt-container" ref="pptContainer">
      <!-- Carousel Navigation -->
      <button class="carousel-btn prev-btn" @click="prevSlide" :disabled="currentSlide === 0">
        <img src="../assets/images/action/ic-arrow_left.svg" alt="Previous" class="nav-icon">
      </button>

      <div class="ppt-slide">
        <!-- PPT content -->
        <div class="slide-content">
          <div class="slide-image-container">
            <img :src="currentSlideImage" alt="PPT Slide" class="slide-image">
            <button class="play-button" @click="togglePlayPause" v-if="!isPlaying">
              <img src="../assets/images/action/ic_play.svg" alt="Play" class="play-icon">
            </button>
          </div>
        </div>
      </div>

      <button class="carousel-btn next-btn" @click="nextSlide" :disabled="currentSlide === pptSlides.length - 1">
        <img src="../assets/images/action/ic-arrow_left.svg" alt="Next" class="nav-icon next-icon">
      </button>

    </div>

    <!-- Collapsible Sidebar -->
    <div class="sidebar-container" :class="{ 'collapsed': isSidebarCollapsed }">
      <!-- Sidebar Toggle -->
      <button class="sidebar-toggle" @click="toggleSidebar">
        <img src="../assets/images/action/ic-arrow_left.svg" alt="Toggle Sidebar" class="sidebar-toggle-icon">
      </button>
      <div class="sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
        <!-- Tab Navigation -->
        <div class="tab-header">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.name }}
          </button>
        </div>
        
        <!-- Tab Content -->
        <div class="tab-content">
          <!-- AI Assistant Tab -->
          <div v-if="activeTab === 'ai-assistant'" class="ai-chat-panel">
            <div class="chat-messages">
              <!-- Empty State -->
              <div class="empty-chat">
                <div class="empty-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="9" y1="9" x2="15" y2="9"></line>
                    <line x1="9" y1="13" x2="15" y2="13"></line>
                    <line x1="9" y1="17" x2="11" y2="17"></line>
                  </svg>
                </div>
                <p class="empty-text">你好同学，若有任何疑问，欢迎随时与我沟通</p>
              </div>
            </div>
            <div class="ai-chat-input">
              <input type="text" placeholder="请输入你的问题" class="question-input" v-model="questionInput">
              <button class="voice-button" @click="toggleVoiceInput">
                <img src="../assets/images/action/ic_mic_active.svg" alt="Voice" class="voice-icon">
              </button>
              <button class="send-button" @click="handleSendQuestion('ai-assistant')" :disabled="!questionInput.trim()"> 发送 </button>
            </div>
          </div>
          
          <!-- History Tab -->
          <div v-if="activeTab === 'history'" class="history-panel">
            <div class="history-list">
              <div class="history-item" v-for="i in 7" :key="i">
                <div class="history-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"></path>
                  </svg>
                </div>
                <span class="history-title">如何选中目标？</span>
              </div>
            </div>
            <div class="ai-chat-input">
              <input type="text" placeholder="请输入你的问题" class="question-input" v-model="questionInput">
              <button class="voice-button" @click="toggleVoiceInput">
                <img src="../assets/images/action/ic_mic_active.svg" alt="Voice" class="voice-icon">
              </button>
              <button class="send-button" @click="handleSendQuestion('history')" :disabled="!questionInput.trim()"> 发送 </button>
            </div>
          </div>
          
          <!-- Mind Map Tab -->
          <div v-if="activeTab === 'mindmap'" class="mindmap-panel">
            <div class="mindmap-container">
              <!-- 思维导图内容区域 -->
            </div>
            <div class="ai-chat-input">
              <input type="text" placeholder="请输入你的问题" class="question-input" v-model="questionInput">
              <button class="voice-button" @click="toggleVoiceInput">
                <img src="../assets/images/action/ic_mic_active.svg" alt="Voice" class="voice-icon">
              </button>
              <button class="send-button" @click="handleSendQuestion('mindmap')" :disabled="!questionInput.trim()"> 发送 </button>
            </div>
          </div>
          
          <!-- Course Summary Tab -->
          <div v-if="activeTab === 'summary'" class="summary-panel">
            <div class="summary-content">
              <h3 class="summary-title">课程概要：</h3>
              <div class="summary-section">
                <h4>方法 2：</h4>
                <p>用「Frame + 遮罩」实现通用裁剪（适合所有图层）</p>
                <ol>
                  <li>选中要裁剪的图层，右键菜单里选择 <span class="highlight">「Use as mask」</span>（快捷键 Ctrl+Alt+M），或者先给它套一个 Frame（Ctrl+Alt+G）。</li>
                  <li>调整 Frame 的大小和位置，超出 Frame 的部分会被自动隐藏，实现和裁剪一样的效果。</li>
                  <li>这种方法不会破坏原图层，随时可以调整裁剪范围</li>
                  <li></li>
                </ol>
              </div>
              <div class="summary-section">
                <h4>方法 3：</h4>
                <p>插件裁剪</p>
                <ol>
                  <li>如果需要更灵活的裁剪，也可以在右键菜单里打开 <span class="highlight">「Plugins」</span>，搜索并安装裁剪类插件（比如 Crop 相关插件）来使用。。</li>
                </ol>
              </div>
            </div>
            <div class="ai-chat-input">
              <input type="text" placeholder="请输入你的问题" class="question-input" v-model="questionInput">
              <button class="voice-button" @click="toggleVoiceInput">
                <img src="../assets/images/action/ic_mic_active.svg" alt="Voice" class="voice-icon">
              </button>
              <button class="send-button" @click="handleSendQuestion('summary')" :disabled="!questionInput.trim()"> 发送 </button>
            </div>
          </div>
          
          <!-- Lesson Plan Tab -->
          <div v-if="activeTab === 'lesson-plan'" class="lesson-plan-panel">
            <div class="lesson-plan-content">
              <h4>教案总览</h4>
              <p>教案总览内容将显示在这里</p>
            </div>
            <div class="ai-chat-input">
              <input type="text" placeholder="请输入你的问题" class="question-input" v-model="questionInput">
              <button class="voice-button" @click="toggleVoiceInput">
                <img src="../assets/images/action/ic_mic_active.svg" alt="Voice" class="voice-icon">
              </button>
              <button class="send-button" @click="handleSendQuestion('lesson-plan')" :disabled="!questionInput.trim()"> 发送 </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Subtitle Area -->
    <div class="subtitle-area">
      <div class="subtitle-text">{{ currentSubtitle }}</div>
    </div>

    <!-- Bottom Control Bar -->
    <div class="bottom-bar">
      <button class="control-btn play-pause" @click="togglePlayPause">
        <img v-if="isPlaying" src="../assets/images/action/ic-pause.svg" alt="Pause" class="control-icon">
        <img v-else src="../assets/images/action/ic_play.svg" alt="Play" class="control-icon">
      </button>

      <!-- Progress Bar -->
      <div class="progress-container">
        <div class="time-display">{{ formatTime(currentTime) }}</div>
        <div class="progress-bar" @click="seek">
          <div class="progress-filled" :style="{ width: `${progress}%` }"></div>
        </div>
        <div class="time-display">{{ formatTime(totalTime) }}</div>
      </div>

      <div class="control-group">
        <button class="control-btn subtitle" @click="toggleSubtitles">
          <img v-if="showSubtitles" src="../assets/images/action/ic-subtitle.svg" alt="Subtitles" class="control-icon">
          <img v-else src="../assets/images/action/IC-NOsubtitle.svg" alt="No Subtitles" class="control-icon">
        </button>

        <button class="speed-btn" @click="toggleSpeedMenu">{{ playbackSpeed }}x</button>
        <div v-if="showSpeedMenu" class="speed-menu">
          <button v-for="speed in playbackSpeeds" :key="speed" @click="setPlaybackSpeed(speed)">{{ speed }}x</button>
        </div>

        <button class="control-btn volume" @click="toggleMute">
          <img v-if="isMuted" src="../assets/images/action/ic_volume_off.svg" alt="Muted" class="control-icon">
          <img v-else src="../assets/images/action/ic_volume_on.svg" alt="Volume" class="control-icon">
        </button>

        <button class="control-btn fullscreen" @click="toggleFullscreenMode">
          <img src="../assets/images/action/ic-fullscreen.svg" alt="Exit Fullscreen" class="control-icon">
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  courseTitle: {
    type: String,
    default: '课程标题'
  },
  pptSlides: {
    type: Array,
    default: () => [
      { content: 'PPT 页面 1 内容' },
      { content: 'PPT 页面 2 内容' },
      { content: 'PPT 页面 3 内容' }
    ]
  }
})

// Emits
const emit = defineEmits(['exit-fullscreen'])

// State
const isSidebarCollapsed = ref(false)
const currentSlide = ref(0)
const isPlaying = ref(false)
const isMuted = ref(false)
const playbackSpeed = ref(2)
const playbackSpeeds = [0.5, 1, 1.25, 1.5, 2]
const showSpeedMenu = ref(false)
const currentTime = ref(25)
const totalTime = ref(2534)
const showSubtitles = ref(true)
const currentSubtitle = ref('教案字幕区')
const zoomLevel = ref(1)
const isZooming = ref(false)

// Tab configuration
const tabs = [
  { id: 'ai-assistant', name: 'AI助手' },
  { id: 'history', name: '历史对话' },
  { id: 'mindmap', name: '思维导图' },
  { id: 'summary', name: '课程概要' },
  { id: 'lesson-plan', name: '教案总览' }
]
const activeTab = ref('ai-assistant')

// Input state
const questionInput = ref('')
const isVoiceInputActive = ref(false)

// Refs
const pptContainer = ref(null)

// Computed
const progress = computed(() => {
  return (currentTime.value / totalTime.value) * 100
})

const currentSlideImage = computed(() => {
  // 使用与参考图片相似的长城图片
  return `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Great%20Wall%20of%20China%20landscape%20with%20mountains%20and%20green%20trees&image_size=landscape_16_9`
})

// Methods
const exitFullscreen = () => {
  emit('exit-fullscreen')
}

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const nextSlide = () => {
  if (currentSlide.value < props.pptSlides.length - 1) {
    currentSlide.value++
  }
}

const prevSlide = () => {
  if (currentSlide.value > 0) {
    currentSlide.value--
  }
}

const goToSlide = (index) => {
  currentSlide.value = index
}

const togglePlayPause = () => {
  isPlaying.value = !isPlaying.value
}

const toggleMute = () => {
  isMuted.value = !isMuted.value
}

const toggleSpeedMenu = () => {
  showSpeedMenu.value = !showSpeedMenu.value
}

const setPlaybackSpeed = (speed) => {
  playbackSpeed.value = speed
  showSpeedMenu.value = false
}

const toggleSubtitles = () => {
  showSubtitles.value = !showSubtitles.value
}

const toggleFullscreenMode = () => {
  exitFullscreen()
}

// Voice input toggle
const toggleVoiceInput = () => {
  isVoiceInputActive.value = !isVoiceInputActive.value
  // 这里可以添加语音输入的具体实现
  console.log('Voice input toggled:', isVoiceInputActive.value)
}

// Handle send question
const handleSendQuestion = (tabId) => {
  if (!questionInput.value.trim()) return
  
  console.log(`Sending question from ${tabId}:`, questionInput.value)
  
  // 这里可以添加发送问题的具体实现
  // 例如，调用API发送问题并获取回答
  
  // 清空输入框
  questionInput.value = ''
  
  // 如果从其他标签页发送，切换到AI助手标签页
  if (tabId !== 'ai-assistant') {
    activeTab.value = 'ai-assistant'
  }
}

const seek = (event) => {
  const progressBar = event.currentTarget
  const rect = progressBar.getBoundingClientRect()
  const position = (event.clientX - rect.left) / rect.width
  currentTime.value = position * totalTime.value
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const handleWheel = (event) => {
  if (!isPlaying.value) {
    event.preventDefault()
    const delta = event.deltaY > 0 ? 0.9 : 1.1
    zoomLevel.value = Math.max(0.5, Math.min(2, zoomLevel.value * delta))
  }
}

const handleDoubleClick = () => {
  zoomLevel.value = 1
}

const handleKeydown = (event) => {
  switch (event.key) {
    case ' ': // Spacebar
      event.preventDefault()
      togglePlayPause()
      break
    case 'Escape': // ESC
      exitFullscreen()
      break
    case 'ArrowLeft': // Left arrow
      prevSlide()
      break
    case 'ArrowRight': // Right arrow
      nextSlide()
      break
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  if (pptContainer.value) {
    pptContainer.value.addEventListener('wheel', handleWheel)
    pptContainer.value.addEventListener('dblclick', handleDoubleClick)
  }
  
  // Simulate playback
  if (isPlaying.value) {
    const interval = setInterval(() => {
      currentTime.value = (currentTime.value + 1) % totalTime.value
    }, 1000 / playbackSpeed.value)
    
    return () => clearInterval(interval)
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  if (pptContainer.value) {
    pptContainer.value.removeEventListener('wheel', handleWheel)
    pptContainer.value.removeEventListener('dblclick', handleDoubleClick)
  }
})
</script>

<style scoped>
.fullscreen-viewer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: white;
  color: #333;
  display: flex;
  flex-direction: column;
  z-index: 9999;
  overflow: hidden;
  border: 2px solid #e0e0e0;
}

/* Top Bar */
.top-bar {
  width: 100%;
  height: 50px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e0e0e0;
}

.course-title {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
  color: #333;
}

/* PPT Container */
.ppt-container {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 40px;
  transition: all 0.3s ease;
}

.sidebar-container:not(.collapsed) ~ .ppt-container {
  margin-right: 300px;
}

.sidebar-container.collapsed ~ .ppt-container {
  margin-right: 60px;
}

.ppt-slide {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.slide-content {
  width: 100%;
  max-width: 800px;
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.slide-image-container {
  position: relative;
  width: 100%;
  max-width: 800px;
  height: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.slide-image {
  width: 100%;
  height: auto;
  display: block;
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border: none;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.play-button:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translate(-50%, -50%) scale(1.05);
}

.play-icon {
  width: 32px;
  height: 32px;
}

/* Carousel Buttons */
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border: none;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.carousel-btn:hover {
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.carousel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: translateY(-50%);
}

.prev-btn {
  left: 20px;
}

.next-btn {
  right: 20px;
}

.nav-icon {
  width: 20px;
  height: 20px;
}

.next-icon {
  transform: rotate(180deg);
}

/* Sidebar */
.sidebar-container {
  position: fixed;
  top: 50px;
  right: 0;
  height: calc(100vh - 130px);
  display: flex;
  align-items: flex-start;
  z-index: 999;
  transition: right 0.3s ease;
}

.sidebar {
  width: 300px;
  height: 100%;
  background: #FFE6CE;
  border-left: 1px solid rgba(201, 96, 48, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.05);
}

.sidebar.sidebar-collapsed {
  width: 60px;
}

.sidebar-toggle {
  position: absolute;
  top: 0;
  left: -30px;
  height: 60px;
  width: 30px;
  border: none;
  background: #FFE6CE;
  border-radius: 8px 0 0 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: -1;
}

.sidebar-toggle-icon {
  width: 16px;
  height: 16px;
  transform: rotate(180deg);
  color: #C96030;
}

/* Tab Navigation */
.tab-header {
  display: flex;
  background: #FFE6CE;
  border-bottom: 1px solid rgba(201, 96, 48, 0.1);
  padding: 0;
  gap: 0;
  position: relative;
  overflow: hidden;
}

.tab-btn {
  flex: 1;
  padding: 12px 8px;
  border: none;
  background: #FFE6CE;
  color: #C96030;
  font-size: 14px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  text-align: center;
  border-radius: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tab-btn:hover {
  background: #FFD9B3;
  color: #C96030;
}

.tab-btn.active {
  background: #FF9E5F;
  color: white;
  font-weight: 500;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #FF6B00;
  z-index: 1;
}

/* Tab Content */
.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #FFE6CE;
  position: relative;
  z-index: 1;
}

/* AI Assistant Panel */
.ai-chat-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Empty State */
.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #F18B5B;
  opacity: 0.5;
  margin-bottom: 16px;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-text {
  font-size: 14px;
  color: #F18B5B;
  text-align: center;
}

/* AI Chat Input */
.ai-chat-input {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border-radius: 24px;
  padding: 6px 6px 6px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0e0e0;
  margin-top: 16px;
}

.ai-chat-input input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 13px;
  color: #333;
  outline: none;
  padding: 8px 0;
}

.ai-chat-input input::placeholder {
  color: #999;
}

.voice-button {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(241, 139, 91, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.voice-icon {
  width: 16px;
  height: 16px;
}

.send-button {
  padding: 8px 16px;
  border: none;
  background: #F18B5B;
  color: white;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(241, 139, 91, 0.3);
}

.send-button:hover {
  background: #E07A4A;
}

/* Other Panels */
.history-panel,
.mindmap-panel,
.summary-panel,
.lesson-plan-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* History Panel */
.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-radius: 8px;
  margin: 0 16px 8px 16px;
}

.history-item:hover {
  background-color: rgba(241, 139, 91, 0.1);
}

.history-icon {
  width: 24px;
  height: 24px;
  color: #F18B5B;
  margin-right: 12px;
  flex-shrink: 0;
}

.history-icon svg {
  width: 100%;
  height: 100%;
}

.history-title {
  font-size: 14px;
  color: #333;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Mind Map Panel */
.mindmap-container {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  margin: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

/* Summary Panel */
.summary-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  text-align: left;
}

.summary-title {
  color: #C96030;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.summary-section {
  background-color: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.summary-section h4 {
  color: #C96030;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.summary-section p {
  color: #333;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.5;
}

.summary-section ol {
  padding-left: 20px;
  color: #333;
  font-size: 14px;
  line-height: 1.5;
}

.summary-section ol li {
  margin-bottom: 8px;
}

.highlight {
  background-color: #FFF3E0;
  color: #F18B5B;
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 500;
}

/* Lesson Plan Panel */
.lesson-plan-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 16px;
}

.lesson-plan-content h4 {
  color: #C96030;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 600;
}

.lesson-plan-content p {
  color: #666;
  font-size: 14px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    width: 260px;
  }
  
  .sidebar-container.collapsed ~ .ppt-container {
    margin-right: 60px;
  }
  
  .tab-btn {
    font-size: 12px;
    padding: 10px 6px;
  }
}

@media (max-width: 480px) {
  .tab-btn {
    font-size: 11px;
    padding: 8px 4px;
  }
}



/* Subtitle Area */
.subtitle-area {
  padding: 12px 20px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
  text-align: center;
}

.subtitle-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* Bottom Bar */
.bottom-bar {
  width: 100%;
  height: 60px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-top: 1px solid #e0e0e0;
}

.control-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  border-radius: 4px;
}

.control-btn:hover {
  background: #e9ecef;
}

.control-btn.play-pause {
  background: #F18B5B;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(241, 139, 91, 0.3);
}

.control-btn.play-pause:hover {
  background: #E07A4A;
}

.control-icon {
  width: 16px;
  height: 16px;
}

.progress-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 20px;
}

.time-display {
  font-size: 12px;
  min-width: 40px;
  text-align: center;
  color: #666;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.progress-filled {
  height: 100%;
  background: #F18B5B;
  border-radius: 2px;
  transition: width 0.2s ease;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.speed-btn {
  border: 1px solid #e0e0e0;
  background: white;
  color: #333;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.speed-btn:hover {
  background: #f8f9fa;
  border-color: #F18B5B;
}

.speed-menu {
  position: absolute;
  bottom: 100%;
  right: 0;
  background: white;
  border-radius: 8px;
  padding: 6px 0;
  margin-bottom: 8px;
  min-width: 60px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  border: 1px solid #e0e0e0;
}

.speed-menu button {
  display: block;
  width: 100%;
  border: none;
  background: transparent;
  color: #333;
  padding: 6px 12px;
  font-size: 12px;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 4px;
  margin: 0 4px;
}

.speed-menu button:hover {
  background: #f8f9fa;
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    width: 260px;
  }
  
  .sidebar-toggle {
    right: 260px;
  }
  
  .sidebar.sidebar-collapsed + .sidebar-toggle {
    right: 60px;
  }
  
  .top-bar {
    height: 44px;
  }
  
  .course-title {
    font-size: 14px;
  }
  
  .bottom-bar {
    height: 56px;
    padding: 0 16px;
  }
  
  .progress-container {
    margin: 0 16px;
  }
  
  .control-group {
    gap: 8px;
  }
  
  .carousel-btn {
    width: 36px;
    height: 36px;
  }
  
  .nav-icon {
    width: 18px;
    height: 18px;
  }
}

/* Touch Device Support */
@media (hover: none) and (pointer: coarse) {
  .control-btn {
    width: 40px;
    height: 40px;
  }
  
  .carousel-btn {
    width: 48px;
    height: 48px;
  }
  
  .speed-btn {
    padding: 6px 12px;
  }
  
  .control-icon {
    width: 20px;
    height: 20px;
  }
}

/* Scrollbar Styling */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>