<template>
  <div class="ppt-show-page">
    <!-- 背景渐变 -->
    <div class="bg-gradient"></div>
    
    <!-- 动态气泡 -->
    <div class="bubbles">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div>
    </div>
    
    <!-- 导航栏 -->
    <nav class="navbar">
      <button class="navbar-back-button" @click="handleBack">
        <svg class="back-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"></path>
        </svg>
      </button>
      <div class="navbar-logo">AI智教</div>
      <div class="navbar-user" @click="toggleUserMenu">
        <div class="user-avatar"></div>
        <span class="user-greeting">你好，同学</span>
        <!-- 下拉伸缩栏 -->
        <div class="user-menu" :class="{ 'visible': showUserMenu }">
          <div class="menu-item" @click.stop="navigateTo('profile')">
            <svg class="menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <span>个人信息</span>
          </div>
          <div class="menu-item" @click.stop="navigateTo('about')">
            <svg class="menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span>关于我们</span>
          </div>
          <div class="menu-item" @click.stop="handleLogout">
            <svg class="menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span>退出登录</span>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <h2 class="page-title">我的课程</h2>
      
      <!-- 卡片网格 -->
      <div class="cards-grid">
        <!-- 新建卡片 -->
        <div class="card new-card" @click="handleNewPPT">
          <div class="new-card-content">
            <div class="plus-button">
              +
            </div>
            <p class="new-card-text">添加PPT</p>
          </div>
        </div>
        
        <!-- PPT卡片 -->
        <div 
          v-for="(ppt, index) in pptList" 
          :key="ppt.id"
          class="card ppt-card"
          @click="handlePptClick(ppt.id)"
          @mouseenter="handlePptHover(index, true)"
          @mouseleave="handlePptHover(index, false)"
        >
          <!-- 标题栏 -->
          <div class="card-header">
            <h3 class="card-title">{{ ppt.title }}</h3>
            <span class="card-date">{{ ppt.lastEdited }}</span>
          </div>
          
          <!-- 封面图区域 -->
          <div class="card-cover" :class="{ hovered: hoveredPptIndex === index }">
            <img :src="ppt.cover" alt="PPT封面" class="cover-image" />
          </div>
          
          <!-- 五角星按钮 -->
          <button 
            class="star-button" 
            :class="{ active: ppt.isFavorite }"
            @click.stop="toggleFavorite(ppt.id)"
            aria-label="收藏"
          >
            ★
          </button>
          
          <!-- 简介面板 -->
          <div class="card-description" :class="{ visible: hoveredPptIndex === index }">
            <p>{{ ppt.description }}</p>
          </div>
        </div>
      </div>
    </div>
    

    
    <!-- 添加PPT弹窗 -->
    <AddPPTPopup 
      v-if="showAddPPTPopup" 
      @close="showAddPPTPopup = false"
      @success="handleAddPPTSuccess"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AddPPTPopup from '../components/AddPPTPopup.vue'

// 状态
const showAddPPTPopup = ref(false)
const hoveredPptIndex = ref(-1)
const showUserMenu = ref(false)
let hoverTimer = null

// 模拟PPT数据
const pptList = ref([
  {
    id: 1,
    title: '数学基础课程',
    subtitle: '初中数学知识点总结',
    description: '本PPT包含了初中数学的核心知识点，包括代数、几何等内容，适合学生复习使用。',
    cover: 'https://via.placeholder.com/600x338/FFD700/333?text=数学基础课程',
    lastEdited: '2026-03-04 14:30',
    isFavorite: false
  },
  {
    id: 2,
    title: '英语语法精讲',
    subtitle: '高中英语语法重点解析',
    description: '详细讲解高中英语语法知识点，包含时态、语态、从句等内容，配有大量例句。',
    cover: 'https://via.placeholder.com/600x338/4682B4/FFF?text=英语语法精讲',
    lastEdited: '2026-03-03 09:15',
    isFavorite: false
  },
  {
    id: 3,
    title: '物理实验指南',
    subtitle: '初中物理实验操作步骤',
    description: '介绍初中物理常见实验的操作步骤和注意事项，帮助学生掌握实验技能。',
    cover: 'https://via.placeholder.com/600x338/32CD32/333?text=物理实验指南',
    lastEdited: '2026-03-02 16:45',
    isFavorite: false
  },
  {
    id: 4,
    title: '历史事件分析',
    subtitle: '中国近代史重要事件解读',
    description: '深入分析中国近代史上的重要事件，帮助学生理解历史发展脉络。',
    cover: 'https://via.placeholder.com/600x338/8B4513/FFF?text=历史事件分析',
    lastEdited: '2026-03-01 11:20',
    isFavorite: false
  }
])

// 返回
const handleBack = () => {
  window.history.back()
}

// 处理添加PPT成功
const handleAddPPTSuccess = () => {
  console.log('添加PPT成功')
  // 这里可以添加成功后的处理逻辑
}

