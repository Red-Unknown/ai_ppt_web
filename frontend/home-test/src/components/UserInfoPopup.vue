<template>
  <div class="user-info-popup-overlay" @click="close">
    <div class="user-info-popup" @click.stop>
      <!-- 弹窗头部 -->
      <div class="popup-header">
        <h3 class="popup-title">个人中心</h3>
        <button class="close-button" @click="close">×</button>
      </div>
      
      <!-- 用户信息区域 -->
      <div class="user-info-section">
        <div class="user-avatar">{{ userInitial }}</div>
        <div class="user-details">
          <h4 class="user-name">{{ userInfo.name || '用户' }}</h4>
          <p class="user-student-id">{{ userInfo.studentId || '学号: 未设置' }}</p>
          <p class="user-major">{{ userInfo.major || '专业: 未设置' }}</p>
        </div>
      </div>
      
      <!-- 菜单项 -->
      <div class="menu-section">
        <div class="menu-item" @click="handleMenuItemClick('profile')">
          <span class="menu-text">个人资料</span>
        </div>
        <div class="menu-item" @click="handleMenuItemClick('settings')">
          <span class="menu-text">设置</span>
        </div>
        <div class="menu-item" @click="handleMenuItemClick('aiConfig')">
          <span class="menu-text">AI配置</span>
        </div>
        <div class="menu-item" @click="handleMenuItemClick('about')">
          <span class="menu-text">关于我们</span>
        </div>
        <div class="menu-item logout" @click="handleLogout">
          <span class="menu-text">退出登录</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// 定义props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  userInfo: {
    type: Object,
    default: () => ({
      name: '学生',
      studentId: '',
      major: ''
    })
  }
})

// 定义事件
const emit = defineEmits(['close', 'menuClick', 'logout'])

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
  emit('menuClick', menuItem)
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