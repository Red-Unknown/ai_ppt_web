<template>
  <div class="name-popup-overlay" v-if="visible" @click="handleOverlayClick">
    <div class="name-popup" @click.stop>
      <!-- 弹窗头部 -->
      <div class="popup-header">
        <h2 class="popup-title">完善个人信息</h2>
      </div>
      
      <!-- 成功提示 -->
      <div v-if="showSuccess" class="success-message">
        <svg class="success-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 11-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <span>{{ successMessage }}</span>
      </div>
      
      <!-- 弹窗内容 -->
      <div class="popup-content" v-if="!showSuccess">
        <form @submit.prevent="handleSubmit" class="info-form">
          <!-- 姓名输入框 -->
          <div class="form-group">
            <label class="form-label" for="userName">姓名</label>
            <div class="input-wrapper">
              <input
                id="userName"
                v-model="form.user_name"
                type="text"
                class="form-input"
                :placeholder="errors.user_name || '请输入真实姓名'"
                @focus="handleInputFocus"
                @blur="handleInputBlur('user_name')"
                @input="handleInput('user_name')"
                :class="{ 'input-error': errors.user_name }"
              />
            </div>
          </div>
          
          <!-- 头像选择 -->
          <div class="form-group">
            <label class="form-label">头像</label>
            <div class="avatar-section">
              <!-- 预设头像 -->
              <div class="avatar-presets">
                <div
                  v-for="(avatar, index) in presetAvatars"
                  :key="index"
                  class="avatar-item"
                  :class="{ 'avatar-selected': form.avatar === avatar }"
                  @click="selectAvatar(avatar)"
                >
                  <img :src="avatar" :alt="`预设头像 ${index + 1}`" class="avatar-image" />
                </div>
              </div>
              <!-- 自定义头像上传 -->
              <div class="avatar-upload">
                <input
                  type="file"
                  id="avatarUpload"
                  accept="image/jpeg, image/png"
                  @change="handleAvatarUpload"
                  class="avatar-input"
                  :disabled="isSubmitting"
                />
                <label for="avatarUpload" class="avatar-upload-label" :class="{ 'upload-disabled': isSubmitting }">
                  <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  <span>上传头像</span>
                </label>
              </div>
            </div>
            <!-- 头像预览 -->
            <div class="avatar-preview" v-if="form.avatar">
            </div>
          </div>
          
          <!-- 年级选择 -->
          <div class="form-group">
            <label class="form-label" for="grade">年级</label>
            <div class="select-wrapper">
              <select
                id="grade"
                v-model="form.grade"
                class="form-select"
                @change="handleGradeChange"
                @blur="handleInputBlur('grade')"
                :class="{ 'input-error': errors.grade }"
                :disabled="isSubmitting"
              >
                <option value="">{{ errors.grade || '请选择年级' }}</option>
                <option value="大一">大一</option>
                <option value="大二">大二</option>
                <option value="大三">大三</option>
                <option value="大四">大四</option>
                <option value="研究生">研究生</option>
              </select>
            </div>
          </div>
          
          <!-- 专业选择 -->
          <div class="form-group">
            <label class="form-label" for="major">专业</label>
            <div class="select-wrapper">
              <select
                id="major"
                v-model="form.major"
                class="form-select"
                :disabled="!form.grade || isSubmitting"
                @blur="handleInputBlur('major')"
                :class="{ 'input-error': errors.major, 'select-disabled': !form.grade || isSubmitting }"
              >
                <option value="">{{ errors.major || '请选择专业' }}</option>
                <option v-for="major in availableMajors" :key="major" :value="major">
                  {{ major }}
                </option>
              </select>
            </div>
          </div>
          
          <!-- 自我介绍 -->
          <div class="form-group">
            <label class="form-label" for="profileText">自我介绍</label>
            <div class="textarea-wrapper">
              <textarea
                id="profileText"
                v-model="form.profile_text"
                class="form-textarea"
                placeholder="请简要介绍自己，最多500字符"
                rows="5"
                maxlength="500"
                :disabled="isSubmitting"
              ></textarea>
              <div class="char-count">{{ form.profile_text.length }}/500</div>
            </div>
          </div>
          
          <!-- 附加信息 -->
          <div class="form-group">
            <label class="form-label" for="profileExt">附加信息</label>
            <div class="textarea-wrapper">
              <textarea
                id="profileExt"
                v-model="form.profile_ext"
                class="form-textarea"
                placeholder="请填写其他补充信息，最多300字符"
                rows="3"
                maxlength="300"
                :disabled="isSubmitting"
              ></textarea>
              <div class="char-count">{{ form.profile_ext.length }}/300</div>
            </div>
          </div>
          
          <!-- 隐藏字段：创建时间戳 -->
          <input type="hidden" v-model="form.created_at" />
        </form>
      </div>
      
      <!-- 弹窗底部 -->
      <div class="popup-footer" v-if="!showSuccess">
        <button
          type="button"
          class="submit-button"
          :disabled="!isFormValid || isSubmitting"
          @click="handleSubmit"
        >
          <span v-if="!isSubmitting">确认</span>
          <span v-else class="loading">
            <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle class="spinner-track" cx="12" cy="12" r="10" stroke-opacity="0.2"/>
              <path class="spinner-path" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            提交中...
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import boy1 from '@/assets/images/avatars/boy1.png'
import boy2 from '@/assets/images/avatars/boy2.png'
import girl1 from '@/assets/images/avatars/girl1.png'
import girl2 from '@/assets/images/avatars/girl2.png'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'success', 'cancel'])

