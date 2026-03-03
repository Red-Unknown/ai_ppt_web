<template>
  <div class="flex h-screen bg-gray-50 font-sans text-gray-900">
    <!-- Toast Notification -->
    <div v-if="showToast" class="fixed top-20 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-in fade-in slide-in-from-top-4 flex items-center gap-2 pointer-events-none">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
      </svg>
      {{ toastMessage }}
    </div>
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
      
      <div class="p-4 border-t border-gray-200 bg-gray-50 space-y-2">
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
        <ModernButton 
          block 
          variant="ghost" 
          size="sm" 
          @click="showSettings = true"
          aria-label="Settings"
        >
          <template #icon>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </template>
          Settings
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
      <div class="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth relative" ref="messagesContainer">
        
        <!-- Loading State Overlay -->
        <div v-if="isSessionLoading" class="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center transition-opacity duration-300">
          <div class="flex flex-col items-center gap-3">
             <div class="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
             <p class="text-sm font-medium text-gray-500 animate-pulse">Loading session...</p>
          </div>
        </div>

        <div v-if="!isSessionLoading && messages.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400 select-none animate-in fade-in duration-500">
          <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
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

        <!-- Session Thinking Process & Evaluation -->
        <div v-if="!isSessionLoading && (thinkingPath || evaluation)" class="animate-in fade-in slide-in-from-bottom-4 duration-500 mb-6">
          <!-- Thinking Process -->
          <div v-if="thinkingPath" class="mb-6 border border-purple-200 bg-purple-50 rounded-xl overflow-hidden shadow-sm">
             <div class="px-4 py-3 bg-purple-100/50 border-b border-purple-200 flex items-center justify-between">
                <div class="flex items-center gap-2 text-sm font-semibold text-purple-800">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
                  </svg>
                  Session Thought Process
                </div>
             </div>
             <div class="p-4 text-sm font-mono text-purple-900 bg-white/50 whitespace-pre-wrap max-h-60 overflow-y-auto custom-scrollbar">
                {{ thinkingPath }}
             </div>
          </div>

          <!-- Evaluation -->
          <div v-if="evaluation" class="border border-amber-200 bg-amber-50 rounded-xl overflow-hidden shadow-sm">
             <div class="px-4 py-3 bg-amber-100/50 border-b border-amber-200 flex items-center justify-between">
                <div class="flex items-center gap-2 text-sm font-semibold text-amber-800">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  Evaluation & Feedback
                </div>
                <div class="flex items-center gap-1">
                   <template v-for="i in 5" :key="i">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" :class="i <= evaluation.score ? 'text-amber-500' : 'text-gray-300'" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                   </template>
                </div>
             </div>
             <div class="p-4">
                <p class="text-sm text-amber-900 mb-4">{{ evaluation.comment }}</p>
                <div class="grid grid-cols-3 gap-4">
                   <div v-for="(score, dim) in evaluation.dimensions" :key="dim" class="bg-white rounded-lg p-2 border border-amber-100 text-center">
                      <div class="text-xs text-gray-500 uppercase tracking-wider mb-1">{{ dim }}</div>
                      <div class="text-lg font-bold text-amber-600">{{ score }}/5</div>
                   </div>
                </div>
             </div>
          </div>
        </div>

        <div v-for="(msg, index) in messages" :key="index" v-show="!isSessionLoading" :class="['flex w-full group items-start gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300', msg.role === 'user' ? 'flex-row-reverse' : '']">
          
          <!-- Avatar -->
          <div :class="['w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm', msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-emerald-600 text-white']">
            <span v-if="msg.role === 'user'" class="text-xs font-bold">ME</span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
            </svg>
          </div>

          <div :class="['max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-4 shadow-sm text-sm md:text-base', 
            msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none']">
            
            <!-- Real-time Status Panel -->
            <div v-if="msg.role === 'assistant' && msg.status_updates && msg.status_updates.length > 0" class="mb-4 bg-gray-50 rounded-lg border border-gray-100 p-2 text-xs font-mono text-gray-600 space-y-1">
               <div v-for="(status, sIdx) in msg.status_updates" :key="sIdx" class="flex items-center gap-2 animate-in fade-in duration-300">
                  <span class="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0"></span>
                  <span>{{ status }}</span>
               </div>
            </div>

            <!-- ReAct Chain Visualization -->
            <div v-if="msg.role === 'assistant' && msg.react_steps && msg.react_steps.length > 0" class="mb-4 space-y-2 w-full">
              <div class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1 ml-1">Thinking Process</div>
              <div v-for="(step, stepIdx) in msg.react_steps" :key="stepIdx" class="border border-purple-100 bg-purple-50/30 rounded-lg overflow-hidden transition-all duration-200 hover:shadow-sm">
                <!-- Step Header -->
                <div class="px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-purple-50 transition-colors select-none" @click="step.expanded = !step.expanded">
                   <div class="flex items-center gap-2">
                      <div class="w-5 h-5 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-[10px] font-bold border border-purple-200">
                        {{ step.iteration || stepIdx + 1 }}
                      </div>
                      <span class="text-xs font-semibold text-purple-900 truncate max-w-[150px]">{{ step.tool_name || 'Reasoning' }}</span>
                   </div>
                   <div class="flex items-center gap-2 text-[10px] text-gray-400">
                      <span v-if="step.duration">{{ step.duration.toFixed(2) }}s</span>
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 transform transition-transform duration-200" :class="{ 'rotate-180': step.expanded }" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                   </div>
                </div>
                
                <!-- Step Details -->
                <div v-if="step.expanded" class="px-3 py-2 border-t border-purple-100 bg-white text-xs font-mono overflow-x-auto max-h-80 custom-scrollbar">
                   <!-- Thought -->
                   <div v-if="step.thought" class="mb-3">
                      <div class="text-purple-400 mb-1 font-bold flex items-center gap-1">Thought</div>
                      <div class="bg-purple-50 p-2 rounded text-gray-700 border border-purple-100 whitespace-pre-wrap">{{ step.thought }}</div>
                   </div>
                   
                   <!-- Tool Input -->
                   <div v-if="step.inputs" class="mb-3">
                      <div class="text-blue-400 mb-1 font-bold flex items-center gap-1">Input</div>
                      <pre class="bg-blue-50 p-2 rounded text-gray-700 border border-blue-100">{{ JSON.stringify(step.inputs, null, 2) }}</pre>
                   </div>
                   
                   <!-- Tool Output -->
                   <div v-if="step.output" class="mb-1">
                      <div class="text-emerald-400 mb-1 font-bold flex items-center gap-1">Output</div>
                      <pre class="bg-emerald-50 p-2 rounded text-gray-700 border border-emerald-100 whitespace-pre-wrap">{{ step.output }}</pre>
                   </div>
                   
                   <!-- Error -->
                   <div v-if="step.error" class="mb-1">
                      <div class="text-red-400 mb-1 font-bold flex items-center gap-1">Error</div>
                      <div class="bg-red-50 p-2 rounded text-red-700 border border-red-100 whitespace-pre-wrap">{{ step.error }}</div>
                   </div>
                </div>
              </div>
            </div>

            <!-- Skill Executions (Legacy/Direct) -->
            <div v-if="msg.role === 'assistant' && msg.skills && msg.skills.length > 0 && (!msg.react_steps || msg.react_steps.length === 0)" class="mb-4 space-y-2 w-full">
              <div v-for="(skill, sIdx) in msg.skills" :key="sIdx" class="border border-blue-100 bg-blue-50/50 rounded-lg overflow-hidden transition-all duration-200 hover:shadow-sm">
                <!-- Header -->
                <div class="px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-blue-50 transition-colors select-none" @click="skill.expanded = !skill.expanded">
                  <div class="flex items-center gap-2">
                    <div v-if="skill.status === 'running'" class="w-2 h-2 bg-blue-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
                    <div v-else-if="skill.status === 'success'" class="w-2 h-2 bg-emerald-500 rounded-full"></div>
                    <div v-else class="w-2 h-2 bg-red-500 rounded-full"></div>
                    
                    <span class="text-xs font-semibold text-blue-900 uppercase tracking-wide">{{ skill.name }}</span>
                    <span v-if="skill.status === 'running'" class="text-[10px] text-blue-500 animate-pulse">Running...</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-[10px] text-gray-400 font-mono">{{ skill.status === 'success' ? 'COMPLETED' : (skill.status === 'running' ? 'EXECUTING' : 'FAILED') }}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-blue-400 transform transition-transform duration-200" :class="{ 'rotate-180': skill.expanded }" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </div>
                
                <!-- Details (Collapsible) -->
                <div v-if="skill.expanded" class="px-3 py-2 border-t border-blue-100 bg-white text-xs font-mono overflow-x-auto max-h-60 custom-scrollbar animate-in slide-in-from-top-1">
                   <!-- Inputs -->
                   <div v-if="skill.inputs" class="mb-3">
                      <div class="text-gray-400 mb-1 select-none flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                        Inputs
                      </div>
                      <pre class="bg-gray-50 p-2 rounded text-gray-700 border border-gray-100">{{ JSON.stringify(skill.inputs, null, 2) }}</pre>
                   </div>
                   
                   <div v-if="skill.details">
                       <!-- Success Output -->
                       <div v-if="skill.status === 'success'" class="mb-1">
                         <div class="text-gray-400 mb-1 select-none flex items-center gap-1">
                           <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>
                           Result
                         </div>
                         <!-- Render based on type -->
                         <div v-if="skill.details.render_type === 'json'">
                            <pre class="text-emerald-700 bg-emerald-50 p-2 rounded border border-emerald-100">{{ skill.details.output }}</pre>
                         </div>
                         <div v-else-if="skill.details.render_type === 'markdown'">
                            <div class="prose prose-sm max-w-none text-emerald-900 bg-emerald-50/50 p-2 rounded" v-html="skill.details.output"></div>
                         </div>
                         <div v-else>
                            <pre class="text-emerald-700 bg-emerald-50 p-2 rounded border border-emerald-100 whitespace-pre-wrap">{{ skill.details.output }}</pre>
                         </div>
                       </div>
                       
                       <!-- Error Output -->
                       <div v-else-if="skill.status === 'error'" class="mb-1">
                          <div class="text-red-400 mb-1 select-none flex items-center gap-1">
                             <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
                             Error
                          </div>
                          <div class="text-red-700 bg-red-50 p-2 rounded border border-red-100">
                             <div class="font-bold">{{ skill.details.error_message }}</div>
                             <div class="text-xs mt-1 opacity-75">{{ skill.details.error_details }}</div>
                          </div>
                       </div>
                   </div>
                   <div v-else class="text-gray-400 italic py-2 text-center">
                     Running...
                   </div>
                </div>
              </div>
            </div>

            <!-- Thinking Process (DeepSeek Reasoner) -->
            <div v-if="msg.reasoning_content" class="mb-4">
              <details class="group border border-gray-200 bg-gray-50 rounded-lg overflow-hidden transition-all duration-200" :open="msg.isReasoningOpen">
                <summary 
                  @click.prevent="msg.isReasoningOpen = !msg.isReasoningOpen"
                  class="px-3 py-2 cursor-pointer bg-gray-100 hover:bg-gray-200 transition-colors flex items-center justify-between text-xs font-semibold text-gray-600 uppercase tracking-wide select-none"
                >
                  <div class="flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-purple-500" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
                    </svg>
                    Thinking Process
                    <span v-if="!msg.isReasoningOpen" class="text-gray-400 text-[10px] ml-2 font-normal lowercase">(collapsed)</span>
                  </div>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 transform transition-transform duration-200" :class="{ 'rotate-180': msg.isReasoningOpen }" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </summary>
                <div class="p-3 text-xs font-mono text-gray-600 bg-gray-50/50 whitespace-pre-wrap leading-relaxed border-t border-gray-200 animate-in slide-in-from-top-2 duration-200" style="min-height: 120px; max-height: 400px; overflow-y: auto;">
                  {{ msg.reasoning_content }}
                </div>
              </details>
            </div>

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

            <!-- Suggested Questions -->
            <div v-if="msg.role === 'assistant' && msg.suggestions && msg.suggestions.length && enableSuggestions" class="mt-4 pt-3 border-t border-gray-100 animate-in fade-in slide-in-from-bottom-2 duration-500 delay-300">
              <div class="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                Suggested Follow-up
              </div>
              <div class="flex flex-wrap gap-2">
                <button 
                  v-for="(suggestion, sIdx) in msg.suggestions" 
                  :key="sIdx"
                  @click="sendMessage(suggestion)"
                  class="px-3 py-1.5 bg-blue-50 text-blue-700 text-xs rounded-full hover:bg-blue-100 transition-colors border border-blue-200 text-left"
                >
                  {{ suggestion }}
                </button>
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
              @keydown="handleShortcut"
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

    <!-- Debug Panel -->
    <div v-if="debugMode" class="fixed bottom-20 right-4 w-80 bg-gray-900/90 text-white p-4 rounded-lg shadow-2xl backdrop-blur-sm border border-gray-700 z-50 text-xs font-mono">
      <div class="flex justify-between items-center mb-2 border-b border-gray-700 pb-2">
        <span class="font-bold text-green-400">Search Debug Panel</span>
        <button @click="debugMode = false" class="text-gray-400 hover:text-white">&times;</button>
      </div>
      <div v-if="lastSearchInfo" class="space-y-2">
        <div class="grid grid-cols-[80px_1fr] gap-1">
          <span class="text-gray-500">Time:</span>
          <span>{{ lastSearchInfo.timestamp }}</span>
          
          <span class="text-gray-500">Provider:</span>
          <span class="text-blue-400">{{ lastSearchInfo.provider }}</span>
          
          <span class="text-gray-500">Latency:</span>
          <span :class="parseInt(lastSearchInfo.latency) > 1000 ? 'text-red-400' : 'text-green-400'">{{ lastSearchInfo.latency }}</span>
          
          <span class="text-gray-500">Status:</span>
          <span>{{ lastSearchInfo.status }}</span>
          
          <span class="text-gray-500">ReqID:</span>
          <span class="truncate" :title="lastSearchInfo.request_id">{{ lastSearchInfo.request_id }}</span>
        </div>
        <div class="mt-2 pt-2 border-t border-gray-700">
          <span class="text-gray-500 block mb-1">Query:</span>
          <div class="bg-gray-800 p-2 rounded break-words">{{ lastSearchInfo.query }}</div>
        </div>
      </div>
      <div v-else class="text-gray-500 italic text-center py-4">
        No search requests recorded yet.
      </div>
    </div>

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

    <!-- Settings Modal -->
    <Modal :isOpen="showSettings" @close="showSettings = false">
      <template #title>Settings</template>
      <div class="space-y-6">
        <!-- Feature Toggles -->
        <div>
          <h3 class="text-sm font-medium text-gray-900 mb-3">Features</h3>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <div class="text-sm font-medium text-gray-900">Next Question Suggestions</div>
              <div class="text-xs text-gray-500">Automatically suggest follow-up questions</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="enableSuggestions" class="sr-only peer">
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>

        <!-- Shortcuts Configuration -->
        <div>
          <h3 class="text-sm font-medium text-gray-900 mb-3">Keyboard Shortcuts</h3>
          <div class="space-y-2">
            <div v-for="(shortcut, index) in shortcuts" :key="index" class="p-3 bg-gray-50 rounded-lg border border-gray-200 flex flex-col gap-2">
              <div class="flex items-center justify-between">
                <div class="inline-flex items-center px-2 py-1 rounded text-xs font-mono bg-white border border-gray-200 shadow-sm text-gray-600">
                  Alt + {{ shortcut.key }}
                </div>
                <input 
                  v-model="shortcut.label" 
                  class="text-xs font-medium text-right bg-transparent border-none focus:ring-0 text-gray-600 p-0 placeholder-gray-400"
                  placeholder="Button Label"
                />
              </div>
              <textarea 
                v-model="shortcut.text" 
                rows="2"
                class="w-full text-xs text-gray-700 bg-white border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 resize-none"
                placeholder="Message text to send..."
              ></textarea>
            </div>
          </div>
          <p class="text-xs text-gray-400 mt-2 text-center">
            Press <span class="font-mono bg-gray-100 px-1 rounded text-gray-600">Alt</span> + <span class="font-mono bg-gray-100 px-1 rounded text-gray-600">Number</span> to trigger
          </p>
        </div>
      </div>
      <template #footer>
        <ModernButton variant="primary" @click="showSettings = false">Done</ModernButton>
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
const isSending = ref(false) // 新增：发送状态锁
const sessionStreamingStatus = ref({}) // Session ID -> Boolean
const expectedQuestions = ref([]) // 当前会话的预期问题
const thinkingPath = ref('') // Session Thinking Path
const evaluation = ref(null) // Session Evaluation

