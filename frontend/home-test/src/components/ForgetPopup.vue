<template>
  <div class="login-card" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
    <div class="card-content">
      <!-- 标题 -->
      <div class="login-header">
        <h1 class="login-title">忘记密码</h1>
        <p class="login-subtitle">请填写以下信息重置您的密码</p>
      </div>
      
      <!-- 忘记密码表单 -->
      <form @submit.prevent="handleSubmit" class="login-form">
        <!-- 手机号输入框 -->
        <div class="form-group">
          <div class="input-wrapper">
            <div class="input-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
              </svg>
            </div>
            <input
              v-model="form.phone"
              type="tel"
              class="form-input"
              :placeholder="errors.phone || '请输入注册手机号'"
              @focus="handleInputFocus"
              @blur="handleInputBlur"
              @input="validatePhone"
              :class="{ 'input-error': errors.phone }"
            />
          </div>
        </div>
        

        
        <!-- 新密码输入框 -->
        <div class="form-group">
          <div class="input-wrapper password-wrapper">
            <div class="input-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
            </div>
            <input
              v-model="form.newPassword"
              :type="'password'"
              class="form-input"
              :placeholder="errors.newPassword || '设置新密码'"
              @focus="handleInputFocus"
              @blur="handleInputBlur"
              @input="validateNewPassword"
              :class="{ 'input-error': errors.newPassword }"
            />
          </div>
          <div class="password-strength" v-if="form.newPassword">
            <div class="strength-bar" :class="passwordStrengthClass"></div>
            <span class="strength-text">{{ passwordStrengthText }}</span>
          </div>
        </div>
        
        <!-- 确认密码输入框 -->
        <div class="form-group">
          <div class="input-wrapper password-wrapper">
            <div class="input-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
            </div>
            <input
              v-model="form.confirmPassword"
              :type="'password'"
              class="form-input"
              :placeholder="errors.confirmPassword || '确认新密码'"
              @focus="handleInputFocus"
              @blur="handleInputBlur"
              @input="validateConfirmPassword"
              :class="{ 'input-error': errors.confirmPassword }"
            />
          </div>
          <p class="password-rule">密码要求 8-16 位，至少包含数字、字母、字符两种元素</p>
        </div>
        
        <!-- 操作按钮区域 -->
        <div class="button-group">
          <button
            type="submit"
            class="login-button full-width"
            :disabled="!isFormValid"
          >
            <span v-if="!isSubmitting">重置密码</span>
            <span v-else class="loading">
              <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle class="spinner-track" cx="12" cy="12" r="10" stroke-opacity="0.2"/>
                <path class="spinner-path" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              重置中...
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

// 路由实例
const router = useRouter()

// 事件
const emit = defineEmits(['close', 'success'])

// 状态
const isSubmitting = ref(false)
const countdown = ref(0)
const isPhoneValid = ref(false)

// 表单数据
const form = ref({
  phone: '',
  captcha: '',
  newPassword: '',
  confirmPassword: ''
})

// 错误信息
const errors = ref({
  phone: '',
  captcha: '',
  newPassword: '',
  confirmPassword: ''
})

// 计算属性
const isFormValid = computed(() => {
  return (
    isPhoneValid.value &&
    form.value.newPassword &&
    form.value.confirmPassword &&
    form.value.newPassword === form.value.confirmPassword &&
    !errors.value.phone &&
    !errors.value.newPassword &&
    !errors.value.confirmPassword
  )
})

