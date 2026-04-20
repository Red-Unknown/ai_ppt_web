<template>
  <div class="lesson-plan-content">
    <div class="content-scroll">
      <div 
        class="lesson-content" 
        :class="{ 'editable': isEditMode }"
        contenteditable="true"
        @input="handleContentChange"
        @keydown="handleKeydown"
        @compositionstart="handleCompositionStart"
        @compositionend="handleCompositionEnd"
      >
        <!-- 教案内容 -->
        <template v-if="displayContent.objectives.length > 0 || displayContent.keyPoints.length > 0 || displayContent.teachingSteps.length > 0 || displayContent.exercises.length > 0">
          <h3>课程目标</h3>
          <p v-for="(objective, index) in displayContent.objectives" :key="index">
            {{ index + 1 }}. {{ objective }}
          </p>
          
          <h3>课程重点</h3>
          <p v-for="(point, index) in displayContent.keyPoints" :key="index">
            {{ point }}
          </p>
          
          <h3>教学步骤</h3>
          <p v-for="(step, index) in displayContent.teachingSteps" :key="index">
            {{ index + 1 }}. {{ step }}
          </p>
          
          <h3>课堂练习</h3>
          <p v-for="(exercise, index) in displayContent.exercises" :key="index">
            {{ index + 1 }}. {{ exercise }}
          </p>
        </template>
        
        <!-- 空内容时显示提示 -->
        <template v-else>
          <div class="empty-content">
            <div class="empty-icon">
              {{ contentTypeIcon }}
            </div>
            <div class="empty-text">
              <div class="empty-title">{{ contentTypeTitle }}</div>
              <div class="empty-subtitle">在此处输入内容</div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineExpose } from 'vue'

// Props
const props = defineProps({
  content: {
    type: Object,
    default: () => ({
      objectives: [],
      keyPoints: [],
      teachingSteps: [],
      exercises: []
    })
  },
  isEditMode: {
    type: Boolean,
    default: true
  },
  contentType: {
    type: String,
    default: 'lesson'
  }
})

// Emits
const emit = defineEmits(['content-change'])

// 状态
const history = ref([])
const historyIndex = ref(-1)
const isComposing = ref(false)
const compositionStartContent = ref('')

// 计算属性
const displayContent = computed(() => {
  return props.content || {
    objectives: [],
    keyPoints: [],
    teachingSteps: [],
    exercises: []
  }
})

// 判断是否为思维导图内容
const isMindMapContent = computed(() => {
  return props.contentType === 'mindmap'
})

// 内容类型图标
const contentTypeIcon = computed(() => {
  switch (props.contentType) {
    case 'mindmap':
      return '🧠'
    case 'summary':
      return '📋'
    default:
      return '📄'
  }
})

// 内容类型标题
const contentTypeTitle = computed(() => {
  switch (props.contentType) {
    case 'mindmap':
      return '思维导图'
    case 'summary':
      return '课程概要'
    default:
      return '教案'
  }
})

// 撤销/重做状态
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

// 方法
const handleCompositionStart = (event) => {
  isComposing.value = true
  // 保存开始输入时的内容
  compositionStartContent.value = event.target.innerHTML
}

const handleCompositionEnd = (event) => {
  isComposing.value = false
  // 输入完成后保存最终内容
  const content = event.target.innerHTML
  saveToHistory(content)
  emit('content-change', { html: content })
}

const handleContentChange = (event) => {
  // 只有在非组合输入状态下才保存历史记录
  if (!isComposing.value) {
    const content = event.target.innerHTML
    // 保存到历史记录
    saveToHistory(content)
    // 这里可以添加内容解析逻辑，将HTML转换回结构化数据
    // 暂时直接发送HTML内容
    emit('content-change', { html: content })
  }
}

const handleKeydown = (event) => {
  // 处理撤销/重做
  if ((event.ctrlKey || event.metaKey) && event.key === 'z') {
    if (event.shiftKey) {
      redo()
    } else {
      undo()
    }
    event.preventDefault()
  }
}

