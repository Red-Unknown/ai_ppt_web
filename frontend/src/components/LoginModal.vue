<!-- 登录注册组件 -->

<template>
  <div v-if="visible" class="fixed inset-0 bg-black/30 z-50 flex items-center justify-center">
    <!-- 登录卡片 -->
    <div class="bg-white w-[90%] max-w-md rounded-lg shadow-lg relative overflow-hidden">
      <!-- 关闭按钮 -->
      <button @click="handleClose" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- 选项卡：登录 / 注册 -->
      <div class="flex border-b"> 
        <button 
          @click="activeTab = 'login'"
          :class="[
            'flex-1 py-3 text-lg font-medium',
            activeTab === 'login' ? 'text-red-500 border-b-2 border-red-500' : 'text-gray-400'
          ]"
        >
          登录
        </button>
        <button
          @click="activeTab = 'register'"
          :class="[
            'flex-1 py-3 text-lg font-medium',
            activeTab === 'register' ? 'text-red-500 border-b-2 border-red-500' : 'text-gray-400'
          ]"
        >
          注册
        </button>
      </div>

      <!-- 登录 AA表单 -->
      <div v-if="activeTab === 'login'" class="p-6">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- 账号 -->
          <div>
            <input
              v-model="loginForm.username"
              type="text"
              placeholder="账号:"
              class="w-full py-3 px-4 border border-gray-300 rounded-full outline-none focus:border-red-500"
              required
            />
          </div>
          <!-- 密码 -->
          <div class="relative">
            <input
              v-model="loginForm.password"
              type="password"
              placeholder="密码:"
              class="w-full py-3 px-4 border border-gray-300 rounded-full outline-none focus:border-red-500"
              required
            />
            <a href="#" class="absolute right-4 top-1/2 -translate-y-1/2 text-sm text-gray-500">
              忘记密码
            </a>
          </div>

          <!-- 验证码登录 -->
          <div class="text-right">
            <a href="#" class="text-sm text-gray-500">验证码登录</a>
          </div>

          <!-- 选项 -->
          <div class="space-y-2 text-sm">
            <label class="flex items-center">
              <input type="checkbox" v-model="loginForm.autoLogin" class="mr-2" />
              <span class="text-red-500">下次自动登录</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" v-model="loginForm.agree" class="mr-2" />
              <span class="text-gray-500">
                我已阅读并同意习通
                <a href="#" class="text-red-500">《隐私政策》</a> 和
                <a href="#" class="text-red-500">《用户协议》</a>
              </span>
            </label>
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            class="w-full py-3 bg-red-500 text-white rounded-full font-medium hover:bg-red-600 transition"
          >
            登录
          </button>
        </form>
      </div>

      <!-- 注册表单（可后续扩展） -->
      <div v-else class="p-6">
        <p class="text-center text-gray-500">注册功能开发中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// 接收父组件传入的显示状态
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

// 向父组件发送关闭事件
const emit = defineEmits(['update:visible'])

// 选项卡
const activeTab = ref('login')

// 登录表单数据
const loginForm = ref({
  username: '',
  password: '',
  autoLogin: false,
  agree: false
})

// 关闭弹窗
const handleClose = () => {
  emit('update:visible', false)
}

// 监听 visible，重置表单（可选）
watch(() => props.visible, (val) => {
  if (val) {
    loginForm.value = {
      username: '',
      password: '',
      autoLogin: false,
      agree: false
    }
  }
})

// 登录提交
const handleLogin = () => {
  if (!loginForm.value.agree) {
    alert('请先同意用户协议和隐私政策')
    return
  }
  // 这里替换为你的登录接口调用
  console.log('登录信息：', loginForm.value)
  alert('登录成功')
  handleClose()
}
</script>

<style scoped>
/* 可根据需要补充自定义样式 */
</style>