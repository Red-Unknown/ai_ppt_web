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
    
    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="card-content">
        <!-- 返回键 -->
        <button class="back-button" @click="handleBack">
          <svg class="back-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"></path>
          </svg>
        </button>
        
        <!-- 标题 -->
        <div class="login-header">
          <h1 class="login-title">欢迎登录</h1>
          <p class="login-subtitle">请输入您的账号和密码</p>
        </div>
        
        <!-- 登录表单 -->
        <form @submit.prevent="handleSubmit" class="login-form">
          <!-- 账号输入框 -->
          <div class="form-group">
            <div class="input-wrapper">
              <div class="input-icon">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <input
                v-model="form.username"
                type="text"
                class="form-input"
                placeholder="请输入账号"
                @focus="handleInputFocus"
                @blur="handleInputBlur"
              />
            </div>
          </div>
          
          <!-- 密码输入框 -->
          <div class="form-group">
            <div class="input-wrapper">
              <div class="input-icon">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
              </div>
              <input
                v-model="form.password"
                type="password"
                class="form-input"
                placeholder="请输入密码"
                @focus="handleInputFocus"
                @blur="handleInputBlur"
              />
            </div>
          </div>
          
          <!-- 验证码输入框 -->
          <div class="form-group">
            <div class="input-wrapper captcha-wrapper">
              <div class="input-icon">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 18l6-6-6-6"></path>
                  <path d="M8 6l-6 6 6 6"></path>
                </svg>
              </div>
              <input
                v-model="form.captcha"
                type="text"
                class="form-input"
                placeholder="请输入验证码"
                @focus="handleInputFocus"
                @blur="handleInputBlur"
              />
              <div class="captcha-code" @click="generateCaptcha">
                {{ captchaCode }}
              </div>
            </div>
          </div>
          
          <!-- 辅助选项 -->
          <div class="form-options">
            <label class="checkbox-wrapper">
              <input
                v-model="form.rememberMe"
                type="checkbox"
                class="checkbox-input"
              />
              <span class="checkbox-custom"></span>
              <span class="checkbox-label">记住我</span>
            </label>
            <button
              type="button"
              class="link-button"
              @click="handleForgotPassword"
            >
              忘记密码？
            </button>
          </div>
          
          <!-- 登录按钮 -->
          <button
            type="submit"
            class="login-button"
            :disabled="isSubmitting"
          >
            <span v-if="!isSubmitting">登录</span>
            <span v-else class="loading">
              <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle class="spinner-track" cx="12" cy="12" r="10" stroke-opacity="0.2"/>
                <path class="spinner-path" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              登录中...
            </span>
          </button>
        </form>
        
        <!-- 注册链接 -->
        <div class="register-section">
          <span class="register-text">还没有账号？</span>
          <button
            type="button"
            class="register-link"
            @click="handleRegister"
          >
            立即注册
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 表单数据
const form = ref({
  username: '',
  password: '',
  captcha: '',
  rememberMe: false
})

// 状态
const isSubmitting = ref(false)
const captchaCode = ref('')

