<template>
  <div class="screen">
    <!-- 顶部栏 -->
    <Header 
      :user-name="userName"
      user-role="teacher"
      theme="blue"
      @back="goBack"
      @avatar-click="() => showUserInfoPopup = true"
    />


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

    <!-- 用户信息弹窗 -->
    <UserInfoPopup
      v-if="showUserInfoPopup"
      :visible="showUserInfoPopup"
      :user-info="userInfo"
      theme="blue"
      @close="showUserInfoPopup = false"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @save-profile="handleSaveProfile"
    />

    <!-- 关于我们弹窗 -->
    <AboutUsPopup
      v-if="showAboutUsPopup"
      theme="blue"
      @close="showAboutUsPopup = false"
    />
    
    <!-- 文件导入弹窗 -->
    <div v-if="showFileImportPopup" class="popup-overlay" @click="showFileImportPopup = false">
      <div class="popup-content" @click.stop>
        <h3 class="popup-title">导入文件</h3>
        <div class="file-upload-area" :class="{ 'has-files': selectedFiles.length > 0 }">
          <input type="file" class="file-input" multiple @change="handleFileChange" accept=".ppt,.pptx,.pdf,.jpg,.jpeg,.png">
          <div class="upload-hint" v-if="selectedFiles.length === 0">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <p>点击或拖拽文件到此处</p>
            <p class="hint-text">支持 PPT、PDF、图片文件</p>
          </div>
          <div class="selected-files" v-else>
            <h4 class="files-title">已选择的文件</h4>
            <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
              <div class="file-info">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
              </div>
              <button class="remove-file-btn" @click.stop="removeFile(index)">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 上传进度 -->
        <div class="upload-progress" v-if="isUploading && wsStatus === 'disconnected'">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <span class="progress-text">{{ uploadProgress }}%</span>
        </div>
        
        <!-- WebSocket解析进度 -->
        <div class="ws-progress" v-if="isUploading && wsStatus !== 'disconnected'">
          <div class="ws-status">
            <span class="status-label">解析状态:</span>
            <span class="status-value" :class="wsStatus">
              {{ wsStatus === 'connecting' ? '连接中' : 
                 wsStatus === 'connected' ? '解析中' : 
                 wsStatus === 'completed' ? '完成' : '错误' }}
            </span>
          </div>
          <div class="ws-message" v-if="wsMessage">
            <span class="message-label">当前步骤:</span>
            <span class="message-value">{{ wsMessage }}</span>
          </div>
          <div class="progress-bar" v-if="wsProgress > 0">
            <div class="progress-fill" :style="{ width: wsProgress + '%' }"></div>
          </div>
          <span class="progress-text" v-if="wsProgress > 0">{{ wsProgress }}%</span>
        </div>
        
        <div class="popup-actions">
          <button class="btn-cancel" @click="showFileImportPopup = false" :disabled="isUploading">取消</button>
          <button class="btn-confirm" @click="handleFileUpload" :disabled="selectedFiles.length === 0 || isUploading">
            {{ isUploading ? '导入中...' : '导入' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Header from '@/components/Header.vue'
import SubjectSidebar from '@/components/SubjectSidebar.vue'
import ChapterSidebar from '@/components/ChapterSidebar.vue'
import UserInfoPopup from '@/components/UserInfoPopup.vue'
import AboutUsPopup from '@/components/AboutUsPopup.vue'

// 预览模式状态
const isPreviewMode = ref(false)
const showPreviewModeIndicator = ref(false)

// 状态
const hoveredPptIndex = ref(-1)
const showUserMenu = ref(false)
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
  major: '计算机科学与技术',
  portrait: '热爱教育事业，致力于培养优秀的学生'
})

// 用户信息弹窗状态
const showUserInfoPopup = ref(false)

// 关于我们弹窗状态
const showAboutUsPopup = ref(false)

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
  // 直接跳转到PptTeach2页面
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
    case 'settings':
      // 处理设置
      alert('设置功能暂未开放')
      break
    case 'aiConfig':
      // 处理AI配置
      alert('AI配置功能暂未开放')
      break
    case 'about':
      // 处理关于我们
      showUserInfoPopup.value = false
      showAboutUsPopup.value = true
      break
    default:
      break
  }
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

