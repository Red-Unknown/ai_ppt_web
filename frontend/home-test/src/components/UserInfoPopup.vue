<template>
  <div>
    <!-- 用户信息弹窗 -->
    <div v-if="visible" class="user-info-popup-overlay" @click="close" :class="themeClass">
      <div class="user-info-popup" @click.stop :class="themeClass">
        <!-- 弹窗头部 -->
        <div class="popup-header" :class="themeClass">
          <h3 class="popup-title" :class="themeClass">{{ isEditing ? '编辑个人资料' : '个人中心' }}</h3>
          <button class="close-button" :class="themeClass" @click="close">×</button>
        </div>
        
        <!-- 编辑模式 -->
        <div v-if="isEditing" class="profile-edit-section">
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
          
          <div class="form-section">
            <div class="form-grid">
              <div class="form-group full-width">
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
              <div class="form-group full-width">
                <label class="form-label">
                  <span class="label-icon">🖼️</span>
                  人物画像
                </label>
                <input 
                  type="text" 
                  class="form-input" 
                  :class="themeClass"
                  v-model="formData.portrait"
                  placeholder="请输入人物画像描述"
                >
                <small class="form-hint">描述您的人物特征、性格特点等，用于AI生成个性化内容</small>
              </div>
            </div>
          </div>
          
          <div class="popup-footer" :class="themeClass">
            <button class="btn-cancel" :class="themeClass" @click="cancelEdit">
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
        
        <!-- 查看模式 -->
        <div v-else>
          <!-- 用户信息区域 -->
          <div class="user-info-section">
            <div class="user-avatar" :class="themeClass">{{ userInitial }}</div>
            <div class="user-details">
              <h4 class="user-name">{{ userInfo.name || '用户' }}</h4>
              <p class="user-portrait" v-if="userInfo.portrait">{{ userInfo.portrait }}</p>
              <p class="user-portrait" v-else>人物画像: 未设置</p>
            </div>
          </div>
          
          <!-- 菜单项 -->
          <div class="menu-section">
            <div class="menu-item" :class="themeClass" @click="startEdit">
              <span class="menu-text">个人资料</span>
            </div>
            <div class="menu-item" :class="themeClass" @click="handleMenuItemClick('settings')">
              <span class="menu-text">设置</span>
            </div>
            <div class="menu-item" :class="themeClass" @click="handleMenuItemClick('aiConfig')">
              <span class="menu-text">AI配置</span>
            </div>
            <div class="menu-item" :class="themeClass" @click="handleMenuItemClick('about')">
              <span class="menu-text">关于我们</span>
            </div>
            <div class="menu-item logout" :class="themeClass" @click="handleLogout">
              <span class="menu-text">退出登录</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

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
      avatar: '',
      portrait: ''
    })
  },
  theme: {
    type: String,
    default: 'orange',
    validator: (value) => ['orange', 'blue'].includes(value)
  }
})

// 计算主题类
const themeClass = computed(() => {
  return props.theme === 'blue' ? 'theme-blue' : ''
})

// 定义事件
const emit = defineEmits(['close', 'menuClick', 'logout', 'save-profile'])

// 编辑模式状态
const isEditing = ref(false)
const formData = ref({ ...props.userInfo })
const avatarInput = ref(null)

// 计算用户名首字母
const userInitial = computed(() => {
  if (formData.value.name) {
    return formData.value.name.charAt(0).toUpperCase()
  }
  return 'U'
})

// 监听userInfo变化，更新formData
watch(() => props.userInfo, (newUserInfo) => {
  formData.value = { ...newUserInfo }
}, { deep: true })

// 关闭弹窗
const close = () => {
  isEditing.value = false
  emit('close')
}

// 开始编辑
const startEdit = () => {
  formData.value = { ...props.userInfo }
  isEditing.value = true
}

// 取消编辑
const cancelEdit = () => {
  formData.value = { ...props.userInfo }
  isEditing.value = false
}

// 保存个人资料
const saveProfile = () => {
  emit('save-profile', formData.value)
  isEditing.value = false
}

// 处理菜单项点击
const handleMenuItemClick = (menuItem) => {
  emit('menuClick', menuItem)
}

// 触发头像上传
const triggerAvatarUpload = () => {
  if (avatarInput.value) {
    avatarInput.value.click()
  }
}

// 处理头像变化
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

// 处理退出登录
const handleLogout = () => {
  emit('logout')
}
</script>

