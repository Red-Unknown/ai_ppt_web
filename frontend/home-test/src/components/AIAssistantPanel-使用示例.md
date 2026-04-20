# AIAssistantPanel 组件使用说明

## 组件特点

✅ **双主题支持**：橙色（学生端）和蓝色（教师端）  
✅ **可自定义标签页**：支持任意标签配置  
✅ **插槽系统**：可自定义任意标签页内容  
✅ **完整功能**：内置 AI 聊天、历史对话  
✅ **样式统一**：自动适配主题色

---

## 基本使用

### 1. 引入组件

```vue
<script setup>
import AIAssistantPanel from '@/components/AIAssistantPanel.vue'
import { ref } from 'vue'

// 状态定义
const messages = ref([])
const historyList = ref([])
const historyMessages = ref([])
const selectedHistory = ref(null)
const showHistoryDetail = ref(false)
const inputMessage = ref('')
const isRecording = ref(false)
</script>
```

---

## 学生端使用示例（橙色主题）

```vue
<template>
  <AIAssistantPanel
    theme="orange"
    :tabs="[
      { id: 'ai-assistant', name: 'AI助手' },
      { id: 'history', name: '历史对话' },
      { id: 'mindmap', name: '思维导图' },
      { id: 'summary', name: '课程概要' }
    ]"
    empty-text="你好同学，若有任何疑问，欢迎随时与我沟通"
    v-model:messages="messages"
    v-model:history-list="historyList"
    v-model:history-messages="historyMessages"
    v-model:selected-history="selectedHistory"
    v-model:show-history-detail="showHistoryDetail"
    v-model:input-message="inputMessage"
    v-model:is-recording="isRecording"
    @new-chat="startNewChat"
    @open-settings="openSettings"
    @send-message="handleSendMessage"
    @toggle-recording="handleToggleRecording"
    @open-history-detail="handleOpenHistoryDetail"
    @close-history-detail="handleCloseHistoryDetail"
  >
    <!-- 自定义思维导图标签 -->
    <template #tab-mindmap>
      <div v-if="activeTab === 'mindmap'" class="mindmap-panel">
        <div class="mindmap-container">
          <!-- 你的思维导图内容 -->
        </div>
      </div>
    </template>

    <!-- 自定义课程概要标签 -->
    <template #tab-summary>
      <div v-if="activeTab === 'summary'" class="summary-panel">
        <div class="summary-content">
          <!-- 你的课程概要内容 -->
        </div>
      </div>
    </template>

    <!-- 自定义底部输入区（可选） -->
    <template #input-area>
      <!-- 你的自定义输入区 -->
    </template>
  </AIAssistantPanel>
</template>

<script setup>
import { ref } from 'vue'
import AIAssistantPanel from '@/components/AIAssistantPanel.vue'

// 状态
const activeTab = ref('ai-assistant')
const messages = ref([])
const historyList = ref([])
const historyMessages = ref([])
const selectedHistory = ref(null)
const showHistoryDetail = ref(false)
const inputMessage = ref('')
const isRecording = ref(false)

// 事件处理
const startNewChat = () => {
  console.log('开启新对话')
}

const openSettings = () => {
  console.log('打开设置')
}

const handleSendMessage = (text) => {
  console.log('发送消息:', text)
}

const handleToggleRecording = (recording) => {
  isRecording.value = recording
}

const handleOpenHistoryDetail = (item) => {
  selectedHistory.value = item
  showHistoryDetail.value = true
}

const handleCloseHistoryDetail = () => {
  showHistoryDetail.value = false
  selectedHistory.value = null
}
</script>
```

---

## 教师端使用示例（蓝色主题）

