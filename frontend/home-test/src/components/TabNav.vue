<template>
  <div class="tab-nav">
    <button 
      v-for="tab in tabs" 
      :key="tab.id"
      class="tab-button"
      :class="{ active: activeTab === tab.id }"
      @click="handleTabClick(tab.id)"
    >
      {{ tab.name }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Props
const props = defineProps({
  activeTab: {
    type: String,
    default: 'courseware'
  }
})

// Emits
const emit = defineEmits(['tab-change'])

// 标签数据
const tabs = [
  {
    id: 'courseware',
    name: '课件'
  },
  {
    id: 'ai-assistant',
    name: 'AI助手'
  },
  {
    id: 'history',
    name: '历史对话'
  }
]

// 方法
const handleTabClick = (tabId) => {
  emit('tab-change', tabId)
}
</script>

<style scoped>
.tab-nav {
  display: flex;
  background: #E0F0FF;
  border-bottom: 1px solid rgba(0, 128, 185, 0.1);
  padding: 0;
  gap: 0;
  position: relative;
  overflow: hidden;
}

.tab-button {
  flex: 1;
  padding: 12px 8px;
  border: none;
  background: #E0F0FF;
  color: #0080B9;
  font-size: 14px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  text-align: center;
  border-radius: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tab-button {
    font-size: 12px;
    padding: 10px 6px;
  }
}

@media (max-width: 480px) {
  .tab-button {
    font-size: 11px;
    padding: 8px 4px;
  }
}

.tab-button:hover {
  background: #CCE6FF;
  color: #0080B9;
}

.tab-button.active {
  background: #0080B9;
  color: white;
  font-weight: 500;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #006090;
  z-index: 1;
}
</style>