// Shortcuts & Toast
const showToast = ref(false)
const toastMessage = ref('')

// Settings & Feature Flags
const showSettings = ref(false)
const enableSuggestions = ref(true)

const shortcuts = ref([
  { key: '1', alt: true, label: '没听懂', text: '我不理解，请用更通俗的语言解释一遍' },
  { key: '2', alt: true, label: '继续', text: '请继续' },
  { key: '3', alt: true, label: '举例', text: '请举一个具体的例子' }
])

const selectedModel = ref('deepseek')
const selectedStyle = ref('default')

// Debug
const debugMode = ref(false)
const lastSearchInfo = ref(null)

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
    isSidebarOpen.value = false
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

const isSessionLoading = ref(false)

async function switchSession(id) {
  if (id === currentSessionId.value) return
  
  try {
    const session = sessions.value.find(s => s.id === id)
    if (session) {
      // 1. Clear current state and show loader
      isSessionLoading.value = true
      messages.value = [] 
      expectedQuestions.value = [] // Clear expected questions
      thinkingPath.value = ''
      evaluation.value = null
      
      currentSessionId.value = session.id
      currentSessionTitle.value = session.title || 'Chat'
      currentSessionMode.value = session.mode || 'learning'
      
      // Sync streaming status from session map
      isStreaming.value = !!sessionStreamingStatus.value[id]

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
        // Double check session ID in case of race condition
        if (currentSessionId.value === id) {
             messages.value = data
        }
      } else {
        if (currentSessionId.value === id) {
            messages.value = []
        }
      }

      // Fetch Session Context (Expected Questions)
      try {
        const ctxRes = await fetch(`/api/v1/chat/history/${id}/context`)
        if (ctxRes.ok) {
          const ctxData = await ctxRes.json()
          if (currentSessionId.value === id) {
            expectedQuestions.value = ctxData.expect_questions || []
            // Sync with new fields if they exist in context (fallback)
            if (ctxData.thinking_path) thinkingPath.value = ctxData.thinking_path
            if (ctxData.evaluation) evaluation.value = ctxData.evaluation
          }
        }
        
        // Fetch Thinking Process
        const thinkRes = await fetch(`/api/v1/chat/session/${id}/thinking`)
        if (thinkRes.ok) {
           const thinkData = await thinkRes.json()
           if (currentSessionId.value === id && thinkData.thoughtProcess) {
              thinkingPath.value = thinkData.thoughtProcess
           }
        }

        // Fetch Evaluation
        const evalRes = await fetch(`/api/v1/chat/session/${id}/evaluation`)
        if (evalRes.ok) {
           const evalData = await evalRes.json()
           if (currentSessionId.value === id && evalData.evaluation && Object.keys(evalData.evaluation).length > 0) {
              evaluation.value = evalData.evaluation
           }
        }

      } catch (e) {
        console.warn('Failed to fetch session context', e)
      }

    }
  } catch (e) {
    console.error('Failed to load history', e)
    messages.value = []
  } finally {
      if (currentSessionId.value === id) {
          isSessionLoading.value = false
      }
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
  // 仅停止流式输出，保持WebSocket连接活跃
  isStreaming.value = false
  // 不清除WebSocket连接，保持持久连接
}