```vue
<template>
  <AIAssistantPanel
    theme="blue"
    :tabs="[
      { id: 'courseware', name: '课件' },
      { id: 'ai-assistant', name: 'AI助手' },
      { id: 'history', name: '历史对话' }
    ]"
    empty-text="老师您好，若有任何想法，欢迎随时与我沟通"
    v-model:messages="messages"
    v-model:history-list="historyList"
    v-model:history-messages="historyMessages"
    v-model:selected-history="selectedHistory"
    v-model:show-history-detail="showHistoryDetail"
    v-model:input-message="inputMessage"
    v-model:is-recording="isRecording"
    @new-chat="startNewChat"
    @open-settings="openSettings"
    @send-message="handleSendMessage"
    @toggle-recording="handleToggleRecording"
    @open-history-detail="handleOpenHistoryDetail"
    @close-history-detail="handleCloseHistoryDetail"
  >
    <!-- 自定义课件标签 -->
    <template #tab-courseware>
      <div v-if="activeTab === 'courseware'" class="courseware-panel">
        <div class="courseware-content">
          <!-- 你的课件预览内容 -->
        </div>
      </div>
    </template>
  </AIAssistantPanel>
</template>

<script setup>
import { ref } from 'vue'
import AIAssistantPanel from '@/components/AIAssistantPanel.vue'

// 状态
const activeTab = ref('courseware')
const messages = ref([])
const historyList = ref([])
const historyMessages = ref([])
const selectedHistory = ref(null)
const showHistoryDetail = ref(false)
const inputMessage = ref('')
const isRecording = ref(false)

// 事件处理（同上）
// ...
</script>
```

---

## Props 说明

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `theme` | String | `'orange'` | 主题色：`'orange'` 或 `'blue'` |
| `tabs` | Array | `[{ id: 'ai-assistant', name: 'AI助手' }, { id: 'history', name: '历史对话' }]` | 标签页配置数组 |
| `emptyText` | String | `'你好，若有任何疑问，欢迎随时与我沟通'` | 空聊天提示文字 |
| `messages` | Array | `[]` | 聊天消息列表（双向绑定） |
| `historyList` | Array | `[]` | 历史对话列表（双向绑定） |
| `historyMessages` | Array | `[]` | 历史对话详情消息（双向绑定） |
| `selectedHistory` | Object | `null` | 选中的历史对话（双向绑定） |
| `showHistoryDetail` | Boolean | `false` | 是否显示历史对话详情（双向绑定） |
| `inputMessage` | String | `''` | 输入框内容（双向绑定） |
| `isRecording` | Boolean | `false` | 是否正在录音（双向绑定） |

---

## Events 说明

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `new-chat` | - | 点击"新对话"按钮 |
| `open-settings` | - | 点击"设置"按钮 |
| `send-message` | `text: String` | 发送消息 |
| `toggle-recording` | `recording: Boolean` | 切换录音状态 |
| `open-history-detail` | `item: Object` | 打开历史对话详情 |
| `close-history-detail` | - | 关闭历史对话详情 |
| `update:activeTab` | `tabId: String` | 标签页切换 |

---

## 插槽说明

| 插槽名 | 说明 |
|--------|------|
| `tab-${tabId}` | 自定义标签页内容，例如 `tab-mindmap`、`tab-courseware` |
| `input-area` | 自定义底部输入区 |

---

## 暴露的方法/属性

通过 `ref` 可以访问组件的以下功能：

```vue
<template>
  <AIAssistantPanel ref="panelRef" ... />
</template>

<script setup>
const panelRef = ref(null)

// 滚动到底部
panelRef.value?.scrollToBottom()

// 访问聊天容器
console.log(panelRef.value?.chatContainer)
</script>
```

| 方法/属性 | 说明 |
|-----------|------|
| `scrollToBottom()` | 滚动聊天区到底部 |
| `chatContainer` | 聊天消息容器的 ref |
| `detailChatContainer` | 历史对话详情容器的 ref |

---

## 消息数据格式

### 聊天消息 (messages)

```javascript
[
  {
    type: 'user',     // 'user' 或 'ai'
    content: '你好',  // 消息内容
    timestamp: 1234567890  // 时间戳（可选）
  }
]
```

### 历史对话列表 (historyList)

```javascript
[
  {
    id: 'unique-id',
    title: '如何选中目标？',
    messages: [...],  // 同上面的消息格式
    createdAt: 1234567890,
    updatedAt: 1234567890
  }
]
```

---

## 注意事项

1. **图标路径**：组件默认使用 `@/assets/images/` 下的图标，请确保路径正确
2. **双向绑定**：使用 `v-model:` 语法进行双向绑定
3. **插槽条件**：自定义插槽内容需要配合 `v-if="activeTab === 'tabId'"` 使用
4. **颜色主题**：通过 CSS 变量自动适配，无需额外修改样式
