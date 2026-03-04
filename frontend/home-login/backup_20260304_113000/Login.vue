<template>
  <!-- 简化后的登录弹窗（无外层卡片、无关闭按钮、无背景） -->
  <div class="login-modal">
    <!-- 登录表单核心区域 -->
    <div class="login-form-container">
      <!-- 登录表单标题 -->
      <div class="login-form-header">
        <h1 class="login-title">欢迎回来</h1>
        <p class="login-subtitle">请登录您的账户以继续</p>
      </div>

      <!-- 登录表单 -->
      <form @submit.prevent="handleSubmit" class="login-form" novalidate>
        <!-- 用户名/邮箱输入框 -->
        <div class="form-group">
          <label for="username" class="form-label">
            用户名/邮箱
          </label>
          <div class="input-wrapper">
            <div class="input-icon">
              <svg class="icon-user" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </div>
            <input
              id="username"
              v-model="form.username"
              type="text"
              autocomplete="username"
              :class="[
                'form-input',
                errors.username ? 'input-error' : ''
              ]"
              placeholder="请输入用户名或邮箱"
              @blur="validateField('username')"
              @input="clearError('username')"
              aria-required="true"
              :aria-invalid="errors.username ? 'true' : 'false'"
              :aria-describedby="errors.username ? 'username-error' : undefined"
            />
          </div>
          <p 
            v-if="errors.username" 
            id="username-error" 
            class="error-message"
            role="alert"
          >
            <svg class="error-icon" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
            </svg>
            {{ errors.username }}
          </p>
        </div>

        <!-- 密码输入框 -->
        <div class="form-group">
          <label for="password" class="form-label">
            密码
          </label>
          <div class="input-wrapper">
            <div class="input-icon">
              <svg class="icon-lock" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
            </div>
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              :class="[
                'form-input',
                'input-with-action',
                errors.password ? 'input-error' : ''
              ]"
              placeholder="请输入密码"
              @blur="validateField('password')"
              @input="clearError('password')"
              aria-required="true"
              :aria-invalid="errors.password ? 'true' : 'false'"
              :aria-describedby="errors.password ? 'password-error' : undefined"
            />
            <button
              type="button"
              class="password-toggle"
              @click="togglePasswordVisibility"
              :aria-label="showPassword ? '隐藏密码' : '显示密码'"
              tabindex="-1"
            >
              <svg v-if="!showPassword" class="icon-eye" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
              <svg v-else class="icon-eye-off" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
              </svg>
            </button>
          </div>
          <p 
            v-if="errors.password" 
            id="password-error" 
            class="error-message"
            role="alert"
          >
            <svg class="error-icon" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
            </svg>
            {{ errors.password }}
          </p>
        </div>

        <!-- 记住我和忘记密码 -->
        <div class="form-options">
          <label class="checkbox-wrapper">
            <input
              type="checkbox"
              v-model="form.rememberMe"
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
            忘记密码?
          </button>
        </div>

        <!-- 登录按钮 -->
        <button
          type="submit"
          :disabled="!isFormValid || isSubmitting"
          :class="[
            'submit-button',
            (!isFormValid || isSubmitting) ? 'button-disabled' : 'button-active'
          ]"
        >
          <svg v-if="isSubmitting" class="spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <circle class="spinner-track" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="spinner-path" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isSubmitting ? '登录中...' : '登录' }}
        </button>

        <!-- 第三方登录 -->
        <div class="divider">
          <span class="divider-text">或使用以下方式登录</span>
        </div>

        <div class="social-login">
          <button
            type="button"
            class="social-button"
            @click="handleThirdPartyLogin('wechat')"
          >
            <svg class="social-icon wechat-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.27-.027-.407-.03zm-2.53 3.274c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.969-.982z"/>
            </svg>
            <span>微信登录</span>
          </button>
          <button
            type="button"
            class="social-button"
            @click="handleThirdPartyLogin('qq')"
          >
            <svg class="social-icon qq-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12.003 2c-2.265 0-6.29 1.364-6.29 7.325v1.195S3.55 14.96 3.55 17.474c0 .665.17 1.025.281 1.025.114 0 .902-.484 1.748-2.072 0 0-.18 2.197 1.904 3.967 0 0-1.77.495-1.77 1.182 0 .686 4.078.43 6.29.43 2.21 0 6.287.257 6.287-.43 0-.687-1.768-1.182-1.768-1.182 2.085-1.77 1.905-3.967 1.905-3.967.845 1.588 1.634 2.072 1.746 2.072.111 0 .283-.36.283-1.025 0-2.514-2.166-6.954-2.166-6.954V9.325C18.29 3.364 14.268 2 12.003 2z"/>
            </svg>
            <span>QQ登录</span>
          </button>
        </div>

        <!-- 注册链接 -->
        <div class="register-section">
          <span class="register-text">还没有账户?</span>
          <button
            type="button"
            class="register-link"
            @click="handleRegister"
          >
            立即注册
          </button>
        </div>
      </form>
    </div>

    <!-- 通知组件 -->
    <Transition name="notification">
      <div v-if="notification.show" :class="['notification', `notification-${notification.type}`]" role="alert">
        <div class="notification-content">
          <div class="notification-icon-wrapper">
            <svg v-if="notification.type === 'success'" class="notification-icon success-icon" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            <svg v-else-if="notification.type === 'error'" class="notification-icon error-icon" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
            </svg>
            <svg v-else class="notification-icon info-icon" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
            </svg>
          </div>
          <div class="notification-text">
            <h3 class="notification-title">{{ notification.title }}</h3>
            <p class="notification-message">{{ notification.message }}</p>
          </div>
          <button 
            @click="closeNotification" 
            class="notification-close"
            aria-label="关闭通知"
          >
            <svg class="close-icon-small" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const emit = defineEmits(['login-success'])