// 密码强度计算
const passwordStrengthClass = computed(() => {
  const password = form.value.newPassword
  if (!password) return ''
  
  let strength = 0
  if (password.length >= 8) strength++
  if (/\d/.test(password)) strength++
  if (/[a-zA-Z]/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++
  
  switch (strength) {
    case 1: return 'weak'
    case 2: return 'medium'
    case 3: return 'strong'
    case 4: return 'very-strong'
    default: return ''
  }
})

const passwordStrengthText = computed(() => {
  const password = form.value.newPassword
  if (!password) return ''
  
  let strength = 0
  if (password.length >= 8) strength++
  if (/\d/.test(password)) strength++
  if (/[a-zA-Z]/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++
  
  switch (strength) {
    case 1: return '弱'
    case 2: return '中等'
    case 3: return '强'
    case 4: return '非常强'
    default: return ''
  }
})



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

// 验证手机号
const validatePhone = () => {
  const phone = form.value.phone
  if (!phone) {
    errors.value.phone = '请输入手机号'
    isPhoneValid.value = false
    return
  }
  
  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(phone)) {
    errors.value.phone = '请输入正确的手机号'
    isPhoneValid.value = false
    return
  }
  
  errors.value.phone = ''
  isPhoneValid.value = true
}

// 验证验证码
const validateCaptcha = () => {
  const captcha = form.value.captcha
  if (!captcha) {
    errors.value.captcha = '请输入验证码'
    return
  }
  
  if (captcha.length !== 4) {
    errors.value.captcha = '验证码为4位数字'
    return
  }
  
  errors.value.captcha = ''
}

// 验证新密码
const validateNewPassword = () => {
  const password = form.value.newPassword
  if (!password) {
    errors.value.newPassword = '请设置新密码'
    return
  }
  
  if (password.length < 8 || password.length > 16) {
    errors.value.newPassword = '密码长度为8-16位'
    return
  }
  
  let strength = 0
  if (/\d/.test(password)) strength++
  if (/[a-zA-Z]/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++
  
  if (strength < 2) {
    errors.value.newPassword = '密码至少包含两种字符类型'
    return
  }
  
  errors.value.newPassword = ''
  validateConfirmPassword()
}

// 验证确认密码
const validateConfirmPassword = () => {
  const confirmPassword = form.value.confirmPassword
  if (!confirmPassword) {
    errors.value.confirmPassword = '请确认新密码'
    return
  }
  
  if (confirmPassword !== form.value.newPassword) {
    errors.value.confirmPassword = '两次输入的密码不一致'
    return
  }
  
  errors.value.confirmPassword = ''
}

// 发送验证码
const sendCaptcha = async () => {
  if (!isPhoneValid.value) {
    validatePhone()
    return
  }
  
  try {
    // 调用后端API发送验证码
    const response = await fetch('http://localhost:8000/api/v1/forget/send-code', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ phone: form.value.phone })
    })
    
    if (response.ok) {
      const data = await response.json()
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
      
      alert(data.message || '验证码已发送')
    } else {
      const errorData = await response.json()
      alert(`发送验证码失败: ${errorData.detail || '发送失败，请重试'}`)
    }
  } catch (error) {
    console.error('发送验证码失败', error)
    alert('发送验证码失败，请检查网络连接')
  }
}

// 提交处理
const handleSubmit = async () => {
  if (isSubmitting.value) return
  
  // 验证表单
  validatePhone()
  validateNewPassword()
  validateConfirmPassword()
  
  if (!isFormValid.value) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    // 调用后端API重置密码
    const response = await fetch('http://localhost:8000/api/v1/forget/reset-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        phone: form.value.phone,
        new_password: form.value.newPassword
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      console.log('密码重置成功', data)
      
      alert(data.message || '密码重置成功！')
      
      // 通知父组件重置成功
      emit('success')
      
      // 关闭弹窗
      emit('close')
    } else {
      const errorData = await response.json()
      alert(`密码重置失败: ${errorData.detail || '重置失败，请重试'}`)
    }
  } catch (error) {
    console.error('密码重置失败', error)
    alert('密码重置失败，请检查网络连接')
  } finally {
    isSubmitting.value = false
  }
}



// 鼠标悬停特效
const hoverCircle = ref(null)
const isAnimating = ref(false)

// 鼠标进入事件
const handleMouseEnter = (e) => {
  if (isAnimating.value) return
  
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
  hoverCircle.value = circle
  isAnimating.value = true
  
  // 动画结束后重置状态
  setTimeout(() => {
    isAnimating.value = false
  }, 500)
}