// --- WebSocket & Messaging ---

function connectWS() {
  // 清理已失效的连接
  if (ws) {
    if (ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING) {
      ws = null
    } else if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
      return
    }
  }

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
    // 自动重连机制
    if (isStreaming.value) {
      setTimeout(connectWS, 1000)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    wsConnected.value = false
    // 错误时也尝试重连
    setTimeout(connectWS, 2000)
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

async function sendMessage(text = null) {
  const query = text || inputQuery.value
  
  if (!query.trim() || isStreaming.value || isSending.value) return
  
  isSending.value = true
  
  try {
    if (!currentSessionId.value) {
      await createDefaultSession()
    }

    // Clear input only if we used it directly (not shortcut/suggestion)
    if (!text) {
      inputQuery.value = ''
    }
    
    messages.value.push({
      role: 'user',
      content: query
    })
    
    isStreaming.value = true
    sessionStreamingStatus.value[currentSessionId.value] = true
    
    messages.value.push({
      role: 'assistant',
      content: '',
      reasoning_content: '', // Changed from reasoning to match schema
      sources: [],
      skills: [],
      suggestions: [],
      status: null,
      status_updates: [],
      react_steps: []
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
  } finally {
    isSending.value = false
  }
}

function handleWSMessage(data) {
  // Update streaming status for the session if end/error
  if (data.session_id) {
    if (data.type === 'end' || data.type === 'error') {
      sessionStreamingStatus.value[data.session_id] = false
      if (data.session_id === currentSessionId.value) {
        isStreaming.value = false
      }
    }
  }

  // Check if the message belongs to the current session
  if (data.session_id && data.session_id !== currentSessionId.value) {
    console.log(`Received message for background session ${data.session_id}, ignoring render.`)
    return
  }

  const currentMsg = messages.value[messages.value.length - 1]
  if (!currentMsg || currentMsg.role !== 'assistant') return

  switch (data.type) {
    case 'evaluation':
      evaluation.value = data.content
      scrollToBottom()
      break
    
    case 'token':
      currentMsg.content += data.content
      scrollToBottom()
      break
    
    case 'status':
      if (!currentMsg.status_updates) currentMsg.status_updates = []
      currentMsg.status_updates.push(data.content)
      // Keep only last 5 status updates to avoid clutter
      if (currentMsg.status_updates.length > 5) {
         currentMsg.status_updates.shift()
      }
      break

    case 'iteration':
      // Backend signals new ReAct iteration
      // We can create a placeholder step or just log it
      break

    case 'tool_start':
      if (!currentMsg.react_steps) currentMsg.react_steps = []
      currentMsg.react_steps.push({
        type: 'tool',
        tool_name: data.tool_name,
        inputs: data.inputs,
        expanded: true,
        status: 'running',
        iteration: currentMsg.react_steps.length + 1 // Or use data.iteration if available
      })
      scrollToBottom()
      break

    case 'tool_result':
      if (currentMsg.react_steps && currentMsg.react_steps.length > 0) {
        // Find the last running tool step
        // Ideally we should match by ID, but for now assuming sequential
        const step = currentMsg.react_steps[currentMsg.react_steps.length - 1]
        if (step) {
          step.output = data.output
          step.status = 'success'
          step.duration = data.execution_time
          step.expanded = false // Auto-collapse on success
        }
      }
      break

    case 'tool_error':
      if (currentMsg.react_steps && currentMsg.react_steps.length > 0) {
        const step = currentMsg.react_steps[currentMsg.react_steps.length - 1]
        if (step) {
          step.error = data.error_message
          step.status = 'error'
          step.expanded = true
        }
      }
      break
      
    case 'thought':
      if (!currentMsg.react_steps) currentMsg.react_steps = []
      // Check if last step is a thought step, if so append, else create new
      // But ReAct usually does Thought -> Action.
      // Let's attach thought to the next action or create a standalone thought block?
      // Simpler: Just create a step for thought.
      currentMsg.react_steps.push({
         type: 'thought',
         thought: data.content,
         expanded: true,
         iteration: currentMsg.react_steps.length + 1
      })
      scrollToBottom()
      break
      
    case 'usage':
      // Handle usage stats if needed
      console.log('Usage:', data)
      break

    case 'reasoning':
      if (!currentMsg.reasoning_content) {
        currentMsg.reasoning_content = ''
        currentMsg.isReasoningOpen = true
      }
      currentMsg.reasoning_content += data.content
      currentMsg.status = 'thinking'
      scrollToBottom()
      break
    
    case 'reasoning_end':
      setTimeout(() => {
        if (currentMsg) {
          currentMsg.isReasoningOpen = false
          currentMsg.status = 'reasoning_complete'
        }
      }, 500)
      break

    case 'suggestions':
      if (!currentMsg.suggestions) currentMsg.suggestions = []
      currentMsg.suggestions = data.content
      expectedQuestions.value = data.content // Update expected questions for sidebar
      scrollToBottom()
      break

    case 'sources':
      currentMsg.sources = data.data
      break
      
    case 'end':
      // Handled at top of function for state sync
      currentMsg.status = null
      break
      
    case 'error':
      currentMsg.content += `\n[Error: ${data.content}]`
      // Handled at top of function for state sync
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

function handleShortcut(event) {
  // Check for Alt+Number shortcuts
  if (event.altKey && !event.ctrlKey && !event.shiftKey && !event.metaKey) {
    const key = event.key
    const shortcut = shortcuts.value.find(s => s.key === key)
    
    if (shortcut) {
      event.preventDefault()
      triggerShortcut(shortcut)
    }
  }
}

function triggerShortcut(shortcut) {
  if (isStreaming.value) return
  
  // Show Toast
  toastMessage.value = `Sending: "${shortcut.label}"`
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 2000)
  
  // Send Message
  sendMessage(shortcut.text)
}

const handleEnterKey = debounce(() => {
  sendMessage()
}, 300, true)

// Expose for testing
defineExpose({
  handleWSMessage,
  messages,
  debugMode,
  lastSearchInfo
})
</script>

<style scoped>
/* Scoped styles mainly for specific overrides, main styles are utility-first via Tailwind */
</style>