// 处理保存个人资料
const handleSaveProfile = (profileData) => {
  console.log('保存个人资料:', profileData)
  // 这里可以添加保存个人资料的逻辑
  userInfo.value = { ...userInfo.value, ...profileData }
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
const isUploading = ref(false)
const uploadProgress = ref(0)

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

// WebSocket连接状态
const wsConnection = ref(null)
const wsStatus = ref('disconnected')
const wsProgress = ref(0)
const wsMessage = ref('')

// 生成唯一的lesson_id
const generateLessonId = () => {
  return 'lesson_' + Date.now() + '_' + Math.floor(Math.random() * 10000)
}

// 建立WebSocket连接并发送首帧请求
const establishWebSocketConnection = (uploadData, courseId, schoolId) => {
  return new Promise((resolve, reject) => {
    try {
      // 生成唯一的lesson_id
      const lessonId = generateLessonId()
      
      // 从上传数据中获取文件信息
      const fileUrl = uploadData.fileUrl || uploadData.data?.fileUrl
      const fileType = uploadData.fileType || uploadData.data?.fileType
      const fileName = uploadData.fileName || uploadData.data?.fileName || 'unknown.ppt'
      
      if (!fileUrl || !fileType) {
        reject(new Error('上传响应缺少必要的文件信息'))
        return
      }
      
      // 构建WebSocket连接
      const ws = new WebSocket('ws://127.0.0.1:8001/api/v1/ws/script')
      wsConnection.value = ws
      wsStatus.value = 'connecting'
      
      // 连接成功处理
      ws.onopen = () => {
        console.log('WebSocket连接已建立')
        wsStatus.value = 'connected'
        
        // 构建输出文件路径
        const baseName = fileName.replace(/\.[^/.]+$/, '')
        
        // 发送首帧请求 - 根据接口文档要求
        const firstFrame = {
          service: 'full_pipeline',
          file_path: fileUrl,
          file_type: fileType,
          output_raw_json_path: `sandbox/${baseName}_全流程测试.json`,
          output_text_path: `sandbox/${baseName}_全流程测试.txt`,
          lesson_id: lessonId,
          course_id: courseId,
          school_id: schoolId,
          title: baseName,
          voice: 'zh-CN-XiaoxiaoNeural',
          enable_script_llm: true
        }
        
        console.log('发送首帧请求:', firstFrame)
        ws.send(JSON.stringify(firstFrame))
      }
      
      // 消息接收处理
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          console.log('收到WebSocket消息:', message)
          
          // 处理不同类型的消息
          if (message.type === 'status') {
            wsMessage.value = message.message || `步骤: ${message.step}`
            console.log('状态消息:', wsMessage.value)
          } else if (message.type === 'progress' && message.step === 'tts') {
            // 计算TTS进度百分比
            if (message.total > 0) {
              wsProgress.value = Math.round((message.current / message.total) * 100)
              console.log('TTS进度:', wsProgress.value, '%')
            }
          } else if (message.type === 'done') {
            console.log('解析完成:', message)
            wsStatus.value = 'completed'
            resolve({ success: true, lessonId: message.lesson_id })
          } else if (message.type === 'error') {
            console.error('WebSocket错误:', message)
            wsStatus.value = 'error'
            reject(new Error(message.error || '解析过程中发生错误'))
          }
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }
      
      // 连接错误处理
      ws.onerror = (error) => {
        console.error('WebSocket连接错误:', error)
        wsStatus.value = 'error'
        reject(new Error('WebSocket连接失败'))
      }
      
      // 连接关闭处理
      ws.onclose = (event) => {
        console.log('WebSocket连接已关闭:', event.code, event.reason)
        wsStatus.value = 'disconnected'
        wsConnection.value = null
      }
      
    } catch (error) {
      console.error('建立WebSocket连接失败:', error)
      wsStatus.value = 'error'
      reject(new Error('建立WebSocket连接失败'))
    }
  })
}

// 关闭WebSocket连接
const closeWebSocketConnection = () => {
  if (wsConnection.value) {
    wsConnection.value.close()
    wsConnection.value = null
    wsStatus.value = 'disconnected'
    wsProgress.value = 0
    wsMessage.value = ''
  }
}

