<template>
  <div class="chapter-sidebar" :class="{ 'theme-orange': theme === 'orange', 'theme-blue': theme === 'blue' }">
    <!-- 固定标题区域 -->
    <div class="fixed-header">
  <div class="title-container">
    <div class="sidebar-title">章节</div>
    <div class="title-actions" v-if="theme === 'blue'">
      <button class="action-btn delete-btn" @click="enterDeleteMode">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
        </svg>
      </button>
      <button class="action-btn add-btn" @click="showAddChapterPopup = true">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
      </button>
    </div>
  </div>
  <div class="divider" />
</div>
    
    <!-- 可滚动内容区域 -->
    <div class="scrollable-content" ref="chapterListRef">
      <div
        v-for="chapter in chapters"
        :key="chapter.id"
        class="chapter-item"
        :data-id="chapter.id"
        :class="{ 'selected': chapter.id === selectedChapter }"
        @click="handleSelect(chapter)"
      >
        <span v-if="isDeleteMode && theme === 'blue'" class="delete-icon" @click.stop="confirmDeleteChapter(chapter)">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </span>
        <span class="chapter-name">{{ chapter.name }}</span>
      </div>
      <div class="highlight-indicator" ref="highlightIndicatorRef"></div>
    </div>
  </div>

  <!-- 新增章节弹窗 -->
  <div v-if="showAddChapterPopup" class="popup-overlay" @click="showAddChapterPopup = false">
    <div class="popup-content" @click.stop>
      <h3 class="popup-title">新增章节</h3>
      <div class="popup-input-area">
        <input 
          type="text" 
          v-model="newChapterName" 
          placeholder="请输入章节名称" 
          class="popup-input"
          @keyup.enter="addNewChapter"
        >
      </div>
      <div class="popup-actions">
        <button class="btn-cancel" @click="showAddChapterPopup = false">取消</button>
        <button class="btn-confirm" @click="addNewChapter">确定</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'

/**
 * 章节侧边栏组件
 * @description 显示课程章节列表，支持章节选择、添加和删除
 * @example
 * <ChapterSidebar
 *   :chapters="chaptersList"
 *   :selected-chapter="currentChapterId"
 *   theme="blue"
 *   @select="handleSelectChapter"
 *   @add="handleAddChapter"
 *   @delete="handleDeleteChapter"
 * />
 */
export default {
  name: 'ChapterSidebar',
  props: {
    /**
     * 章节列表数据
     * @type {Array<{id: string, name: string, isCollected?: boolean}>}
     * @default []
     */
    chapters: { 
      type: Array, 
      default: () => [],
      validator: (value) => {
        if (!Array.isArray(value)) {
          console.warn('[ChapterSidebar] chapters must be an array')
          return false
        }
        const isValid = value.every(chapter => 
          typeof chapter === 'object' && 
          chapter !== null && 
          typeof chapter.id === 'string' && 
          typeof chapter.name === 'string'
        )
        if (!isValid) {
          console.warn('[ChapterSidebar] Each chapter must have id and name properties')
        }
        return isValid
      }
    },
    /**
     * 当前选中的章节ID
     * @type {string}
     * @default ''
     */
    selectedChapter: { type: String, default: '' },
    /**
     * 主题类型
     * @type {'blue' | 'orange'}
     * @default 'blue'
     */
    theme: { 
      type: String, 
      default: 'blue',
      validator: (value) => {
        const validThemes = ['blue', 'orange']
        if (!validThemes.includes(value)) {
          console.warn(`[ChapterSidebar] Invalid theme: "${value}". Must be one of: ${validThemes.join(', ')}`)
          return false
        }
        return true
      }
    }
  },
  emits: ['select', 'collect', 'delete', 'add'],
  setup(props, { emit }) {
    const chapterListRef = ref(null)
    const highlightIndicatorRef = ref(null)
    const isDeleteMode = ref(false)
    const showAddChapterPopup = ref(false)
    const newChapterName = ref('')

    const handleSelect = (chapter) => {
      emit('select', chapter)
    }

    const handleCollect = (chapter) => {
      chapter.isCollected = !chapter.isCollected
      emit('collect', chapter)
    }

    const getStarIcon = (isCollected) => {
      if (isCollected) {
        return require('@/assets/images/action/ic-star-active.svg')
      } else {
        return require('@/assets/images/action/ic-collect.svg')
      }
    }

    // 进入删除模式
    const enterDeleteMode = () => {
      isDeleteMode.value = !isDeleteMode.value
    }

    // 确认删除章节
    const confirmDeleteChapter = (chapter) => {
      if (confirm(`确定要删除章节「${chapter.name}」吗？`)) {
        emit('delete', chapter.id)
      }
    }

    // 添加新章节
    const addNewChapter = () => {
      if (newChapterName.value.trim()) {
        const newChapter = {
          id: 'chapter_' + Date.now(),
          name: newChapterName.value.trim(),
          isCollected: false
        }
        emit('add', newChapter)
        newChapterName.value = ''
        showAddChapterPopup.value = false
      }
    }

    // 更新高亮指示器位置
    const updateHighlightPosition = () => {
      if (!chapterListRef.value || !highlightIndicatorRef.value || !props.selectedChapter) {
        return
      }

      const selectedItem = chapterListRef.value.querySelector(`[data-id="${props.selectedChapter}"]`)
      if (selectedItem) {
        const { top, height, width, left } = selectedItem.getBoundingClientRect()
        const listRect = chapterListRef.value.getBoundingClientRect()
        
        const relativeTop = top - listRect.top
        
        highlightIndicatorRef.value.style.transition = 'all 0.4s ease'
        highlightIndicatorRef.value.style.top = `${relativeTop}px`
        highlightIndicatorRef.value.style.height = `${height}px`
        highlightIndicatorRef.value.style.width = `${width - 8}px`
        highlightIndicatorRef.value.style.left = `${left - listRect.left + 8}px`
      }
    }

    // 监听选中状态变化
    watch(() => props.selectedChapter, () => {
      updateHighlightPosition()
    })

    // 监听窗口大小变化
    const handleResize = () => {
      updateHighlightPosition()
    }

    onMounted(() => {
      // 初始化高亮位置
      setTimeout(updateHighlightPosition, 100)
      
      // 添加窗口大小变化监听
      window.addEventListener('resize', handleResize)
    })

    return {
      chapterListRef,
      highlightIndicatorRef,
      handleSelect,
      handleCollect,
      getStarIcon,
      isDeleteMode,
      showAddChapterPopup,
      newChapterName,
      enterDeleteMode,
      confirmDeleteChapter,
      addNewChapter
    }
  }
}
</script>

