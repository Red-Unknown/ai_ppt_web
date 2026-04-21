<template>
  <header class="header" :class="[themeClass, { 'header-shadow': isScrolled }]">
    <button class="back-button" @click="handleBack" aria-label="返回">
      <img src="@/assets/images/action/ic-arrow_left2.svg" alt="返回" class="back-icon">
    </button>
    <div class="user-info">
      <div class="avatar" @click="handleAvatarClick" aria-label="用户信息">
        <span v-if="userInitial" class="avatar-text">{{ userInitial }}</span>
      </div>
      <span class="username">{{ greeting }}</span>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 定义props
const props = defineProps({
  userName: {
    type: String,
    default: '用户'
  },
  userRole: {
    type: String,
    default: 'student',
    validator: (value) => ['student', 'teacher'].includes(value)
  },
  theme: {
    type: String,
    default: 'orange',
    validator: (value) => ['orange', 'blue'].includes(value)
  },
  showAvatar: {
    type: Boolean,
    default: true
  }
})

// 定义事件
const emit = defineEmits(['back', 'avatarClick'])

// 滚动状态
const isScrolled = ref(false)

// 计算主题类
const themeClass = computed(() => {
  return `theme-${props.theme}`
})

// 计算用户名首字母
const userInitial = computed(() => {
  if (props.userName) {
    return props.userName.charAt(0).toUpperCase()
  }
  return 'U'
})

// 计算问候语
const greeting = computed(() => {
  const roleSuffix = props.userRole === 'teacher' ? '老师' : '同学'
  return `你好，${props.userName}${roleSuffix}`
})

// 处理返回按钮点击
const handleBack = () => {
  emit('back')
}

// 处理头像点击
const handleAvatarClick = () => {
  emit('avatarClick')
}

// 监听滚动事件
const handleScroll = () => {
  isScrolled.value = window.scrollY > 10
}

// 生命周期钩子
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.header {
  height: 60px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: sticky;
  top: 0;
}

.header-shadow {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.back-button {
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  border-radius: 50%;
}

.back-button:hover {
  transform: translateX(-2px);
  background: rgba(241, 139, 91, 0.05);
}

.back-icon {
  width: 20px;
  height: 20px;
  transition: all 0.2s ease;
}

.back-button:hover .back-icon {
  filter: brightness(0) saturate(100%) invert(54%) sepia(22%) saturate(1764%) hue-rotate(328deg) brightness(99%) contrast(93%);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #F18B5B;
  transition: all 0.2s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.avatar:hover {
  box-shadow: 0 0 0 4px rgba(241, 139, 91, 0.2);
  transform: scale(1.05);
}

.avatar-text {
  font-size: 18px;
  font-weight: 600;
}

.username {
  font-size: 16px;
  color: #C96030;
  font-weight: 400;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  white-space: nowrap;
}

/* 蓝色主题样式 */
.theme-blue .back-button:hover {
  background: rgba(0, 138, 197, 0.05);
}

.theme-blue .back-button:hover .back-icon {
  filter: brightness(0) saturate(100%) invert(43%) sepia(79%) saturate(2476%) hue-rotate(180deg) brightness(100%) contrast(100%);
}

.theme-blue .avatar {
  background: #008AC5;
}

.theme-blue .avatar:hover {
  box-shadow: 0 0 0 4px rgba(0, 138, 197, 0.2);
}

.theme-blue .username {
  color: #008AC5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }
  
  .username {
    font-size: 14px;
  }
  
  .avatar {
    width: 36px;
    height: 36px;
  }
  
  .avatar-text {
    font-size: 16px;
  }
  
  .back-button {
    width: 36px;
    height: 36px;
  }
  
  .back-icon {
    width: 18px;
    height: 18px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 0 12px;
  }
  
  .username {
    font-size: 12px;
  }
  
  .user-info {
    gap: 8px;
  }
  
  .avatar {
    width: 32px;
    height: 32px;
  }
  
  .avatar-text {
    font-size: 14px;
  }
  
  .back-button {
    width: 32px;
    height: 32px;
  }
  
  .back-icon {
    width: 16px;
    height: 16px;
  }
}
</style>