// 表单数据
const form = ref({
  user_name: '',
  avatar: '',
  grade: '',
  major: '',
  profile_text: '',
  profile_ext: '',
  created_at: Math.floor(Date.now() / 1000) // 精确到秒
})

// 错误信息
const errors = ref({
  user_name: '',
  grade: '',
  major: ''
})

// 状态
const isSubmitting = ref(false)
const showSuccess = ref(false)
const successMessage = ref('')

// 预设头像
const presetAvatars = ref([
  boy1, // boy1.png
  boy2, // boy2.png
  girl1, // girl1.png
  girl2  // girl2.png
])

// 专业选项（根据年级动态加载）
const availableMajors = ref([])

// 年级对应的专业
const gradeMajors = {
  '大一': ['计算机科学与技术', '软件工程', '数据科学', '人工智能', '信息安全'],
  '大二': ['计算机科学与技术', '软件工程', '数据科学', '人工智能', '信息安全', '网络工程'],
  '大三': ['计算机科学与技术', '软件工程', '数据科学', '人工智能', '信息安全', '网络工程', '物联网工程'],
  '大四': ['计算机科学与技术', '软件工程', '数据科学', '人工智能', '信息安全', '网络工程', '物联网工程'],
  '研究生': ['计算机科学与技术', '软件工程', '数据科学', '人工智能', '信息安全', '网络工程', '物联网工程', '云计算']
}

// 计算属性：表单是否有效
const isFormValid = computed(() => {
  return (
    form.value.user_name.trim() !== '' &&
    form.value.grade !== '' &&
    form.value.major !== '' &&
    !errors.value.user_name &&
    !errors.value.grade &&
    !errors.value.major
  )
})

// 选择头像
const selectAvatar = (avatar) => {
  if (isSubmitting.value) return
  form.value.avatar = avatar
}

