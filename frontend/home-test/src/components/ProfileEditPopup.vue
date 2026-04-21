<template>
  <div v-if="visible" class="profile-edit-popup-overlay" @click="close" :class="themeClass">
    <div class="profile-edit-popup" @click.stop :class="themeClass">
      <div class="popup-header" :class="themeClass">
        <div class="header-content">
          <h3 class="popup-title" :class="themeClass">编辑个人资料</h3>
          <p class="popup-subtitle">完善您的个人信息</p>
        </div>
        <button class="close-button" :class="themeClass" @click="close">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <div class="popup-body">
        <div class="avatar-section" :class="themeClass">
          <div class="avatar-wrapper">
            <div class="avatar" :class="themeClass">
              <span v-if="!formData.avatar">{{ userInitial }}</span>
              <img v-else :src="formData.avatar" alt="avatar" />
            </div>
            <button class="avatar-edit-btn" :class="themeClass" @click="triggerAvatarUpload">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 10.5V12.5M8 12.5V10.5M8 12.5C8 12.5 10 11 10 8C10 5 8 3.5 8 3.5C8 3.5 6 5 6 8C6 11 8 12.5 8 12.5ZM12.5 13.5H3.5C3.22 13.5 2.5 12.78 2.5 12.5V11.5C2.5 11.22 2.5 10.5 3.5 10.5V10.5C4.28 10.5 4.5 9.72 4.5 9V7.5C4.5 6.12 5.62 5 7 5H9C10.38 5 11.5 6.12 11.5 7.5V9C11.5 9.72 11.72 10.5 12.5 10.5V10.5C13.5 10.5 13.5 11.22 13.5 11.5V12.5C13.5 12.78 12.78 13.5 12.5 13.5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <input type="file" ref="avatarInput" @change="handleAvatarChange" accept="image/*" style="display: none;" />
          </div>
          <div class="avatar-info">
            <span class="avatar-name">{{ formData.name || '未设置姓名' }}</span>
            <span class="avatar-hint">点击更换头像</span>
          </div>
        </div>

        <div class="tabs" :class="themeClass">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            :class="['tab-btn', { active: activeTab === tab.id }, themeClass]"
            @click="activeTab = tab.id"
          >
            <component :is="tab.icon" />
            {{ tab.label }}
          </button>
        </div>

        <div class="tab-content">
          <div v-show="activeTab === 'basic'" class="form-section">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">👤</span>
                  姓名
                </label>
                <input 
                  type="text" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData.name"
                  placeholder="请输入姓名"
                >
              </div>
              
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">🆔</span>
                  {{ userType === 'student' ? '学号' : '工号' }}
                </label>
                <input 
                  type="text" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData[userType === 'student' ? 'studentId' : 'teacherId']"
                  :placeholder="`请输入${userType === 'student' ? '学号' : '工号'}`"
                >
              </div>
              
              <div v-if="userType === 'teacher'" class="form-group">
                <label class="form-label">
                  <span class="label-icon">💼</span>
                  职称
                </label>
                <input 
                  type="text" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData.title"
                  placeholder="请输入职称"
                >
              </div>

              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">🎓</span>
                  专业
                </label>
                <input 
                  type="text" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData.major"
                  placeholder="请输入专业"
                >
              </div>
            </div>
          </div>

          <div v-show="activeTab === 'contact'" class="form-section">
            <div class="form-grid">
              <div v-if="userType === 'teacher'" class="form-group full-width">
                <label class="form-label">
                  <span class="label-icon">📧</span>
                  邮箱
                </label>
                <input 
                  type="email" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData.email"
                  placeholder="请输入邮箱"
                >
              </div>
              
              <div v-if="userType === 'teacher'" class="form-group full-width">
                <label class="form-label">
                  <span class="label-icon">📞</span>
                  电话
                </label>
                <input 
                  type="tel" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData.phone"
                  placeholder="请输入电话"
                >
              </div>
            </div>
          </div>

          <div v-show="activeTab === 'education'" class="form-section">
            <div class="form-grid">
              <div v-if="userType === 'teacher'" class="form-group">
                <label class="form-label">
                  <span class="label-icon">🎓</span>
                  学历
                </label>
                <input 
                  type="text" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData.education"
                  placeholder="请输入学历"
                >
              </div>

              <div v-if="userType === 'teacher'" class="form-group">
                <label class="form-label">
                  <span class="label-icon">🏛️</span>
                  毕业院校
                </label>
                <input 
                  type="text" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData.university"
                  placeholder="请输入毕业院校"
                >
              </div>

              <div v-if="userType === 'teacher'" class="form-group full-width">
                <label class="form-label">
                  <span class="label-icon">🔬</span>
                  研究方向
                </label>
                <input 
                  type="text" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData.researchArea"
                  placeholder="请输入研究方向"
                >
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="popup-footer" :class="themeClass">
        <button class="btn-cancel" :class="themeClass" @click="close">
          取消
        </button>
        <button class="btn-save" :class="themeClass" @click="saveProfile">
          <span>保存修改</span>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M3 8H13M13 8L9 4M13 8L9 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, h } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  userInfo: {
    type: Object,
    default: () => ({})
  },
  userType: {
    type: String,
    default: 'student',
    validator: (value) => ['student', 'teacher'].includes(value)
  },
  theme: {
    type: String,
    default: 'orange',
    validator: (value) => ['orange', 'blue'].includes(value)
  }
})

