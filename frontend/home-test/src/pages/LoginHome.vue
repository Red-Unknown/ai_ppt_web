<template>
  <div class="login-page">
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
      <div class="navbar-logo"></div>
      <div class="navbar-avatar"></div>
    </nav>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 标题区域 -->
      <div class="title-section">
        <h1 class="main-title">欢迎使用AI智教</h1>
        <p class="sub-title">AI智能分析PPT生成教案，讲课过程可随时提问，高效沟通</p>
      </div>
      
      <!-- 认证按钮部分 -->
      <div class="auth-buttons">
        <button class="login-button" @click="showLoginPopup = true">
          登录
        </button>
        <button class="register-button" @click="showRegisterPopup = true">
          注册
        </button>
      </div>
    </div>
    
    <!-- 登录弹窗 -->
    <div v-if="showLoginPopup" class="popup-overlay" @click="closeLoginPopup">
      <div class="popup-content" @click.stop>
        <LoginPopup @close="closeLoginPopup" @success="handleLoginSuccess" @register="handleRegisterFromLogin" @forgot="handleForgotFromLogin" />
      </div>
    </div>
    
    <!-- 注册弹窗 -->
    <div v-if="showRegisterPopup" class="popup-overlay" @click="closeRegisterPopup">
      <div class="popup-content" @click.stop>
        <RegisterPopup @close="closeRegisterPopup" @success="handleRegisterSuccess" @showNamePopup="handleShowNamePopup" />
      </div>
    </div>
    
    <!-- 忘记密码弹窗 -->
    <div v-if="showForgetPopup" class="popup-overlay" @click="closeForgetPopup">
      <div class="popup-content" @click.stop>
        <ForgetPopup @close="closeForgetPopup" @success="handleForgetSuccess" />
      </div>
    </div>
    
    <!-- 学生信息采集弹窗 -->
    <NamePopup 
      v-if="showNamePopup" 
      :visible="showNamePopup"
      @close="closeNamePopup" 
      @success="handleNamePopupSuccess" 
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoginPopup from '../components/LoginPopup.vue'
import RegisterPopup from '../components/RegisterPopup.vue'
import ForgetPopup from '../components/ForgetPopup.vue'
import NamePopup from '../components/NamePopup.vue'
import { useRouter } from 'vue-router'

// 路由实例
const router = useRouter()

// 状态
const showLoginPopup = ref(false)
const showRegisterPopup = ref(false)
const showForgetPopup = ref(false)
const showNamePopup = ref(false)



// 关闭登录弹窗
const closeLoginPopup = () => {
  showLoginPopup.value = false
}

// 关闭注册弹窗
const closeRegisterPopup = () => {
  showRegisterPopup.value = false
}

// 处理登录成功
const handleLoginSuccess = () => {
  showLoginPopup.value = false
}

// 处理注册成功
const handleRegisterSuccess = () => {
  showRegisterPopup.value = false
}

// 处理显示NamePopup弹窗
const handleShowNamePopup = () => {
  showRegisterPopup.value = false
  showNamePopup.value = true
}

// 关闭NamePopup弹窗
const closeNamePopup = () => {
  showNamePopup.value = false
}

// 处理NamePopup提交成功
const handleNamePopupSuccess = () => {
  showNamePopup.value = false
  // 学生信息收集成功后跳转到学生页面
  router.push('/ppt-show')
}

// 从登录弹窗打开注册弹窗
const handleRegisterFromLogin = () => {
  showLoginPopup.value = false
  showRegisterPopup.value = true
}

// 关闭忘记密码弹窗
const closeForgetPopup = () => {
  showForgetPopup.value = false
}

// 处理忘记密码成功
const handleForgetSuccess = () => {
  showForgetPopup.value = false
  // 可以在这里添加其他逻辑，比如显示登录弹窗
  showLoginPopup.value = true
}

// 从登录弹窗打开忘记密码弹窗
const handleForgotFromLogin = () => {
  showLoginPopup.value = false
  showForgetPopup.value = true
}
</script>

<style scoped>
/* 登录页面容器 */
.login-page {
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

@keyframes dynamicIn {
  0% {
    opacity: 0;
    transform: translateY(60px) scale(0.8) rotateX(20deg);
  }
  60% {
    transform: translateY(-10px) scale(1.05) rotateX(-5deg);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1) rotateX(0);
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



.navbar-logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
}

.navbar-avatar {
  display: flex;
  align-items: center;
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
  background: rgba(255, 255, 255, 0.5);
}

/* 标题区域 */
.title-section {
  text-align: center;
  margin-bottom: 2rem;
  max-width: 800px;
  z-index: 4;
}

.main-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  letter-spacing: -0.02em;
  animation: dynamicIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  opacity: 0;
}

.sub-title {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.01em;
  animation: dynamicIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards;
  opacity: 0;
}

/* 认证按钮部分 */
.auth-buttons {
  display: flex;
  gap: 1.5rem;
  width: 100%;
  max-width: 400px;
  justify-content: center;
  animation: dynamicIn 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.4s forwards;
  opacity: 0;
}

.login-button {
  flex: 1;
  padding: 1rem 2rem;
  background: rgb(252, 126, 56);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(252, 126, 56, 0.4);
}

.login-button:hover {
  background: rgb(240, 115, 45);
  box-shadow: 0 6px 16px rgba(252, 126, 56, 0.5);
  transform: translateY(-2px);
}

.login-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(252, 126, 56, 0.4);
}

.register-button {
  flex: 1;
  padding: 1rem 2rem;
  background: white;
  color: rgb(252, 126, 56);
  border: 2px solid rgb(252, 126, 56);
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.register-button:hover {
  background: rgba(252, 126, 56, 0.05);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(252, 126, 56, 0.2);
}

.register-button:active {
  transform: translateY(0);
  box-shadow: none;
}

/* 登录弹窗 */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(5px);
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

.popup-content {
  position: relative;
  width: 100%;
  max-width: 450px;
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

.popup-close {
  position: absolute;
  top: -40px;
  right: 0;
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.popup-close:hover {
  background: white;
  transform: scale(1.1);
}

.close-icon {
  width: 16px;
  height: 16px;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .main-title {
    font-size: 2rem;
  }
  
  .sub-title {
    font-size: 1rem;
  }
  
}

@media (max-width: 768px) {
  .navbar {
    padding: 0 1rem;
  }
  
  .main-content {
    padding: 80px 1rem 1rem;
  }
  
  .main-title {
    font-size: 1.75rem;
  }
  
  .sub-title {
    font-size: 0.875rem;
  }
  
  .auth-buttons {
    flex-direction: column;
    max-width: 100%;
  }
  
  .login-button,
  .register-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .login-button,
  .register-button {
    padding: 0.875rem 1.5rem;
    font-size: 0.875rem;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .bubble,
  .bg-gradient,
  .popup-overlay,
  .popup-content {
    animation: none;
  }
  
  .login-button,
  .register-button,
  .popup-close {
    transition: none;
  }
}
</style>