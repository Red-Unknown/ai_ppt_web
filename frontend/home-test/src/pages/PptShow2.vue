<template>
  <div class="screen">
    <!-- 顶部栏 -->
    <div class="header" :class="{ 'header-shadow': isScrolled }">
      <button class="back-icon" @click="goBack">
        <img src="@/assets/images/action/ic-arrow_left.svg" alt="返回" />
      </button>
      <div class="user-info">
        <div class="avatar" @click="showUserInfoPopup = true"></div>
        <span class="username">你好，{{ userName }}老师</span>
      </div>
    </div>

    <!-- 主体布局 -->
    <div class="main-layout">
      <!-- 左侧：科目栏 -->
      <SubjectSidebar 
        :subjects="subjectList" 
        :selectedSubject="currentSubject?.id"
        theme="blue"
        @select="handleSubjectSelect"
        @delete="handleSubjectDelete"
        @add="handleSubjectAdd"
      />
      
      <!-- 中间：章节栏 -->
      <ChapterSidebar 
        :chapters="chapterList" 
        :selectedChapter="currentChapter?.id"
        theme="blue"
        @select="handleChapterSelect"
        @delete="handleChapterDelete"
        @add="handleChapterAdd"
      />
      
      <!-- 右侧：课程内容区 -->
      <div class="course-content">
        <!-- 固定顶部区域 -->
        <div class="fixed-header">
          <!-- 标题和搜索栏 -->
          <div class="header-row">
            <!-- 课程标题 -->
            <div class="course-title-container">
              <h2 class="course-title">课程</h2>
              <div class="title-actions">
                <button class="action-btn delete-btn" @click="enterDeleteMode">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                  </svg>
                </button>
                <button class="action-btn add-btn" @click="showFileImportPopup = true">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                  </svg>
                </button>
              </div>
            </div>
            
            <!-- 搜索栏 -->
            <div class="search-container">
              <input type="text" class="search-input" placeholder="请输入搜索关键词" v-model="searchQuery" @input="handleSearch">
              <button class="search-button" @click="handleSearch">搜索</button>
            </div>
          </div>
          
          <!-- 横线 -->
          <div class="header-divider"></div>
        </div>
        
        <!-- 可滚动内容区域 -->
        <div class="scrollable-content">
          <!-- 课程列表 -->
          <div class="course-grid">
          <div
            v-for="course in courseList"
            :key="course.id"
            class="course-card"
            @click="handlePptClick(course.id)"
          >
            <div class="card-header">
              <div class="header-content">
                <h3 class="card-title">
                  <span v-if="isDeleteMode" class="delete-icon" @click.stop="confirmDeleteCourse(course)">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                  </span>
                  {{ course.title }}
                </h3>
                <div class="card-info">
                  <span class="card-teacher">{{ course.teacher }}</span>
                  <span class="card-date">{{ course.date }}</span>
                </div>
              </div>
              <img 
                :src="course.isCollected ? require('@/assets/images/action/ic-star-active.svg') : require('@/assets/images/action/ic-collect.svg')" 
                class="star-button" 
                @click.stop="handleToggleCollect(course.id)"
                alt="收藏"
              />
            </div>
            <div class="card-cover">
              <img v-if="course.cover" :src="course.cover" alt="PPT封面" class="cover-image" />
              <div v-else class="cover-placeholder"></div>
              <!-- 课程简介遮罩 -->
              <div class="card-description-overlay">
                <p>{{ course.key_points || '本课程系统讲解核心知识与实战技巧，帮助学生掌握数学基础概念和解题方法。' }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-if="courseList.length === 0" class="empty-state">
          <p>暂无课程</p>
        </div>
        </div>
      </div>
      
      <!-- 右侧悬浮收藏按钮 -->
      <div class="favorite-button" @click="toggleFavoritePanel">
        <span class="favorite-text">收藏</span>
      </div>
      
      <!-- 收藏面板 -->
      <div class="favorite-panel" :class="{ active: showFavoritePanel }">
        <div class="favorite-panel-content">
          <h3 class="favorite-panel-title">已收藏课程</h3>
          <div class="favorite-list">
            <div
              v-for="course in favoriteCourses"
              :key="course.id"
              class="favorite-item"
              @click="handlePptClick(course.id)"
            >
              <!-- 面包屑指示 -->
              <div class="favorite-item-breadcrumb">
                {{ currentSubject?.name }} &gt; {{ currentChapter?.name }}
              </div>
              <!-- 标题和收藏按钮 -->
              <div class="favorite-item-header">
                <div class="favorite-item-title">{{ course.title }}</div>
                <img 
                  src="@/assets/images/action/ic-star-active.svg" 
                  class="favorite-star-button" 
                  @click.stop="handleToggleCollect(course.id)"
                  alt="取消收藏"
                />
              </div>
              <div class="favorite-item-info">{{ course.teacher }} | {{ course.date }}</div>
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
    
    <!-- 用户信息弹窗 -->
    <UserInfoPopup
      v-if="showUserInfoPopup"
      :user-info="userInfo"
      @close="showUserInfoPopup = false"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
    />
    
    <!-- 文件导入弹窗 -->
    <div v-if="showFileImportPopup" class="popup-overlay" @click="showFileImportPopup = false">
      <div class="popup-content" @click.stop>
        <h3 class="popup-title">导入文件</h3>
        <div class="file-upload-area">
          <input type="file" class="file-input" multiple @change="handleFileChange" accept=".ppt,.pptx,.pdf,.jpg,.jpeg,.png">
          <div class="upload-hint">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <p>点击或拖拽文件到此处</p>
            <p class="hint-text">支持 PPT、PDF、图片文件</p>
          </div>
        </div>
        <div class="popup-actions">
          <button class="btn-cancel" @click="showFileImportPopup = false">取消</button>
          <button class="btn-confirm" @click="handleFileUpload">导入</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import StartLearningPopup from '@/components/StartLearningPopup.vue'
import SubjectSidebar from '@/components/SubjectSidebar.vue'
import ChapterSidebar from '@/components/ChapterSidebar.vue'
import UserInfoPopup from '@/components/UserInfoPopup.vue'

// 预览模式状态
const isPreviewMode = ref(false)
const showPreviewModeIndicator = ref(false)

// 状态
const hoveredPptIndex = ref(-1)
const showUserMenu = ref(false)
const showStartLearningPopup = ref(false)
const selectedPPT = ref(null)
let hoverTimer = null

// 搜索状态
const searchQuery = ref('')

// 加载状态
const loading = ref(false)

// 收藏面板状态
const showFavoritePanel = ref(false)

// 鼠标悬停课程ID
const hoveredCourseId = ref(null)

// 删除模式状态
const isDeleteMode = ref(false)

// 文件导入弹窗状态
const showFileImportPopup = ref(false)

// 科目列表
const subjectList = ref([
  { id: 'math', name: '高等数学', isCollected: false },
  { id: 'physics', name: '大学物理', isCollected: false },
  { id: 'english', name: '大学英语', isCollected: false },
  { id: 'chemistry', name: '有机化学', isCollected: false },
  { id: 'biology', name: '生物化学', isCollected: false },
  { id: 'computer', name: '计算机基础', isCollected: false },
  { id: 'history', name: '中国历史', isCollected: false },
  { id: 'politics', name: '政治理论', isCollected: false },
  { id: 'economics', name: '经济学原理', isCollected: false },
  { id: 'literature', name: '文学鉴赏', isCollected: false },
  { id: 'philosophy', name: '哲学导论', isCollected: false },
  { id: 'sociology', name: '社会学', isCollected: false }
])

// 章节列表
const chapterList = ref([
  { id: 'chapter1', name: '第一章 函数与极限', isCollected: false },
  { id: 'chapter2', name: '第二章 导数与微分', isCollected: false },
  { id: 'chapter3', name: '第三章 微分中值定理与导数的应用', isCollected: false },
  { id: 'chapter4', name: '第四章 不定积分', isCollected: false },
  { id: 'chapter5', name: '第五章 定积分', isCollected: false },
  { id: 'chapter6', name: '第六章 定积分的应用', isCollected: false },
  { id: 'chapter7', name: '第七章 微分方程', isCollected: false },
  { id: 'chapter8', name: '第八章 空间解析几何与向量代数', isCollected: false },
  { id: 'chapter9', name: '第九章 多元函数微分法及其应用', isCollected: false },
  { id: 'chapter10', name: '第十章 重积分', isCollected: false },
  { id: 'chapter11', name: '第十一章 曲线积分与曲面积分', isCollected: false },
  { id: 'chapter12', name: '第十二章 无穷级数', isCollected: false }
])

// 当前选中的科目和章节
const currentSubject = ref(null)
const currentChapter = ref(null)

// 课程列表
const courseList = ref([
  {
    id: 1,
    title: '数学基础课程',
    teacher: '张老师',
    date: '2026-03-04',
    cover: '',
    isCollected: false,
    key_points: '本课程系统讲解核心知识与实战技巧，帮助学生掌握数学基础概念和解题方法。'
  },
  {
    id: 2,
    title: '英语语法精讲',
    teacher: '李老师',
    date: '2026-03-03',
    cover: '',
    isCollected: false,
    key_points: '详细讲解英语语法规则，通过大量实例帮助学生理解和应用。'
  },
  {
    id: 3,
    title: '物理实验指南',
    teacher: '王老师',
    date: '2026-03-02',
    cover: '',
    isCollected: false,
    key_points: '介绍物理实验的基本原理和操作方法，培养学生的实验技能。'
  },
  {
    id: 4,
    title: '高等数学进阶',
    teacher: '张老师',
    date: '2026-03-01',
    cover: '',
    isCollected: false,
    key_points: '深入讲解高等数学的核心概念和应用，提高学生的数学思维能力。'
  },
  {
    id: 5,
    title: '大学物理实验',
    teacher: '王老师',
    date: '2026-02-28',
    cover: '',
    isCollected: false,
    key_points: '通过实验教学，帮助学生理解物理概念和规律。'
  },
  {
    id: 6,
    title: '英语听力训练',
    teacher: '李老师',
    date: '2026-02-27',
    cover: '',
    isCollected: false,
    key_points: '针对英语听力进行系统训练，提高学生的听力水平。'
  },
  {
    id: 7,
    title: '数学建模',
    teacher: '张老师',
    date: '2026-02-26',
    cover: '',
    isCollected: false,
    key_points: '介绍数学建模的基本方法和应用，培养学生的建模能力。'
  },
  {
    id: 8,
    title: '物理光学',
    teacher: '王老师',
    date: '2026-02-25',
    cover: '',
    isCollected: false,
    key_points: '详细讲解光学的基本原理和应用，帮助学生理解光的本质。'
  },
  {
    id: 9,
    title: '英语口语',
    teacher: '李老师',
    date: '2026-02-24',
    cover: '',
    isCollected: false,
    key_points: '通过大量口语练习，提高学生的英语口语表达能力。'
  }
])

// 计算已收藏课程
const favoriteCourses = computed(() => {
  return courseList.value.filter(course => course.isCollected)
})

// 用户名
const userName = ref('老师')

// 用户信息
const userInfo = ref({
  name: '老师',
  studentId: '20260001',
  major: '计算机科学与技术'
})

// 用户信息弹窗状态
const showUserInfoPopup = ref(false)

// 检查是否为开发环境
const isDevelopment = () => {
  return import.meta.env.DEV || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
}

// 检查是否启用预览模式
const checkPreviewMode = () => {
  if (!isDevelopment()) {
    return false
  }
  
  // 检查URL参数
  const urlParams = new URLSearchParams(window.location.search)
  return urlParams.get('preview') === 'true'
}

// 生命周期钩子
onMounted(async () => {
  // 检查是否启用预览模式
  isPreviewMode.value = checkPreviewMode()
  showPreviewModeIndicator.value = isPreviewMode.value
  
  // 模拟加载数据
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 加载完成
  loading.value = false
  
  // 默认选中第一个科目和章节
  if (subjectList.value.length > 0) {
    currentSubject.value = subjectList.value[0]
  }
  if (chapterList.value.length > 0) {
    currentChapter.value = chapterList.value[0]
  }
})

// 处理搜索
const handleSearch = () => {
  console.log('搜索:', searchQuery.value)
  // 这里可以添加搜索逻辑
}

// 处理科目选择
const handleSubjectSelect = (subject) => {
  console.log('选择科目:', subject)
  currentSubject.value = subject
  // 这里可以根据科目加载对应的章节
}

// 处理章节选择
const handleChapterSelect = (chapter) => {
  console.log('选择章节:', chapter)
  currentChapter.value = chapter
  // 这里可以根据章节加载对应的课程
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
  // 跳转到PptTeach2页面
  window.location.href = '/ppt-teach2'
}

// 处理收藏状态切换
const handleToggleCollect = (id) => {
  const course = courseList.value.find(item => item.id === id)
  if (course) {
    course.isCollected = !course.isCollected
    console.log('切换收藏状态:', course)
  }
}

// 切换收藏面板
const toggleFavoritePanel = () => {
  showFavoritePanel.value = !showFavoritePanel.value
}

// 返回
const goBack = () => {
  window.history.back()
}

// 处理菜单点击
const handleMenuClick = (menuItem) => {
  console.log('点击菜单:', menuItem)
  // 这里可以根据不同的菜单项执行不同的操作
  switch (menuItem) {
    case 'profile':
      // 处理个人资料
      break
    case 'settings':
      // 处理设置
      break
    case 'aiConfig':
      // 处理AI配置
      break
    case 'about':
      // 处理关于我们
      break
    default:
      break
  }
  // 关闭弹窗
  showUserInfoPopup.value = false
}

// 处理退出登录
const handleLogout = () => {
  console.log('退出登录')
  // 这里可以添加退出登录的逻辑
  // 例如清除localStorage中的session_id
  localStorage.removeItem('session_id')
  // 跳转到登录页面
  window.location.href = '/'
}

// 进入删除模式
const enterDeleteMode = () => {
  isDeleteMode.value = !isDeleteMode.value
}

// 确认删除课程
const confirmDeleteCourse = (course) => {
  if (confirm(`确定要删除课程「${course.title}」吗？`)) {
    const index = courseList.value.findIndex(item => item.id === course.id)
    if (index !== -1) {
      courseList.value.splice(index, 1)
      console.log('删除课程:', course.title)
    }
  }
}

// 选中的文件
const selectedFiles = ref([])

// 处理文件导入
const handleFileImport = (file) => {
  console.log('导入文件:', file)
  // 这里可以添加文件上传和处理逻辑
  showFileImportPopup.value = false
}

// 处理文件选择
const handleFileChange = (event) => {
  selectedFiles.value = Array.from(event.target.files)
  console.log('选择的文件:', selectedFiles.value)
}

// 处理文件上传
const handleFileUpload = () => {
  if (selectedFiles.value.length > 0) {
    selectedFiles.value.forEach(file => {
      console.log('上传文件:', file.name)
      // 这里可以添加文件上传和处理逻辑
      // 例如创建新的课程
      const newCourse = {
        id: courseList.value.length + 1,
        title: file.name,
        teacher: '张老师',
        date: new Date().toISOString().split('T')[0],
        cover: '',
        isCollected: false,
        key_points: `课程内容来自文件: ${file.name}`
      }
      courseList.value.push(newCourse)
    })
    selectedFiles.value = []
    showFileImportPopup.value = false
  }
}

// 处理科目删除
const handleSubjectDelete = (subjectId) => {
  const index = subjectList.value.findIndex(item => item.id === subjectId)
  if (index !== -1) {
    const deletedSubject = subjectList.value[index]
    subjectList.value.splice(index, 1)
    console.log('删除科目:', deletedSubject.name)
    
    // 如果删除的是当前选中的科目，重置选中状态
    if (currentSubject.value && currentSubject.value.id === subjectId) {
      currentSubject.value = subjectList.value.length > 0 ? subjectList.value[0] : null
    }
  }
}

// 处理科目添加
const handleSubjectAdd = (newSubject) => {
  subjectList.value.push(newSubject)
  console.log('添加科目:', newSubject.name)
  // 选中新添加的科目
  currentSubject.value = newSubject
}

// 处理章节删除
const handleChapterDelete = (chapterId) => {
  const index = chapterList.value.findIndex(item => item.id === chapterId)
  if (index !== -1) {
    const deletedChapter = chapterList.value[index]
    chapterList.value.splice(index, 1)
    console.log('删除章节:', deletedChapter.name)
    
    // 如果删除的是当前选中的章节，重置选中状态
    if (currentChapter.value && currentChapter.value.id === chapterId) {
      currentChapter.value = chapterList.value.length > 0 ? chapterList.value[0] : null
    }
  }
}

// 处理章节添加
const handleChapterAdd = (newChapter) => {
  chapterList.value.push(newChapter)
  console.log('添加章节:', newChapter.name)
  // 选中新添加的章节
  currentChapter.value = newChapter
}
</script>

<style scoped>
/* 屏幕容器 */
.screen {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部栏 */
.header {
  height: 60px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.back-icon {
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.back-icon:hover {
  transform: translateX(-2px);
}

.back-icon img {
  width: 24px;
  height: 24px;
  transition: all 0.2s ease;
}

.back-icon:hover img {
  filter: invert(45%) sepia(70%) saturate(300%) hue-rotate(180deg) brightness(90%) contrast(90%);
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
  background: #008AC5;
  transition: all 0.2s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.avatar:hover {
  box-shadow: 0 0 0 4px rgba(0, 138, 197, 0.2);
}

.username {
  font-size: 16px;
  color: #008AC5;
  font-weight: 400;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

/* 主体布局 */
.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* 右侧：课程内容区 */
.course-content {
  flex: 1;
  background: #E1F4FF;
  padding: 24px;
  height: calc(100vh - 60px);
  box-shadow: -4px 0 12px rgba(0, 138, 197, 0.1);
  display: flex;
  flex-direction: column;
}

/* 固定顶部区域 */
.fixed-header {
  margin-bottom: 20px;
}

/* 标题和搜索栏行 */
.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

/* 课程标题容器 */
.course-title-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 课程标题 */
.course-title {
  font-size: 24px;
  font-weight: bold;
  color: #008AC5;
  margin: 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

/* 标题操作按钮 */
.title-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 138, 197, 0.2);
  color: #008AC5;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(0, 138, 197, 0.3);
  transform: scale(1.1);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.delete-btn:hover {
  background: rgba(255, 0, 0, 0.3);
  color: white;
}

.add-btn:hover {
  background: rgba(0, 255, 0, 0.3);
  color: white;
}

/* 课程卡片标题删除图标 */
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.delete-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(255, 0, 0, 0.3);
  color: #008AC5;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.delete-icon:hover {
  background: rgba(255, 0, 0, 0.5);
  color: white;
  transform: scale(1.1);
}

.delete-icon svg {
  width: 12px;
  height: 12px;
}

/* 横线 */
.header-divider {
  height: 1px;
  background-color: #008AC5;
  margin: 0 0 16px 0;
  width: 100%;
}

/* 搜索栏 */
.search-container {
  width: 100%;
  max-width: 400px;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

/* 可滚动内容区域 */
.scrollable-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 0;
}

/* 隐藏滚动条 */
.scrollable-content::-webkit-scrollbar {
  width: 0;
  height: 0;
}

.scrollable-content::-webkit-scrollbar-track {
  background: transparent;
}

.scrollable-content::-webkit-scrollbar-thumb {
  background: transparent;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #008AC5;
  border-radius: 4px;
  font-size: 14px;
  background: #FFFFFF;
  transition: all 0.2s ease;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  background-image: url('@/assets/images/action/ic-Search.svg');
  background-repeat: no-repeat;
  background-position: 8px center;
  background-size: 16px 16px;
  padding-left: 32px;
}

.search-input::placeholder {
  color: #999999;
}

.search-input:focus {
  outline: none;
  border-color: #006B9A;
  box-shadow: 0 0 0 2px rgba(0, 138, 197, 0.1);
}

.search-button {
  padding: 8px 16px;
  background: #008AC5;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.search-button:hover {
  background: #006B9A;
  transform: translateY(-1px);
}

/* 课程网格 */
.course-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  justify-content: flex-start;
  margin-bottom: 20px;
}

/* 课程卡片 */
.course-card {
  background: #FFFFFF;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.course-card:hover {
  box-shadow: 0 4px 8px rgba(0, 138, 197, 0.15);
  transform: translateY(-2px);
}

.card-header {
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: #E1F4FF;
}

.header-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #008AC5;
  margin: 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.star-button {
  width: 20px;
  height: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 12px;
}

.star-button:hover {
  transform: scale(1.1);
}

.card-info {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.card-teacher {
  font-size: 12px;
  color: #008AC5;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.card-date {
  font-size: 12px;
  color: #008AC5;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.card-cover {
  height: 150px;
  background: #f5f5f5;
  position: relative;
  overflow: hidden;
}

/* 课程简介遮罩 */
.card-description-overlay {
  position: absolute;
  top: -100%;
  left: 0;
  right: 0;
  height: 66.67%; /* 占卡片的三分之二 */
  background: linear-gradient(to bottom, rgba(225, 244, 255, 1), rgba(225, 244, 255, 0));
  padding: 12px;
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 10;
}

.card-description-overlay p {
  font-size: 12px;
  color: #008AC5;
  margin: 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

/* 鼠标移入时的动画效果 */
.course-card:hover .card-description-overlay {
  top: 0;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
}

/* 右侧悬浮收藏按钮 */
.favorite-button {
  position: fixed;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  background: #008AC5;
  width: 40px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 50;
  transition: all 0.2s ease;
  border-radius: 8px 0 0 8px;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
}

.favorite-button:hover {
  background: #006B9A;
  width: 48px;
}

.favorite-text {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  color: #FFFFFF;
  font-size: 16px;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  font-weight: bold;
}

/* 收藏面板 */
.favorite-panel {
  position: fixed;
  right: -300px;
  top: 60px;
  width: 300px;
  height: calc(100vh - 60px);
  background: #E1F4FF;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  z-index: 40;
  overflow-y: auto;
  border-left: 1px solid #CDE8FF;
}

.favorite-panel.active {
  right: 40px;
}

.favorite-panel-content {
  padding: 24px;
}

.favorite-panel-title {
  font-size: 18px;
  font-weight: bold;
  color: #008AC5;
  margin-bottom: 16px;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  text-align: center;
}

.favorite-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.favorite-item {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.favorite-item:hover {
  box-shadow: 0 2px 8px rgba(0, 138, 197, 0.1);
  transform: translateY(-2px);
}

/* 面包屑指示 */
.favorite-item-breadcrumb {
  font-size: 10px;
  color: #999999;
  margin-bottom: 4px;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

/* 标题和收藏按钮容器 */
.favorite-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.favorite-item-title {
  font-size: 14px;
  font-weight: bold;
  color: #008AC5;
  flex: 1;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

/* 收藏按钮 */
.favorite-star-button {
  width: 16px;
  height: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 8px;
}

.favorite-star-button:hover {
  transform: scale(1.1);
  filter: brightness(1.2);
}

.favorite-item-info {
  font-size: 12px;
  color: #999999;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .course-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }
  
  .subject-sidebar,
  .chapter-sidebar {
    width: 100% !important;
    height: auto !important;
    padding: 12px 0;
  }
  
  .subject-list,
  .chapter-list {
    flex-direction: row;
    overflow-x: auto;
    padding: 0 16px;
  }
  
  .subject-item,
  .chapter-item {
    white-space: nowrap;
  }
  
  .course-content {
    padding: 16px;
  }
  
  /* 调整小屏幕下的标题和搜索栏布局 */
  .header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .search-container {
    max-width: 100%;
    width: 100%;
  }
  
  .course-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .course-card {
    width: 100%;
  }
  
  .favorite-panel {
    width: 250px;
  }
  
  .favorite-panel.active {
    right: 40px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 0 16px;
  }
  
  .username {
    font-size: 14px;
  }
  
  .back-icon img {
    width: 20px;
    height: 20px;
  }
  
  .avatar {
    width: 36px;
    height: 36px;
  }
  
  .course-card {
    min-width: 100%;
  }
  
  .card-cover {
    height: 120px;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .back-icon,
  .search-button,
  .course-card,
  .star-button,
  .avatar,
  .favorite-button,
  .favorite-panel,
  .action-btn,
  .delete-icon {
    transition: none;
  }
  
  .back-icon:hover {
    transform: none;
  }
  
  .search-button:hover {
    transform: none;
  }
  
  .course-card:hover {
    transform: none;
  }
  
  .star-button:hover {
    transform: none;
  }
  
  .favorite-item:hover {
    transform: none;
  }
  
  .action-btn:hover {
    transform: none;
  }
  
  .delete-icon:hover {
    transform: none;
  }
}

/* 弹窗样式 */
.popup-overlay {
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
}

.popup-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: popupFadeIn 0.3s ease;
}

@keyframes popupFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.popup-title {
  font-size: 18px;
  font-weight: bold;
  color: #008AC5;
  margin: 0 0 20px 0;
  text-align: center;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.file-upload-area {
  border: 2px dashed #008AC5;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  margin-bottom: 20px;
  position: relative;
  transition: all 0.2s ease;
}

.file-upload-area:hover {
  border-color: #006B9A;
  background: rgba(0, 138, 197, 0.05);
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 1;
}

.upload-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 0;
}

.upload-hint svg {
  width: 48px;
  height: 48px;
  color: #008AC5;
  opacity: 0.6;
}

.upload-hint p {
  margin: 0;
  font-size: 14px;
  color: #008AC5;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.hint-text {
  font-size: 12px !important;
  color: #999 !important;
}

.popup-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-cancel,
.btn-confirm {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-confirm {
  background: #008AC5;
  color: white;
}

.btn-confirm:hover {
  background: #006B9A;
  transform: translateY(-1px);
}

/* 响应式弹窗 */
@media (max-width: 480px) {
  .popup-content {
    padding: 16px;
    width: 95%;
  }
  
  .file-upload-area {
    padding: 20px 16px;
  }
  
  .upload-hint svg {
    width: 32px;
    height: 32px;
  }
  
  .upload-hint p {
    font-size: 12px;
  }
}
</style>
