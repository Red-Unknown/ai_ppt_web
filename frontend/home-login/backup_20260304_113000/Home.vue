<template>
  <div class="home-container" :class="{ 'loaded': isLoaded }">
    <div class="dynamic-background">
      <div class="gradient-overlay"></div>
      <div class="blur-blob blob-1"></div>
      <div class="blur-blob blob-2"></div>
      <div class="blur-blob blob-3"></div>
    </div>

    <header class="nav-header" :class="{ 'nav-fixed': isNavFixed }">
      <div class="nav-content">
        <div class="logo">
          <button class="logo-btn" @click="handleExit" aria-label="退出应用">
            <svg class="logo-icon" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <span class="logo-text">AI智教</span>
        </div>

        <nav class="nav-buttons">
          <button class="btn btn-login" @click="handleLogin" aria-label="登录">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>登录</span>
          </button>
          <button class="btn btn-register" @click="handleRegister" aria-label="注册">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M8.5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM20 8v6M23 11h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>注册</span>
          </button>
        </nav>
      </div>
    </header>

    <main class="main-content" :class="{ 'blurred': showLoginModal }">
      <section class="video-section">
        <div class="video-wrapper">
          <div class="video-container" :class="{ 'fullscreen': isFullscreen }">
            <div v-if="isVideoLoading" class="video-loading">
              <div class="loading-spinner"></div>
              <p>视频加载中...</p>
            </div>

            <video
              ref="videoPlayer"
              class="video-player"
              preload="metadata"
              playsinline
              @loadstart="onVideoLoadStart"
              @canplay="onVideoCanPlay"
              @play="onVideoPlay"
              @pause="onVideoPause"
              @ended="onVideoEnded"
              @timeupdate="onTimeUpdate"
            >
              <source src="https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4" type="video/mp4">
              您的浏览器不支持视频播放
            </video>

            <div class="video-controls" :class="{ 'visible': showControls }">
              <button class="control-btn play-btn" @click="togglePlay" :aria-label="isPlaying ? '暂停' : '播放'">
                <svg v-if="!isPlaying" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                </svg>
              </button>

              <div class="progress-container">
                <div class="progress-bar" @click="seekVideo">
                  <div class="progress-filled" :style="{ width: progressPercent + '%' }"></div>
                </div>
                <span class="time-display">{{ currentTime }} / {{ duration }}</span>
              </div>

              <div class="volume-control">
                <button class="control-btn volume-btn" @click="toggleMute" :aria-label="isMuted ? '取消静音' : '静音'">
                  <svg v-if="!isMuted && volume > 0" viewBox="0 0 24 24" fill="none">
                    <path d="M11 5L6 9H2v6h4l5 4V5zM19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none">
                    <path d="M11 5L6 9H2v6h4l5 4V5zM23 9l-6 6M17 9l6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </button>
                <input v-model="volume" type="range" min="0" max="1" step="0.1" class="volume-slider" @input="changeVolume" aria-label="音量">
              </div>

              <button class="control-btn fullscreen-btn" @click="toggleFullscreen" :aria-label="isFullscreen ? '退出全屏' : '全屏'">
                <svg v-if="!isFullscreen" viewBox="0 0 24 24" fill="none">
                  <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none">
                  <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="video-info">
            <h2 class="video-title">探索AI智能教育的无限可能</h2>
            <p class="video-description">通过AI技术，为每个学习者提供个性化的学习体验，让教育更加智能、高效、有趣</p>
          </div>
        </div>
      </section>
    </main>

    <footer class="footer">
      <p>&copy; 2024 AI智教. 保留所有权利.</p>
    </footer>

    <Transition name="modal">
      <div v-if="showLoginModal" class="login-modal-wrapper">
        <div class="login-modal-overlay"></div>
        <div class="login-modal-container">
          <button class="modal-close-btn" @click="closeLoginModal" aria-label="关闭登录弹窗">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
          <Login @login-success="handleLoginSuccess" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Login from './Login.vue'

const isLoaded = ref(false)
const isPlaying = ref(false)
const isVideoLoading = ref(true)
const isFullscreen = ref(false)
const isMuted = ref(false)
const showControls = ref(true)
const showLoginModal = ref(false)
const volume = ref(0.7)
const currentTime = ref('0:00')
const duration = ref('0:00')
const progressPercent = ref(0)

const videoPlayer = ref(null)