// 处理PPT悬停
const handlePptHover = (index, isHovering) => {
  // 清除之前的定时器
  if (hoverTimer) {
    clearTimeout(hoverTimer)
    hoverTimer = null
  }
  
  if (isHovering) {
    // 设置防抖动延迟，200毫秒后显示简介
    hoverTimer = setTimeout(() => {
      hoveredPptIndex.value = index
    }, 200)
  } else {
    // 鼠标移出时，300毫秒后隐藏简介
    hoverTimer = setTimeout(() => {
      hoveredPptIndex.value = -1
    }, 300)
  }
}

// 处理PPT点击
const handlePptClick = (id) => {
  console.log('点击PPT:', id)
  // 跳转到PptTeach页面
  window.location.href = '/ppt-teach'
}

// 处理添加PPT
const handleNewPPT = () => {
  showAddPPTPopup.value = true
}

// 切换收藏状态
const toggleFavorite = (id) => {
  const ppt = pptList.value.find(item => item.id === id)
  if (ppt) {
    ppt.isFavorite = !ppt.isFavorite
    if (ppt.isFavorite) {
      // 添加收藏时间
      ppt.favoriteTime = new Date().getTime()
    } else {
      // 取消收藏时移除收藏时间
      delete ppt.favoriteTime
    }
    // 重新排序
    sortPptList()
    // 保存到本地存储
    saveFavorites()
  }
}

// 排序PPT列表，收藏的卡片置顶
const sortPptList = () => {
  pptList.value.sort((a, b) => {
    // 收藏的卡片排在前面
    if (a.isFavorite && !b.isFavorite) return -1
    if (!a.isFavorite && b.isFavorite) return 1
    // 都是收藏的卡片，按收藏时间倒序排列
    if (a.isFavorite && b.isFavorite) {
      return (b.favoriteTime || 0) - (a.favoriteTime || 0)
    }
    // 都不是收藏的卡片，按原有顺序排列
    return 0
  })
}

// 保存收藏状态到本地存储
const saveFavorites = () => {
  localStorage.setItem('favoritePPTs', JSON.stringify(pptList.value.map(item => ({
    id: item.id, 
    isFavorite: item.isFavorite,
    favoriteTime: item.favoriteTime
  }))))
}

// 初始化收藏状态
const initFavorites = () => {
  const savedFavorites = localStorage.getItem('favoritePPTs')
  if (savedFavorites) {
    const favorites = JSON.parse(savedFavorites)
    pptList.value.forEach(ppt => {
      const saved = favorites.find(item => item.id === ppt.id)
      if (saved) {
        ppt.isFavorite = saved.isFavorite
        ppt.favoriteTime = saved.favoriteTime
      }
    })
  }
  // 初始化后排序
  sortPptList()
}

// 初始化
initFavorites()

// 切换用户菜单显示/隐藏
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

// 导航到指定页面
const navigateTo = (page) => {
  console.log(`导航到 ${page} 页面`)
  // 这里可以添加实际的页面跳转逻辑
  showUserMenu.value = false
}

// 处理退出登录
const handleLogout = () => {
  console.log('退出登录')
  // 这里可以添加实际的退出登录逻辑
  showUserMenu.value = false
}

// 点击页面其他区域关闭下拉菜单
document.addEventListener('click', (e) => {
  const userMenu = document.querySelector('.navbar-user')
  if (userMenu && !userMenu.contains(e.target)) {
    showUserMenu.value = false
  }
})
</script>

<style scoped>
/* PPT展示页面容器 */
.ppt-show-page {
  min-height: 100vh;
  width: 100%;
  position: relative;
  overflow: hidden;
  padding: 0;
  box-sizing: border-box;
}

/* 背景渐变 */
.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #ff6b6b, #ffd93d, #ff6b6b);
  background-size: 400% 400%;
  animation: gradientFlow 8s ease infinite;
  z-index: 1;
}



/* 背景流动动画 */
@keyframes gradientFlow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* 气泡容器 */
.bubbles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
  pointer-events: none;
}

/* 气泡样式 */
.bubble {
  position: absolute;
  border-radius: 50%;
  backdrop-filter: blur(50px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: float 10s ease-in-out infinite;
  filter: blur(5px);
}

.bubble-1 {
  width: 200px;
  height: 200px;
  top: 20%;
  left: 25%;
  background: rgba(255, 255, 255, 0.4);
  animation-delay: 0s;
}

.bubble-2 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 20%;
  background: rgba(255, 255, 255, 0.4);
  animation-delay: 3s;
}

.bubble-3 {
  width: 120px;
  height: 120px;
  bottom: 20%;
  left: 20%;
  background: rgba(255, 255, 255, 0.4);
  animation-delay: 6s;
}

/* 气泡浮动动画 */
@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(20px, -20px) scale(1.1);
  }
  50% {
    transform: translate(0, 20px) scale(1);
  }
  75% {
    transform: translate(-20px, 10px) scale(0.9);
  }
}

/* 导航栏 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #EEEEEE;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  z-index: 100;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.navbar-back-button {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.navbar-back-button:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateX(-2px);
}

.back-icon {
  width: 20px;
  height: 20px;
}

.navbar-logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  border: 2px solid rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.user-avatar:hover {
  transform: scale(1.1);
}

.user-greeting {
  font-size: 0.875rem;
  color: #333333;
  font-weight: 500;
}

/* 下拉伸缩栏 */
.navbar-user {
  position: relative;
  cursor: pointer;
}

