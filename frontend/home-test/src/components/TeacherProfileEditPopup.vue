<template>
  <div class="profile-edit-popup-overlay" @click="close">
    <div class="profile-edit-popup" @click.stop>
      <!-- 弹窗头部 -->
      <div class="popup-header">
        <h3 class="popup-title">编辑个人资料</h3>
        <button class="close-button" @click="close">×</button>
      </div>
      
      <!-- 编辑表单 -->
      <div class="edit-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <h4 class="section-title">基本信息</h4>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">姓名</label>
              <input 
                type="text" 
                class="form-input" 
                v-model="formData.name"
                placeholder="请输入姓名"
              >
            </div>
            <div class="form-group">
              <label class="form-label">工号</label>
              <input 
                type="text" 
                class="form-input" 
                v-model="formData.teacherId"
                placeholder="请输入工号"
              >
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">职称</label>
            <input 
              type="text" 
              class="form-input" 
              v-model="formData.title"
              placeholder="请输入职称"
            >
          </div>
        </div>
        
        <!-- 联系方式 -->
        <div class="form-section">
          <h4 class="section-title">联系方式</h4>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">邮箱</label>
              <input 
                type="email" 
                class="form-input" 
                v-model="formData.email"
                placeholder="请输入邮箱"
              >
            </div>
            <div class="form-group">
              <label class="form-label">电话</label>
              <input 
                type="tel" 
                class="form-input" 
                v-model="formData.phone"
                placeholder="请输入电话"
              >
            </div>
          </div>
        </div>
        
        <!-- 专业领域 -->
        <div class="form-section">
          <h4 class="section-title">专业领域</h4>
          <div class="form-group">
            <label class="form-label">专业</label>
            <input 
              type="text" 
              class="form-input" 
              v-model="formData.major"
              placeholder="请输入专业"
            >
          </div>
          <div class="form-group">
            <label class="form-label">研究方向</label>
            <input 
              type="text" 
              class="form-input" 
              v-model="formData.researchArea"
              placeholder="请输入研究方向"
            >
          </div>
        </div>
        
        <!-- 教育背景 -->
        <div class="form-section">
          <h4 class="section-title">教育背景</h4>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">学历</label>
              <input 
                type="text" 
                class="form-input" 
                v-model="formData.education"
                placeholder="请输入学历"
              >
            </div>
            <div class="form-group">
              <label class="form-label">毕业院校</label>
              <input 
                type="text" 
                class="form-input" 
                v-model="formData.university"
                placeholder="请输入毕业院校"
              >
            </div>
          </div>
        </div>
      </div>
      
      <!-- 按钮区域 -->
      <div class="popup-footer">
        <button class="btn-cancel" @click="close">取消</button>
        <button class="btn-save" @click="saveProfile">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

// 定义props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  userInfo: {
    type: Object,
    default: () => ({
      name: '老师',
      teacherId: '',
      title: '',
      email: '',
      phone: '',
      major: '',
      researchArea: '',
      education: '',
      university: ''
    })
  }
})

// 定义事件
const emit = defineEmits(['close', 'save'])

// 表单数据
const formData = ref({
  name: '',
  teacherId: '',
  title: '',
  email: '',
  phone: '',
  major: '',
  researchArea: '',
  education: '',
  university: ''
})

// 监听userInfo变化
watch(() => props.userInfo, (newUserInfo) => {
  formData.value = {
    name: newUserInfo.name || '',
    teacherId: newUserInfo.teacherId || '',
    title: newUserInfo.title || '',
    email: newUserInfo.email || '',
    phone: newUserInfo.phone || '',
    major: newUserInfo.major || '',
    researchArea: newUserInfo.researchArea || '',
    education: newUserInfo.education || '',
    university: newUserInfo.university || ''
  }
}, { deep: true })

// 初始化表单数据
onMounted(() => {
  formData.value = {
    name: props.userInfo.name || '',
    teacherId: props.userInfo.teacherId || '',
    title: props.userInfo.title || '',
    email: props.userInfo.email || '',
    phone: props.userInfo.phone || '',
    major: props.userInfo.major || '',
    researchArea: props.userInfo.researchArea || '',
    education: props.userInfo.education || '',
    university: props.userInfo.university || ''
  }
})

// 关闭弹窗
const close = () => {
  emit('close')
}

// 验证邮箱格式
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// 验证手机号格式
const validatePhone = (phone) => {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

// 保存个人资料
const saveProfile = () => {
  // 验证表单
  if (!formData.value.name) {
    alert('请输入姓名')
    return
  }
  
  if (!formData.value.teacherId) {
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
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
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

.profile-edit-popup {
  background: #FFFFFF;
  border-radius: 12px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
  max-height: 80vh;
  overflow-y: auto;
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

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #F0F0F0;
  background: #F9F9F9;
  border-radius: 12px 12px 0 0;
}

.popup-title {
  font-size: 18px;
  font-weight: bold;
  color: #008AC5;
  margin: 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.close-button {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #E0E0E0;
  color: #333;
}

.edit-form {
  padding: 24px;
}

.form-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #F0F0F0;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  flex: 1;
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  font-size: 14px;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #008AC5;
  box-shadow: 0 0 0 2px rgba(0, 138, 197, 0.1);
}

.popup-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #F0F0F0;
  background: #F9F9F9;
  border-radius: 0 0 12px 12px;
}

.btn-cancel,
.btn-save {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.btn-cancel {
  background: #F0F0F0;
  color: #666;
}

.btn-cancel:hover {
  background: #E0E0E0;
}

.btn-save {
  background: #008AC5;
  color: white;
}

.btn-save:hover {
  background: #006B9E;
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .profile-edit-popup {
    width: 320px;
  }
  
  .edit-form {
    padding: 20px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .popup-footer {
    padding: 12px 16px;
  }
}

/* 滚动条样式 */
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