<template>
  <div class="bg-[url('/assets/images/bg-main.jpg')] bg-cover bg-center bg-no-repeat min-h-screen m-0 p-0 font-sans">
    <!-- 1. 导航栏（带下阴影） -->
    <nav class="bg-white/80 backdrop-blur-sm shadow-md py-3 px-6">
      <h1 class="text-2xl font-bold text-red-600">AI智教</h1>
      <!-- Optional: Add logo here -->
      <!-- <img src="/assets/images/logo.png" alt="Logo" class="h-8"> -->
    </nav>

    <!-- 2. 核心内容区 -->
    <div class="flex flex-col md:flex-row items-center justify-center gap-10 px-6 py-12 min-h-[calc(100vh-80px)]">
      <!-- 左侧视频展示区 -->
      <div class="bg-white rounded-xl shadow-xl overflow-hidden w-full md:w-[400px]">
        <img :src="videoCover" alt="视频封面" class="w-full h-auto">
      </div>

      <!-- 右侧动态图标区 -->
      <div class="w-full md:w-[300px] flex items-center justify-center">
        <video 
          src="/assets/images/ppt-icon.mp4" 
          alt="PPT动态图标" 
          class="w-64"  
          muted 
          autoplay 
          loop 
          playsinline
        ></video>
      </div>
    </div>

    <!-- 3. 登录/注册按钮区（仅展示） -->
    <div class="flex justify-center gap-6 pb-12">
      <button class="bg-red-600 text-white px-8 py-3 rounded-full font-medium hover:bg-red-700 transition-colors">登录</button>
      <button class="bg-white text-red-600 border border-red-600 px-8 py-3 rounded-full font-medium hover:bg-red-50 transition-colors">注册</button>
    </div>
  </div>
</template>

<script setup>
// Import the video cover image
import videoCover from '@/assets/images/video-cover.jpg';
</script>

<style scoped>
/* 如需补充自定义样式可写在这里 */
</style>