const form = reactive({
  username: '',
  password: '',
  rememberMe: false
})

const errors = reactive({
  username: '',
  password: ''
})

const showPassword = ref(false)
const isSubmitting = ref(false)

const notification = reactive({
  show: false,
  type: 'success',
  title: '',
  message: ''
})

const isFormValid = computed(() => {
  return form.username.trim() !== '' && 
         form.password !== '' && 
         !errors.username && 
         !errors.password
})

const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const isValidUsername = (username) => {
  const usernameRegex = /^[\w\u4e00-\u9fa5]{3,20}$/
  return usernameRegex.test(username)
}

const validateField = (field) => {
  const value = form[field].trim()
  
  switch (field) {
    case 'username':
      if (!value) {
        errors.username = '请输入用户名或邮箱'
      } else if (value.includes('@')) {
        if (!isValidEmail(value)) {
          errors.username = '请输入有效的邮箱地址'
        } else {
          errors.username = ''
        }
      } else if (!isValidUsername(value)) {
        errors.username = '用户名长度应为3-20个字符，支持字母、数字、下划线和中文'
      } else {
        errors.username = ''
      }
      break
      
    case 'password':
      if (!value) {
        errors.password = '请输入密码'
      } else if (value.length < 6) {
        errors.password = '密码长度至少为6个字符'
      } else if (value.length > 20) {
        errors.password = '密码长度不能超过20个字符'
      } else {
        errors.password = ''
      }
      break
  }
}

const clearError = (field) => {
  errors[field] = ''
}

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const showNotification = (type, title, message, duration = 3000) => {
  notification.type = type
  notification.title = title
  notification.message = message
  notification.show = true
  
  if (duration > 0) {
    setTimeout(() => {
      closeNotification()
    }, duration)
  }
}

const closeNotification = () => {
  notification.show = false
}

const handleForgotPassword = () => {
  showNotification('info', '提示', '密码重置功能即将上线，敬请期待！')
}

const handleRegister = () => {
  showNotification('info', '提示', '注册功能即将上线，敬请期待！')
}

const handleThirdPartyLogin = (provider) => {
  const providerNames = {
    wechat: '微信',
    qq: 'QQ'
  }
  showNotification('info', '提示', `${providerNames[provider]}登录功能即将上线，敬请期待！`)
}

// 移除了handleExit方法（原关闭按钮的逻辑）