// 处理文件上传
const handleFileUpload = async () => {
  if (selectedFiles.value.length > 0) {
    isUploading.value = true
    
    try {
      for (const file of selectedFiles.value) {
        console.log('上传文件:', file.name)
        
        // 准备FormData
        const formData = new FormData()
        formData.append('file', file)
        formData.append('course_id', 'course_mechanics_001')
        formData.append('school_id', 'SCH001')
        
        // 使用XMLHttpRequest监听上传进度
        const response = await new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest()
          
          xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable) {
              const percentComplete = Math.round((event.loaded / event.total) * 100)
              uploadProgress.value = percentComplete
            }
          })
          
          xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const data = JSON.parse(xhr.responseText)
                resolve({ ok: true, data })
              } catch (error) {
                reject(new Error('Invalid response format'))
              }
            } else {
              try {
                const errorData = JSON.parse(xhr.responseText)
                reject(new Error(errorData.detail || `上传失败: ${xhr.status}`))
              } catch (error) {
                reject(new Error(`上传失败: ${xhr.status}`))
              }
            }
          })
          
          xhr.addEventListener('error', () => {
            reject(new Error('网络错误，请检查连接'))
          })
          
          xhr.addEventListener('abort', () => {
            reject(new Error('上传被取消'))
          })
          
          xhr.open('POST', 'http://127.0.0.1:8001/api/v1/lesson/upload')
          xhr.send(formData)
        })
        
        // 上传成功，获取上传响应数据
        const uploadResult = response.data
        console.log('上传成功，响应数据:', uploadResult)
        
        // 上传成功，建立WebSocket连接进行解析
        try {
          console.log('开始WebSocket解析流程')
          await establishWebSocketConnection(uploadResult, 'course_mechanics_001', 'SCH001')
          console.log('WebSocket解析流程完成')
        } catch (wsError) {
          console.error('WebSocket解析失败:', wsError)
          // 解析失败不影响课程创建，继续执行
        } finally {
          // 关闭WebSocket连接
          closeWebSocketConnection()
        }
        
        // 上传成功，创建新的课程
        const newCourse = {
          id: courseList.value.length + 1,
          title: file.name,
          teacher: userInfo.value.name || '老师',
          date: new Date().toISOString().split('T')[0],
          cover: '',
          isCollected: false,
          key_points: `课程内容来自文件: ${file.name}`
        }
        courseList.value.push(newCourse)
      }
      
      selectedFiles.value = []
      showFileImportPopup.value = false
      uploadProgress.value = 0
    } catch (error) {
      console.error('文件上传失败:', error)
      alert(`上传失败: ${error.message}`)
      uploadProgress.value = 0
    } finally {
      isUploading.value = false
      // 确保WebSocket连接已关闭
      closeWebSocketConnection()
    }
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 移除文件
const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
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
  background: #F2FCFF;
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
  color: #276884;
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
  color: #276884;
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
  color: #276884;
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
  background: #CDF4FF;
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
  color: #276884;
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
  color: #276884;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.card-date {
  font-size: 12px;
  color: #276884;
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
  background: linear-gradient(to bottom, rgba(205, 244, 255, 1), rgba(205, 244, 255, 0));
  padding: 12px;
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 10;
}

.card-description-overlay p {
  font-size: 12px;
  color: #276884;
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
  background: #F2FCFF;
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
  color: #276884;
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
  color: #276884;
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
  color: #276884;
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

.file-upload-area.has-files .file-input {
  z-index: -1;
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
  color: #276884;
  opacity: 0.6;
}

.upload-hint p {
  margin: 0;
  font-size: 14px;
  color: #276884;
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

/* 已选择文件样式 */
.selected-files {
  width: 100%;
  text-align: left;
}

.files-title {
  font-size: 14px;
  font-weight: 600;
  color: #276884;
  margin: 0 0 12px 0;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.file-item:hover {
  background: #e9ecef;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-size: 14px;
  color: #333;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: #666;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.remove-file-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: #dc3545;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2);
}

.remove-file-btn:hover {
  background: #c82333;
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(220, 53, 69, 0.3);
}

.remove-file-btn:active {
  transform: scale(0.95);
  box-shadow: 0 1px 2px rgba(220, 53, 69, 0.2);
}

.remove-file-btn svg {
  width: 14px;
  height: 14px;
  fill: white;
}

/* 上传进度样式 */
.upload-progress,
.ws-progress {
  margin: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #008AC5, #006B9A);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #666;
  text-align: right;
  font-weight: 500;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

/* WebSocket解析进度样式 */
.ws-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 8px;
}

.status-label {
  font-size: 12px;
  font-weight: 600;
  color: #276884;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.status-value {
  font-size: 12px;
  font-weight: 500;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  padding: 2px 8px;
  border-radius: 12px;
}

.status-value.connecting {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.status-value.connected {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.status-value.completed {
  background: rgba(0, 123, 255, 0.2);
  color: #007bff;
}

.status-value.error {
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.ws-message {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 8px;
}

.message-label {
  font-size: 12px;
  font-weight: 600;
  color: #276884;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.message-value {
  font-size: 12px;
  color: #333;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  line-height: 1.4;
}

/* 按钮禁用状态 */
.btn-cancel:disabled,
.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-confirm:disabled:hover {
  background: #008AC5;
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
  
  .file-name {
    font-size: 12px;
  }
  
  .file-size {
    font-size: 10px;
  }
  
  .remove-file-btn {
    width: 20px;
    height: 20px;
  }
  
  .remove-file-btn svg {
    width: 12px;
    height: 12px;
  }
}
</style>