const emit = defineEmits(['close', 'save'])

const themeClass = computed(() => {
  return props.theme === 'blue' ? 'theme-blue' : ''
})

const activeTab = ref('basic')
const avatarInput = ref(null)

const IconBasic = {
  render() {
    return h('svg', { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none' }, [
      h('path', { d: 'M8 8C9.65685 8 11 6.65685 11 5C11 3.34315 9.65685 2 8 2C6.34315 2 5 3.34315 5 5C5 6.65685 6.34315 8 8 8Z', stroke: 'currentColor', 'stroke-width': 1.5 }),
      h('path', { d: 'M3 14C3 11.2386 5.23858 9 8 9C10.7614 9 13 11.2386 13 14', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linecap': 'round' })
    ])
  }
}

const IconContact = {
  render() {
    return h('svg', { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none' }, [
      h('path', { d: 'M2 3H5L6.5 7L4.5 8.5C5.5 10.5 7 11 8 11C9 11 10.5 10.5 11.5 8.5L9.5 7L11 5H14', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const IconEducation = {
  render() {
    return h('svg', { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none' }, [
      h('path', { d: 'M8 2L1 6L8 10L15 6L8 2Z', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linejoin': 'round' }),
      h('path', { d: 'M1 9V10C1 10 3 11 8 11C13 11 15 10 15 10V9', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linecap': 'round' })
    ])
  }
}

const tabs = computed(() => {
  const basicTab = { id: 'basic', label: '基本信息', icon: IconBasic }
  const contactTab = { id: 'contact', label: '联系方式', icon: IconContact }
  const educationTab = { id: 'education', label: '教育背景', icon: IconEducation }
  
  if (props.userType === 'student') {
    return [basicTab]
  }
  return [basicTab, contactTab, educationTab]
})

const formData = ref({
  name: '',
  studentId: '',
  teacherId: '',
  title: '',
  email: '',
  phone: '',
  major: '',
  researchArea: '',
  education: '',
  university: '',
  avatar: ''
})

const userInitial = computed(() => {
  if (formData.value.name) {
    return formData.value.name.charAt(0).toUpperCase()
  }
  return 'U'
})

watch(() => props.userInfo, (newUserInfo) => {
  formData.value = {
    name: newUserInfo.name || '',
    studentId: newUserInfo.studentId || '',
    teacherId: newUserInfo.teacherId || '',
    title: newUserInfo.title || '',
    email: newUserInfo.email || '',
    phone: newUserInfo.phone || '',
    major: newUserInfo.major || '',
    researchArea: newUserInfo.researchArea || '',
    education: newUserInfo.education || '',
    university: newUserInfo.university || '',
    avatar: newUserInfo.avatar || ''
  }
}, { deep: true })

onMounted(() => {
  formData.value = {
    name: props.userInfo.name || '',
    studentId: props.userInfo.studentId || '',
    teacherId: props.userInfo.teacherId || '',
    title: props.userInfo.title || '',
    email: props.userInfo.email || '',
    phone: props.userInfo.phone || '',
    major: props.userInfo.major || '',
    researchArea: props.userInfo.researchArea || '',
    education: props.userInfo.education || '',
    university: props.userInfo.university || '',
    avatar: props.userInfo.avatar || ''
  }
})

const close = () => {
  emit('close')
}

const triggerAvatarUpload = () => {
  avatarInput.value.click()
}

const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      formData.value.avatar = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const validateEmail = (email) => {
  if (!email) return true
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validatePhone = (phone) => {
  if (!phone) return true
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

const saveProfile = () => {
  if (!formData.value.name) {
    alert('请输入姓名')
    return
  }
  
  if (props.userType === 'student' && !formData.value.studentId) {
    alert('请输入学号')
    return
  }
  
  if (props.userType === 'teacher' && !formData.value.teacherId) {
    alert('请输入工号')
    return
  }
  
  if (formData.value.email && !validateEmail(formData.value.email)) {
    alert('请输入有效的邮箱地址')
    return
  }
  
  if (formData.value.phone && !validatePhone(formData.value.phone)) {
    alert('请输入有效的手机号')
    return
  }
  
  emit('save', formData.value)
  close()
}
</script>

<style scoped>
.profile-edit-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.profile-edit-popup {
  background: #FFFFFF;
  border-radius: 16px;
  width: 480px;
  max-width: 95%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
}

@keyframes slideIn {
  from {
    transform: translateY(-30px) scale(0.95);
    opacity: 0;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 24px 20px;
  background: linear-gradient(135deg, #FFF5E7 0%, #FFFFFF 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.theme-blue.popup-header {
  background: linear-gradient(135deg, #F2FCFF 0%, #FFFFFF 100%);
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.popup-title {
  font-size: 20px;
  font-weight: 700;
  color: #C96030;
  margin: 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.theme-blue .popup-title {
  color: #008AC5;
}

.popup-subtitle {
  font-size: 13px;
  color: #999;
  margin: 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.close-button {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
  color: #666;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.1);
  transform: rotate(90deg);
}

.popup-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #FFF8F3 0%, #FFF5E7 100%);
  border-radius: 12px;
  margin-bottom: 24px;
}

.theme-blue.avatar-section {
  background: linear-gradient(135deg, #F0FAFF 0%, #E6F4FB 100%);
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #F18B5B 0%, #C96030 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  font-weight: 700;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  box-shadow: 0 4px 12px rgba(201, 96, 48, 0.3);
  overflow: hidden;
}

.theme-blue.avatar {
  background: linear-gradient(135deg, #008AC5 0%, #276884 100%);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.3);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-edit-btn {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid white;
  background: #F18B5B;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.theme-blue.avatar-edit-btn {
  background: #008AC5;
}

.avatar-edit-btn:hover {
  transform: scale(1.1);
}

.avatar-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.avatar-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.avatar-hint {
  font-size: 13px;
  color: #999;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  background: #F5F5F5;
  padding: 4px;
  border-radius: 10px;
}

.tab-btn {
  flex: 1;
  padding: 10px 12px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.tab-btn:hover {
  color: #333;
  background: rgba(255, 255, 255, 0.5);
}

.tab-btn.active {
  background: #FFFFFF;
  color: #C96030;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.theme-blue.tab-btn.active {
  color: #008AC5;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

.form-section {
  padding: 4px 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group {
  margin-bottom: 0;
}

.form-group.full-width {
  grid-column: span 2;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.label-icon {
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid #E8E8E8;
  border-radius: 10px;
  font-size: 14px;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  transition: all 0.3s ease;
  background: #FAFAFA;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #F18B5B;
  background: #FFFFFF;
  box-shadow: 0 0 0 4px rgba(241, 139, 91, 0.1);
}

.theme-blue.form-input:focus {
  border-color: #008AC5;
  box-shadow: 0 0 0 4px rgba(0, 138, 197, 0.1);
}

.form-input::placeholder {
  color: #BBB;
}

.popup-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px 24px;
  background: #FAFAFA;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.btn-cancel,
.btn-save {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-cancel {
  background: #F0F0F0;
  color: #666;
}

.btn-cancel:hover {
  background: #E0E0E0;
  transform: translateY(-1px);
}

.btn-save {
  background: linear-gradient(135deg, #F18B5B 0%, #C96030 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(201, 96, 48, 0.3);
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(201, 96, 48, 0.4);
}

.theme-blue.btn-save {
  background: linear-gradient(135deg, #008AC5 0%, #276884 100%);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.3);
}

.theme-blue.btn-save:hover {
  box-shadow: 0 6px 16px rgba(0, 138, 197, 0.4);
}

.theme-blue.close-button:hover {
  background: #E6F4FB;
  color: #008AC5;
}

@media (max-width: 520px) {
  .profile-edit-popup {
    width: 340px;
  }
  
  .popup-body {
    padding: 16px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-group.full-width {
    grid-column: span 1;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
  }
  
  .tabs {
    flex-direction: column;
  }
}

.profile-edit-popup::-webkit-scrollbar {
  width: 6px;
}

.profile-edit-popup::-webkit-scrollbar-track {
  background: #F1F1F1;
  border-radius: 3px;
}

.profile-edit-popup::-webkit-scrollbar-thumb {
  background: #C1C1C1;
  border-radius: 3px;
}

.profile-edit-popup::-webkit-scrollbar-thumb:hover {
  background: #A8A8A8;
}
</style>