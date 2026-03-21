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
          @click="handleRoleClick($event, 'teacher')"
        >
          老师
        </button>
        <button 
          class="role-button student-button" 
          :class="{ active: selectedRole === 'student' }"
          @click="handleRoleClick($event, 'student')"
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
              :placeholder="errors.phone || '请输入手机号'"
              @focus="handleInputFocus"
              @blur="handleInputBlur; validateField('phone')"
              :class="{ 'input-error': errors.phone }"
            />
          </div>
        </div>
        
        <!-- 学号/工号输入框 -->
        <div class="form-group">
          <div class="input-wrapper">
            <div class="input-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
            <input
              v-model="form.idNumber"
              type="text"
              class="form-input"
              :placeholder="errors.idNumber || (selectedRole === 'student' ? '请输入学号' : '请输入工号')"
              @focus="handleInputFocus"
              @blur="handleInputBlur; validateField('idNumber')"
              :class="{ 'input-error': errors.idNumber }"
            />
          </div>
        </div>
        
        <!-- 验证码输入框 - 暂时隐藏，短信服务未开通 -->
        <div class="form-group" style="display: none;">
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
        
        <!-- 短信服务暂停提示 -->
        <div class="form-group">
          <div class="info-message">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>短信服务暂未开通，验证码功能暂不可用</span>
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
              :placeholder="errors.password || '设置密码'"
              @focus="handleInputFocus"
              @blur="handleInputBlur; validateField('password')"
              :class="{ 'input-error': errors.password }"
            />
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
        <a href="https://homewh.chaoxing.com/agree/privacyPolicy?appId=900001" target="_blank" class="agreement-link" :class="{ 'teacher-theme': selectedRole === 'teacher', 'student-theme': selectedRole === 'student' }">《隐私政策》</a>
        <span class="agreement-text">和</span>
        <a href="https://homewh.chaoxing.com/agree/userAgreement?appId=900001" target="_blank" class="agreement-link" :class="{ 'teacher-theme': selectedRole === 'teacher', 'student-theme': selectedRole === 'student' }">《用户协议》</a>
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
const isSubmitting = ref(false)
const countdown = ref(0)

// 表单数据
const form = ref({
  phone: '',
  idNumber: '',
  captcha: '',
  password: ''
})

// 验证错误信息
const errors = ref({
  phone: '',
  idNumber: '',
  password: ''
})

// 输入状态跟踪
const inputStatus = ref({
  phone: false, // 是否已经输入过
  idNumber: false, // 是否已经输入过
  password: false // 是否已经输入过
})

// 验证规则
const validatePhone = (phone) => {
  if (!phone) {
    return '请输入手机号'
  }
  if (!/^1[3-9]\d{9}$/.test(phone)) {
    return '请输入正确的中国大陆11位手机号'
  }
  return ''
}

const validateIdNumber = (idNumber, role) => {
  if (!idNumber) {
    return role === 'student' ? '请输入学号' : '请输入工号'
  }
  // 根据实际业务规则设置验证格式
  // 示例：学号/工号为6-20位字母和数字组合
  if (!/^[a-zA-Z0-9]{6,20}$/.test(idNumber)) {
    return role === 'student' ? '学号格式不正确，应包含6-20位字母和数字' : '工号格式不正确，应包含6-20位字母和数字'
  }
  return ''
}

const validatePassword = (password) => {
  if (!password) {
    return '请设置密码'
  }
  if (password.length < 8) {
    return '密码长度至少为8位'
  }
  if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/.test(password)) {
    return '密码应包含大小写字母、数字和特殊符号'
  }
  return ''
}

// 验证字段（仅在失焦或提交时调用）
const validateField = (field) => {
  // 标记该字段已经输入过
  inputStatus.value[field] = true
  
  switch (field) {
    case 'phone':
      errors.value.phone = validatePhone(form.value.phone)
      break
    case 'idNumber':
      errors.value.idNumber = validateIdNumber(form.value.idNumber, selectedRole.value)
      break
    case 'password':
      errors.value.password = validatePassword(form.value.password)
      break
  }
}

// 验证所有字段
const validateAllFields = () => {
  // 标记所有字段为已输入
  inputStatus.value.phone = true
  inputStatus.value.idNumber = true
  inputStatus.value.password = true
  
  // 验证所有字段
  errors.value.phone = validatePhone(form.value.phone)
  errors.value.idNumber = validateIdNumber(form.value.idNumber, selectedRole.value)
  errors.value.password = validatePassword(form.value.password)
  
  // 检查是否所有字段都验证通过
  return !errors.value.phone && !errors.value.idNumber && !errors.value.password
}

