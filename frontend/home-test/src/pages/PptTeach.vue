<template>
  <div class="ppt-teach-page">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <button class="back-btn" @click="handleBack">
        <img class="back-icon" src="@/assets/images/action/ic-keyboard_arrow_up.svg" alt="返回">
      </button>
      <div class="user-info">
        <div class="user-avatar">{{ userName.charAt(0) }}</div>
        <span class="user-greeting">你好，{{ userName }}同学</span>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 左侧：核心学习区 -->
      <div class="left-section">
        <!-- 视频播放器 -->
        <div class="video-player-wrapper">
          <div class="video-container">
            <video
              ref="videoRef"
              class="video-element"
              :src="videoSrc"
              @timeupdate="handleTimeUpdate"
              @loadedmetadata="handleLoadedMetadata"
              @ended="handleEnded"
              @click="togglePlay"
            ></video>
            <!-- 播放按钮覆盖层 -->
            <div v-if="!isPlaying" class="video-overlay" @click="togglePlay">
              <div class="play-btn-large">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
            </div>
          </div>
          <!-- 视频控制栏 -->
          <div class="video-controls">
            <button class="control-btn play-pause" @click="togglePlay">
              <svg v-if="!isPlaying" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
              </svg>
            </button>
            <button class="control-btn volume" @click="toggleMute">
              <svg v-if="!isMuted" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor">
                <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73 4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
              </svg>
            </button>
            <div class="progress-container" @click="seekVideo">
              <div class="progress-bar">
                <div class="progress-filled" :style="{ width: progressPercent + '%' }"></div>
              </div>
            </div>
            <div class="speed-control">
              <button class="speed-btn" @click="showSpeedMenu = !showSpeedMenu">
                {{ playbackSpeed }}x
              </button>
              <div v-if="showSpeedMenu" class="speed-menu">
                <div
                  v-for="speed in [0.5, 0.75, 1, 1.25, 1.5, 2]"
                  :key="speed"
                  class="speed-option"
                  :class="{ active: playbackSpeed === speed }"
                  @click="setPlaybackSpeed(speed)"
                >
                  {{ speed }}x
                </div>
              </div>
            </div>
            <button class="control-btn fullscreen" @click="toggleFullscreen">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 课程文档 -->
        <div class="course-document">
          <div class="doc-section">
            <h3 class="doc-title">方法 2：</h3>
            <p class="doc-subtitle">用「Frame + 遮罩」实现通用裁剪（适合所有图层）</p>
            <ol class="doc-list">
              <li>选中要裁剪的图层，右键菜单里选择 <span class="highlight">「Use as mask」</span>（快捷键 Ctrl+Alt+M），或者先给它套一个 Frame（Ctrl+Alt+G）。</li>
              <li>调整 Frame 的大小和位置，超出 Frame 的部分会被自动隐藏，实现和裁剪一样的效果。</li>
              <li>这种方法不会破坏原图层，随时可以调整裁剪范围</li>
              <li></li>
            </ol>
          </div>
          <div class="doc-section">
            <h3 class="doc-title">方法 3：</h3>
            <p class="doc-subtitle">插件裁剪</p>
            <ol class="doc-list">
              <li>如果需要更灵活的裁剪，也可以在右键菜单里打开 <span class="highlight">「Plugins」</span>，搜索并安装裁剪类插件（比如 Crop 相关插件）来使用。。</li>
            </ol>
          </div>
        </div>
      </div>

      <!-- 右侧：AI助手交互区 -->
      <div class="right-section">
        <!-- Tab标签页 -->
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

        <!-- Tab内容区 -->
        <div class="tab-content">
          <!-- AI助手Tab -->
          <div v-if="activeTab === 'ai-assistant'" class="ai-chat-panel">
            <div class="chat-messages" ref="chatContainer">
              <!-- 空状态 -->
              <div v-if="messages.length === 0" class="empty-chat">
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
              <!-- 消息列表 -->
              <template v-else>
                <div
                  v-for="(msg, index) in messages"
                  :key="index"
                  class="message"
                  :class="{ 'user-msg': msg.type === 'user', 'ai-msg': msg.type === 'ai' }"
                >
                  <div v-if="msg.type === 'ai'" class="avatar ai-avatar">AI</div>
                  <div class="message-bubble">
                    <div class="message-content" v-html="formatMessage(msg.content)"></div>
                  </div>
                  <div v-if="msg.type === 'user'" class="avatar user-avatar">{{ userName.charAt(0) }}</div>
                </div>
              </template>
            </div>
          </div>

          <!-- 历史对话Tab -->
          <div v-if="activeTab === 'history'" class="history-panel">
            <div v-if="showHistoryDetail" class="history-detail">
              <div class="history-detail-header">
                <button class="back-to-list" @click="showHistoryDetail = false">
                  <img src="@/assets/images/action/ic-keyboard_arrow_up.svg" alt="返回" style="width: 20px; height: 20px; transform: rotate(180deg);">
                </button>
                <span class="detail-title">{{ selectedHistory?.title }}</span>
                <div class="detail-actions">
                  <button class="action-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                  </button>
                  <button class="action-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="3"></circle>
                      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="history-messages">
                <div
                  v-for="(msg, index) in selectedHistory?.messages"
                  :key="index"
                  class="message"
                  :class="{ 'user-msg': msg.type === 'user', 'ai-msg': msg.type === 'ai' }"
                >
                  <div v-if="msg.type === 'ai'" class="avatar ai-avatar">AI</div>
                  <div class="message-bubble">
                    <div class="message-content" v-html="formatMessage(msg.content)"></div>
                  </div>
                  <div v-if="msg.type === 'user'" class="avatar user-avatar">{{ userName.charAt(0) }}</div>
                </div>
              </div>
            </div>
            <div v-else class="history-list">
              <div
                v-for="item in historyList"
                :key="item.id"
                class="history-item"
                @click="openHistoryDetail(item)"
              >
                <div class="history-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                  </svg>
                </div>
                <span class="history-title">{{ item.title }}</span>
              </div>
            </div>
          </div>

          <!-- 思维导图Tab -->
          <div v-if="activeTab === 'mindmap'" class="mindmap-panel">
            <div class="mindmap-container">
              <!-- 思维导图内容区域 -->
            </div>
          </div>

          <!-- 课程概要Tab -->
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
          </div>
        </div>

        <!-- 底部输入区 -->
        <div class="chat-input-area">
          <div class="input-wrapper">
            <input
              type="text"
              v-model="inputMessage"
              placeholder="请输入你的问题"
              @keyup.enter="sendMessage"
            />
            <button
              class="voice-btn"
              :class="{ recording: isRecording }"
              @mousedown="startRecording"
              @mouseup="stopRecording"
              @mouseleave="stopRecording"
            >
              <svg v-if="!isRecording" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="6" width="12" height="12" rx="2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'

