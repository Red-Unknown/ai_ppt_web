<template>
  <div class="editor-toolbar">
    <div class="toolbar-left">
      <div class="dropdown" ref="dropdownRef">
        <button class="dropdown-toggle" @click="toggleDropdown" :class="{ 'active': isDropdownOpen }">
          {{ selectedOption }}
          <svg class="dropdown-icon" :class="{ 'rotated': isDropdownOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        <div class="dropdown-menu" v-if="isDropdownOpen" :class="{ 'open': isDropdownOpen }">
          <div 
            v-for="option in options" 
            :key="option.value"
            class="dropdown-item" 
            :class="{ 'active': option.value === selectedOption }"
            @click="selectOption(option.value)"
          >
            {{ option.label }}
          </div>
        </div>
      </div>
    </div>
    <div v-if="isEditMode" class="toolbar-center">
      <button class="icon-button" @click="handleUndo" :disabled="!canUndo">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 7v6h6"></path>
          <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path>
        </svg>
      </button>
      <button class="icon-button" @click="handleRedo" :disabled="!canRedo">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 7v6h-6"></path>
          <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7"></path>
        </svg>
      </button>
      <div class="save-button-wrapper" ref="saveButtonWrapper">
        <button class="icon-button" @click="handleSave">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
            <polyline points="17 21 17 13 7 13 7 21"></polyline>
            <polyline points="7 3 7 8 15 8"></polyline>
          </svg>
        </button>
      </div>
      <button class="icon-button" @click="handleBold">
        <img src="@/assets/images/action/ic_pen.svg" class="icon" alt="Select Element">
      </button>
    </div>
    <div class="toolbar-right">
      <div class="edit-preview-tabs">
        <button 
          class="tab-button" 
          :class="{ active: isEditMode }"
          @click="toggleEditMode"
        >
          编辑
        </button>
        <button 
          class="tab-button" 
          :class="{ active: !isEditMode }"
          @click="toggleEditMode"
        >
          预览
        </button>
      </div>
    </div>
  </div>
  
  <!-- 使用 Teleport 将弹窗挂载到 body 上，避免被父容器遮挡 -->
  <Teleport to="body">
    <div 
      class="upload-status-tooltip" 
      v-if="uploadStatus"
      :style="{
        position: 'fixed',
        top: tooltipPosition.top,
        left: tooltipPosition.left,
        transform: 'translateX(-50%)'
      }"
    >
      {{ uploadStatus }}
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  isEditMode: {
    type: Boolean,
    default: true
  },
  canUndo: {
    type: Boolean,
    default: false
  },
  canRedo: {
    type: Boolean,
    default: false
  },
  selectedOption: {
    type: String,
    default: '教案编辑区'
  }
})

// Emits
const emit = defineEmits([
  'undo',
  'redo',
  'save',
  'upload',
  'select-element',
  'toggle-edit-mode',
  'option-change',
  'bold'
])

// 状态
const uploadStatus = ref('')
const isDropdownOpen = ref(false)
const dropdownRef = ref(null)
const saveButtonWrapper = ref(null)

// 计算弹窗位置
const tooltipPosition = computed(() => {
  if (!saveButtonWrapper.value) return { top: '0px', left: '50%' }
  const rect = saveButtonWrapper.value.getBoundingClientRect()
  return {
    top: `${rect.top + window.scrollY - 50}px`,
    left: `${rect.left + window.scrollX + rect.width / 2}px`
  }
})

// 选项数据
const options = ref([
  { label: '教案编辑区', value: '教案编辑区' },
  { label: '思维导图编辑区', value: '思维导图编辑区' },
  { label: '课程概要编辑区', value: '课程概要编辑区' }
])

// Methods
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
  
  if (isDropdownOpen.value) {
    // 添加点击外部关闭的事件
    setTimeout(() => {
      document.addEventListener('click', handleClickOutside)
    }, 10)
  } else {
    // 移除点击外部关闭的事件
    document.removeEventListener('click', handleClickOutside)
  }
}

// 点击外部关闭下拉框
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isDropdownOpen.value = false
    document.removeEventListener('click', handleClickOutside)
  }
}

