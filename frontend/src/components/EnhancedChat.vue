<template>
  <div class="flex h-screen bg-gray-50 font-sans text-gray-900">
    <!-- Sidebar -->
    <aside 
      :class="['fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-gray-200 flex flex-col transition-transform duration-300 ease-in-out md:relative md:translate-x-0',
               isSidebarOpen ? 'translate-x-0' : '-translate-x-full']"
    >
      <div class="p-4 border-b border-gray-100">
        <ModernButton 
          block 
          variant="primary" 
          @click="openNewChatModal"
          aria-label="Start a new chat session"
        >
          <template #icon>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
            </svg>
          </template>
          New Chat
        </ModernButton>
      </div>
      
      <div class="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        <div v-if="sessions.length === 0" class="text-center text-gray-400 py-4 text-sm">
          No history yet.
        </div>
        <button 
          v-for="session in sessions" 
          :key="session.id" 
          @click="switchSession(session.id); isSidebarOpen = false"
          :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-colors truncate flex items-center gap-2', 
            currentSessionId === session.id ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100']"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span class="truncate">{{ session.title || 'Untitled Session' }}</span>
        </button>
      </div>
      
      <div class="p-4 border-t border-gray-200 bg-gray-50">
        <ModernButton 
          block 
          variant="outline" 
          size="sm" 
          @click="showProfile = true"
          aria-label="Edit Student Profile"
        >
          <template #icon>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </template>
          Student Profile
        </ModernButton>
      </div>
    </aside>

    <!-- Overlay for mobile -->
    <div 
      v-if="isSidebarOpen" 
      @click="isSidebarOpen = false"
      class="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm transition-opacity"
    ></div>

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col h-full relative w-full bg-white">
      <!-- Header -->
      <header class="h-16 border-b border-gray-200 flex items-center justify-between px-4 md:px-6 bg-white/80 backdrop-blur-md sticky top-0 z-20">
        <div class="flex items-center gap-3">
          <button @click="isSidebarOpen = true" class="md:hidden p-2 -ml-2 text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div>
            <h2 class="font-semibold text-gray-800 text-lg leading-tight truncate max-w-[200px] md:max-w-md">
              {{ currentSessionTitle }}
            </h2>
            <div v-if="currentSessionMode" class="text-xs text-gray-500 font-medium uppercase tracking-wider">
              {{ currentSessionMode }} Mode
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-2">
           <div class="hidden md:flex items-center gap-2 bg-gray-100 p-1 rounded-lg">
             <select v-model="selectedModel" class="bg-transparent text-sm font-medium text-gray-700 py-1 px-2 rounded focus:outline-none focus:bg-white focus:shadow-sm transition-all cursor-pointer border-none">
               <option value="deepseek">DeepSeek-V3</option>
               <option value="gpt-4o">GPT-4o</option>
             </select>
             <div class="w-px h-4 bg-gray-300"></div>
             <select v-model="selectedStyle" class="bg-transparent text-sm font-medium text-gray-700 py-1 px-2 rounded focus:outline-none focus:bg-white focus:shadow-sm transition-all cursor-pointer border-none">
               <option value="default">Default</option>
               <option value="creative">Creative</option>
               <option value="socratic">Socratic</option>
             </select>
           </div>
        </div>
      </header>
      
      <!-- Video Preview Area (only for Preview Mode) -->
      <div v-if="currentSessionMode === 'preview' && videoStatus" class="bg-gray-900 text-white p-4">
        <div class="max-w-3xl mx-auto">
          <div v-if="videoStatus.status === 'completed'" class="aspect-video bg-black rounded-lg overflow-hidden shadow-lg">
            <video :src="videoStatus.video_url" controls class="w-full h-full"></video>
          </div>
          <div v-else class="aspect-video bg-gray-800 rounded-lg flex flex-col items-center justify-center gap-3 animate-pulse">
            <div class="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p class="text-sm font-medium text-gray-300">Generating Course Video... {{ videoStatus.progress }}%</p>
          </div>
        </div>
      </div>

      <!-- Messages Area -->
      <div class="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth" ref="messagesContainer">
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400 select-none">
          <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h3 class="text-xl font-medium text-gray-600 mb-2">Welcome to AI Tutor</h3>
          <p class="text-gray-500 max-w-md text-center">Start a new session to begin learning or previewing course materials.</p>
          <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
            <button @click="quickStart('Explain Newton\'s Second Law')" class="p-4 border border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-all text-left group">
              <span class="font-medium text-gray-700 group-hover:text-blue-700 block mb-1">Physics 101</span>
              <span class="text-sm text-gray-500">Explain Newton's Second Law</span>
            </button>
            <button @click="quickStart('Summarize the key concepts of Calculus')" class="p-4 border border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-all text-left group">
              <span class="font-medium text-gray-700 group-hover:text-blue-700 block mb-1">Math Review</span>
              <span class="text-sm text-gray-500">Summarize Calculus concepts</span>
            </button>
          </div>
        </div>

        <div v-for="(msg, index) in messages" :key="index" :class="['flex w-full group items-start gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300', msg.role === 'user' ? 'flex-row-reverse' : '']">
          
          <!-- Avatar -->
          <div :class="['w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm', msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-emerald-600 text-white']">
            <span v-if="msg.role === 'user'" class="text-xs font-bold">ME</span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
            </svg>
          </div>

          <div :class="['max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-4 shadow-sm text-sm md:text-base', 
            msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none']">
            
            <div class="prose prose-sm max-w-none break-words" :class="{ 'text-white prose-invert': msg.role === 'user' }">
              <div class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</div>
            </div>
            
            <!-- Sources -->
            <div v-if="msg.role === 'assistant' && msg.sources && msg.sources.length" class="mt-4 pt-3 border-t border-gray-100">
              <div class="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                </svg>
                Sources
              </div>
              <div class="grid grid-cols-1 gap-2">
                <div v-for="(source, sIdx) in msg.sources" :key="sIdx" class="bg-gray-50 p-2 rounded border border-gray-100 text-xs text-gray-600 flex items-start gap-2 hover:bg-gray-100 transition-colors cursor-pointer">
                  <span class="bg-blue-100 text-blue-700 px-1.5 rounded font-mono text-[10px] mt-0.5">{{ (source.relevance_score * 100).toFixed(0) }}%</span>
                  <span class="line-clamp-2">{{ source.content }}</span>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="mt-2 flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button 
                v-if="msg.role === 'user' && !isStreaming"
                @click="undoMessage(index)" 
                class="p-1.5 rounded-md hover:bg-white/20 text-xs flex items-center gap-1 transition-colors"
                :class="msg.role === 'user' ? 'text-blue-100 hover:text-white' : 'text-gray-400 hover:text-gray-600'"
                title="Edit & Resend"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
                </svg>
                Undo
              </button>
            </div>
          </div>
        </div>
        
        <!-- Loading Indicator -->
        <div v-if="isStreaming" class="flex w-full items-start gap-4">
           <div class="w-8 h-8 bg-emerald-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm text-white">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
               <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
             </svg>
           </div>
           <div class="bg-white border border-gray-100 rounded-2xl rounded-tl-none px-5 py-4 shadow-sm flex items-center gap-2">
             <span class="flex gap-1">
               <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
               <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></span>
               <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></span>
             </span>
             <span class="text-xs text-gray-500 font-medium ml-2">Thinking...</span>
           </div>
        </div>
      </div>

      <!-- Input Area -->
      <footer class="p-4 md:p-6 bg-white border-t border-gray-100 relative z-20">
        <div class="max-w-4xl mx-auto relative">
          <div class="absolute -top-12 left-0 right-0 flex justify-center" v-if="!isStreaming && messages.length > 0">
            <ModernButton variant="ghost" size="sm" @click="refreshChat" aria-label="Regenerate response">
              <template #icon>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </template>
              Regenerate
            </ModernButton>
          </div>

          <div class="relative shadow-lg rounded-xl overflow-hidden ring-1 ring-gray-200 focus-within:ring-2 focus-within:ring-blue-500 transition-shadow">
            <textarea 
              v-model="inputQuery" 
              @keydown.enter.exact.prevent="handleEnterKey"
              placeholder="Ask a question about the course..." 
              class="w-full bg-white text-gray-800 pl-4 pr-14 py-4 focus:outline-none resize-none"
              rows="1"
              style="min-height: 56px; max-height: 200px;"
            ></textarea>
            
            <div class="absolute right-2 bottom-2">
              <ModernButton 
                v-if="isStreaming" 
                variant="danger" 
                size="sm" 
                @click="stopGeneration" 
                aria-label="Stop generation"
              >
                <template #icon>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
                  </svg>
                </template>
              </ModernButton>
              
              <ModernButton 
                v-else
                variant="primary" 
                size="sm" 
                @click="sendMessage" 
                :disabled="!inputQuery.trim()"
                aria-label="Send message"
              >
                <template #icon>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 transform rotate-90" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                  </svg>
                </template>
              </ModernButton>
            </div>
          </div>
          <div class="text-center text-xs text-gray-400 mt-3 font-medium">
            AI can make mistakes. Please verify important information.
          </div>
        </div>
      </footer>
    </main>

    <!-- Modals -->
    <Modal :isOpen="showProfile" @close="showProfile = false">
      <template #title>Student Profile</template>
      <StudentProfile />
    </Modal>

    <Modal :isOpen="showNewChat" @close="showNewChat = false">
      <template #title>Start New Session</template>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Mode</label>
          <select v-model="newSessionMode" @keydown.enter="confirmNewChat" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
            <option value="learning">Learning Mode (Interactive QA)</option>
            <option value="preview">Preview Mode (Video Generation)</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Course ID</label>
          <input v-model="newSessionCourseId" @keydown.enter="confirmNewChat" type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" placeholder="phys101">
        </div>
      </div>
      <template #footer>
        <ModernButton variant="ghost" @click="showNewChat = false">Cancel</ModernButton>
        <ModernButton variant="primary" :loading="startingSession" @click="confirmNewChat">Start Session</ModernButton>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import ModernButton from './ui/ModernButton.vue'