// 用户信息
const userName = ref('小米')

// Tab配置
const tabs = [
  { id: 'ai-assistant', name: 'AI助手' },
  { id: 'history', name: '历史对话' },
  { id: 'mindmap', name: '思维导图' },
  { id: 'summary', name: '课程概要' }
]
const activeTab = ref('ai-assistant')

// 视频相关
const videoRef = ref(null)
const videoSrc = ref('') // 视频源地址
const isPlaying = ref(false)
const isMuted = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const progressPercent = ref(0)
const playbackSpeed = ref(1)
const showSpeedMenu = ref(false)

// 聊天相关
const inputMessage = ref('')
const messages = ref([])
const chatContainer = ref(null)
const isRecording = ref(false)

// 历史对话
const showHistoryDetail = ref(false)
const selectedHistory = ref(null)
const historyList = ref([
  { id: 1, title: '如何选中目标？', messages: [] },
  { id: 2, title: '如何选中目标？', messages: [] },
  { id: 3, title: '如何选中目标？', messages: [] },
  { id: 4, title: '如何选中目标？', messages: [] },
  { id: 5, title: '如何选中目标？', messages: [] },
  { id: 6, title: '如何选中目标？', messages: [] },
  { id: 7, title: '如何选中目标？', messages: [] }
])

// 播放/暂停
const togglePlay = () => {
  if (videoRef.value) {
    if (isPlaying.value) {
      videoRef.value.pause()
    } else {
      videoRef.value.play()
    }
    isPlaying.value = !isPlaying.value
  }
}

// 静音切换
const toggleMute = () => {
  if (videoRef.value) {
    videoRef.value.muted = !isMuted.value
    isMuted.value = !isMuted.value
  }
}

// 更新进度
const handleTimeUpdate = () => {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime
    progressPercent.value = (currentTime.value / duration.value) * 100
  }
}

// 加载元数据
const handleLoadedMetadata = () => {
  if (videoRef.value) {
    duration.value = videoRef.value.duration
  }
}

// 视频结束
const handleEnded = () => {
  isPlaying.value = false
}

// 拖动进度
const seekVideo = (e) => {
  if (videoRef.value) {
    const rect = e.currentTarget.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    videoRef.value.currentTime = percent * duration.value
  }
}

// 设置播放速度
const setPlaybackSpeed = (speed) => {
  if (videoRef.value) {
    videoRef.value.playbackRate = speed
    playbackSpeed.value = speed
    showSpeedMenu.value = false
  }
}

