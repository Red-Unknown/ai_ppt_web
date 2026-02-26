<template>
  <div class="p-6 max-w-6xl mx-auto space-y-6">
    <h1 class="text-3xl font-semibold">Role D Playground</h1>
    <div class="grid md:grid-cols-3 gap-6">
      <div class="space-y-2">
        <label class="block text-sm">Query</label>
        <input v-model="query" class="w-full border rounded px-3 py-2" placeholder="请输入问题，如：课程介绍" />
        <label class="block text-sm">Session ID</label>
        <input v-model="sessionId" class="w-full border rounded px-3 py-2" placeholder="sess_001" />
        <label class="block text-sm">Current Path</label>
        <input v-model="currentPath" class="w-full border rounded px-3 py-2" placeholder="力学/牛顿定律" />
        <div class="flex flex-wrap gap-2 pt-3">
          <button @click="connectWS" class="px-3 py-1 bg-blue-600 text-white rounded">连接WS</button>
          <button @click="sendWS" class="px-3 py-1 bg-blue-600 text-white rounded" :disabled="!wsConnected">发送</button>
          <button @click="closeWS" class="px-3 py-1 bg-gray-600 text-white rounded" :disabled="!wsConnected">断开</button>
        </div>
        <div class="flex flex-wrap gap-2">
          <button @click="startSSE" class="px-3 py-1 bg-emerald-600 text-white rounded">SSE 查询</button>
          <button @click="stopSSE" class="px-3 py-1 bg-gray-600 text-white rounded" :disabled="!sse">停止SSE</button>
        </div>
        <div class="flex flex-wrap gap-2">
          <button @click="reloadConfig" class="px-3 py-1 bg-indigo-600 text-white rounded">热加载配置</button>
          <button @click="loadMetrics" class="px-3 py-1 bg-indigo-600 text-white rounded">加载指标</button>
        </div>
      </div>
      <div class="md:col-span-2">
        <div class="border rounded p-3 h-72 overflow-auto bg-white">
          <div class="text-xs text-gray-500 mb-1">Streaming Output</div>
          <pre class="whitespace-pre-wrap text-sm font-mono leading-5">{{ output }}</pre>
        </div>
        <div class="border rounded p-3 mt-3 bg-white">
          <div class="text-xs text-gray-500">Sources</div>
          <ul class="list-disc pl-5 text-sm">
            <li v-for="s in sources" :key="s.node_id">{{ s.content }} ({{ s.relevance }})</li>
          </ul>
        </div>
        <div class="border rounded p-3 mt-3 bg-white">
          <div class="text-xs text-gray-500">Suggestions</div>
          <div class="flex flex-wrap gap-2">
            <span v-for="s in suggestions" :key="s" class="px-2 py-1 bg-gray-100 border rounded text-sm">{{ s }}</span>
          </div>
        </div>
        <div class="border rounded p-3 mt-3 bg-white">
          <div class="text-xs text-gray-500">Metrics</div>
          <pre class="whitespace-pre-wrap text-sm font-mono leading-5">{{ JSON.stringify(metrics, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const apiBase = '/api/v1/chat'
const query = ref('课程介绍')
const sessionId = ref('sess_ui')
const currentPath = ref('力学/牛顿定律')

const output = ref('')
const sources = ref([])
const suggestions = ref([])
const metrics = ref({})

let ws = null
const wsConnected = ref(false)
let sse = null

function connectWS() {
  if (ws) ws.close()
  const url = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + `${apiBase}/ws`
  ws = new WebSocket(url)
  ws.onopen = () => { wsConnected.value = true; output.value += '[WS] Connected\n' }
  ws.onmessage = (evt) => {
    try {
      const data = JSON.parse(evt.data)
      handleEvent(data)
    } catch {
      output.value += evt.data + '\n'
    }
  }
  ws.onclose = () => { wsConnected.value = false; output.value += '[WS] Closed\n' }
}

function sendWS() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return
  const payload = { query: query.value, session_id: sessionId.value, current_path: currentPath.value, top_k: 3 }
  ws.send(JSON.stringify(payload))
  output.value += `[WS] Sent: ${payload.query}\n`
}

function closeWS() {
  if (ws) ws.close()
}

function startSSE() {
  stopSSE()
  const url = `${apiBase.replace('/api/v1/chat','')}/api/v1/chat/sse?query=${encodeURIComponent(query.value)}&session_id=${encodeURIComponent(sessionId.value)}&current_path=${encodeURIComponent(currentPath.value)}`
  sse = new EventSource(url)
  sse.onmessage = (evt) => {
    try {
      const data = JSON.parse(evt.data)
      handleEvent(data)
    } catch {
      output.value += evt.data + '\n'
    }
  }
  sse.onerror = () => { stopSSE() }
}

function stopSSE() {
  if (sse) { sse.close(); sse = null }
}

async function reloadConfig() {
  const res = await fetch(`${apiBase}/config/reload`, { method: 'POST' })
  output.value += `[CFG] Reload: ${res.status}\n`
}

async function loadMetrics() {
  const res = await fetch(`${apiBase}/metrics`)
  metrics.value = await res.json()
}

function handleEvent(data) {
  if (data.type === 'token') {
    output.value += data.content
  } else if (data.type === 'sources') {
    sources.value = data.data || []
  } else if (data.type === 'suggestions') {
    suggestions.value = data.content || []
  } else if (data.type === 'metrics') {
    metrics.value = data.data || data
  } else if (data.type === 'error') {
    output.value += `\n[ERROR] ${data.content}\n`
  } else if (data.type === 'start') {
    output.value += `\n[START] ${data.action || ''}\n`
  } else if (data.type === 'end') {
    output.value += `\n[END]\n`
  }
}
</script>

<style scoped>
body { background: #f7fafc; }
</style>