import Modal from './ui/Modal.vue'
import StudentProfile from './StudentProfile.vue'

// --- State ---
const sessions = ref([])
const currentSessionId = ref(null)
const currentSessionTitle = ref('New Chat')
const currentSessionMode = ref(null)
const isSidebarOpen = ref(false)

const messages = ref([])
const inputQuery = ref('')
const isStreaming = ref(false)

const selectedModel = ref('deepseek')
const selectedStyle = ref('default')

// Modals
const showProfile = ref(false)
const showNewChat = ref(false)
const newSessionMode = ref('learning')
const newSessionCourseId = ref('phys101')
const startingSession = ref(false)

// Video Status
const videoStatus = ref(null)
let videoPollInterval = null

// WebSocket
let ws = null
const wsConnected = ref(false)

// --- Lifecycle ---
onMounted(async () => {
  await loadSessions()
  connectWS()
})

onUnmounted(() => {
  if (videoPollInterval) clearInterval(videoPollInterval)
  if (ws) ws.close()
})

// --- API & Actions ---

async function loadSessions() {
  try {
    const res = await fetch('/api/v1/chat/sessions')
    const data = await res.json()
    sessions.value = data || []
    if (sessions.value.length > 0) {
      await switchSession(sessions.value[0].id)
    } else {
      // Don't auto-start, let user choose via UI
      // But for initial state, maybe just show empty
    }
  } catch (e) {
    console.error('Failed to load sessions', e)
    sessions.value = []
  }
}