<style scoped>
.user-info-popup-overlay {
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

.user-info-popup {
  background: #FFFFFF;
  border-radius: 12px;
  width: 320px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
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

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #F0F0F0;
}

.popup-title {
  font-size: 18px;
  font-weight: bold;
  color: #C96030;
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
  background: #F0F0F0;
  color: #333;
}

.user-info-section {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #F0F0F0;
}

.user-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #F18B5B;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0 0 4px 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.user-student-id,
.user-major,
.user-portrait {
  font-size: 14px;
  color: #999;
  margin: 4px 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.menu-section {
  padding: 8px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.menu-item:hover {
  background: #FFF5E7;
}

.menu-text {
  font-size: 16px;
  color: #333;
  flex: 1;
}

.menu-item.logout {
  margin-top: 16px;
  border-top: 1px solid #F0F0F0;
  color: #E86A3F;
}

.menu-item.logout .menu-text {
  color: #E86A3F;
}

.menu-item.logout:hover {
  background: #FFF0EB;
}

/* 蓝色主题样式 */
.theme-blue .popup-title {
  color: #008AC5;
}

.theme-blue .user-avatar {
  background: #008AC5;
}

.theme-blue .menu-item:hover {
  background: #E6F4FB;
}

.theme-blue .menu-item.logout {
  color: #C7432A;
}

.theme-blue .menu-item.logout .menu-text {
  color: #C7432A;
}

.theme-blue .menu-item.logout:hover {
  background: #FFF0F0;
}

.theme-blue .close-button:hover {
  background: #E6F4FB;
  color: #008AC5;
}

/* 编辑模式样式 */
.profile-edit-section {
  padding: 20px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #F0F0F0;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #F18B5B;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  font-weight: bold;
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-edit-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: #FFFFFF;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #F18B5B;
}

.avatar-edit-btn:hover {
  transform: scale(1.1);
}

.theme-blue .avatar {
  background: #008AC5;
}

.theme-blue .avatar-edit-btn {
  color: #008AC5;
}

.avatar-info {
  flex: 1;
}

.avatar-name {
  display: block;
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.avatar-hint {
  font-size: 14px;
  color: #999;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 1px solid #F0F0F0;
  padding-bottom: 8px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tab-btn:hover {
  background: #FFF5E7;
  color: #C96030;
}

.tab-btn.active {
  background: #FFF5E7;
  color: #C96030;
  font-weight: 600;
}

.theme-blue .tab-btn:hover {
  background: #E6F4FB;
  color: #008AC5;
}

.theme-blue .tab-btn.active {
  background: #E6F4FB;
  color: #008AC5;
}

.form-section {
  margin-bottom: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
  gap: 6px;
}

.label-icon {
  font-size: 16px;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.form-input:focus {
  outline: none;
  border-color: #F18B5B;
  box-shadow: 0 0 0 3px rgba(241, 139, 91, 0.1);
}

.theme-blue .form-input:focus {
  border-color: #008AC5;
  box-shadow: 0 0 0 3px rgba(0, 138, 197, 0.1);
}

.form-hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  line-height: 1.4;
}

.popup-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #F0F0F0;
}

.btn-cancel,
.btn-save {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-cancel {
  background: #F5F5F5;
  color: #666;
}

.btn-cancel:hover {
  background: #E0E0E0;
}

.btn-save {
  background: linear-gradient(135deg, #F18B5B 0%, #E86A3F 100%);
  color: white;
  font-weight: 600;
}

.btn-save:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(241, 139, 91, 0.3);
}

.theme-blue .btn-save {
  background: linear-gradient(135deg, #008AC5 0%, #006B9E 100%);
}

.theme-blue .btn-save:hover {
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.3);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .user-info-popup {
    width: 280px;
  }
  
  .user-info-section {
    padding: 20px;
  }
  
  .user-avatar {
    width: 56px;
    height: 56px;
    font-size: 20px;
  }
  
  .user-name {
    font-size: 16px;
  }
  
  .menu-item {
    padding: 10px 20px;
  }
  
  .menu-text {
    font-size: 14px;
  }
  
  .profile-edit-section {
    padding: 16px;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .tabs {
    flex-direction: column;
  }
  
  .tab-btn {
    justify-content: flex-start;
  }
  
  .popup-footer {
    flex-direction: column;
  }
  
  .btn-cancel,
  .btn-save {
    width: 100%;
    justify-content: center;
  }
}
</style>