const handleSubmit = async () => {
  validateField('username')
  validateField('password')
  
  if (errors.username || errors.password) {
    return
  }
  
  if (isSubmitting.value) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    const sanitizedUsername = escapeHtml(form.username.trim())
    const sanitizedPassword = form.password
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    console.log('登录信息：', {
      username: sanitizedUsername,
      rememberMe: form.rememberMe
    })
    
    if (form.rememberMe) {
      localStorage.setItem('rememberedUsername', sanitizedUsername)
    } else {
      localStorage.removeItem('rememberedUsername')
    }
    
    showNotification('success', '登录成功', '欢迎回来！正在跳转...')
    
    emit('login-success')
    
    setTimeout(() => {
      console.log('跳转到首页')
    }, 1500)
    
  } catch (error) {
    console.error('登录失败：', error)
    showNotification('error', '登录失败', '用户名或密码错误，请重试')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  const rememberedUsername = localStorage.getItem('rememberedUsername')
  if (rememberedUsername) {
    form.username = rememberedUsername
    form.rememberMe = true
  }
})
</script>

<style scoped>
/* 基础弹窗容器 - 无背景、居中展示 */
.login-modal {
  width: 100%;
  max-width: 440px;
  margin: 0 auto;
  padding: 1rem;
}

/* 登录表单核心容器 - 纯表单样式，无背景/阴影/装饰 */
.login-form-container {
  width: 100%;
}

/* 登录表单头部 */
.login-form-header {
  padding: 2.25rem 2rem 1.75rem;
  position: relative;
  z-index: 1;
}

.login-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.3;
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  font-size: 0.9375rem;
  color: #64748b;
  line-height: 1.6;
  letter-spacing: 0.01em;
}

/* 登录表单 */
.login-form {
  padding: 0;
}

/* 表单组 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.625rem;
  letter-spacing: 0.01em;
  line-height: 1.4;
}

/* 输入框包装器 */
.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  z-index: 1;
}

.icon-user,
.icon-lock {
  width: 1.25rem;
  height: 1.25rem;
  color: #9ca3af;
}

/* 表单输入框 */
.form-input {
  width: 100%;
  padding: 0.9375rem 1rem 0.9375rem 2.875rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  font-size: 0.9375rem;
  color: #1f2937;
  background: #ffffff;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  line-height: 1.5;
  letter-spacing: 0.005em;
}

.form-input:hover {
  border-color: #d1d5db;
}

.form-input:focus {
  border-color: #DC2626;
  box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
  letter-spacing: 0.01em;
}

.input-with-action {
  padding-right: 3.25rem;
}

.input-error {
  border-color: #ef4444;
  background: #fef2f2;
}

.input-error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1);
}

/* 密码切换按钮 */
.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  transition: color 0.2s ease;
}

.password-toggle:hover {
  color: #6b7280;
}

.icon-eye,
.icon-eye-off {
  width: 1.25rem;
  height: 1.25rem;
}

/* 错误消息 */
.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.625rem;
  font-size: 0.8125rem;
  color: #ef4444;
  margin-bottom: 0;
  line-height: 1.4;
  letter-spacing: 0.01em;
}

.error-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

/* 表单选项 */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.75rem;
}

/* 复选框 */
.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 0.625rem;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 1.125rem;
  height: 1.125rem;
  border: 2px solid #d1d5db;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background: #ffffff;
}

.checkbox-input:checked + .checkbox-custom {
  background: #DC2626;
  border-color: #DC2626;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '';
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-bottom: 2px;
}

.checkbox-label {
  font-size: 0.875rem;
  color: #4b5563;
  user-select: none;
  font-weight: 500;
  letter-spacing: 0.01em;
  line-height: 1.4;
}

/* 链接按钮 */
.link-button {
  font-size: 0.875rem;
  color: #DC2626;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: color 0.2s ease;
  padding: 0;
  letter-spacing: 0.01em;
  line-height: 1.4;
}

.link-button:hover {
  color: #B91C1C;
  text-decoration: underline;
}

/* 提交按钮 */
.submit-button {
  width: 100%;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  outline: none;
  line-height: 1.4;
  letter-spacing: 0.01em;
}

.button-active {
  background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(220, 38, 38, 0.35);
}

.button-active:hover {
  background: linear-gradient(135deg, #B91C1C 0%, #DC2626 100%);
  box-shadow: 0 6px 20px rgba(220, 38, 38, 0.45);
  transform: translateY(-1px);
}

.button-active:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.35);
}