function openNewChatModal() {
  showNewChat.value = true
}

async function confirmNewChat() {
  startingSession.value = true
  try {
    const payload = {
      course_id: newSessionCourseId.value,
      mode: newSessionMode.value,
      target_node_id: 'n1' // Default for now
    }
    
    const res = await fetch('/api/v1/chat/session/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    const data = await res.json()
    
    const newSession = {
      id: data.session_id,
      title: `${newSessionMode.value === 'learning' ? 'Learning' : 'Preview'} Session`,
      mode: newSessionMode.value,
      updated_at: new Date().toISOString()
    }
    
    sessions.value.unshift(newSession)
    await switchSession(newSession.id)
    showNewChat.value = false
  } catch (e) {
    console.error('Failed to start session', e)
  } finally {
    startingSession.value = false
  }
}

function quickStart(query) {
  // If no session, create one implicitly (default learning)
  if (!currentSessionId.value) {
    // Ideally we should create a session first.
    // For now, let's trigger the modal or just create a default one.
    // Let's create a default one silently.
    createDefaultSession().then(() => {
      inputQuery.value = query
      sendMessage()
    })
  } else {
    inputQuery.value = query
    sendMessage()
  }
}

async function createDefaultSession() {
  const payload = { course_id: 'phys101', mode: 'learning', target_node_id: 'n1' }
  const res = await fetch('/api/v1/chat/session/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
  })
  const data = await res.json()
  const newSession = {
      id: data.session_id,
      title: 'Quick Start Session',
      mode: 'learning',
      updated_at: new Date().toISOString()
  }
  sessions.value.unshift(newSession)
  currentSessionId.value = newSession.id
  currentSessionTitle.value = newSession.title
  currentSessionMode.value = 'learning'
  messages.value = []
}

async function switchSession(id) {
  try {
    const session = sessions.value.find(s => s.id === id)
    if (session) {
      currentSessionId.value = session.id
      currentSessionTitle.value = session.title || 'Chat'
      currentSessionMode.value = session.mode || 'learning'
      
      // Stop previous polling
      if (videoPollInterval) clearInterval(videoPollInterval)
      videoStatus.value = null

      // Start polling if preview mode
      if (currentSessionMode.value === 'preview') {
        startVideoPolling(id)
      }

      // Fetch history
      const res = await fetch(`/api/v1/chat/history/${id}`)
      if (res.ok) {
        const data = await res.json()
        messages.value = data
      } else {
        messages.value = []
      }
    }
  } catch (e) {
    console.error('Failed to load history', e)
    messages.value = []
  }
}