const formatTime = (seconds) => {
  if (isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const onVideoLoadStart = () => {
  isVideoLoading.value = true
}

const onVideoCanPlay = () => {
  isVideoLoading.value = false
  if (videoPlayer.value) {
    duration.value = formatTime(videoPlayer.value.duration)
  }
}

const onVideoPlay = () => {
  isPlaying.value = true
}

const onVideoPause = () => {
  isPlaying.value = false
}

const onVideoEnded = () => {
  isPlaying.value = false
  progressPercent.value = 0
}

const onTimeUpdate = () => {
  if (videoPlayer.value) {
    currentTime.value = formatTime(videoPlayer.value.currentTime)
    progressPercent.value = (videoPlayer.value.currentTime / videoPlayer.value.duration) * 100
  }
}

const togglePlay = () => {
  if (videoPlayer.value) {
    if (isPlaying.value) {
      videoPlayer.value.pause()
    } else {
      videoPlayer.value.play()
    }
  }
}

const toggleMute = () => {
  if (videoPlayer.value) {
    isMuted.value = !isMuted.value
    videoPlayer.value.muted = isMuted.value
  }
}

const changeVolume = () => {
  if (videoPlayer.value) {
    videoPlayer.value.volume = volume.value
    isMuted.value = volume.value === 0
  }
}

const seekVideo = (event) => {
  if (videoPlayer.value) {
    const rect = event.currentTarget.getBoundingClientRect()
    const percent = (event.clientX - rect.left) / rect.width
    videoPlayer.value.currentTime = percent * videoPlayer.value.duration
  }
}

const toggleFullscreen = () => {
  const container = videoPlayer.value.parentElement
  if (!isFullscreen.value) {
    if (container.requestFullscreen) {
      container.requestFullscreen()
    } else if (container.webkitRequestFullscreen) {
      container.webkitRequestFullscreen()
    } else if (container.msRequestFullscreen) {
      container.msRequestFullscreen()
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen()
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen()
    }
  }
  isFullscreen.value = !isFullscreen.value
}

const handleLogin = () => {
  showLoginModal.value = true
}

const handleRegister = () => {
  showLoginModal.value = true
}

const closeLoginModal = () => {
  showLoginModal.value = false
}

const handleLoginSuccess = () => {
  closeLoginModal()
}

const handleExit = () => {
  window.close()
}

const isNavFixed = ref(false)
const SCROLL_THRESHOLD = 80
let ticking = false

const handleScroll = () => {
  if (!ticking) {
    window.requestAnimationFrame(() => {
      const scrollY = window.scrollY || window.pageYOffset
      isNavFixed.value = scrollY > SCROLL_THRESHOLD
      ticking = false
    })
    ticking = true
  }
}

onMounted(() => {
  setTimeout(() => {
    isLoaded.value = true
  }, 100)

  if (videoPlayer.value) {
    videoPlayer.value.volume = volume.value
  }

  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement
  })

  window.addEventListener('scroll', handleScroll, { passive: true })

  let hideControlsTimeout
  const showControlsTemporarily = () => {
    showControls.value = true
    clearTimeout(hideControlsTimeout)
    if (isPlaying.value) {
      hideControlsTimeout = setTimeout(() => {
        showControls.value = false
      }, 3000)
    }
  }

  const videoContainer = videoPlayer.value?.parentElement
  if (videoContainer) {
    videoContainer.addEventListener('mousemove', showControlsTemporarily)
    videoContainer.addEventListener('touchstart', showControlsTemporarily)
  }
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', () => {})
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.home-container {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
  opacity: 0;
  transition: opacity 0.6s ease-in-out;
}

.home-container.loaded {
  opacity: 1;
}

.dynamic-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 25%, #FCA5A5 50%, #F87171 75%, #EF4444 100%);
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 30% 50%, rgba(254, 243, 199, 0.3) 0%, transparent 50%),
              radial-gradient(circle at 70% 80%, rgba(239, 68, 68, 0.2) 0%, transparent 50%);
}

.blur-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 20s infinite ease-in-out;
}

.blob-1 {
  width: 500px;
  height: 500px;
  background: rgba(220, 38, 38, 0.3);
  top: -10%;
  left: -10%;
  animation-delay: 0s;
}

.blob-2 {
  width: 400px;
  height: 400px;
  background: rgba(254, 243, 199, 0.4);
  bottom: -10%;
  right: -10%;
  animation-delay: -7s;
}

