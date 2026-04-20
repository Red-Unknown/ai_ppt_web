<template>
  <div class="courseware-preview" :class="{ 'select-mode': isSelectMode }">
    <div class="preview-header">
      <button class="select-element-btn" :class="{ active: isSelectMode }" @click="toggleSelectMode">
        <img src="@/assets/images/action/ic_pen.svg" class="select-icon" alt="Select Element">
        {{ isSelectMode ? '取消选择' : '选择元素' }}
      </button>
    </div>
    <div class="preview-content">
      <div class="courseware-scroll">
        <div class="courseware-grid">
          <div 
            v-for="(slide, index) in slides" 
            :key="index"
            class="courseware-card"
            :class="{ active: selectedSlide === index }"
            @click="handleSlideClick(index)"
          >
            <div class="card-content" @click.stop="handleContentClick($event, slide, index)">
              <img :src="slide.imageUrl" alt="PPT幻灯片" class="slide-image" :class="{ 'selectable': isSelectMode }">
              <div class="slide-number">{{ index + 1 }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加到对话选项 -->
    <div v-if="showAddToChat" class="add-to-chat-option" :style="{ top: addToChatPosition.top + 'px', left: addToChatPosition.left + 'px' }">
      <div class="option-arrow"></div>
      <button class="add-to-chat-btn" @click="handleAddToChat">
        添加到对话
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Props
const props = defineProps({
  slides: {
    type: Array,
    default: () => [
      {
        imageUrl: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Great%20Wall%20of%20China%20landscape%20with%20mountains&image_size=landscape_16_9'
      },
      {
        imageUrl: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Great%20Wall%20of%20China%20architecture%20details&image_size=landscape_16_9'
      }
    ]
  },
  selectedSlide: {
    type: Number,
    default: 0
  }
})

// Emits
const emit = defineEmits(['slide-click', 'select-element', 'add-to-chat'])

// 状态
const isSelectMode = ref(false)
const showAddToChat = ref(false)
const addToChatPosition = ref({ top: 0, left: 0 })
const selectedContent = ref(null)

// 方法
const handleSlideClick = (index) => {
  // 如果在选择模式下，不触发幻灯片切换
  if (isSelectMode.value) return
  emit('slide-click', index)
}

const toggleSelectMode = () => {
  isSelectMode.value = !isSelectMode.value
  // 关闭添加到对话选项
  showAddToChat.value = false
  // 重置选中内容
  selectedContent.value = null
  // 触发选择模式切换事件
  emit('select-element', isSelectMode.value)
}

const handleContentClick = (event, slide, index) => {
  if (!isSelectMode.value) return
  
  // 计算点击位置（相对于courseware-preview容器）
  const previewRect = event.currentTarget.closest('.courseware-preview').getBoundingClientRect()
  
  // 设置添加到对话选项的位置
  addToChatPosition.value = {
    top: event.clientY - previewRect.top + 10,
    left: event.clientX - previewRect.left + 10
  }
  
  console.log('点击位置:', event.clientX, event.clientY)
  console.log('容器位置:', previewRect.top, previewRect.left)
  console.log('添加到对话选项位置:', addToChatPosition.value)
  
  // 显示添加到对话选项
  showAddToChat.value = true
  console.log('显示添加到对话选项:', showAddToChat.value)
  
  // 保存选中的内容
  selectedContent.value = {
    slideIndex: index,
    content: slide,
    position: {
      x: event.clientX,
      y: event.clientY
    }
  }
  console.log('选中的内容:', selectedContent.value)
}

const handleAddToChat = () => {
  if (!selectedContent.value) return
  
  // 触发添加到对话事件
  emit('add-to-chat', selectedContent.value)
  
  // 关闭添加到对话选项
  showAddToChat.value = false
  
  // 重置选中内容
  selectedContent.value = null
}
</script>

<style scoped>
.courseware-preview {
  height: 100%;
  width: 100%;
  background: white;
  display: flex;
  flex-direction: column;
  position: relative;
}

.preview-header {
  padding: 12px 16px;
  border-bottom: 1px solid #E0F0FF;
  background: #f8f9fa;
}

.select-element-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #276884;
  background: white;
  color: #276884;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.select-element-btn:hover {
  background: #276884;
  color: white;
}

.select-icon {
  width: 16px;
  height: 16px;
  filter: invert(24%) sepia(37%) saturate(1553%) hue-rotate(173deg) brightness(93%) contrast(91%);
  transition: all 0.2s ease;
}

.select-element-btn:hover .select-icon {
  filter: brightness(0) invert(1);
}

.select-element-btn.active {
  background: #276884;
  color: white;
}

.select-element-btn.active .select-icon {
  filter: brightness(0) invert(1);
}

/* 选择模式样式 */
.courseware-preview.select-mode {
  cursor: crosshair;
}

.slide-image.selectable {
  cursor: pointer;
  transition: all 0.2s ease;
}

.slide-image.selectable:hover {
  opacity: 0.8;
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.2);
}

/* 添加到对话选项样式 */
.add-to-chat-option {
  position: absolute;
  z-index: 1000;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.option-arrow {
  position: absolute;
  top: -5px;
  left: 12px;
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 5px solid white;
}

.add-to-chat-btn {
  padding: 8px 16px;
  border: none;
  background: #008AC5;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  text-align: left;
}

.add-to-chat-btn:hover {
  background: #006699;
}

.preview-content {
  flex: 1;
  overflow: hidden;
}

.courseware-scroll {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

.courseware-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.courseware-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.courseware-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #276884;
}

.courseware-card.active {
  border-color: #276884;
  box-shadow: 0 4px 8px rgba(39, 104, 132, 0.2);
}

.card-content {
  position: relative;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.slide-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: 4px;
}

.slide-number {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

/* 滚动条样式 */
.courseware-scroll::-webkit-scrollbar {
  width: 8px;
}

.courseware-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.courseware-scroll::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.courseware-scroll::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>