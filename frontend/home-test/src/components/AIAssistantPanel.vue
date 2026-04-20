<template>
  <div class="ai-assistant-panel" :class="`theme-${theme}`">
    <!-- Tab标签页 -->
    <div class="tab-header">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="switchTab(tab.id)"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- Tab内容区 -->
    <div class="tab-content">
      <!-- 自定义插槽内容 -->
      <slot v-for="tab in tabs" :name="`tab-${tab.id}`" :tab="tab"></slot>

      <!-- AI助手Tab（默认） -->
      <div v-if="activeTab === 'ai-assistant' && !hasTabSlot('ai-assistant')" class="ai-chat-panel">
        <div class="chat-actions">
          <button class="action-icon-btn" @click="handleNewChat" title="开启新对话">
            <img :src="icons.addChat" alt="新对话" />
          </button>
          <button class="action-icon-btn" @click="handleOpenSettings" title="设置">
            <img :src="icons.settings" alt="设置" />
          </button>
        </div>
        <div class="chat-messages" ref="chatContainer">
          <div v-if="messages.length === 0" class="empty-chat">
            <div class="empty-icon">
              <img :src="icons.ai" alt="AI" class="ai-icon" />
            </div>
            <p class="empty-text">{{ emptyText }}</p>
          </div>
          <template v-else>
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message"
              :class="{ 'user-msg': msg.type === 'user', 'ai-msg': msg.type === 'ai' }"
            >
              <template v-if="msg.type === 'ai'">
                <div class="avatar ai-avatar">
                  <img :src="icons.ai" alt="AI" class="ai-avatar-img" />
                </div>
                <div class="message-bubble">
                  <div class="message-content" v-html="formatMessage(msg.content)"></div>
                </div>
              </template>
              <template v-else>
                <div class="message-bubble">
                  <div class="message-content" v-html="formatMessage(msg.content)"></div>
                </div>
                <div class="avatar user-avatar"></div>
              </template>
            </div>
          </template>
        </div>
      </div>

      <!-- 历史对话Tab（默认） -->
      <div v-if="activeTab === 'history' && !hasTabSlot('history')" class="history-panel">
        <div v-if="!showHistoryDetail" class="history-list">
          <div
            v-for="item in historyList"
            :key="item.id"
            class="history-item"
            @click="openHistoryDetail(item)"
          >
            <div class="history-icon">
              <img :src="icons.chat" alt="聊天" />
            </div>
            <div class="history-info">
              <span class="history-title">{{ item.title }}</span>
              <span class="history-time">{{ formatHistoryTime(item.updatedAt) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="history-detail">
          <div class="chat-actions detail-actions">
            <button class="action-icon-btn" @click="closeHistoryDetail" title="返回">
              <img :src="icons.back" alt="返回" />
            </button>
            <div class="detail-title-wrapper">
              <h3 class="detail-title" v-if="selectedHistory">{{ selectedHistory.title }}</h3>
            </div>
            <button class="action-icon-btn" @click="handleOpenSettings" title="设置">
              <img :src="icons.settings" alt="设置" />
            </button>
          </div>
          <div class="detail-messages" ref="detailChatContainer">
            <div
              v-for="(msg, index) in historyMessages"
              :key="index"
              class="message"
              :class="{ 'user-msg': msg.type === 'user', 'ai-msg': msg.type === 'ai' }"
            >
              <template v-if="msg.type === 'ai'">
                <div class="avatar ai-avatar">
                  <img :src="icons.ai" alt="AI" class="ai-avatar-img" />
                </div>
                <div class="message-bubble">
                  <div class="message-content" v-html="formatMessage(msg.content)"></div>
                </div>
              </template>
              <template v-else>
                <div class="message-bubble">
                  <div class="message-content" v-html="formatMessage(msg.content)"></div>
                </div>
                <div class="avatar user-avatar"></div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部输入区（插槽） -->
    <div v-if="$slots['input-area']" class="chat-input-area">
      <slot name="input-area"></slot>
    </div>
    <!-- 默认底部输入区 -->
    <div v-else class="chat-input-area">
      <div class="input-wrapper">
        <input
          type="text"
          v-model="localInputMessage"
          :placeholder="inputPlaceholder"
          @keyup.enter="sendMessage"
        />
        <button
          class="voice-btn"
          :class="{ active: isRecording }"
          @click="toggleRecording"
        >
          <img v-if="!isRecording" :src="icons.micOff" alt="语音" class="voice-icon" />
          <img v-else :src="icons.micActive" alt="录音中" class="voice-icon" />
          <div v-if="isRecording" class="voice-waves">
            <span class="wave"></span>
            <span class="wave"></span>
            <span class="wave"></span>
          </div>
        </button>
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="!localInputMessage.trim()"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, useSlots } from 'vue'
import iconAi from '@/assets/images/logo/ic-AI3.svg'
import iconAddChat from '@/assets/images/action/ic-addchat.svg'
import iconSettings from '@/assets/images/action/ic-set.svg'
import iconChat from '@/assets/images/action/ic_chat.svg'
import iconBack from '@/assets/images/action/ic-arrow_left2.svg'
import iconMicOff from '@/assets/images/action/ic_mic_off.svg'
import iconMicActive from '@/assets/images/action/ic_mic_active.svg'

const props = defineProps({
  theme: {
    type: String,
    default: 'orange',
    validator: (value) => ['orange', 'blue'].includes(value)
  },
  tabs: {
    type: Array,
    default: () => [
      { id: 'ai-assistant', name: 'AI助手' },
      { id: 'history', name: '历史对话' }
    ]
  },
  emptyText: {
    type: String,
    default: '你好，若有任何疑问，欢迎随时与我沟通'
  },
  messages: {
    type: Array,
    default: () => []
  },
  historyList: {
    type: Array,
    default: () => []
  },
  historyMessages: {
    type: Array,
    default: () => []
  },
  selectedHistory: {
    type: Object,
    default: null
  },
  showHistoryDetail: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: String,
    default: ''
  },
  isRecording: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'update:messages',
  'update:historyList',
  'update:historyMessages',
  'update:selectedHistory',
  'update:showHistoryDetail',
  'update:modelValue',
  'update:isRecording',
  'update:activeTab',
  'new-chat',
  'open-settings',
  'send-message',
  'toggle-recording',
  'open-history-detail',
  'close-history-detail'
])