.blob-3 {
  width: 450px;
  height: 450px;
  background: rgba(248, 113, 113, 0.3);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

.nav-header {
  position: sticky;
  top: 0;
  z-index: 100;
  width: 100%;
  max-width: 1920px;
  height: 80px;
  padding: 1rem 1.5rem;
  background: transparent;
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid transparent;
  box-shadow: none;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-header.nav-fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgba(220, 38, 38, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.logo-btn:hover {
  background: rgba(220, 38, 38, 0.1);
  transform: scale(1.05);
}

.logo-btn:active {
  transform: scale(0.95);
}

.logo-icon {
  width: 40px;
  height: 40px;
  color: #DC2626;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: #DC2626;
  letter-spacing: -0.025em;
}

.nav-buttons {
  display: flex;
  gap: 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  outline: none;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.btn-login {
  background: transparent;
  color: #DC2626;
  border-color: #DC2626;
}

.btn-login:hover {
  background: rgba(220, 38, 38, 0.05);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15);
}

.btn-login:active {
  transform: translateY(0);
}

.btn-register {
  background: linear-gradient(135deg, #DC2626, #EF4444);
  color: white;
  box-shadow: 0 4px 14px rgba(220, 38, 38, 0.25);
}

.btn-register:hover {
  background: linear-gradient(135deg, #EF4444, #F87171);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(220, 38, 38, 0.35);
}

.btn-register:active {
  transform: translateY(0);
}

.main-content {
  position: relative;
  z-index: 1;
  padding: 3rem 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  transition: filter 0.3s ease;
}

.main-content.blurred {
  filter: blur(4px);
  pointer-events: none;
}

.video-section {
  margin-bottom: 4rem;
}

.video-wrapper {
  max-width: 1000px;
  margin: 0 auto;
}

.video-container {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 20px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2),
              0 0 0 1px rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.video-container.fullscreen {
  border-radius: 0;
}

.video-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  z-index: 10;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.video-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1.5rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  display: flex;
  align-items: center;
  gap: 1rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-controls.visible {
  opacity: 1;
}

.control-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.control-btn:active {
  transform: scale(0.95);
}

.control-btn svg {
  width: 20px;
  height: 20px;
}

.progress-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  cursor: pointer;
  overflow: hidden;
  position: relative;
}

.progress-filled {
  height: 100%;
  background: linear-gradient(90deg, #DC2626, #EF4444);
  border-radius: 3px;
  transition: width 0.1s ease;
}

.time-display {
  color: white;
  font-size: 0.85rem;
  font-weight: 500;
  min-width: 90px;
  text-align: right;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.volume-slider {
  width: 80px;
  height: 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.3);
  outline: none;
  cursor: pointer;
  -webkit-appearance: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.volume-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.video-info {
  text-align: center;
  margin-top: 2rem;
}

.video-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 0.75rem;
}

.video-description {
  font-size: 1.1rem;
  color: #6B7280;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.footer {
  text-align: center;
  padding: 2rem 1.5rem;
  color: #6B7280;
  font-size: 0.9rem;
  border-top: 1px solid rgba(220, 38, 38, 0.1);
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
}

.login-modal-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  z-index: 1;
}

.login-modal-container {
  position: relative;
  width: 90%;
  max-width: 420px;
  max-height: 90vh;
  overflow-y: auto;
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  z-index: 2;
}

.modal-close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.05);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 10;
}

.modal-close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  transform: scale(1.1);
}

.modal-close-btn svg {
  width: 24px;
  height: 24px;
  color: #6B7280;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .login-modal-container,
.modal-leave-active .login-modal-container {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-enter-from .login-modal-container,
.modal-leave-to .login-modal-container {
  transform: scale(0.95) translateY(-20px);
}

@media (max-width: 1199px) {
  .main-content {
    padding: 2rem 1rem;
  }

  .video-title {
    font-size: 1.75rem;
  }
}

@media (max-width: 767px) {
  .nav-header {
    height: 64px;
    padding: 0.75rem 1rem;
  }

  .nav-header.nav-fixed {
    height: 64px;
  }

  .logo-text {
    font-size: 1.25rem;
  }

  .nav-buttons {
    gap: 0.5rem;
  }

  .btn {
    padding: 0.6rem 1rem;
    font-size: 0.875rem;
  }

  .btn-icon {
    width: 16px;
    height: 16px;
  }

  .main-content {
    padding: 1.5rem 1rem;
  }

  .video-container {
    border-radius: 16px;
  }

  .video-controls {
    padding: 1rem;
    gap: 0.75rem;
  }

  .control-btn {
    width: 36px;
    height: 36px;
  }

  .control-btn svg {
    width: 18px;
    height: 18px;
  }

  .volume-slider {
    width: 60px;
  }

  .video-title {
    font-size: 1.5rem;
  }

  .video-description {
    font-size: 1rem;
  }

  .login-modal-container {
    width: 95%;
    max-width: 380px;
  }

  .modal-close-btn {
    width: 36px;
    height: 36px;
    top: 0.75rem;
    right: 0.75rem;
  }

  .modal-close-btn svg {
    width: 20px;
    height: 20px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .blur-blob {
    animation: none;
  }

  .loading-spinner {
    animation: none;
  }

  * {
    transition-duration: 0.01ms !important;
  }
}

.btn:focus-visible,
.control-btn:focus-visible {
  outline: 3px solid #DC2626;
  outline-offset: 2px;
}

@media (prefers-contrast: high) {
  .btn-login {
    border-width: 3px;
  }
}
</style>
