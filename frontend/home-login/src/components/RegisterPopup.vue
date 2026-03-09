<template>
  <div class="login-card" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
    <div class="card-content">

      
      <!-- 标题 -->
      <div class="login-header">
        <h1 class="login-title" :class="{ 'teacher-theme': selectedRole === 'teacher', 'student-theme': selectedRole === 'student' }">注册账号</h1>
        <p class="login-subtitle">请填写以下信息完成注册</p>
      </div>
      
      <!-- 身份选择区 -->
      <div class="role-selection">
        <button 
          class="role-button teacher-button" 
          :class="{ active: selectedRole === 'teacher' }"
          @click="selectRole('teacher')"
        >
          老师
        </button>
        <button 
          class="role-button student-button" 
          :class="{ active: selectedRole === 'student' }"
          @click="selectRole('student')"
        >
          学生
        </button>
      </div>
      
      <!-- 注册表单 -->
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
              placeholder="请输入手机号"
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
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <input
              v-model="form.captcha"
              type="text"
              class="form-input"
              placeholder="验证码"
              @focus="handleInputFocus"
              @blur="handleInputBlur"
            />
            <button 
              type="button" 
              class="captcha-button" 
              :class="{ 'teacher-theme': selectedRole === 'teacher', 'student-theme': selectedRole === 'student' }"
              @click="sendCaptcha"
              :disabled="countdown > 0"
            >
              {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
            </button>
          </div>
        </div>
        
        <!-- 密码输入框 -->
        <div class="form-group">
          <div class="input-wrapper password-wrapper">
            <div class="input-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
            </div>
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="设置密码"
              @focus="handleInputFocus"
              @blur="handleInputBlur"
            />
            <button class="password-toggle" @click.prevent="togglePassword">
              <svg v-show="!showPassword" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"></path>
                <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"></path>
                <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"></path>
                <line x1="2" y1="2" x2="22" y2="22"></line>
              </svg>
              <svg v-show="showPassword" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
            </button>
          </div>
          <p class="password-rule">密码要求 8-16 位，至少包含数字、字母、字符两种元素</p>
        </div>
        
        <!-- 注册按钮 -->
        <button
          type="submit"
          class="login-button"
          :class="{ 'teacher-theme': selectedRole === 'teacher', 'student-theme': selectedRole === 'student' }"
          :disabled="!isFormValid"
        >
          <span v-if="!isSubmitting">注册</span>
          <span v-else class="loading">
            <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle class="spinner-track" cx="12" cy="12" r="10" stroke-opacity="0.2"/>
              <path class="spinner-path" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            注册中...
          </span>
        </button>
      </form>
      
      <!-- 协议区 -->
      <div class="agreement-section">
        <span class="agreement-text">我已阅读并同意学习通</span>
        <a href="#" class="agreement-link" :class="{ 'teacher-theme': selectedRole === 'teacher', 'student-theme': selectedRole === 'student' }">《隐私政策》</a>
        <span class="agreement-text">和</span>
        <a href="#" class="agreement-link" :class="{ 'teacher-theme': selectedRole === 'teacher', 'student-theme': selectedRole === 'student' }">《用户协议》</a>
      </div>
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
const selectedRole = ref('student')
const showPassword = ref(false)
const isSubmitting = ref(false)
const countdown = ref(0)

// 表单数据
const form = ref({
  phone: '',
  captcha: '',
  password: ''
})

// 计算属性
const isFormValid = computed(() => {
  return selectedRole.value && form.value.phone && form.value.captcha && form.value.password
})

// 选择角色
const selectRole = (role) => {
  selectedRole.value = role
}

// 切换密码显示
const togglePassword = () => {
  showPassword.value = !showPassword.value
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

// 发送验证码
const sendCaptcha = () => {
  if (!form.value.phone) {
    alert('请输入手机号')
    return
  }
  
  // 模拟发送验证码
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
  
  alert('验证码已发送')
}

// 提交处理
const handleSubmit = async () => {
  if (isSubmitting.value) return
  
  // 简单验证
  if (!isFormValid.value) {
    alert('请填写所有字段')
    return
  }
  
  isSubmitting.value = true
  
  try {
    // 模拟注册请求
    await new Promise(resolve => setTimeout(resolve, 1500))
    console.log('注册成功', form.value)
    
    // 保存登录状态
    localStorage.setItem('token', 'mock-token') // 模拟token
    localStorage.setItem('userRole', selectedRole.value)
    
    alert('注册成功！')
    
    // 通知父组件注册成功
    emit('success')
    
    // 根据角色跳转到不同页面
    if (selectedRole.value === 'teacher') {
      router.push('/ppt-show2')
    } else {
      router.push('/ppt-show')
    }
  } catch (error) {
    console.error('注册失败', error)
    alert('注册失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}

// 鼠标悬停特效
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
  circle.className = `hover-circle in ${selectedRole.value}-theme`
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
  hoverCircle.className = `hover-circle out ${selectedRole.value}-theme`
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

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 2rem;
  position: relative;
}

.login-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #94a3b8;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  letter-spacing: -0.02em;
  transition: color 0.3s ease;
}



.login-title.teacher-theme {
  color: #3283fd;
}

.login-title.student-theme {
  color: #f5622b;
}

.login-subtitle {
  font-size: 0.9375rem;
  color: #64748b;
  line-height: 1.6;
  letter-spacing: 0.01em;
}

/* 身份选择区 */
.role-selection {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.role-button {
  flex: 1;
  padding: 0.75rem;
  border-radius: 12px;
  border: 2px solid;
  background: white;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.teacher-button {
  color: #318de2;
  border-color: #318de2;
}

.teacher-button.active {
  background: #3283fd;
  color: white;
  border-color: #3283fd;
}

.student-button {
  color: #f5622b;
  border-color: #f5622b;
}

.student-button.active {
  background: #f5622b;
  color: white;
  border-color: #f5622b;
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

/* 验证码按钮 */
.captcha-button {
  padding: 1rem 1.25rem;
  background: none;
  border-left: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.01em;
  white-space: nowrap;
}

.captcha-button.teacher-theme {
  color: #3283fd;
}

.captcha-button.student-theme {
  color: #f5622b;
}

.captcha-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 注册按钮 */
.login-button {
  width: 100%;
  padding: 1rem 1.5rem;
  background: #94a3b8;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px rgba(148, 163, 184, 0.35);
  letter-spacing: 0.01em;
  margin-top: 0.5rem;
}

.login-button.teacher-theme {
  background: linear-gradient(135deg, #3283fd 0%, #318de2 100%);
  box-shadow: 0 4px 14px rgba(50, 131, 253, 0.35);
}

.login-button.student-theme {
  background: linear-gradient(135deg, #f5622b 0%, #ff8a3d 100%);
  box-shadow: 0 4px 14px rgba(245, 98, 43, 0.35);
}

.login-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(148, 163, 184, 0.45);
}

.login-button.teacher-theme:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(50, 131, 253, 0.45);
}

.login-button.student-theme:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(245, 98, 43, 0.45);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(148, 163, 184, 0.35);
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

/* 协议区 */
.agreement-section {
  text-align: center;
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.agreement-text {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  letter-spacing: 0.01em;
}

.agreement-link {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s ease;
  letter-spacing: 0.01em;
}

.agreement-link.teacher-theme {
  color: #3283fd;
}

.agreement-link.student-theme {
  color: #f5622b;
}

.agreement-link:hover {
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
  
  .role-selection {
    flex-direction: column;
  }
}

@media (max-width: 380px) {
  .card-content {
    padding: 1.5rem;
  }
  
  .login-title {
    font-size: 1.375rem;
  }
  
  .agreement-section {
    flex-direction: column;
    gap: 0.5rem;
  }
}

/* 鼠标悬停特效 */
:global(.hover-circle) {
  position: absolute;
  border-radius: 50%;
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

/* 老师角色颜色 */
:global(.hover-circle.teacher-theme) {
  background: rgba(202, 127, 255, 0.3);
}

/* 学生角色颜色 */
:global(.hover-circle.student-theme) {
  background: rgba(255, 215, 0, 0.3);
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

/* 卡片内容 */
.card-content {
  padding: 2.5rem;
  position: relative;
  z-index: 1;
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .login-card,
  .input-wrapper,
  .login-button,
  .close-button,
  .password-toggle,
  :global(.hover-circle) {
    transition: none;
    animation: none;
  }
  
  .spinner {
    animation: none;
  }
}
</style>