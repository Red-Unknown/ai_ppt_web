<template>
  <div class="login-card" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
    <div class="card-content">

      
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
              v-model="form.identifier"
              type="text"
              class="form-input"
              placeholder="请输入学号/工号、手机号"
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
  
  <!-- 注册弹窗 -->
  <RegisterPopup
    v-if="showRegisterPopup"
    @close="closeRegisterPopup"
    @success="handleRegisterSuccess"
  />
  

</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import RegisterPopup from './RegisterPopup.vue'

// 路由实例
const router = useRouter()

// 事件
const emit = defineEmits(['close', 'success', 'register', 'forgot'])

// 表单数据
const form = ref({
  identifier: '',
  password: '',
  captcha: '',
  rememberMe: false
})

// 状态
const isSubmitting = ref(false)
const captchaCode = ref('')
const showRegisterPopup = ref(false)

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
  if (!form.value.identifier || !form.value.password || !form.value.captcha) {
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
    // 调用后端登录API
    const response = await fetch('http://localhost:8000/api/v1/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        identifier: form.value.identifier,
        password: form.value.password
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      console.log('登录成功', data)
      
      // 保存登录状态
      if (form.value.rememberMe) {
        localStorage.setItem('rememberedIdentifier', form.value.identifier)
      } else {
        localStorage.removeItem('rememberedIdentifier')
      }
      
      // 保存会话ID
      localStorage.setItem('session_id', data.data.session_id)
      localStorage.setItem('user_info', JSON.stringify(data.data.user))
      
      alert('登录成功！')
      
      // 通知父组件登录成功
      emit('success')
      
      // 根据用户角色跳转到不同页面
      if (data.data.user.role === 'teacher') {
        router.push('/ppt-show2')
      } else {
        router.push('/ppt-show')
      }
    } else {
      alert(`登录失败: ${data.error}`)
    }
  } catch (error) {
    console.error('登录失败', error)
    alert('登录失败，请检查网络连接')
  } finally {
    isSubmitting.value = false
  }
}

// 显示忘记密码弹窗
const handleForgotPassword = () => {
  // 发出忘记密码事件
  emit('forgot')
}



// 显示注册弹窗
const handleRegister = () => {
  emit('register')
}

// 关闭注册弹窗
const closeRegisterPopup = () => {
  showRegisterPopup.value = false
}

// 注册成功处理
const handleRegisterSuccess = () => {
  showRegisterPopup.value = false
  // 通知父组件注册成功
  emit('success')
}

// 初始化
generateCaptcha()

// 鼠标悬停特效
const loginCard = ref(null)
let hoverCircle = null
let isAnimating = false

// 鼠标进入事件
const handleMouseEnter = (e) => {
  if (isAnimating) return
  
  // 计算鼠标在容器内的位置
  const rect = e.target.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  // 创建圆形元素
  const circle = document.createElement('div')
  circle.className = 'hover-circle in'
  circle.style.left = x + 'px'
  circle.style.top = y + 'px'
  
  e.target.appendChild(circle)
  hoverCircle = circle
  isAnimating = true
  
  // 动画结束后重置状态
  setTimeout(() => {
    isAnimating = false
  }, 500)
}

// 鼠标离开事件
const handleMouseLeave = (e) => {
  if (isAnimating || !hoverCircle) return
  
  // 计算鼠标离开时的位置
  const rect = e.target.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  // 应用离开动画
  hoverCircle.className = 'hover-circle out'
  hoverCircle.style.left = x + 'px'
  hoverCircle.style.top = y + 'px'
  
  isAnimating = true
  
  // 动画结束后移除元素
  setTimeout(() => {
    if (hoverCircle && hoverCircle.parentNode) {
      hoverCircle.parentNode.removeChild(hoverCircle)
    }
    hoverCircle = null
    isAnimating = false
  }, 500)
}
</script>

<style scoped>
/* 登录卡片 */
.login-card {
  position: relative;
  z-index: 3;
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 1);
  backdrop-filter: blur(24px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 1);
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
  z-index: 1;
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
  background: rgba(255, 255, 255, 0.8);
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

/* 鼠标悬停特效 */
:global(.hover-circle) {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 215, 0, 0.3);
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: -1;
  will-change: transform, width, height;
}

:global(.hover-circle.in) {
  width: 10px;
  height: 10px;
  animation: hoverIn 0.5s ease-out forwards;
}

:global(.hover-circle.out) {
  width: 1200px;
  height: 1200px;
  animation: hoverOut 0.5s ease-in forwards;
}

@keyframes hoverIn {
  0% {
    width: 10px;
    height: 10px;
  }
  100% {
    width: 1200px;
    height: 1200px;
  }
}

@keyframes hoverOut {
  0% {
    width: 1200px;
    height: 1200px;
  }
  100% {
    width: 0;
    height: 0;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .login-card,
  .input-wrapper,
  .login-button,
  :global(.hover-circle) {
    transition: none;
    animation: none;
  }
}
</style>