// 全屏
const toggleFullscreen = () => {
  if (videoRef.value) {
    if (videoRef.value.requestFullscreen) {
      videoRef.value.requestFullscreen()
    }
  }
}

// 发送消息
const sendMessage = () => {
  if (!inputMessage.value.trim()) return

  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: inputMessage.value
  })

  const userQuestion = inputMessage.value
  inputMessage.value = ''

  // 模拟AI回复
  setTimeout(() => {
    messages.value.push({
      type: 'ai',
      content: `选中目标图层，在左侧 Layers 面板里，选中你要处理的图标（比如图中的 Volume 2 或 mic 图层）。<br><br>扁平化 / 轮廓化：<br>• 如果是文字 / 形状组合，先右键 → Flatten（扁平化），把组合变成单一形状。<br>• 如果要描边线条，选中线条 → 右侧面板 Stroke → 点击 Outline stroke（轮廓化描边），把线条变成可编辑的填充形状。<br><br>布尔运算合并：<br>• 选中所有组成图标的形状图层 → 顶部工具栏选择 Union selection（合并），把多个形状合并成一个大路径。<br>• 如果有镂空部分，用 Subtract selection（减去）来实现。`
    })
    scrollToBottom()
  }, 1000)
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// 格式化消息内容
const formatMessage = (content) => {
  return content.replace(/\n/g, '<br>')
}

// 语音输入
const startRecording = () => {
  isRecording.value = true
}

const stopRecording = () => {
  if (isRecording.value) {
    isRecording.value = false
    // 模拟语音输入
    inputMessage.value = '语音输入的内容...'
  }
}

// 打开历史对话详情
const openHistoryDetail = (item) => {
  selectedHistory.value = item
  showHistoryDetail.value = true
}

// 返回
const handleBack = () => {
  window.history.back()
}

// 监听消息变化，自动滚动
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped>
/* 页面容器 */
.ppt-teach-page {
  min-height: 100vh;
  background: #FFF9F3;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.top-header {
  height: 70px;
  background: #FFF9F3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.back-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #C96030;
  transition: all 0.2s ease;
}

.back-btn:hover {
  color: #F18B5B;
}

.back-icon {
  width: 24px;
  height: 24px;
  transform: rotate(180deg);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #F18B5B;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  font-weight: 500;
}

.user-greeting {
  font-size: 16px;
  color: #C96030;
  font-weight: 500;
}

/* 主内容区 */
.main-container {
  flex: 1;
  display: flex;
  gap: 20px;
  padding: 0 24px 24px;
  overflow: hidden;
}

/* 左侧：核心学习区 */
.left-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  min-width: 0;
}

/* 视频播放器 */
.video-player-wrapper {
  background: #FFE6CE;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(201, 96, 48, 0.1);
}

.video-container {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  background: #000;
}

.video-element {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
}

.play-btn-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(241, 139, 91, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
}

.play-btn-large:hover {
  transform: scale(1.1);
  background: rgba(241, 139, 91, 1);
}

.play-btn-large svg {
  width: 40px;
  height: 40px;
  margin-left: 4px;
}

/* 视频控制栏 */
.video-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #FFE6CE;
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
  color: #C96030;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.control-btn:hover {
  color: #F18B5B;
}

.control-btn svg {
  width: 24px;
  height: 24px;
}