function startVideoPolling(sessionId) {
  const poll = async () => {
    try {
      const res = await fetch(`/api/v1/chat/session/${sessionId}/preview`)
      const data = await res.json()
      videoStatus.value = data
      if (data.status === 'completed' || data.status === 'failed') {
        clearInterval(videoPollInterval)
      }
    } catch (e) {
      console.error('Video poll error', e)
    }
  }
  
  poll() // Initial check
  videoPollInterval = setInterval(poll, 3000)
}

async function undoMessage(index) {
  if (isStreaming.value) return
  
  const msg = messages.value[index]
  if (msg.role !== 'user') return

  inputQuery.value = msg.content
  
  try {
    await fetch(`/api/v1/chat/history/${currentSessionId.value}/truncate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ index: index }) 
    })
    messages.value = messages.value.slice(0, index)
  } catch (e) {
    console.error('Failed to undo', e)
  }
}

async function refreshChat() {
  if (isStreaming.value || messages.length === 0) return
  
  let lastUserIndex = -1
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].role === 'user') {
      lastUserIndex = i
      break
    }
  }
  
  if (lastUserIndex === -1) return

  const lastUserMsg = messages.value[lastUserIndex]
  const content = lastUserMsg.content

  await fetch(`/api/v1/chat/history/${currentSessionId.value}/truncate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ index: lastUserIndex }) 
  })
  
  messages.value = messages.value.slice(0, lastUserIndex)
  inputQuery.value = content
  sendMessage()
}

function stopGeneration() {
  if (ws) {
    ws.close()
    ws = null
  }
  isStreaming.value = false
  setTimeout(connectWS, 500)
}

// --- WebSocket & Messaging ---

function connectWS() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return

  const protocol = location.protocol === 'https:' ? 'wss://' : 'ws://'
  const url = `${protocol}${location.host}/api/v1/chat/ws`
  
  ws = new WebSocket(url)
  
  ws.onopen = () => {
    wsConnected.value = true
    console.log('WS Connected')
  }
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleWSMessage(data)
    } catch (e) {
      console.error('WS Parse Error', e)
    }
  }
  
  ws.onclose = () => {
    wsConnected.value = false
    console.log('WS Closed')
    ws = null 
  }
}

async function waitForConnection() {
  if (!ws) connectWS()
  if (ws.readyState === WebSocket.OPEN) return true

  return new Promise((resolve) => {
    const checkInterval = setInterval(() => {
      if (!ws) {
         clearInterval(checkInterval)
         resolve(false)
         return
      }
      if (ws.readyState === WebSocket.OPEN) {
        clearInterval(checkInterval)
        resolve(true)
      } else if (ws.readyState === WebSocket.CLOSED) {
         clearInterval(checkInterval)
         resolve(false)
      }
    }, 100)
    
    setTimeout(() => {
      clearInterval(checkInterval)
      resolve(false)
    }, 5000)
  })
}

async function sendMessage() {
  if (!inputQuery.value.trim() || isStreaming.value) return
  
  if (!currentSessionId.value) {
    await createDefaultSession()
  }

  const query = inputQuery.value
  
  messages.value.push({
    role: 'user',
    content: query
  })
  
  inputQuery.value = ''
  isStreaming.value = true
  
  messages.value.push({
    role: 'assistant',
    content: '',
    sources: []
  })
  
  scrollToBottom()
  
  const connected = await waitForConnection()
  
  if (connected) {
    const payload = {
      query: query,
      session_id: currentSessionId.value,
      current_path: '/ui/chat',
      model: selectedModel.value,
      prompt_style: selectedStyle.value
    }
    ws.send(JSON.stringify(payload))
  } else {
     messages.value[messages.value.length - 1].content = "Error: Connection lost or failed to connect."
     isStreaming.value = false
  }
}

function handleWSMessage(data) {
  const currentMsg = messages.value[messages.value.length - 1]
  if (!currentMsg || currentMsg.role !== 'assistant') return

  switch (data.type) {
    case 'token':
      currentMsg.content += data.content
      scrollToBottom()
      break
    case 'sources':
      currentMsg.sources = data.data
      break
    case 'end':
      isStreaming.value = false
      break
    case 'error':
      currentMsg.content += `\n[Error: ${data.content}]`
      isStreaming.value = false
      break
  }
}

function scrollToBottom() {
  nextTick(() => {
    const container = document.querySelector('main .overflow-y-auto')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

function debounce(func, wait, immediate) {
  let timeout
  return function() {
    const context = this
    const args = arguments
    const later = function() {
      timeout = null
      if (!immediate) func.apply(context, args)
    }
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    if (callNow) func.apply(context, args)
  }
}

const handleEnterKey = debounce(() => {
  sendMessage()
}, 300, true)
</script>

<style scoped>
/* Scoped styles mainly for specific overrides, main styles are utility-first via Tailwind */
</style>