const activeTab = ref(props.tabs[0]?.id || 'ai-assistant')

// 内部状态变量
const localInputMessage = ref(props.modelValue)

// 监听 modelValue 的变化
watch(() => props.modelValue, (newVal) => {
  localInputMessage.value = newVal
})

// 监听本地输入变化，同步到父组件
watch(localInputMessage, (newVal) => {
  emit('update:modelValue', newVal)
})

const icons = computed(() => {
  return {
    ai: iconAi,
    addChat: iconAddChat,
    settings: iconSettings,
    chat: iconChat,
    back: iconBack,
    micOff: iconMicOff,
    micActive: iconMicActive
  }
})

const inputPlaceholder = computed(() => {
  if (props.showHistoryDetail && props.selectedHistory) {
    return `继续对话：${props.selectedHistory.title}`
  }
  return '请输入你的问题'
})

const chatContainer = ref(null)
const detailChatContainer = ref(null)

const slots = useSlots()

const hasTabSlot = (tabId) => {
  return !!slots[`tab-${tabId}`]
}

const switchTab = (tabId) => {
  if (tabId !== 'history' && props.showHistoryDetail) {
    emit('update:showHistoryDetail', false)
    emit('update:selectedHistory', null)
  }
  activeTab.value = tabId
  emit('update:activeTab', tabId)
}

const handleNewChat = () => {
  emit('new-chat')
}

const handleOpenSettings = () => {
  emit('open-settings')
}

const sendMessage = () => {
  emit('send-message', localInputMessage.value)
}

const toggleRecording = () => {
  emit('toggle-recording', !props.isRecording)
}

const openHistoryDetail = (item) => {
  emit('open-history-detail', item)
}

const closeHistoryDetail = () => {
  emit('close-history-detail')
}

const formatMessage = (content) => {
  return content?.replace(/\n/g, '<br>') || ''
}

const formatHistoryTime = (timestamp) => {
  if (!timestamp) return ''
  const now = Date.now()
  const diff = now - timestamp
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  const date = new Date(timestamp)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
    if (detailChatContainer.value) {
      detailChatContainer.value.scrollTop = detailChatContainer.value.scrollHeight
    }
  })
}

watch(() => props.messages, () => {
  scrollToBottom()
}, { deep: true })

watch(() => props.historyMessages, () => {
  scrollToBottom()
}, { deep: true })

defineExpose({
  scrollToBottom,
  chatContainer,
  detailChatContainer
})
</script>

<style scoped>
.ai-assistant-panel {
  background: #FFFFFF;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 橙色主题 */
.theme-orange {
  --theme-color: #F18B5B;
  --theme-color-dark: #C96030;
  --theme-color-light: rgba(241, 139, 91, 0.1);
}

/* 蓝色主题 */
.theme-blue {
  --theme-color: #008AC5;
  --theme-color-dark: #276884;
  --theme-color-light: rgba(0, 138, 197, 0.1);
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #E8E8E8;
  background: #FAFAFA;
}

.tab-btn {
  flex: 1;
  padding: 12px 14px;
  border: none;
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.tab-btn:hover {
  color: var(--theme-color-dark);
}

.tab-btn.active {
  color: var(--theme-color);
  font-weight: 600;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 3px;
  background: var(--theme-color);
  border-radius: 3px 3px 0 0;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #FFFFFF;
  min-height: 0;
}

.ai-chat-panel,
.history-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  padding-right: 40px;
  border-bottom: 1px solid rgba(201, 96, 48, 0.15);
}

.theme-blue .chat-actions {
  border-bottom: 1px solid rgba(0, 138, 197, 0.15);
}

.detail-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(201, 96, 48, 0.15);
}