<style scoped>
.chapter-sidebar {
  width: 180px;
  padding: 20px 0;
  height: calc(100vh - 60px);
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: var(--theme-background);
  box-shadow: -4px 0 12px var(--theme-shadow);
}

.sidebar-title {
  color: var(--theme-text-primary);
}

.divider {
  background-color: var(--theme-border);
}

.action-btn {
  background: var(--theme-primary-opacity-20);
  color: var(--theme-text-primary);
}

.action-btn:hover {
  background: var(--theme-primary-opacity-30);
  transform: scale(1.1);
}

.delete-btn:hover {
  background: rgba(255, 0, 0, 0.3);
  color: white;
}

.add-btn:hover {
  background: rgba(0, 255, 0, 0.3);
  color: white;
}

.chapter-item {
  color: var(--theme-text-primary);
}

.chapter-item:hover {
  background-color: var(--theme-hover-background);
}

.chapter-item.selected:hover {
  background-color: transparent;
}

.delete-icon {
  color: var(--theme-text-primary);
}

.highlight-indicator {
  background-color: var(--theme-surface);
  box-shadow: 0 2px 4px var(--theme-shadow-medium);
  border-radius: 12px 0 0 12px;
}

.popup-title,
.popup-input {
  color: var(--theme-text-primary);
  border-color: var(--theme-border);
}

.btn-confirm {
  background: var(--theme-primary);
}

.btn-confirm:hover {
  background: var(--theme-hover-primary);
}

/* 固定标题区域 */
.fixed-header {
  margin-bottom: 16px;
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 0 16px;
  margin-bottom: 12px;
}

.sidebar-title {
  font-size: 18px;
  font-weight: bold;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.title-actions {
  position: absolute;
  right: 16px;
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.delete-btn:hover {
  background: rgba(255, 0, 0, 0.3);
  color: white;
}

.add-btn:hover {
  background: rgba(0, 255, 0, 0.3);
  color: white;
}

.divider {
  height: 1px;
  margin: 0 10% 0;
  width: 80%;
}

/* 可滚动内容区域 */
.scrollable-content {
  flex: 1;
  overflow-y: auto;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 2px 0 20px 0;
  margin-top: 0;
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

.chapter-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  font-size: 14px;
  position: relative;
  z-index: 1;
}

.delete-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(255, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-right: 8px;
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

.highlight-indicator {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 0;
  pointer-events: none;
}

.highlight-indicator + .chapter-item {
  font-weight: bold;
}

.chapter-item.selected .chapter-name {
  font-weight: bold;
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
  max-width: 400px;
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
  margin: 0 0 20px 0;
  text-align: center;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.popup-input-area {
  margin-bottom: 20px;
}

.popup-input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  outline: none;
  transition: all 0.2s ease;
}

.popup-input:focus {
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.popup-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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
  transform: translateY(-1px);
}

/* 响应式弹窗 */
@media (max-width: 480px) {
  .popup-content {
    padding: 16px;
    width: 95%;
  }
}
</style>