.button-disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

/* 加载动画 */
.spinner {
  width: 1.25rem;
  height: 1.25rem;
  animation: spin 1s linear infinite;
}

.spinner-track {
  opacity: 0.25;
}

.spinner-path {
  opacity: 0.75;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 分隔线 */
.divider {
  display: flex;
  align-items: center;
  margin: 2rem 0;
  position: relative;
}

.divider::before {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, #e5e7eb);
}

.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(to left, transparent, #e5e7eb);
}

.divider-text {
  padding: 0 1rem;
  font-size: 0.8125rem;
  color: #9ca3af;
  white-space: nowrap;
  font-weight: 500;
  letter-spacing: 0.01em;
  line-height: 1.4;
}

/* 社交登录 */
.social-login {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.875rem;
  margin-bottom: 1.75rem;
}

.social-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  padding: 0.875rem 1rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  background: #ffffff;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  line-height: 1.4;
  letter-spacing: 0.01em;
}

.social-button:hover {
  background: #f9fafb;
  border-color: #d1d5db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.social-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.wechat-icon {
  color: #10B981;
}

.qq-icon {
  color: #3B82F6;
}

/* 注册区域 */
.register-section {
  text-align: center;
  padding-top: 0.75rem;
}

.register-text {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
  line-height: 1.4;
  letter-spacing: 0.01em;
}

.register-link {
  font-size: 0.875rem;
  color: #DC2626;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 600;
  margin-left: 0.375rem;
  transition: color 0.2s ease;
  padding: 0;
  line-height: 1.4;
  letter-spacing: 0.01em;
}

.register-link:hover {
  color: #B91C1C;
  text-decoration: underline;
}

/* 通知组件 */
.notification {
  position: fixed;
  top: 1rem;
  right: 1rem;
  max-width: 400px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(226, 232, 240, 0.8);
  z-index: 100;
  overflow: hidden;
}

.notification-success {
  border-left: 4px solid #10B981;
}

.notification-error {
  border-left: 4px solid #EF4444;
}

.notification-info {
  border-left: 4px solid #3B82F6;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
}

.notification-icon-wrapper {
  flex-shrink: 0;
}

.notification-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.success-icon {
  color: #10B981;
}

.error-icon {
  color: #EF4444;
}

.info-icon {
  color: #3B82F6;
}

.notification-text {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
  margin-top: 0;
}

.notification-message {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.4;
  margin-bottom: 0;
  margin-top: 0;
}

.notification-close {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 6px;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  transition: all 0.2s ease;
  flex-shrink: 0;
  padding: 0;
}

.notification-close:hover {
  background: #f3f4f6;
  color: #6b7280;
}

.close-icon-small {
  width: 1rem;
  height: 1rem;
}

/* 通知动画 */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* 响应式适配 */
@media (max-width: 640px) {
  .login-modal {
    padding: 0.75rem;
    max-width: 100%;
  }
  
  .login-form-header {
    padding: 0 0 1rem;
  }
  
  .login-title {
    font-size: 1.5rem;
  }
  
  .login-subtitle {
    font-size: 0.875rem;
  }
  
  .login-form {
    padding: 0;
  }
  
  .form-input {
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    font-size: 0.9375rem;
  }
  
  .input-icon {
    left: 0.875rem;
  }
  
  .icon-user,
  .icon-lock {
    width: 1.125rem;
    height: 1.125rem;
  }
  
  .social-login {
    grid-template-columns: 1fr;
    gap: 0.625rem;
  }
  
  .notification {
    left: 1rem;
    right: 1rem;
    max-width: none;
    top: auto;
    bottom: 1rem;
  }
}

@media (max-width: 380px) {
  .login-form-header {
    padding: 0 0 0.875rem;
  }
  
  .login-title {
    font-size: 1.375rem;
  }
  
  .form-options {
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .form-input,
  .submit-button,
  .password-toggle,
  .social-button {
    transition: none;
  }
  
  .spinner {
    animation: none;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .form-input {
    border-width: 2px;
  }
  
  .submit-button {
    border: 2px solid #000000;
  }
}
</style>