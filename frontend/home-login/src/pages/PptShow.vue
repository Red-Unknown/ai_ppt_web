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
      <!-- 标题栏 -->
      <div class="subject-header">
        <h2 class="subject-title">我的课程</h2>
        <div class="search-container">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input type="text" class="search-input" placeholder="搜索PPT..." v-model="searchQuery" @input="handleSearch">
        </div>
      </div>
      
      <!-- 折叠面板系统 -->
      <div class="accordion-container">
        <!-- 动态渲染课程面板 -->
        <div 
          v-for="(chapters, courseId) in chapterList" 
          :key="courseId"
          class="accordion-item"
        >
          <div class="accordion-header" @click="toggleAccordion(courseId)">
            <h3 class="accordion-title">{{ getCourseName(courseId) }}</h3>
            <div class="accordion-actions">
              <svg class="accordion-icon" :class="{ 'rotated': expandedAccordion === courseId }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
          </div>
          <div class="accordion-content" :class="{ 'expanded': expandedAccordion === courseId }">
            <!-- 子折叠面板 -->
            <div class="sub-accordion-container">
              <!-- 动态渲染章节 -->
              <div 
                v-for="(chapter, index) in chapters" 
                :key="`${courseId}-chapter-${index}`"
                class="sub-accordion-item"
              >
                <div class="sub-accordion-header" @click="toggleSubAccordion(courseId, `chapter${index + 1}`)">
                  <h4 class="sub-accordion-title">{{ chapter }}</h4>
                  <svg class="sub-accordion-icon" :class="{ 'rotated': expandedSubAccordion[courseId] === `chapter${index + 1}` }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </div>
                <div class="sub-accordion-content" :class="{ 'expanded': expandedSubAccordion[courseId] === `chapter${index + 1}` }">
                  <div class="card-scroll-container">
                    <!-- 章节PPT卡片 -->
                    <div 
                      v-for="(ppt, pptIndex) in filteredPptList(courseId, `chapter${index + 1}`)" 
                      :key="ppt.id"
                      class="card ppt-card"
                      @click="handlePptClick(ppt.id)"
                      @mouseenter="handlePptHover(pptIndex, true)"
                      @mouseleave="handlePptHover(pptIndex, false)"
                    >
                      <!-- 标题栏 -->
                      <div class="card-header">
                        <h3 class="card-title">{{ ppt.title }}</h3>
                        <span class="card-date">{{ ppt.lastEdited }}</span>
                      </div>
                      
                      <!-- 封面图区域 -->
                      <div class="card-cover" :class="{ hovered: hoveredPptIndex === pptIndex }">
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
                      <div class="card-description" :class="{ visible: hoveredPptIndex === pptIndex }">
                        <p>{{ ppt.description }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 开始学习弹窗 -->
    <StartLearningPopup
      :is-visible="showStartLearningPopup"
      @close="showStartLearningPopup = false"
      @start="handleStartLearning"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import StartLearningPopup from '@/components/StartLearningPopup.vue'

// 状态
const hoveredPptIndex = ref(-1)
const showUserMenu = ref(false)
const showStartLearningPopup = ref(false)
const selectedPPT = ref(null)
let hoverTimer = null

// 折叠面板状态
const expandedAccordion = ref('science') // 默认展开理科面板
const expandedSubAccordion = ref({}) // 子折叠面板状态

// 课程名称映射
const courseNames = ref({
  science: '高等数学',
  arts: '大学物理',
  engineering: '大学英语'
})

// 章节列表
const chapterList = ref({
  science: ['章节1', '章节2', '章节3'],
  arts: ['章节1', '章节2', '章节3'],
  engineering: ['章节1', '章节2', '章节3']
})

// 搜索状态
const searchQuery = ref('')

// 模拟PPT数据
const pptList = ref([
  {
    id: 1,
    title: '数学基础课程',
    subtitle: '高等数学知识点总结',
    description: '本PPT包含了高等数学的核心知识点，包括微积分、线性代数等内容，适合学生复习使用。',
    cover: 'https://via.placeholder.com/600x338/FFD700/333?text=数学基础课程',
    lastEdited: '2026-03-04 14:30',
    isFavorite: false,
    category: 'science',
    chapter: 'chapter1'
  },
  {
    id: 2,
    title: '英语语法精讲',
    subtitle: '大学英语语法重点解析',
    description: '详细讲解大学英语语法知识点，包含时态、语态、从句等内容，配有大量例句。',
    cover: 'https://via.placeholder.com/600x338/4682B4/FFF?text=英语语法精讲',
    lastEdited: '2026-03-03 09:15',
    isFavorite: false,
    category: 'engineering',
    chapter: 'chapter1'
  },
  {
    id: 3,
    title: '物理实验指南',
    subtitle: '大学物理实验操作步骤',
    description: '介绍大学物理常见实验的操作步骤和注意事项，帮助学生掌握实验技能。',
    cover: 'https://via.placeholder.com/600x338/32CD32/333?text=物理实验指南',
    lastEdited: '2026-03-02 16:45',
    isFavorite: false,
    category: 'arts',
    chapter: 'chapter1'
  },
  {
    id: 4,
    title: '数学进阶课程',
    subtitle: '高等数学深入讲解',
    description: '深入讲解高等数学的进阶内容，包括多元微积分、常微分方程等。',
    cover: 'https://via.placeholder.com/600x338/FFA500/333?text=数学进阶课程',
    lastEdited: '2026-03-01 11:20',
    isFavorite: false,
    category: 'science',
    chapter: 'chapter2'
  },
  {
    id: 5,
    title: '英语听力训练',
    subtitle: '大学英语听力技巧',
    description: '介绍大学英语听力的训练方法和技巧，帮助学生提高听力水平。',
    cover: 'https://via.placeholder.com/600x338/1E90FF/FFF?text=英语听力训练',
    lastEdited: '2026-02-28 10:00',
    isFavorite: false,
    category: 'engineering',
    chapter: 'chapter2'
  },
  {
    id: 6,
    title: '物理理论基础',
    subtitle: '大学物理理论讲解',
    description: '详细讲解大学物理的理论基础，包括牛顿力学、电磁学等内容。',
    cover: 'https://via.placeholder.com/600x338/32CD32/333?text=物理理论基础',
    lastEdited: '2026-02-27 15:30',
    isFavorite: false,
    category: 'arts',
    chapter: 'chapter2'
  },
  {
    id: 7,
    title: '数学应用实例',
    subtitle: '高等数学在实际中的应用',
    description: '介绍高等数学在工程、经济等领域的实际应用案例。',
    cover: 'https://via.placeholder.com/600x338/FF6347/333?text=数学应用实例',
    lastEdited: '2026-02-26 14:20',
    isFavorite: false,
    category: 'science',
    chapter: 'chapter3'
  },
  {
    id: 8,
    title: '英语口语练习',
    subtitle: '大学英语口语技巧',
    description: '介绍大学英语口语的练习方法和技巧，帮助学生提高口语水平。',
    cover: 'https://via.placeholder.com/600x338/9370DB/FFF?text=英语口语练习',
    lastEdited: '2026-02-25 09:10',
    isFavorite: false,
    category: 'engineering',
    chapter: 'chapter3'
  },
  {
    id: 9,
    title: '物理实验设计',
    subtitle: '大学物理实验设计方法',
    description: '介绍大学物理实验的设计思路和方法，帮助学生设计自己的实验。',
    cover: 'https://via.placeholder.com/600x338/20B2AA/333?text=物理实验设计',
    lastEdited: '2026-02-24 16:30',
    isFavorite: false,
    category: 'arts',
    chapter: 'chapter3'
  }
])

// 生命周期钩子
onMounted(() => {
  // 从本地存储加载折叠面板状态
  const savedAccordion = localStorage.getItem('expandedAccordion')
  if (savedAccordion) {
    expandedAccordion.value = savedAccordion
  }
  
  // 从本地存储加载章节列表
  loadChapterList()
  
  // 初始化收藏状态
  initFavorites()
  
  // 添加localStorage监听器，实现实时更新
  window.addEventListener('storage', handleStorageChange)
})

onUnmounted(() => {
  // 移除localStorage监听器
  window.removeEventListener('storage', handleStorageChange)
})

// 从本地存储加载章节列表
const loadChapterList = () => {
  // 加载章节列表
  const savedChapters = localStorage.getItem('chapterList')
  if (savedChapters) {
    chapterList.value = JSON.parse(savedChapters)
  }
  
  // 加载课程名称
  const savedCourseNames = localStorage.getItem('courseNames')
  if (savedCourseNames) {
    courseNames.value = JSON.parse(savedCourseNames)
  }
}

// 获取课程名称
const getCourseName = (courseId) => {
  return courseNames.value[courseId] || courseId
}

// 处理localStorage变化
const handleStorageChange = (event) => {
  if (event.key === 'chapterList' || event.key === 'courseNames') {
    // 重新加载章节列表
    loadChapterList()
  }
}

// 切换折叠面板
const toggleAccordion = (accordion) => {
  if (expandedAccordion.value === accordion) {
    expandedAccordion.value = ''
  } else {
    expandedAccordion.value = accordion
  }
  // 保存折叠面板状态到本地存储
  localStorage.setItem('expandedAccordion', expandedAccordion.value)
}

// 切换子折叠面板
const toggleSubAccordion = (parent, child) => {
  if (expandedSubAccordion.value[parent] === child) {
    expandedSubAccordion.value[parent] = ''
  } else {
    expandedSubAccordion.value[parent] = child
  }
}



// 处理搜索
const handleSearch = () => {
  console.log('搜索:', searchQuery.value)
  // 这里可以添加搜索逻辑
}

// 根据分类、章节和搜索过滤PPT列表
const filteredPptList = (category, chapter = null) => {
  let filtered = pptList.value.filter(ppt => ppt.category === category)
  if (chapter) {
    filtered = filtered.filter(ppt => ppt.chapter === chapter)
  }
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(ppt => 
      ppt.title.toLowerCase().includes(query) || 
      ppt.description.toLowerCase().includes(query)
    )
  }
  return filtered
}