.theme-blue .detail-actions {
  border-bottom: 1px solid rgba(0, 138, 197, 0.15);
}

.detail-title-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
}

.detail-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--theme-color-dark);
  margin: 0;
  text-align: center;
}

.action-icon-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.action-icon-btn:hover {
  background: var(--theme-color-light);
}

.action-icon-btn:hover img {
  filter: brightness(0) saturate(100%) invert(54%) sepia(22%) saturate(1764%) hue-rotate(328deg) brightness(99%) contrast(93%);
  opacity: 1;
}

.theme-blue .action-icon-btn:hover img {
  filter: brightness(0) saturate(100%) invert(36%) sepia(62%) saturate(1650%) hue-rotate(178deg) brightness(97%) contrast(101%);
  opacity: 1;
}

.action-icon-btn img {
  width: 22px;
  height: 22px;
  object-fit: contain;
  filter: grayscale(100%) brightness(0.5);
  opacity: 0.7;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(201, 96, 48, 0.2);
  border-radius: 3px;
}

.theme-blue .chat-messages::-webkit-scrollbar-thumb {
  background: rgba(0, 138, 197, 0.2);
}

.detail-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 空状态 */
.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.empty-icon {
  margin-bottom: 20px;
}

.ai-icon {
  width: 80px;
  height: 80px;
  opacity: 0.6;
}

.empty-text {
  font-size: 14px;
  color: var(--theme-color-dark);
  text-align: center;
  opacity: 0.8;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-msg {
  flex-direction: row;
  justify-content: flex-end;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ai-avatar {
  background: linear-gradient(135deg, var(--theme-color), var(--theme-color-dark));
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-avatar-img {
  width: 24px;
  height: 24px;
}

.user-avatar {
  background: linear-gradient(135deg, #4A90E2, #6BB3FF);
}

.message-bubble {
  max-width: calc(100% - 72px);
  padding: 16px 20px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.8;
  position: relative;
  transition: all 0.3s ease;
}

.message-bubble:hover {
  transform: translateY(-2px);
}

.ai-msg .message-bubble {
  background: linear-gradient(135deg, #FFFFFF, #FFF9F3);
  color: #333;
  border-top-left-radius: 4px;
  box-shadow: 0 4px 16px rgba(201, 96, 48, 0.12);
  border: 1px solid rgba(241, 139, 91, 0.1);
}

.theme-blue .ai-msg .message-bubble {
  background: linear-gradient(135deg, #FFFFFF, #F2FCFF);
  box-shadow: 0 4px 16px rgba(0, 138, 197, 0.12);
  border: 1px solid rgba(0, 138, 197, 0.1);
}

.ai-msg .message-bubble::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 16px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-right: 8px solid #FFFFFF;
}

.user-msg .message-bubble {
  background: linear-gradient(135deg, var(--theme-color), var(--theme-color-dark));
  color: white;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 16px rgba(241, 139, 91, 0.3);
}

.theme-blue .user-msg .message-bubble {
  box-shadow: 0 4px 16px rgba(0, 138, 197, 0.3);
}

.user-msg .message-bubble::before {
  content: '';
  position: absolute;
  right: -8px;
  top: 16px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 8px solid var(--theme-color);
}

.message-content {
  word-break: break-word;
}

.message-content br {
  content: '';
  display: block;
  margin-top: 8px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(201, 96, 48, 0.15);
}

.theme-blue .history-item:hover {
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.15);
}

.history-icon {
  width: 32px;
  height: 32px;
  background: var(--theme-color-light);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.history-icon img {
  width: 18px;
  height: 18px;
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-title {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.history-time {
  font-size: 12px;
  color: #999;
}

.history-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-input-area {
  padding: 12px;
  border-top: 1px solid #E8E8E8;
  background: #FAFAFA;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 20px;
  padding: 6px 10px;
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--theme-color);
  box-shadow: 0 0 0 3px var(--theme-color-light);
}

.input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 13px;
  padding: 6px 4px;
  background: transparent;
}

.voice-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.2s;
}

.voice-btn:hover {
  background: var(--theme-color-light);
}

.voice-btn.active {
  background: var(--theme-color);
}

.voice-btn.active .voice-icon {
  filter: brightness(0) invert(1);
}

.voice-icon {
  width: 16px;
  height: 16px;
}

.voice-waves {
  position: absolute;
  display: flex;
  gap: 2px;
}

.voice-waves .wave {
  width: 2px;
  height: 8px;
  background: #FFF;
  border-radius: 2px;
  animation: wave 1s ease-in-out infinite;
}

.voice-waves .wave:nth-child(2) {
  animation-delay: 0.1s;
}

.voice-waves .wave:nth-child(3) {
  animation-delay: 0.2s;
}

@keyframes wave {
  0%, 100% {
    height: 6px;
  }
  50% {
    height: 12px;
  }
}

.send-btn {
  padding: 6px 16px;
  border: none;
  background: var(--theme-color);
  color: #FFFFFF;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: var(--theme-color-dark);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