// 处理头像上传
const handleAvatarUpload = (event) => {
  if (isSubmitting.value) return
  
  const file = event.target.files[0]
  if (file) {
    // 验证文件大小
    if (file.size > 2 * 1024 * 1024) {
      alert('文件大小不能超过2MB')
      return
    }
    
    // 验证文件类型
    if (!file.type.match('image/jpeg') && !file.type.match('image/png')) {
      alert('只支持JPG和PNG格式的图片')
      return
    }
    
    // 创建预览
    const reader = new FileReader()
    reader.onload = (e) => {
      form.value.avatar = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// 年级变化时更新专业选项
const handleGradeChange = () => {
  if (isSubmitting.value) return
  
  if (form.value.grade) {
    availableMajors.value = gradeMajors[form.value.grade]
    form.value.major = '' // 重置专业选择
    validateField('grade')
  } else {
    availableMajors.value = []
  }
}

// 输入框聚焦处理
const handleInputFocus = (event) => {
  const inputWrapper = event.target.closest('.input-wrapper')
  if (inputWrapper) {
    inputWrapper.classList.add('input-focused')
  }
}

// 输入处理（实时验证）
const handleInput = (field) => {
  validateField(field)
}

// 输入框失焦处理
const handleInputBlur = (field) => {
  validateField(field)
}

// 验证字段
const validateField = (field) => {
  switch (field) {
    case 'user_name':
      if (!form.value.user_name.trim()) {
        errors.value.user_name = '请输入姓名'
      } else if (form.value.user_name.length > 20) {
        errors.value.user_name = '姓名长度不能超过20个字符'
      } else {
        errors.value.user_name = ''
      }
      break
    case 'grade':
      if (!form.value.grade) {
        errors.value.grade = '请选择年级'
      } else {
        errors.value.grade = ''
      }
      break
    case 'major':
      if (!form.value.major) {
        errors.value.major = '请选择专业'
      } else {
        errors.value.major = ''
      }
      break
  }
}

// 验证所有字段
const validateAllFields = () => {
  validateField('user_name')
  validateField('grade')
  validateField('major')
  return isFormValid.value
}

// 提交处理
const handleSubmit = async () => {
  if (isSubmitting.value) return
  
  // 验证表单
  if (!validateAllFields()) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    // 准备提交数据
    const submitData = {
      ...form.value,
      created_at: Math.floor(Date.now() / 1000) // 精确到秒
    }
    
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 1500))
    console.log('提交的用户信息:', submitData)
    
    // 提交成功
    showSuccessMessage('信息提交成功！')
    emit('success', submitData)
    
    // 3秒后关闭弹窗
    setTimeout(() => {
      resetForm()
      handleClose()
    }, 3000)
  } catch (error) {
    console.error('提交失败:', error)
    alert('提交失败，请稍后重试')
  } finally {
    isSubmitting.value = false
  }
}

// 显示成功消息
const showSuccessMessage = (message) => {
  successMessage.value = message
  showSuccess.value = true
}

// 取消操作
const handleCancel = () => {
  if (isSubmitting.value) return
  
  emit('cancel')
  resetForm()
  handleClose()
}

// 关闭弹窗
const handleClose = () => {
  emit('close')
}

// 点击遮罩层关闭
const handleOverlayClick = () => {
  if (isSubmitting.value) return
  handleClose()
}

// 重置表单
const resetForm = () => {
  form.value = {
    user_name: '',
    avatar: presetAvatars.value[0], // 默认选中第一个预设头像
    grade: '',
    major: '',
    profile_text: '',
    profile_ext: '',
    created_at: Math.floor(Date.now() / 1000) // 精确到秒
  }
  errors.value = {
    user_name: '',
    grade: '',
    major: ''
  }
  availableMajors.value = []
  showSuccess.value = false
  successMessage.value = ''
}

// 初始化
onMounted(() => {
  // 默认选中第一个预设头像
  if (!form.value.avatar && presetAvatars.value.length > 0) {
    form.value.avatar = presetAvatars.value[0]
  }
})

// 监听visible变化，重置表单
watch(() => props.visible, (newValue) => {
  if (newValue) {
    // 重置表单
    resetForm()
  }
})
</script>

<style scoped>
/* 弹窗遮罩 */
.name-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
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

/* 弹窗容器 */
.name-popup {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
}

/* 隐藏滚动条但保留滚动功能 */
.name-popup::-webkit-scrollbar {
  display: none;
}

.name-popup {
  -ms-overflow-style: none;
  scrollbar-width: none;
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

/* 弹窗头部 */
.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.popup-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #FF7C4B;
  margin: 0;
  text-align: center;
  flex: 1;
}

.close-button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #334155;
}

.close-button .icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* 成功提示 */
.success-message {
  background: rgba(16, 185, 129, 0.1);
  border-left: 4px solid #10b981;
  padding: 1.5rem 2rem;
  margin: 1rem 2rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
  animation: successFadeIn 0.3s ease;
}

@keyframes successFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.success-icon {
  width: 2rem;
  height: 2rem;
  color: #10b981;
  flex-shrink: 0;
}

.success-message span {
  color: #059669;
  font-weight: 600;
  font-size: 0.9375rem;
}

/* 弹窗内容 */
.popup-content {
  padding: 2rem;
  flex: 1;
}

/* 表单 */
.info-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 表单组 */
.form-group {
  width: 100%;
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}

.form-label {
  width: 80px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  margin: 0;
  padding-top: 0.75rem;
  flex-shrink: 0;
  text-align: right;
}

.form-group > div {
  flex: 1;
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

.input-wrapper.input-focused {
  border-color: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.1);
  border: 1px solid #94a3b8;
}