// 鼠标离开事件
const handleMouseLeave = (e) => {
  if (isAnimating.value || !hoverCircle.value) return
  
  // 计算鼠标离开时的位置
  const rect = e.target.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  // 应用离开动画
  hoverCircle.value.className = 'hover-circle out'
  hoverCircle.value.style.left = x + 'px'
  hoverCircle.value.style.top = y + 'px'
  
  isAnimating.value = true
  
  // 动画结束后移除元素
  setTimeout(() => {
    if (hoverCircle.value && hoverCircle.value.parentNode) {
      hoverCircle.value.parentNode.removeChild(hoverCircle.value)
    }
    hoverCircle.value = null
    isAnimating.value = false
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
  position: relative;
}

.login-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: rgb(255, 124, 75);
  margin-bottom: 0.5rem;
  line-height: 1.3;
  letter-spacing: -0.02em;
  transition: color 0.3s ease;
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
  border-color: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.1);
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid #94a3b8;
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

.form-input.input-error::placeholder {
  color: #ef4444;
}

.form-input.input-error {
  border-color: #ef4444;
}

/* 密码包装器 */
.password-wrapper {
  position: relative;
}

.password-wrapper .form-input {
  padding-right: 3rem;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 1;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
}

.password-toggle:hover {
  color: #64748b;
  background: rgba(0, 0, 0, 0.05);
}

.password-toggle .icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* 密码规则 */
.password-rule {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.5rem;
  text-align: left;
}

/* 密码强度 */
.password-strength {
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.strength-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.strength-bar.weak {
  background: #ef4444;
  width: 25%;
}

.strength-bar.medium {
  background: #f59e0b;
  width: 50%;
}

.strength-bar.strong {
  background: #10b981;
  width: 75%;
}

.strength-bar.very-strong {
  background: #3b82f6;
  width: 100%;
}

.strength-text {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

/* 验证码包装器 */
.captcha-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
}

/* 验证码输入框 */
.captcha-wrapper .form-input {
  flex: 1;
  padding-right: 1rem;
  min-width: 0;
}

/* 验证码按钮 */
.captcha-button {
  padding: 1rem 1.25rem;
  background: white;
  border-left: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 0.875rem;
  font-weight: 600;
  color: rgb(255, 124, 75);
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.01em;
  white-space: nowrap;
  min-width: 120px;
  text-align: center;
}

.captcha-button:hover:not(:disabled) {
  background: rgba(255, 124, 75, 0.1);
}

.captcha-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

/* 取消按钮 */
.cancel-button {
  flex: 1;
  padding: 1rem 1.5rem;
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.01em;
}

.cancel-button:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.cancel-button:active {
  transform: translateY(0);
  box-shadow: none;
}

/* 登录按钮 */
.login-button {
  flex: 2;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, rgb(255, 124, 75) 0%, rgb(255, 92, 25) 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px rgba(255, 124, 75, 0.35);
  letter-spacing: 0.01em;
}

.login-button.full-width {
  flex: 1;
  width: 100%;
}

.login-button:hover:not(:disabled) {
  background: linear-gradient(135deg, rgb(255, 92, 25) 0%, rgb(255, 124, 75) 100%);
  box-shadow: 0 6px 20px rgba(245, 98, 43, 0.45);
  transform: translateY(-1px);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(255, 124, 75, 0.35);
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

/* 错误信息 */
.error-message {
  font-size: 0.75rem;
  color: #ef4444;
  margin-top: 0.5rem;
  text-align: left;
}

/* 信息提示 */
.info-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.5;
}

.info-message .icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
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
  
  .login-button,
  .cancel-button {
    padding: 0.875rem 1.5rem;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .cancel-button,
  .login-button {
    width: 100%;
  }
}

@media (max-width: 380px) {
  .card-content {
    padding: 1.5rem;
  }
  
  .login-title {
    font-size: 1.375rem;
  }
}

/* 鼠标悬停特效 */
:global(.hover-circle) {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 236, 205, 1);
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
  .cancel-button,
  .password-toggle,
  .captcha-button,
  :global(.hover-circle) {
    transition: none;
    animation: none;
  }
  
  .spinner {
    animation: none;
  }
}
</style>