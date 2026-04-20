<template>
  <div>
    <!-- 用户信息弹窗 -->
    <div class="user-info-popup-overlay" @click="close" :class="themeClass">
      <div class="user-info-popup" @click.stop :class="themeClass">
        <!-- 弹窗头部 -->
        <div class="popup-header" :class="themeClass">
          <h3 class="popup-title" :class="themeClass">个人中心</h3>
          <button class="close-button" :class="themeClass" @click="close">×</button>
        </div>
        
        <!-- 用户信息区域 -->
        <div class="user-info-section">
          <div class="user-avatar" :class="themeClass">{{ userInitial }}</div>
          <div class="user-details">
            <h4 class="user-name">{{ userInfo.name || '用户' }}</h4>
            <p class="user-student-id">{{ userInfo.teacherId ? `工号: ${userInfo.teacherId}` : '工号: 未设置' }}</p>
            <p class="user-major">{{ userInfo.major || '专业: 未设置' }}</p>
          </div>
        </div>
        
        <!-- 菜单项 -->
        <div class="menu-section">
          <div class="menu-item" :class="themeClass" @click="handleMenuItemClick('profile')">
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
    
    <!-- 编辑个人资料弹窗 -->
    <ProfileEditPopup
      v-if="showEditPopup"
      :visible="showEditPopup"
      :user-info="userInfo"
      :user-type="'teacher'"
      :theme="theme"
      @close="closeEditPopup"
      @save="saveProfile"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import ProfileEditPopup from './ProfileEditPopup.vue'

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

// 编辑资料弹窗
const showEditPopup = ref(false)

// 计算用户名首字母
const userInitial = computed(() => {
  if (props.userInfo.name) {
    return props.userInfo.name.charAt(0).toUpperCase()
  }
  return 'U'
})

// 关闭弹窗
const close = () => {
  emit('close')
}

// 处理菜单项点击
const handleMenuItemClick = (menuItem) => {
  if (menuItem === 'profile') {
    showEditPopup.value = true
  }
  emit('menuClick', menuItem)
}

// 关闭编辑资料弹窗
const closeEditPopup = () => {
  showEditPopup.value = false
}

// 保存个人资料
const saveProfile = (profileData) => {
  emit('save-profile', profileData)
  closeEditPopup()
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
.user-major {
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
}
</style>