const selectOption = (option) => {
  // 这里可以添加选择选项后的逻辑
  console.log('Selected option:', option)
  emit('option-change', option)
  isDropdownOpen.value = false
}
const handleUndo = () => {
  emit('undo')
}

const handleRedo = () => {
  emit('redo')
}

const handleSave = async () => {
  try {
    uploadStatus.value = '上传中...'
    // 模拟上传过程
    await new Promise(resolve => setTimeout(resolve, 1000))
    uploadStatus.value = '上传成功!'
    // 3秒后清除状态
    setTimeout(() => {
      uploadStatus.value = ''
    }, 3000)
    emit('save')
  } catch (error) {
    uploadStatus.value = '上传失败，请重试'
    setTimeout(() => {
      uploadStatus.value = ''
    }, 3000)
  }
}

const handleSelectElement = () => {
  emit('select-element')
}

const handleBold = () => {
  emit('bold')
}

const toggleEditMode = () => {
  emit('toggle-edit-mode')
}
</script>

<style scoped>
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #CDF4FF;
  border-bottom: 1px solid #E0F0FF;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.dropdown {
  position: relative;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: none;
  background: white;
  color: #276884;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 24px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  min-width: 140px;
  justify-content: space-between;
}

.dropdown-toggle:hover {
  background: #f0f8ff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.15);
}

.dropdown-toggle.active {
  background: #008AC5;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.3);
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.2s ease;
}

.dropdown-icon.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  min-width: 190px;
  z-index: 1000;
  overflow: hidden;
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}

.dropdown-menu.open {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.dropdown-item {
  padding: 12px 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #276884;
  font-size: 14px;
  border-left: 3px solid transparent;
  position: relative;
  overflow: hidden;
}

.dropdown-item:hover {
  background-color: #f0f8ff;
  border-left-color: #008AC5;
  padding-left: 22px;
}

.dropdown-item.active {
  background-color: #e0f0ff;
  border-left-color: #008AC5;
  font-weight: 600;
}

.dropdown-item:first-child {
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}

.dropdown-item:last-child {
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}

.dropdown-item::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.6s ease;
}

.dropdown-item:hover::after {
  left: 100%;
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-button {
  width: 40px;
  height: 40px;
  border: none;
  background: white;
  border-radius: 50%;
  color: #276884;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.icon-button:hover {
  background: #f0f8ff;
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 138, 197, 0.1);
}

.icon-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.icon {
  width: 18px;
  height: 18px;
}

.icon-button img.icon {
  filter: invert(24%) sepia(37%) saturate(1553%) hue-rotate(173deg) brightness(93%) contrast(91%);
}

.save-button-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.upload-status-tooltip {
  background: rgba(100, 100, 100, 0.95);
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  z-index: 9999;
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.edit-preview-tabs {
  display: flex;
  background: white;
  border-radius: 24px;
  padding: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.tab-button {
  padding: 8px 20px;
  border: none;
  background: transparent;
  color: #276884;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.tab-button.active {
  background: linear-gradient(135deg, #008AC5, #006699);
  color: white;
  box-shadow: 0 2px 4px rgba(0, 138, 197, 0.3);
}

.tab-button:hover:not(.active) {
  background: #f0f8ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-toolbar {
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .toolbar-center {
    order: 3;
    width: 100%;
    justify-content: center;
  }
  
  .toolbar-left,
  .toolbar-right {
    flex: 1;
  }
  
  .toolbar-right {
    justify-content: flex-end;
    gap: 12px;
  }
  
  .icon-button {
    width: 36px;
    height: 36px;
  }
  
  .tab-button {
    padding: 6px 16px;
  }
}

@media (max-width: 480px) {
  .editor-toolbar {
    padding: 8px 12px;
  }
  
  .dropdown-toggle {
    padding: 6px 12px;
    font-size: 13px;
  }
  
  .icon-button {
    width: 32px;
    height: 32px;
  }
  
  .icon {
    width: 16px;
    height: 16px;
  }
  
  .toolbar-right {
    gap: 8px;
  }
  
  .upload-status {
    font-size: 12px;
    padding: 4px 8px;
  }
}
</style>