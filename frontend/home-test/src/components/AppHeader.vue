<template>
  <Header 
    :user-name="userName"
    user-role="student"
    theme="orange"
    :show-avatar="showAvatar"
    @back="handleBack"
    @avatar-click="handleAvatarClick"
  />
</template>

<script setup>
import Header from './Header.vue'

// 定义props
const props = defineProps({
  userName: {
    type: String,
    default: '学生'
  },
  showAvatar: {
    type: Boolean,
    default: true
  }
})

// 定义事件
const emit = defineEmits(['back', 'avatarClick'])

// 处理返回按钮点击
const handleBack = () => {
  emit('back')
}

// 处理头像点击
const handleAvatarClick = () => {
  emit('avatarClick')
}
</script>