const handleBold = () => {
  const selection = window.getSelection()
  if (selection.toString().length === 0) {
    return
  }

  const range = selection.getRangeAt(0)
  const container = range.commonAncestorContainer

  const checkTextFormat = (element) => {
    if (element.nodeType === Node.TEXT_NODE) {
      const parent = element.parentElement
      return parent && parent.style.fontWeight === 'bold' && 
             (parent.style.color === 'rgb(26, 74, 102)' || 
              parent.style.color === '#1A4A66')
    }
    if (element.style) {
      return element.style.fontWeight === 'bold' && 
             (element.style.color === 'rgb(26, 74, 102)' || 
              element.style.color === '#1A4A66')
    }
    if (element.parentNode) {
      return checkTextFormat(element.parentNode)
    }
    return false
  }

  const isAlreadyFormatted = checkTextFormat(container)

  if (isAlreadyFormatted) {
    document.execCommand('removeFormat', false, null)
  } else {
    document.execCommand('bold', false, null)
    document.execCommand('foreColor', false, '#1A4A66')
  }
}

const saveToHistory = (content) => {
  // 清除当前索引之后的历史记录
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1)
  }
  // 添加新记录
  history.value.push(content)
  // 限制历史记录数量
  const maxHistory = 50
  if (history.value.length > maxHistory) {
    history.value.shift()
    // 调整历史索引
    if (historyIndex.value > 0) {
      historyIndex.value--
    }
  } else {
    historyIndex.value++
  }
  console.log('保存历史记录:', history.value.length, '条, 当前索引:', historyIndex.value)
}

const undo = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--
    const content = history.value[historyIndex.value]
    document.querySelector('.lesson-content').innerHTML = content
    emit('content-change', { html: content })
  }
}

const redo = () => {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    const content = history.value[historyIndex.value]
    document.querySelector('.lesson-content').innerHTML = content
    emit('content-change', { html: content })
  }
}

// 初始化历史记录
watch(() => props.content, (newContent) => {
  // 当内容变化时，更新历史记录
  const lessonContent = document.querySelector('.lesson-content')
  if (lessonContent) {
    const content = lessonContent.innerHTML
    // 只有当历史记录为空时才保存初始内容
    if (history.value.length === 0) {
      saveToHistory(content)
    }
  }
}, { immediate: true })

// 暴露方法给父组件
defineExpose({
  undo,
  redo,
  handleBold,
  canUndo,
  canRedo,
  historyIndex,
  history
})
</script>

<style scoped>
.lesson-plan-content {
  height: 100%;
  width: 100%;
  background: white;
}

.content-scroll {
  height: 100%;
  width: 100%;
  overflow-y: auto;
  padding: 20px;
  box-sizing: border-box;
}

.lesson-content {
  max-width: 800px;
  margin: 0 auto;
}

.lesson-content h3 {
  color: #1a4a66;
  margin-top: 24px;
  margin-bottom: 12px;
  font-size: 1.1rem;
  font-weight: 600;
}

.lesson-content p {
  margin-bottom: 8px;
  line-height: 1.6;
  color: #333;
}

.highlight {
  color: #1a4a66;
  font-weight: bold;
  background: rgba(205, 244, 255, 0.3);
  padding: 0 4px;
  border-radius: 4px;
}

/* 滚动条样式 */
.content-scroll::-webkit-scrollbar {
  width: 8px;
}

.content-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.content-scroll::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.content-scroll::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 可编辑状态样式 */
.lesson-content.editable {
  border: 2px solid #008AC5;
  border-radius: 8px;
  padding: 20px;
  min-height: 300px;
  outline: none;
  transition: all 0.3s ease;
}

.lesson-content.editable:focus {
  border-color: #006B9A;
  box-shadow: 0 0 0 3px rgba(0, 138, 197, 0.1);
}

/* 确保编辑区域的元素样式 */
.lesson-content.editable h3 {
  margin-top: 20px;
  margin-bottom: 10px;
}

.lesson-content.editable p {
  margin-bottom: 8px;
}

/* 位置调整 */
.content-scroll {
  padding-top: 10px;
  transition: all 0.3s ease;
}

/* 空内容提示样式 */
.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  text-align: center;
  color: #999;
  animation: fadeIn 0.5s ease;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
  animation: bounce 2s infinite;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #666;
}

.empty-subtitle {
  font-size: 14px;
  color: #999;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}
</style>