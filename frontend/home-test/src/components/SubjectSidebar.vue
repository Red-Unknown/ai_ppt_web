<template>
  <div class="subject-sidebar" :class="{ 'theme-orange': theme === 'orange', 'theme-blue': theme === 'blue' }">
    <!-- 固定标题区域 -->
    <div class="fixed-header">
  <div class="title-container">
    <div class="sidebar-title">科目</div>
    <div class="title-actions" v-if="theme === 'blue'">
      <button class="action-btn delete-btn" @click="enterDeleteMode">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
        </svg>
      </button>
      <button class="action-btn add-btn" @click="showAddSubjectPopup = true">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
      </button>
    </div>
  </div>
  <div class="divider" />
</div>
    
    <!-- 可滚动内容区域 -->
    <div class="scrollable-content" ref="subjectListRef">
      <div
        v-for="subject in subjects"
        :key="subject.id"
        class="subject-item"
        :data-id="subject.id"
        :class="{ 'selected': subject.id === selectedSubject }"
        @click="handleSelect(subject)"
      >
        <span v-if="isDeleteMode && theme === 'blue'" class="delete-icon" @click.stop="confirmDeleteSubject(subject)">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </span>
        <span class="subject-name">{{ subject.name }}</span>
      </div>
      <div class="highlight-indicator" ref="highlightIndicatorRef"></div>
    </div>
  </div>

  <!-- 新增科目弹窗 -->
  <div v-if="showAddSubjectPopup" class="popup-overlay" @click="showAddSubjectPopup = false">
    <div class="popup-content" @click.stop>
      <h3 class="popup-title">新增科目</h3>
      <div class="popup-input-area">
        <input 
          type="text" 
          v-model="newSubjectName" 
          placeholder="请输入科目名称" 
          class="popup-input"
          @keyup.enter="addNewSubject"
        >
      </div>
      <div class="popup-actions">
        <button class="btn-cancel" @click="showAddSubjectPopup = false">取消</button>
        <button class="btn-confirm" @click="addNewSubject">确定</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'

/**
 * 科目侧边栏组件
 * @description 显示科目列表，支持科目选择、添加和删除
 * @example
 * <SubjectSidebar
 *   :subjects="subjectsList"
 *   :selected-subject="currentSubjectId"
 *   theme="blue"
 *   @select="handleSelectSubject"
 *   @add="handleAddSubject"
 *   @delete="handleDeleteSubject"
 * />
 */
export default {
  name: 'SubjectSidebar',
  props: {
    /**
     * 科目列表数据
     * @type {Array<{id: string, name: string, isCollected?: boolean}>}
     * @default []
     */
    subjects: { 
      type: Array, 
      default: () => [],
      validator: (value) => {
        if (!Array.isArray(value)) {
          console.warn('[SubjectSidebar] subjects must be an array')
          return false
        }
        const isValid = value.every(subject => 
          typeof subject === 'object' && 
          subject !== null && 
          typeof subject.id === 'string' && 
          typeof subject.name === 'string'
        )
        if (!isValid) {
          console.warn('[SubjectSidebar] Each subject must have id and name properties')
        }
        return isValid
      }
    },
    /**
     * 当前选中的科目ID
     * @type {string}
     * @default ''
     */
    selectedSubject: { type: String, default: '' },
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
          console.warn(`[SubjectSidebar] Invalid theme: "${value}". Must be one of: ${validThemes.join(', ')}`)
          return false
        }
        return true
      }
    }
  },
  emits: ['select', 'collect', 'delete', 'add'],
  setup(props, { emit }) {
    const subjectListRef = ref(null)
    const highlightIndicatorRef = ref(null)
    const isDeleteMode = ref(false)
    const showAddSubjectPopup = ref(false)
    const newSubjectName = ref('')

    const handleSelect = (subject) => {
      emit('select', subject)
    }

    const handleCollect = (subject) => {
      subject.isCollected = !subject.isCollected
      emit('collect', subject)
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

    // 确认删除科目
    const confirmDeleteSubject = (subject) => {
      if (confirm(`确定要删除科目「${subject.name}」吗？`)) {
        emit('delete', subject.id)
      }
    }

    // 添加新科目
    const addNewSubject = () => {
      if (newSubjectName.value.trim()) {
        const newSubject = {
          id: 'subject_' + Date.now(),
          name: newSubjectName.value.trim(),
          isCollected: false
        }
        emit('add', newSubject)
        newSubjectName.value = ''
        showAddSubjectPopup.value = false
      }
    }

    // 更新高亮指示器位置
    const updateHighlightPosition = () => {
      if (!subjectListRef.value || !highlightIndicatorRef.value || !props.selectedSubject) {
        return
      }

      const selectedItem = subjectListRef.value.querySelector(`[data-id="${props.selectedSubject}"]`)
      if (selectedItem) {
        const { top, height, width, left } = selectedItem.getBoundingClientRect()
        const listRect = subjectListRef.value.getBoundingClientRect()
        
        const relativeTop = top - listRect.top
        
        highlightIndicatorRef.value.style.transition = 'all 0.4s ease'
        highlightIndicatorRef.value.style.top = `${relativeTop}px`
        highlightIndicatorRef.value.style.height = `${height}px`
        highlightIndicatorRef.value.style.width = `${width - 8}px`
        highlightIndicatorRef.value.style.left = `${left - listRect.left + 8}px`
      }
    }

    // 监听选中状态变化
    watch(() => props.selectedSubject, () => {
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
      subjectListRef,
      highlightIndicatorRef,
      handleSelect,
      handleCollect,
      getStarIcon,
      isDeleteMode,
      showAddSubjectPopup,
      newSubjectName,
      enterDeleteMode,
      confirmDeleteSubject,
      addNewSubject
    }
  }
}
</script>

<style scoped>
.subject-sidebar {
  width: 180px;
  padding: 20px 0;
  height: calc(100vh - 60px);
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: var(--theme-primary);
}

.subject-item:hover {
  background-color: var(--theme-hover-background);
}

.highlight-indicator {
  background-color: var(--theme-background);
  box-shadow: 0 2px 4px var(--theme-shadow-medium);
  border-radius: 12px 0 0 12px;
}

.highlight-indicator + .subject-item {
  color: var(--theme-hover-primary);
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
  color: var(--theme-text-inverse);
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
  background: var(--theme-primary-opacity-20);
  color: var(--theme-text-inverse);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--theme-primary-opacity-30);
  transform: scale(1.1);
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
  background-color: var(--theme-text-inverse);
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

.subject-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  color: var(--theme-text-inverse);
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
  color: var(--theme-text-inverse);
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

.subject-item.selected .subject-name {
  color: var(--theme-text-tertiary) !important;
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