<template>
  <div class="user-header">
    <div class="user-info">
      <div class="user-avatar" @click="handleAvatarClick">
        <img :src="avatarUrl" alt="用户头像" class="avatar-image">
      </div>
      <span class="user-greeting">{{ greeting }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  username: {
    type: String,
    default: '小米同学'
  },
  avatarUrl: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['avatar-click'])

// 计算属性
const greeting = computed(() => {
  const hour = new Date().getHours()
  let greetingText = '你好'
  if (hour < 12) {
    greetingText = '早上好'
  } else if (hour < 18) {
    greetingText = '下午好'
  } else {
    greetingText = '晚上好'
  }
  return `${greetingText}，${props.username}`
})

// 方法
const handleAvatarClick = () => {
  emit('avatar-click')
}
</script>

<style scoped>
.user-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 12px 16px;
  background: #CDF4FF;
  border-bottom: 1px solid #E0F0FF;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f0f0f0;
}

.user-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-greeting {
  font-size: 14px;
  color: #276884;
  font-weight: 500;
}
</style>