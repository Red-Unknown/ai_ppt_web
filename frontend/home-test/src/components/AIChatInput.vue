<template>
  <div class="ai-chat-input-wrapper">
    <!-- 添加的内容 -->
    <div v-if="props.addedContents.length > 0" class="added-contents">
      <div 
        v-for="(content, index) in props.addedContents" 
        :key="index" 
        class="added-content-item"
      >
        <div class="content-preview">
          <img v-if="content.content.imageUrl" :src="content.content.imageUrl" alt="PPT内容" class="content-image">
          <span v-else class="content-text">{{ content.content.text || 'PPT内容' }}</span>
        </div>
        <button class="remove-content-btn" @click="handleRemoveContent(index)">
          ×
        </button>
      </div>
    </div>
    <div class="ai-chat-input">
      <input 
        type="text" 
        placeholder="请输入你的问题" 
        class="question-input" 
        v-model="questionText"
        @keyup.enter="handleSend"
      >
      <button class="voice-button" @click="toggleVoiceInput" :class="{ 'active': isVoiceInputActive }">
        <svg class="voice-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="23"></line>
          <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
      </button>
      <button class="send-button" @click="handleSend" :disabled="!questionText.trim() && props.addedContents.length === 0">
        发送
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  value: {
    type: String,
    default: ''
  },
  pptContent: {
    type: Object,
    default: () => ({})
  },
  disableSwitch: {
    type: Boolean,
    default: false
  },
  addedContents: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['send', 'input', 'switchToAI', 'remove-content'])

// 状态
const questionText = ref(props.value)
const isVoiceInputActive = ref(false)
let recognition = null

// 监听value变化
watch(() => props.value, (newValue) => {
  questionText.value = newValue
})

// 方法
const handleSend = () => {
  const text = questionText.value.trim()
  if (text) {
    emit('send', text)
    if (!props.disableSwitch) {
      emit('switchToAI')
    }
    questionText.value = ''
    showSuggestions.value = false
  }
}

const toggleVoiceInput = () => {
  if (!recognition) {
    initVoiceRecognition()
  }
  
  if (isVoiceInputActive.value) {
    recognition.stop()
    isVoiceInputActive.value = false
  } else {
    if (recognition) {
      recognition.start()
    } else {
      alert('您的浏览器不支持语音识别功能')
    }
  }
}

const initVoiceRecognition = () => {
  if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'zh-CN'
    
    recognition.onstart = () => {
      isVoiceInputActive.value = true
    }
    
    recognition.onresult = (event) => {
      let transcript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript
      }
      questionText.value = transcript
      emit('input', transcript)
    }
    
    recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error)
    }
    
    recognition.onend = () => {
      // 保持isVoiceInputActive状态，只有手动停止时才设为false
    }
  }
}



const handleRemoveContent = (index) => {
  emit('remove-content', index)
}
</script>

<style scoped>
.ai-chat-input-wrapper {
  width: 100%;
  background: transparent;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 添加的内容样式 */
.added-contents {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.added-content-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.3s ease;
  position: relative;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-preview {
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-image {
  width: 40px;
  height: 30px;
  object-fit: cover;
  border-radius: 4px;
}

.content-text {
  font-size: 14px;
  color: #333;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-content-btn {
  width: 20px;
  height: 20px;
  border: none;
  background: #f0f0f0;
  border-radius: 50%;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  opacity: 0.6;
}

.added-content-item:hover .remove-content-btn {
  opacity: 1;
  background: #ff4d4f;
  color: white;
}

.ai-chat-input {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: transparent;
  border-radius: 50px;
  box-shadow: none;
  border: 1px solid #e0e0e0;
  width: 100%;
}

.question-input {
  flex: 0 1 auto;
  max-width: 300px;
  border: none;
  outline: none;
  font-size: 14px;
  color: #333;
  padding: 8px 0;
  background: transparent;
  margin-right: 12px;
  min-width: 150px;
}

.question-input::placeholder {
  color: #999;
}

.voice-button {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
  margin-right: 12px;
}

.voice-button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.voice-button.active {
  background: #008AC5;
  color: white;
  animation: pulse 1.5s infinite;
}

.voice-icon {
  width: 16px;
  height: 16px;
}

.send-button {
  padding: 6px 16px;
  border: none;
  background: #008AC5;
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-width: 60px;
  text-align: center;
}

.send-button:hover:not(:disabled) {
  background: #0077b3;
  transform: scale(1.02);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 138, 197, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(0, 138, 197, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 138, 197, 0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .question-input {
    max-width: 220px;
    min-width: 100px;
  }
}

@media (max-width: 480px) {
  .question-input {
    max-width: 180px;
  }
  
  .send-button {
    padding: 6px 12px;
    font-size: 13px;
    min-width: 50px;
  }
  
  .voice-button {
    margin-right: 8px;
  }
}
</style>