// 计算属性
const isFormValid = computed(() => {
  // 只有当所有字段都输入且验证通过时，表单才有效
  return selectedRole.value && 
         form.value.phone && 
         form.value.idNumber && 
         form.value.password &&
         !errors.value.phone &&
         !errors.value.idNumber &&
         !errors.value.password
})

// 选择角色
const selectRole = (role) => {
  selectedRole.value = role
  // 切换角色后，如果用户已经输入过学号/工号，则重新验证
  if (inputStatus.value.idNumber) {
    validateField('idNumber')
  }
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
  
  // 验证所有字段
  if (!validateAllFields()) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    // 准备注册数据
    const registerData = {
      phone: form.value.phone,
      password: form.value.password,
      name: '用户', // 暂时使用默认名称，实际项目中应该添加姓名输入字段
    }
    
    // 根据角色添加不同的字段
    if (selectedRole.value === 'student') {
      registerData.username = form.value.idNumber
      registerData.student_id = form.value.idNumber
    } else {
      registerData.username = form.value.idNumber
      registerData.teacher_id = form.value.idNumber
    }
    
    // 调用后端注册API
    const response = await fetch(`http://localhost:8000/api/v1/register/${selectedRole.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(registerData)
    })
    
    if (response.ok) {
      const data = await response.json()
      console.log('注册成功', data)
      
      // 保存登录状态
      localStorage.setItem('session_id', data.session_id || 'mock-session')
      localStorage.setItem('userRole', selectedRole.value)
      localStorage.setItem('userId', form.value.idNumber)
      localStorage.setItem('user_info', JSON.stringify(data.user || { username: form.value.idNumber, role: selectedRole.value }))
      
      alert('注册成功！')
      
      // 通知父组件注册成功
      emit('success')
      
      // 根据角色处理后续流程
      if (selectedRole.value === 'teacher') {
        // 老师直接跳转到对应页面
        router.push('/ppt-show2')
      } else {
        // 学生触发NamePopup弹窗来收集个人信息
        emit('showNamePopup')
      }
    } else {
      const errorData = await response.json()
      alert(`注册失败: ${errorData.detail || '注册失败，请重试'}`)
    }
  } catch (error) {
    console.error('注册失败', error)
    alert('注册失败，请检查网络连接')
  } finally {
    isSubmitting.value = false
  }
}

// 鼠标悬停特效
const hoverCircle = ref(null)
const isAnimating = ref(false)
const animationTimer = ref(null)

// 动画配置
const animationConfig = {
  duration: 400, // 动画时长，符合300-500ms要求
  easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)' // 缓动函数，提供自然的动画效果
}

// 防抖函数
const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// 鼠标进入事件（防抖处理）
const handleMouseEnter = debounce((e) => {
  if (isAnimating.value) return
  
  // 计算鼠标在容器内的位置（精准捕获，误差不超过2px）
  const rect = e.target.getBoundingClientRect()
  const x = Math.round(e.clientX - rect.left)
  const y = Math.round(e.clientY - rect.top)
  
  // 清除之前的动画
  if (hoverCircle.value) {
    if (hoverCircle.value.parentNode) {
      hoverCircle.value.parentNode.removeChild(hoverCircle.value)
    }
    hoverCircle.value = null
  }
  
  // 创建圆形元素
  const circle = document.createElement('div')
  circle.className = `hover-circle in ${selectedRole.value}-theme`
  circle.style.left = x + 'px'
  circle.style.top = y + 'px'
  
  e.target.appendChild(circle)
  hoverCircle.value = circle
  isAnimating.value = true
  
  // 动画结束后重置状态
  if (animationTimer.value) {
    clearTimeout(animationTimer.value)
  }
  animationTimer.value = setTimeout(() => {
    isAnimating.value = false
  }, animationConfig.duration)
}, 50)

// 鼠标离开事件
const handleMouseLeave = debounce((e) => {
  if (isAnimating.value || !hoverCircle.value) return
  
  // 计算鼠标离开时的位置（精准捕获，误差不超过2px）
  const rect = e.target.getBoundingClientRect()
  const x = Math.round(e.clientX - rect.left)
  const y = Math.round(e.clientY - rect.top)
  
  // 应用离开动画
  hoverCircle.value.className = `hover-circle out ${selectedRole.value}-theme`
  hoverCircle.value.style.left = x + 'px'
  hoverCircle.value.style.top = y + 'px'
  
  isAnimating.value = true
  
  // 动画结束后移除元素
  if (animationTimer.value) {
    clearTimeout(animationTimer.value)
  }
  animationTimer.value = setTimeout(() => {
    if (hoverCircle.value && hoverCircle.value.parentNode) {
      hoverCircle.value.parentNode.removeChild(hoverCircle.value)
    }
    hoverCircle.value = null
    isAnimating.value = false
  }, animationConfig.duration)
}, 50)

// 角色按钮点击事件
const handleRoleClick = (e, role) => {
  // 计算点击位置
  const rect = e.currentTarget.getBoundingClientRect()
  const cardRect = e.currentTarget.closest('.login-card').getBoundingClientRect()
  const x = Math.round(e.clientX - cardRect.left)
  const y = Math.round(e.clientY - cardRect.top)
  
  // 切换角色
  selectedRole.value = role
  
  // 创建点击扩散效果
  if (!isAnimating.value) {
    // 清除之前的动画
    if (hoverCircle.value) {
      if (hoverCircle.value.parentNode) {
        hoverCircle.value.parentNode.removeChild(hoverCircle.value)
      }
      hoverCircle.value = null
    }
    
    // 创建圆形元素
    const circle = document.createElement('div')
    circle.className = `hover-circle in ${selectedRole.value}-theme click-effect`
    circle.style.left = x + 'px'
    circle.style.top = y + 'px'
    
    const card = e.currentTarget.closest('.login-card')
    card.appendChild(circle)
    hoverCircle.value = circle
    isAnimating.value = true
    
    // 动画结束后重置状态
    if (animationTimer.value) {
      clearTimeout(animationTimer.value)
    }
    animationTimer.value = setTimeout(() => {
      isAnimating.value = false
    }, animationConfig.duration)
  }
  
  // 切换角色后，如果用户已经输入过学号/工号，则重新验证
  if (inputStatus.value.idNumber) {
    validateField('idNumber')
  }
}
</script>

<style scoped>
/* 登录卡片 */
.login-card {
  position: relative;
  z-index: 3;
  width: 100%;
  max-width: 400px;
  background: #FFFFFF;
  backdrop-filter: blur(24px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid #E2E8F0;
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
  color: rgb(0, 138, 197);
}

.login-title.student-theme {
  color: rgb(255, 124, 75);
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
  color: rgb(0, 138, 197);
  border-color: rgb(0, 138, 197);
}

.teacher-button.active {
  background: rgb(0, 138, 197);
  color: white;
  border-color: rgb(0, 138, 197);
}

.student-button {
  color: rgb(255, 124, 75);
  border-color: rgb(255, 124, 75);
}

.student-button.active {
  background: rgb(255, 124, 75);
  color: white;
  border-color: rgb(255, 124, 75);
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
  background: white;
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

/* 输入框聚焦效果 */
.input-wrapper.input-focused {
  border-color: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.1);
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



/* 密码规则 */
.password-rule {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.5rem;
  text-align: left;
}

/* 错误信息 */
.error-message {
  font-size: 0.75rem;
  color: #ef4444;
  margin-top: 0.5rem;
  text-align: left;
  line-height: 1.4;
}

/* 信息提示 */
.info-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  font-size: 0.875rem;
  color: #3b82f6;
  line-height: 1.5;
}

.info-message .icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
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
  background: linear-gradient(135deg, rgb(0, 138, 197) 0%, rgb(0, 110, 158) 100%);
  box-shadow: 0 4px 14px rgba(0, 138, 197, 0.35);
}

.login-button.student-theme {
  background: linear-gradient(135deg, rgb(255, 124, 75) 0%, rgb(255, 92, 25) 100%);
  box-shadow: 0 4px 14px rgba(255, 124, 75, 0.35);
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
  color: rgb(0, 138, 197);
}

.agreement-link.student-theme {
  color: rgb(255, 124, 75);
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
  will-change: transform, scale, opacity;
  /* 使用CSS硬件加速 */
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}

:global(.hover-circle.in) {
  width: 10px;
  height: 10px;
  opacity: 1;
  animation: hoverIn 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

:global(.hover-circle.out) {
  width: 1200px;
  height: 1200px;
  opacity: 1;
  animation: hoverOut 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

/* 点击效果 */
:global(.hover-circle.click-effect) {
  animation: hoverIn 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

/* 老师角色颜色 - 透明度为1 */
:global(.hover-circle.teacher-theme) {
  background: rgba(205, 244, 255, 1); /* 老师主题色，透明度为1 */
}

/* 学生角色颜色 - 透明度为1 */
:global(.hover-circle.student-theme) {
  background: rgba(255, 236, 205, 1); /* 学生主题色，透明度为1 */
}

@keyframes hoverIn {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0.5;
  }
  100% {
    transform: translate(-50%, -50%) scale(300); /* 增大缩放比例，确保完全覆盖整个卡片 */
    opacity: 0.1;
  }
}

@keyframes hoverOut {
  0% {
    transform: translate(-50%, -50%) scale(300);
    opacity: 0.1;
  }
  100% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
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