.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid #EEEEEE;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 180px;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
  opacity: 0;
  z-index: 1000;
}

.user-menu.visible {
  max-height: 200px;
  opacity: 1;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #333333;
}

.menu-item:hover {
  background: rgba(255, 138, 61, 0.1);
  color: #FF8A3D;
}

.menu-icon {
  width: 18px;
  height: 18px;
  margin-right: 12px;
  flex-shrink: 0;
}

.menu-item span {
  font-size: 0.875rem;
  font-weight: 500;
}

/* 主内容区 */
.main-content {
  position: relative;
  z-index: 3;
  min-height: 100vh;
  padding: 80px 2rem 2rem;
  box-sizing: border-box;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 2rem;
  text-align: left;
}

/* 卡片网格 */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px 30px;
  margin-bottom: 2rem;
}

/* 卡片基础样式 */
.card {
  transform: scale(0.8);
  transform-origin: top center;
  margin: 0 auto;
}

/* 响应式网格布局 */
@media (max-width: 1023px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 767px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}

/* 卡片基础样式 */
.card {
  background: #FFFBF5;
  border-radius: 8px;
  border: 1px solid #F0E0D0;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: none;
  transform: scale(0.8);
  transform-origin: top center;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* 新建卡片 */
.new-card {
  background: #FFF8E7;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 220px;
  cursor: pointer;
}

.new-card-content {
  text-align: center;
  padding: 2rem;
}

.plus-button {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #E64340;
  color: white;
  font-size: 2rem;
  font-weight: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  transition: all 0.2s ease;
}



.new-card-text {
  color: #333;
  font-size: 1rem;
  font-weight: 500;
  margin: 0;
}

/* PPT卡片 */
.ppt-card {
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 220px;
  position: relative;
  border: 2px solid transparent;
}

.ppt-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-color: #FF8A3D;
  transition: all 0.3s ease;
}

.ppt-card:active {
  transform: scale(0.98);
  transition: transform 0.1s ease;
}

/* 卡片标题栏 */
.card-header {
  height: auto;
  background: #FF8A3D;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  z-index: 4;
  position: relative;
}

.card-title {
  font-size: 20px;
  font-family: 'Microsoft YaHei', 'Source Han Sans', sans-serif;
  font-weight: bold;
  color: #FFFFFF;
  margin: 0;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  text-align: left;
}

.card-date {
  font-size: 12px;
  font-family: 'Microsoft YaHei', 'Source Han Sans', sans-serif;
  color: #FFFFFF;
  margin: 0;
  line-height: 1;
  white-space: nowrap;
}

/* 卡片封面 */
.card-cover {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 比例 */
  overflow: hidden;
  transition: all 0.3s ease;
  border: 0.5px solid #EEEEEE;
  box-sizing: border-box;
}

.card-cover.hovered .cover-image {
  transform: scale(1.05);
  transition: transform 0.3s ease;
}

.cover-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

/* 五角星按钮 */
.star-button {
  position: absolute;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  background: none;
  border: none;
  font-size: 40px;
  color: #CCCCCC;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
  background-color: currentColor;
  -webkit-clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
  transform: scale(1);
  transform-origin: center;
}

.star-button:hover {
  color: #999999;
  transform: scale(1.1);
}

.star-button.active {
  color: #FF8A3D;
}

/* 卡片描述 */
.card-description {
  position: absolute;
  top: -100%;
  left: 0;
  right: 0;
  background: linear-gradient(to bottom, rgba(255, 102, 0, 1), rgba(255, 165, 0, 0));
  padding: 16px;
  height: 66.67%; /* 卡片总高度的2/3 */
  overflow: hidden;
  transition: top 0.3s ease-out;
  z-index: 2;
  display: flex;
  align-items: center;
}

.card-description.visible {
  top: 0;
}

.card-description p {
  margin: 0;
  font-size: 14px;
  font-family: 'Microsoft YaHei', 'Source Han Sans', sans-serif;
  color: white;
  font-weight: bold;
  line-height: 1.5;
}



/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    padding: 0 1rem;
  }
  
  .main-content {
    padding: 80px 1rem 1rem;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  
  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px 16px;
  }
  
  .user-greeting {
    display: none;
  }
}

@media (max-width: 480px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
  
  .new-card-content {
    padding: 1.5rem;
  }
  
  .plus-button {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
  }
  
  .card-content {
    padding: 12px;
  }
  
  .card-title {
    font-size: 0.9rem;
  }
  
  .card-subtitle {
    font-size: 0.8rem;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .bubble,
  .bg-gradient {
    animation: none;
  }
  
  .navbar-back-button,
  .card,
  .ppt-card,
  .cover-image,
  .card-description,
  .star-button {
    transition: none;
  }
  
  .ppt-card:hover {
    transform: none;
  }
  
  .ppt-card:active {
    transform: none;
  }
  
  .card-cover.hovered .cover-image {
    transform: none;
  }
}
</style>