// 生成验证码
const generateCaptcha = () => {
  const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  let code = ''
  for (let i = 0; i < 4; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaCode.value = code
}

// 输入框聚焦处理
const handleInputFocus = (event) => {
  const inputWrapper = event.target.closest('.input-wrapper')
  if (inputWrapper) {
    inputWrapper.classList.add('input-focused')
  }
}

// 输入框失焦处理
const handleInputBlur = (event) => {
  const inputWrapper = event.target.closest('.input-wrapper')
  if (inputWrapper) {
    inputWrapper.classList.remove('input-focused')
  }
}

// 提交处理
const handleSubmit = async () => {
  if (isSubmitting.value) return
  
  // 简单验证
  if (!form.value.username || !form.value.password || !form.value.captcha) {
    alert('请填写所有字段')
    return
  }
  
  if (form.value.captcha.toUpperCase() !== captchaCode.value) {
    alert('验证码错误')
    generateCaptcha()
    return
  }
  
  isSubmitting.value = true
  
  try {
    // 模拟登录请求
    await new Promise(resolve => setTimeout(resolve, 1500))
    console.log('登录成功', form.value)
    alert('登录成功！')
  } catch (error) {
    console.error('登录失败', error)
    alert('登录失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}

// 忘记密码
const handleForgotPassword = () => {
  alert('忘记密码功能即将上线')
}

// 注册
const handleRegister = () => {
  alert('注册功能即将上线')
}

// 返回
const handleBack = () => {
  window.history.back()
}

// 初始化
onMounted(() => {
  generateCaptcha()
})
</script>

<style scoped>
/* 登录页面容器 */
.login-page {
  min-height: 100vh;
  width: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 2rem;
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

/* 登录卡片 */
.login-card {
  position: relative;
  z-index: 3;
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(24px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

/* 卡片悬停效果 */
.login-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
}

/* 卡片内容 */
.card-content {
  padding: 2.5rem;
  position: relative;
}

/* 返回键 */
.back-button {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  width: 2.5rem;
  height: 2.5rem;
  border: none;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  border-radius: 50%;
  color: #f5622b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 4px 12px rgba(245, 98, 43, 0.2);
  transform: translateX(-2px);
}

.back-icon {
  width: 1.25rem;
  height: 1.25rem;
  stroke: #f5622b;
}

.back-button:hover .back-icon {
  stroke: #e65a27;
}

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #f5622b;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  letter-spacing: -0.02em;
}

.login-subtitle {
  font-size: 0.9375rem;
  color: #64748b;
  line-height: 1.6;
  letter-spacing: 0.01em;
}

/* 登录表单 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* 表单组 */
.form-group {
  width: 100%;
}

/* 输入框包装器 */
.input-wrapper {
  position: relative;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

/* 输入框聚焦效果 */
.input-wrapper.input-focused {
  border-color: rgba(255, 255, 255, 1);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.7);
}

/* 输入框图标 */
.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
  color: #94a3b8;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* 表单输入框 */
.form-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: none;
  background: transparent;
  font-size: 0.9375rem;
  color: #1e293b;
  outline: none;
  transition: all 0.2s ease;
  letter-spacing: 0.01em;
}

.form-input::placeholder {
  color: #94a3b8;
  letter-spacing: 0.01em;
}

/* 验证码包装器 */
.captcha-wrapper {
  display: flex;
  align-items: center;
}

/* 验证码输入框 */
.captcha-wrapper .form-input {
  flex: 1;
  padding-right: 1rem;
}

/* 验证码显示 */
.captcha-code {
  padding: 1rem 1.25rem;
  background: rgba(245, 98, 43, 0.1);
  border-left: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 0.875rem;
  font-weight: 600;
  color: #f5622b;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.2em;
  user-select: none;
}

.captcha-code:hover {
  background: rgba(245, 98, 43, 0.15);
}

/* 表单选项 */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.5rem;
}

/* 复选框 */
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(148, 163, 184, 0.5);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.5);
}

.checkbox-input:checked + .checkbox-custom {
    background: #f5622b;
    border-color: #f5622b;
  }

.checkbox-input:checked + .checkbox-custom::after {
  content: '';
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-bottom: 1px;
}

.checkbox-label {
  font-size: 0.875rem;
  color: #475569;
  font-weight: 500;
  letter-spacing: 0.01em;
  user-select: none;
}

/* 链接按钮 */
.link-button {
  font-size: 0.875rem;
  color: #f5622b;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: color 0.2s ease;
  padding: 0;
  letter-spacing: 0.01em;
}

.link-button:hover {
  color: #e65a27;
  text-decoration: underline;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #f5622b 0%, #ff8a3d 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px rgba(245, 98, 43, 0.35);
  letter-spacing: 0.01em;
  margin-top: 0.5rem;
}

.login-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #e65a27 0%, #f5622b 100%);
  box-shadow: 0 6px 20px rgba(245, 98, 43, 0.45);
  transform: translateY(-1px);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(245, 98, 43, 0.35);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载状态 */
.loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinner {
  width: 1rem;
  height: 1rem;
  animation: spin 1s linear infinite;
}

.spinner-path {
  fill: currentColor;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 注册区域 */
.register-section {
  text-align: center;
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.register-text {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
  letter-spacing: 0.01em;
}

.register-link {
    font-size: 0.875rem;
    color: #f5622b;
    background: none;
    border: none;
    cursor: pointer;
    font-weight: 600;
    transition: color 0.2s ease;
    padding: 0;
    letter-spacing: 0.01em;
  }

  .register-link:hover {
    color: #e65a27;
    text-decoration: underline;
  }

/* 响应式设计 */
@media (max-width: 640px) {
  .login-page {
    padding: 1rem;
  }
  
  .card-content {
    padding: 2rem;
  }
  
  .login-title {
    font-size: 1.5rem;
  }
  
  .form-input {
    padding: 0.875rem 1rem 0.875rem 3rem;
  }
  
  .login-button {
    padding: 0.875rem 1.5rem;
  }
  
  .bubble-1 {
    width: 150px;
    height: 150px;
  }
  
  .bubble-2 {
    width: 120px;
    height: 120px;
  }
  
  .bubble-3 {
    width: 100px;
    height: 100px;
  }
}

@media (max-width: 380px) {
  .card-content {
    padding: 1.5rem;
  }
  
  .login-title {
    font-size: 1.375rem;
  }
  
  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .bubble {
    animation: none;
  }
  
  .spinner {
    animation: none;
  }
  
  .login-card,
  .input-wrapper,
  .login-button {
    transition: none;
  }
}
</style>