// 返回
const handleBack = () => {
  window.history.back()
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
  // 保存选中的PPT
  selectedPPT.value = id
  // 显示开始学习弹窗
  showStartLearningPopup.value = true
}

// 处理开始学习
const handleStartLearning = () => {
  console.log('开始学习PPT:', selectedPPT.value)
  // 跳转到PptTeach页面
  window.location.href = '/ppt-teach'
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
  animation: gradientFlow 15s ease infinite;
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

/* 标题栏 */
.subject-header {
  background: #FF8A3D;
  border-radius: 8px;
  padding: 16px 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.subject-title {
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.search-container {
  position: relative;
  width: 250px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 20px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  width: 16px;
  height: 16px;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 36px;
  border: none;
  border-radius: 20px;
  font-size: 0.875rem;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  background: white;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.5);
}

/* 折叠面板容器 */
.accordion-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 折叠面板项 */
.accordion-item {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(12px);
  border: 1px solid #F0E0D0;
}

/* 折叠面板头部 */
.accordion-header {
  background: #FF8A3D;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.accordion-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.accordion-header:hover {
  background: #FF6B00;
}

.accordion-title {
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.accordion-icon {
  color: white;
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.accordion-icon.rotated {
  transform: rotate(180deg);
}

/* 折叠面板内容 */
.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}

.accordion-content.expanded {
  max-height: 800px;
  transition: max-height 0.5s ease-in;
}

/* 子折叠面板容器 */
.sub-accordion-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
}

/* 子折叠面板项 */
.sub-accordion-item {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #F0E0D0;
}

/* 子折叠面板头部 */
.sub-accordion-header {
  background: #FFA500;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sub-accordion-header:hover {
  background: #FF8C00;
}

.sub-accordion-title {
  color: white;
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.sub-accordion-icon {
  color: white;
  width: 16px;
  height: 16px;
  transition: transform 0.3s ease;
}

.sub-accordion-icon.rotated {
  transform: rotate(180deg);
}

/* 子折叠面板内容 */
.sub-accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}

.sub-accordion-content.expanded {
  max-height: 400px;
  transition: max-height 0.5s ease-in;
}

/* 卡片滚动容器 */
.card-scroll-container {
  display: flex;
  gap: 20px;
  padding: 24px;
  overflow-x: auto;
  scroll-behavior: smooth;
  scrollbar-width: thin;
  scrollbar-color: #FF8A3D #F0E0D0;
}

.card-scroll-container::-webkit-scrollbar {
  height: 6px;
}

.card-scroll-container::-webkit-scrollbar-track {
  background: #F0E0D0;
  border-radius: 3px;
}

.card-scroll-container::-webkit-scrollbar-thumb {
  background: #FF8A3D;
  border-radius: 3px;
}

.card-scroll-container::-webkit-scrollbar-thumb:hover {
  background: #FF6B00;
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
  width: 280px;
  flex-shrink: 0;
  box-sizing: border-box;
}

/* PPT卡片 */
.ppt-card {
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 220px;
  position: relative;
  border: 2px solid transparent;
  transform-origin: center;
}

.ppt-card:hover {
  transform: translateY(-4px) scale(1.02);
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
  width: 40px;
  height: 40px;
  background: none;
  border: none;
  font-size: 32px;
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
  
  .subject-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;
  }
  
  .search-container {
    width: 100%;
  }
  
  .card-scroll-container {
    padding: 16px;
    gap: 12px;
  }
  
  .card {
    width: 240px;
  }
  
  .user-greeting {
    display: none;
  }
}

@media (max-width: 480px) {
  .card {
    width: 200px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .card-date {
    font-size: 10px;
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
  .star-button,
  .accordion-header,
  .accordion-content {
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
  
  .accordion-icon.rotated {
    transform: none;
  }
}
</style>