/* 输入框 */
.form-input {
  width: 100%;
  padding: 1rem;
  border: none;
  background: white;
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

/* 选择框 */
.select-wrapper {
  position: relative;
  border-radius: 12px;
  background: white;
  border: none;
  overflow: hidden;
}

.form-select {
  width: 100%;
  padding: 1rem;
  border: none;
  background: white;
  font-size: 0.9375rem;
  color: #1e293b;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1.25rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.form-select:focus {
  border-color: #FF7C4B;
  box-shadow: 0 0 0 3px rgba(255, 124, 75, 0.1);
  border: 1px solid #FF7C4B;
  outline: none;
}

.form-select.select-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-select.input-error {
  border-color: #ef4444;
  color: #ef4444;
}

/* 头像部分 */
.avatar-section {
  margin-bottom: 1rem;
}

.avatar-presets {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: nowrap;
  justify-content: space-between;
  width: 100%;
}

.avatar-item {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.avatar-item:hover {
  transform: scale(1.05);
}

.avatar-item.avatar-selected {
  border-color: rgb(255, 124, 75);
  box-shadow: 0 0 0 2px rgba(255, 124, 75, 0.2);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-upload {
  margin-bottom: 1rem;
}

.avatar-input {
  display: none;
}

.avatar-upload-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255, 124, 75, 0.1);
  color: rgb(255, 124, 75);
  border: 1px solid rgba(255, 124, 75, 0.3);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 600;
}

.avatar-upload-label:hover:not(.upload-disabled) {
  background: rgba(255, 124, 75, 0.15);
  border-color: rgba(255, 124, 75, 0.5);
}

.avatar-upload-label.upload-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.avatar-upload-label .icon {
  width: 1rem;
  height: 1rem;
}

.avatar-preview {
  margin-top: 1rem;
}

.preview-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 124, 75, 0.3);
}

/* 文本域 */
.textarea-wrapper {
  position: relative;
  border-radius: 12px;
  background: white;
  border: none;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.form-textarea:focus {
  border-color: #FF7C4B;
  box-shadow: 0 0 0 3px rgba(255, 124, 75, 0.1);
  border: 1px solid #FF7C4B;
  outline: none;
}

.form-textarea {
  width: 100%;
  padding: 1rem;
  border: none;
  background: white;
  font-size: 0.9375rem;
  color: #1e293b;
  outline: none;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.char-count {
  position: absolute;
  bottom: 0.5rem;
  right: 1rem;
  font-size: 0.75rem;
  color: #94a3b8;
  pointer-events: none;
}

/* 错误信息 */
.error-message {
  font-size: 0.75rem;
  color: #ef4444;
  margin-top: 0.25rem;
  margin-bottom: 0;
  margin-left: 9.5rem;
}

/* 弹窗底部 */
.popup-footer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e2e8f0;
  align-items: center;
}

/* 按钮 */
.cancel-button {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.01em;
  width: 100%;
  max-width: 300px;
}

.cancel-button:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.cancel-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-button {
  padding: 0.75rem 1.5rem;
  background: #FF7C4B;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.01em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  max-width: 300px;
}

.submit-button:hover:not(:disabled) {
  background: #FF6B35;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 124, 75, 0.3);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
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

/* 响应式设计 */
@media (max-width: 640px) {
  .name-popup {
    margin: 1rem;
    max-height: 95vh;
  }
  
  .popup-header,
  .popup-content,
  .popup-footer {
    padding: 1.25rem;
  }
  
  .popup-title {
    font-size: 1.25rem;
  }
  
  .form-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .form-label {
    width: 100%;
    text-align: left;
    padding-top: 0;
  }
  
  .error-message {
    margin-left: 0;
  }
  
  .avatar-presets {
    gap: 0.75rem;
  }
  
  .avatar-item {
    width: 50px;
    height: 50px;
  }
  
  .popup-footer {
    flex-direction: column;
  }
  
  .cancel-button,
  .submit-button {
    width: 100%;
  }
  
  .success-message {
    margin: 1rem;
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .form-input,
  .form-select,
  .form-textarea {
    padding: 0.875rem;
  }
  
  .avatar-upload-label {
    padding: 0.625rem 1.25rem;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .name-popup,
  .close-button,
  .avatar-item,
  .submit-button,
  .cancel-button,
  .spinner,
  .name-popup-overlay,
  .success-message {
    transition: none;
    animation: none;
  }
}
</style>