.progress-container {
  flex: 1;
  height: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(201, 96, 48, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-filled {
  height: 100%;
  background: #C96030;
  border-radius: 2px;
  transition: width 0.1s linear;
}

.speed-control {
  position: relative;
}

.speed-btn {
  padding: 4px 12px;
  border: none;
  background: transparent;
  color: #C96030;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.speed-btn:hover {
  color: #F18B5B;
}

.speed-menu {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  margin-bottom: 8px;
  min-width: 80px;
  z-index: 100;
}

.speed-option {
  padding: 8px 16px;
  text-align: center;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.speed-option:hover {
  background: #FFF5E7;
  color: #C96030;
}

.speed-option.active {
  color: #F18B5B;
  font-weight: 500;
}

/* 课程文档 */
.course-document {
  background: #FFE6CE;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(201, 96, 48, 0.1);
}

.doc-section {
  margin-bottom: 20px;
}

.doc-section:last-child {
  margin-bottom: 0;
}

.doc-title {
  font-size: 16px;
  font-weight: 600;
  color: #C96030;
  margin: 0 0 4px 0;
}

.doc-subtitle {
  font-size: 14px;
  color: #C96030;
  margin: 0 0 8px 0;
}

.doc-list {
  margin: 0;
  padding-left: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.8;
}

.doc-list li {
  margin-bottom: 4px;
}

.highlight {
  color: #F18B5B;
  font-weight: 500;
}

/* 右侧：AI助手交互区 */
.right-section {
  width: 420px;
  background: #FFE6CE;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(201, 96, 48, 0.1);
  flex-shrink: 0;
}

/* Tab标签页 */
.tab-header {
  display: flex;
  background: #FFE6CE;
  border-bottom: 1px solid rgba(201, 96, 48, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 14px 8px;
  border: none;
  background: transparent;
  color: #C96030;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.tab-btn:hover {
  color: #F18B5B;
}

.tab-btn.active {
  color: #F18B5B;
  font-weight: 500;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background: #F18B5B;
  border-radius: 1px;
}

/* Tab内容区 */
.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #FFE6CE;
}

/* AI助手面板 */
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

/* 空状态 */
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

/* 消息气泡 */
.message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.message.user-msg {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
}

.avatar.ai-avatar {
  background: #E8E8E8;
  color: #999;
}

.avatar.user-avatar {
  background: #F18B5B;
  color: white;
}

.message-bubble {
  max-width: calc(100% - 52px);
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.ai-msg .message-bubble {
  background: #F18B5B;
  color: white;
  border-top-left-radius: 4px;
}

.user-msg .message-bubble {
  background: white;
  color: #333;
  border-top-right-radius: 4px;
}

.message-content {
  word-break: break-word;
}

/* 历史对话面板 */
.history-panel {
  height: 100%;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #FFF5E7;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-item:hover {
  background: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(201, 96, 48, 0.1);
}

.history-icon {
  width: 24px;
  height: 24px;
  color: #F18B5B;
  flex-shrink: 0;
}

.history-icon svg {
  width: 100%;
  height: 100%;
}

.history-title {
  font-size: 14px;
  color: #666;
  flex: 1;
}

/* 历史详情 */
.history-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.history-detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(201, 96, 48, 0.1);
}

.back-to-list {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #C96030;
  transition: all 0.2s ease;
}

.back-to-list:hover {
  color: #F18B5B;
}

.back-to-list svg {
  width: 20px;
  height: 20px;
}

.detail-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #C96030;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #C96030;
  transition: all 0.2s ease;
}

.action-btn:hover {
  color: #F18B5B;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.history-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 思维导图面板 */
.mindmap-panel {
  height: 100%;
}

.mindmap-container {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}

/* 课程概要面板 */
.summary-panel {
  height: 100%;
}

.summary-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.summary-title {
  font-size: 16px;
  font-weight: 600;
  color: #C96030;
  margin: 0 0 16px 0;
}

.summary-section {
  margin-bottom: 20px;
}

.summary-section:last-child {
  margin-bottom: 0;
}

.summary-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #C96030;
  margin: 0 0 4px 0;
}

.summary-section p {
  font-size: 14px;
  color: #C96030;
  margin: 0 0 8px 0;
}

.summary-section ol {
  margin: 0;
  padding-left: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.8;
}

.summary-section li {
  margin-bottom: 4px;
}

/* 底部输入区 */
.chat-input-area {
  padding: 16px;
  background: #FFE6CE;
  border-top: 1px solid rgba(201, 96, 48, 0.1);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  border-radius: 24px;
  padding: 4px 4px 4px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.input-wrapper input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #333;
  outline: none;
  padding: 8px 0;
}

.input-wrapper input::placeholder {
  color: #999;
}

.voice-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  transition: all 0.2s ease;
  border-radius: 50%;
}

.voice-btn:hover {
  background: #FFF5E7;
  color: #F18B5B;
}

.voice-btn.recording {
  background: #F18B5B;
  color: white;
}

.voice-btn svg {
  width: 20px;
  height: 20px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .right-section {
    width: 380px;
  }
}

@media (max-width: 1024px) {
  .main-container {
    flex-direction: column;
  }

  .right-section {
    width: 100%;
    height: 500px;
  }
}

@media (max-width: 768px) {
  .top-header {
    height: 60px;
    padding: 0 16px;
  }

  .main-container {
    padding: 0 16px 16px;
  }

  .user-greeting {
    display: none;
  }

  .right-section {
    height: 400px;
  }

  .tab-btn {
    font-size: 13px;
    padding: 12px 4px;
  }
}

@media (max-width: 480px) {
  .play-btn-large {
    width: 60px;
    height: 60px;
  }

  .play-btn-large svg {
    width: 30px;
    height: 30px;
  }

  .control-btn svg {
    width: 20px;
    height: 20px;
  }

  .speed-btn {
    font-size: 12px;
    padding: 4px 8px;
  }
}
</style>
