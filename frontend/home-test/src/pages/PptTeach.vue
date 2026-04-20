<template>
  <div class="ppt-teach-page">
    <!-- 顶部栏 -->
    <AppHeader 
      :user-name="userName"
      @back="handleBack"
      @avatar-click="handleAvatarClick"
    />

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 左侧：核心学习区 -->
      <div class="left-section" :style="{ width: leftWidth + '%' }">
        <!-- PPT播放器 -->
        <div class="ppt-orange-container">
          <div class="ppt-player-wrapper">
          <!-- PPT标题栏 - 橙色 -->
          <div class="ppt-header">
            <span class="ppt-title">PPT标题</span>
            <div class="ppt-actions">
              <button class="action-btn select-element">选择元素</button>
              <button class="action-btn icon-btn" @click="openExportDialog">
                <img src="@/assets/images/action/ic-share.svg" alt="分享">
              </button>
              <button class="action-btn icon-btn more-btn" @click="togglePptExpand">
                <img src="@/assets/images/action/ic-arrow_down.svg" alt="更多" :class="{ 'rotate-180': !isPptExpanded }">
              </button>
            </div>
          </div>
          
          <!-- PPT内容区 -->
          <div v-if="isPptExpanded" class="ppt-content">
            <div class="ppt-image-wrapper">
              <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Great%20Wall%20of%20China%20landscape%20with%20mountains&image_size=landscape_16_9" alt="PPT" class="ppt-image">
              <div class="play-overlay" @click="togglePlay">
                <img src="@/assets/images/action/ic_play.svg" alt="播放" class="play-icon">
              </div>
            </div>
          </div>
          
          <!-- 视频控制栏 -->
          <div v-if="isPptExpanded" class="video-controls">
            <button class="control-btn play-pause" @click="togglePlay">
              <img v-if="!isPlaying" src="@/assets/images/action/ic_play.svg" alt="播放">
              <img v-else src="@/assets/images/action/ic-pause.svg" alt="暂停">
            </button>
            <div class="progress-container">
              <div class="progress-bar" 
                   @click="seekVideo" 
                   @mousedown="startDrag"
                   :class="{ 'dragging': isDragging }">
                <div class="progress-filled" :style="{ width: progressPercent + '%' }"></div>
                <div class="progress-handle" 
                     :style="{ left: progressPercent + '%' }"
                     :class="{ 'active': isDragging }"></div>
              </div>
            </div>
            <span class="time-display">{{ currentPage }}/{{ totalPages }}</span>
            <button class="control-btn speed-btn" @click="cyclePlaybackSpeed">
              {{ playbackSpeed }}x
            </button>
            <button class="control-btn volume" @click="toggleMute">
              <img v-if="!isMuted" src="@/assets/images/action/ic_volume_on.svg" alt="音量">
              <img v-else src="@/assets/images/action/ic_volume_off.svg" alt="静音">
            </button>
            <button class="control-btn fullscreen" @click="toggleFullscreen">
              <img src="@/assets/images/action/ic-fullscreen.svg" alt="全屏">
            </button>
          </div>
          </div>
        </div>

        <!-- 课程文档 -->
        <div class="course-document-wrapper">
          <div class="course-document" :class="{ 'collapsed': !isDocExpanded }">
            <div class="doc-section">
              <h3 class="doc-title">方法 2：</h3>
              <p class="doc-subtitle">用「Frame + 遮罩」实现通用裁剪（适合所有图层）</p>
              <ol class="doc-list">
                <li>选中要裁剪的图层，右键菜单里选择 <span class="highlight">「Use as mask」</span>（快捷键 Ctrl+Alt+M），或者先给它套一个 Frame（Ctrl+Alt+G）。</li>
                <li>调整 Frame 的大小和位置，超出 Frame 的部分会被自动隐藏，实现和裁剪一样的效果。</li>
                <li>这种方法不会破坏原图层，随时可以调整裁剪范围</li>
              </ol>
            </div>
            <div class="doc-section">
              <h3 class="doc-title">方法 3：</h3>
              <p class="doc-subtitle">插件裁剪</p>
              <ol class="doc-list">
                <li>如果需要更灵活的裁剪，也可以在右键菜单里打开 <span class="highlight">「Plugins」</span>，搜索并安装裁剪类插件（比如 Crop 相关插件）来使用。</li>
              </ol>
            </div>
          </div>
          
          <!-- 展开/折叠教案按钮 -->
          <div class="doc-expand-control">
            <button class="doc-expand-btn" @click="toggleDocExpand">
              {{ isDocExpanded ? '折叠教案' : '展开教案' }}
            </button>
          </div>
        </div>
        

      </div>

      <!-- 中间可滑动的圆形滑块 -->
      <div 
        class="resizer" 
        :class="{ dragging: isResizing }"
        @mousedown="startResize"
        @touchstart="startResizeTouch"
      >
        <div class="resizer-track"></div>
        <div class="resizer-handle">
          <div class="resizer-dot"></div>
        </div>
        <!-- 位置指示 -->
        <div v-if="isResizing" class="resize-indicator">
          {{ Math.round(leftWidth) }}% / {{ Math.round(rightWidth) }}%
        </div>
      </div>

      <!-- 右侧：AI助手交互区 -->
      <div class="right-section" :style="{ width: rightWidth + '%' }">
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
          <!-- AI助手Tab -->
          <div v-if="activeTab === 'ai-assistant'" class="ai-chat-panel">
            <!-- 功能按钮区 -->
            <div class="chat-actions">
              <button class="action-icon-btn" @click="startNewChat" title="开启新对话">
                <img src="@/assets/images/action/ic-addchat.svg" alt="新对话">
              </button>
              <button class="action-icon-btn" @click="openSettings" title="设置">
                <img src="@/assets/images/action/ic-set.svg" alt="设置">
              </button>
            </div>
            <div class="chat-messages" ref="chatContainer">
              <!-- 空状态 -->
              <div v-if="messages.length === 0" class="empty-chat">
                <div class="empty-icon">
                  <img src="@/assets/images/logo/ic-AI.svg" alt="AI" class="ai-icon">
                </div>
                <p class="empty-text">你好同学，若有任何疑问，欢迎随时与我沟通</p>
              </div>
              <!-- 消息列表 -->
              <template v-else>
                <div
                  v-for="(msg, index) in messages"
                  :key="index"
                  class="message"
                  :class="{ 'user-msg': msg.type === 'user', 'ai-msg': msg.type === 'ai' }"
                >
                  <!-- AI消息 - 头像在左 -->
                  <template v-if="msg.type === 'ai'">
                    <div class="avatar ai-avatar">
                      <img src="@/assets/images/logo/ic-AI.svg" alt="AI" class="ai-avatar-img">
                    </div>
                    <div class="message-bubble">
                      <div class="message-content" v-html="formatMessage(msg.content)"></div>
                    </div>
                  </template>
                  <!-- 用户消息 - 头像在右 -->
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

          <!-- 历史对话Tab -->
          <div v-if="activeTab === 'history'" class="history-panel">
            <!-- 历史对话列表 -->
            <div v-if="!showHistoryDetail" class="history-list">
              <div
                v-for="item in historyList"
                :key="item.id"
                class="history-item"
                @click="openHistoryDetail(item)"
              >
                <div class="history-icon">
                  <img src="@/assets/images/action/ic_chat.svg" alt="聊天">
                </div>
                <div class="history-info">
                  <span class="history-title">{{ item.title }}</span>
                  <span class="history-time">{{ formatHistoryTime(item.updatedAt) }}</span>
                </div>
              </div>
            </div>
            <!-- 历史对话详情 -->
            <div v-else class="history-detail">
              <!-- 功能按钮区 -->
              <div class="chat-actions detail-actions">
                <button class="action-icon-btn" @click="closeHistoryDetail" title="返回">
                  <img src="@/assets/images/action/ic-arrow_left2.svg" alt="返回">
                </button>
                <div class="detail-title-wrapper">
                  <h3 class="detail-title" v-if="selectedHistory">{{ selectedHistory.title }}</h3>
                </div>
                <button class="action-icon-btn" @click="openSettings" title="设置">
                  <img src="@/assets/images/action/ic-set.svg" alt="设置">
                </button>
              </div>
              <!-- 历史消息 -->
              <div class="detail-messages" ref="detailChatContainer">
                <div
                  v-for="(msg, index) in historyMessages"
                  :key="index"
                  class="message"
                  :class="{ 'user-msg': msg.type === 'user', 'ai-msg': msg.type === 'ai' }"
                >
                  <!-- AI消息 - 头像在左 -->
                  <template v-if="msg.type === 'ai'">
                    <div class="avatar ai-avatar">
                      <img src="@/assets/images/logo/ic-AI.svg" alt="AI" class="ai-avatar-img">
                    </div>
                    <div class="message-bubble">
                      <div class="message-content" v-html="formatMessage(msg.content)"></div>
                    </div>
                  </template>
                  <!-- 用户消息 - 头像在右 -->
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

          <!-- 思维导图Tab -->
          <div v-if="activeTab === 'mindmap'" class="mindmap-panel">
            <div class="mindmap-container">
            </div>
          </div>

          <!-- 课程概要Tab -->
          <div v-if="activeTab === 'summary'" class="summary-panel">
            <div class="summary-content">
              <h3 class="summary-title">课程概要：</h3>
              <div class="summary-section">
                <h4>方法 2：</h4>
                <p>用「Frame + 遮罩」实现通用裁剪（适合所有图层）</p>
                <ol>
                  <li>选中要裁剪的图层，右键菜单里选择 <span class="highlight">「Use as mask」</span>（快捷键 Ctrl+Alt+M），或者先给它套一个 Frame（Ctrl+Alt+G）。</li>
                  <li>调整 Frame 的大小和位置，超出 Frame 的部分会被自动隐藏，实现和裁剪一样的效果。</li>
                  <li>这种方法不会破坏原图层，随时可以调整裁剪范围</li>
                </ol>
              </div>
              <div class="summary-section">
                <h4>方法 3：</h4>
                <p>插件裁剪</p>
                <ol>
                  <li>如果需要更灵活的裁剪，也可以在右键菜单里打开 <span class="highlight">「Plugins」</span>，搜索并安装裁剪类插件（比如 Crop 相关插件）来使用。</li>
                </ol>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部输入区 -->
        <div class="chat-input-area">
          <div class="input-wrapper">
            <input
              type="text"
              v-model="inputMessage"
              :placeholder="inputPlaceholder"
              @keyup.enter="sendMessage"
            />
            <button
              class="voice-btn"
              :class="{ active: isRecording }"
              @click="toggleRecording"
            >
              <img v-if="!isRecording" src="@/assets/images/action/ic_mic_off.svg" alt="语音" class="voice-icon">
              <img v-else src="@/assets/images/action/ic_mic_active.svg" alt="录音中" class="voice-icon">
              <div v-if="isRecording" class="voice-waves">
                <span class="wave"></span>
                <span class="wave"></span>
                <span class="wave"></span>
              </div>
            </button>
            <button
              class="send-btn"
              @click="sendMessage"
              :disabled="!inputMessage.trim()"
            >
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 资料导出弹窗 -->
  <div v-if="showExportDialog" class="export-dialog-overlay" @click="closeExportDialog">
    <div class="export-dialog" @click.stop>
      <div class="export-dialog-header">
        <h3 class="export-dialog-title">资料导出</h3>
        <button class="export-dialog-close" @click="closeExportDialog">×</button>
      </div>
      <div class="export-dialog-content">
        <div class="export-option">
          <input type="checkbox" id="export-mindmap" v-model="exportOptions.mindmap">
          <label for="export-mindmap">思维导图（图片）</label>
        </div>
        <div class="export-option">
          <input type="checkbox" id="export-ai-lesson-plan" v-model="exportOptions.aiLessonPlan">
          <label for="export-ai-lesson-plan">AI教案（Word文档）</label>
        </div>
        <div class="export-option">
          <input type="checkbox" id="export-course-summary" v-model="exportOptions.courseSummary">
          <label for="export-course-summary">课程概要（Word文档）</label>
        </div>
      </div>
      <div class="export-dialog-footer">
        <button class="export-dialog-btn cancel-btn" @click="closeExportDialog">取消</button>
        <button class="export-dialog-btn confirm-btn" @click="confirmExport">确认导出</button>
      </div>
    </div>
  </div>

  <!-- 设置弹窗 -->
  <div v-if="showSettingsDialog" class="export-dialog-overlay" @click="closeSettingsDialog">
    <div class="export-dialog" @click.stop>
      <div class="export-dialog-header">
        <h3 class="export-dialog-title">对话设置</h3>
        <button class="export-dialog-close" @click="closeSettingsDialog">×</button>
      </div>
      <div class="export-dialog-content">
        <div class="settings-option">
          <label for="model-select" class="settings-label">模型选择</label>
          <select id="model-select" v-model="settingsOptions.model" class="settings-select">
            <option value="chatGPT">chatGPT</option>
            <option value="GPT-4">GPT-4</option>
            <option value="Claude">Claude</option>
          </select>
        </div>
        <div class="settings-option">
          <label for="python-checkbox" class="settings-label">Python计算</label>
          <input type="checkbox" id="python-checkbox" v-model="settingsOptions.python" class="settings-checkbox">
        </div>
        <div class="settings-option">
          <label for="websearch-checkbox" class="settings-label">联网搜索</label>
          <input type="checkbox" id="websearch-checkbox" v-model="settingsOptions.webSearch" class="settings-checkbox">
        </div>
        <div class="settings-option">
          <label for="voice-select" class="settings-label">对话声音</label>
          <select id="voice-select" v-model="settingsOptions.voice" class="settings-select">
            <option value="女声1">女声1</option>
            <option value="女声2">女声2</option>
            <option value="男声1">男声1</option>
            <option value="男声2">男声2</option>
          </select>
        </div>
      </div>
      <div class="export-dialog-footer">
        <button class="export-dialog-btn cancel-btn" @click="closeSettingsDialog">取消</button>
        <button class="export-dialog-btn confirm-btn" @click="confirmSettings">确认设置</button>
      </div>
    </div>
  </div>

  <!-- 全新全屏界面 -->
  <div v-if="isFullscreen" class="fullscreen-container">
    <!-- 顶部标题栏 -->
    <div class="fullscreen-header">
      <span class="fullscreen-title">课程标题</span>
    </div>

    <!-- 主内容区 -->
    <div class="fullscreen-main">
      <!-- PPT展示区 -->
      <div class="ppt-display-area">
        <!-- 上一页按钮 -->
        <button class="nav-btn prev-btn" @click="prevPage">
          <img src="@/assets/images/action/ic-arrow_right1.svg" alt="上一页" style="transform: scaleX(-1); width: 24px; height: 24px;">
        </button>
        
        <!-- PPT图片 -->
        <div class="ppt-display-wrapper" :style="{ transform: `scale(${pptScale})` }">
          <img 
            src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Great%20Wall%20of%20China%20landscape%20with%20mountains&image_size=landscape_16_9" 
            alt="PPT" 
            class="ppt-display-image"
          >
        </div>
        
        <!-- 下一页按钮 -->
        <button class="nav-btn next-btn" @click="nextPage">
          <img src="@/assets/images/action/ic-arrow_right1.svg" alt="下一页" style="width: 24px; height: 24px;">
        </button>

        <!-- 缩放控制 -->
        <div class="zoom-controls">
          <button class="zoom-btn" @click="zoomOut">−</button>
          <span class="zoom-level">{{ Math.round(pptScale * 100) }}%</span>
          <button class="zoom-btn" @click="zoomIn">+</button>
        </div>
      </div>

      <!-- 右侧可伸缩功能栏 -->
      <div 
        class="right-sidebar" 
        :class="{ expanded: isSidebarExpanded }"
      >
        <div 
          class="sidebar-toggle" 
          @click="toggleSidebar"
        >
          <img 
            src="@/assets/images/action/ic-Tool.svg" 
            alt="展开/收起"
            style="width: 20px; height: 20px;"
          >
        </div>
        <div v-if="isSidebarExpanded" class="sidebar-content">
          <div class="sidebar-tabs">
            <button 
              v-for="tab in sidebarTabs" 
              :key="tab.id"
              class="sidebar-tab"
              :class="{ active: activeSidebarTab === tab.id }"
              @click="switchSidebarTab(tab.id)"
            >
              {{ tab.name }}
            </button>
          </div>
          <div class="sidebar-tab-content">
            <!-- AI助手内容 -->
            <div v-if="activeSidebarTab === 'ai-assistant'" class="sidebar-panel">
              <div class="chat-actions">
                <button class="action-icon-btn" @click="startNewChat" title="开启新对话">
                  <img src="@/assets/images/action/ic-addchat.svg" alt="新对话">
                </button>
                <button class="action-icon-btn" @click="openSettings" title="设置">
                  <img src="@/assets/images/action/ic-set.svg" alt="设置">
                </button>
              </div>
              <div class="sidebar-chat-messages" ref="chatContainer">
                <div v-if="messages.length === 0" class="empty-chat">
                  <div class="empty-icon">
                    <img src="@/assets/images/logo/ic-AI.svg" alt="AI" class="ai-icon">
                  </div>
                  <p class="empty-text">你好同学，若有任何疑问，欢迎随时与我沟通</p>
                </div>
                <div v-else class="message-list">
                  <div v-for="(msg, index) in messages" :key="index" class="message" :class="msg.type === 'user' ? 'user-msg' : 'ai-msg'">
                    <!-- AI消息：头像在左，气泡在右 -->
                    <template v-if="msg.type === 'ai'">
                      <div class="avatar ai-avatar">
                        <img src="@/assets/images/logo/ic-AI.svg" alt="AI" class="ai-avatar-img">
                      </div>
                      <div class="message-bubble">
                        <div class="message-content" v-html="msg.content"></div>
                      </div>
                    </template>
                    <!-- 用户消息：气泡在左，头像在右 -->
                    <template v-else>
                      <div class="message-bubble">
                        <div class="message-content" v-html="msg.content"></div>
                      </div>
                      <div class="avatar user-avatar"></div>
                    </template>
                  </div>
                </div>
              </div>
            </div>
            <!-- 历史对话内容 -->
            <div v-else-if="activeSidebarTab === 'history'" class="sidebar-panel">
              <div v-if="!showHistoryDetail" class="history-list">
                <div v-for="item in historyList" :key="item.id" class="history-item" @click="openHistoryDetail(item)">
                  <div class="history-icon">
                    <img src="@/assets/images/action/ic_chat.svg" alt="聊天">
                  </div>
                  <div class="history-info">
                    <span class="history-title">{{ item.title }}</span>
                  </div>
                </div>
              </div>
              <!-- 历史对话详情 -->
              <div v-else class="history-detail">
                <div class="chat-actions detail-actions">
                  <button class="action-icon-btn" @click="closeHistoryDetail" title="返回">
                    <img src="@/assets/images/action/ic-arrow_left2.svg" alt="返回">
                  </button>
                  <div class="detail-title-wrapper">
                    <h3 class="detail-title">{{ selectedHistory?.title }}</h3>
                  </div>
                  <button class="action-icon-btn" @click="openSettings" title="设置">
                    <img src="@/assets/images/action/ic-set.svg" alt="设置">
                  </button>
                </div>
                <div class="detail-messages" ref="detailChatContainer">
                  <div v-for="(msg, index) in historyMessages" :key="index" class="message" :class="msg.type === 'user' ? 'user-msg' : 'ai-msg'">
                    <!-- AI消息：头像在左，气泡在右 -->
                    <template v-if="msg.type === 'ai'">
                      <div class="avatar ai-avatar">
                        <img src="@/assets/images/logo/ic-AI.svg" alt="AI" class="ai-avatar-img">
                      </div>
                      <div class="message-bubble">
                        <div class="message-content" v-html="msg.content"></div>
                      </div>
                    </template>
                    <!-- 用户消息：气泡在左，头像在右 -->
                    <template v-else>
                      <div class="message-bubble">
                        <div class="message-content" v-html="msg.content"></div>
                      </div>
                      <div class="avatar user-avatar"></div>
                    </template>
                  </div>
                </div>
              </div>
            </div>
            <!-- 思维导图内容 -->
            <div v-else-if="activeSidebarTab === 'mindmap'" class="sidebar-panel">
              <div class="mindmap-placeholder">思维导图区域</div>
            </div>
            <!-- 课程概要内容 -->
            <div v-else-if="activeSidebarTab === 'summary'" class="sidebar-panel">
              <div class="summary-content">
                <h3 class="summary-title">课程概要：</h3>
                <div class="summary-section">
                  <h4>方法 2：</h4>
                  <p>用「Frame + 遮罩」实现通用裁剪（适合所有图层）</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 底部提问框 -->
          <div class="sidebar-input-area">
            <div class="input-wrapper">
              <input
                type="text"
                v-model="inputMessage"
                :placeholder="inputPlaceholder"
                @keyup.enter="sendMessage"
              />
              <button
                class="voice-btn"
                :class="{ active: isRecording }"
                @click="toggleRecording"
              >
                <img v-if="!isRecording" src="@/assets/images/action/ic_mic_off.svg" alt="语音" class="voice-icon">
                <img v-else src="@/assets/images/action/ic_mic_active.svg" alt="录音中" class="voice-icon">
                <div v-if="isRecording" class="voice-waves">
                  <span class="wave"></span>
                  <span class="wave"></span>
                  <span class="wave"></span>
                </div>
              </button>
              <button
                class="send-btn"
                @click="sendMessage"
                :disabled="!inputMessage.trim()"
              >
                <img src="@/assets/images/action/ic-arrow-up.svg" alt="发送" class="send-icon">
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部区域 -->
    <div class="fullscreen-footer">
      <!-- 教案字幕区 -->
      <div v-if="showSubtitle" class="subtitle-area">
        <div class="subtitle-content">
          选中目标图层，在左侧 Layers 面板里，选中你要处理的图标。用「Frame + 遮罩」实现通用裁剪（适合所有图层）。
        </div>
      </div>

      <!-- 播放控制区 -->
      <div class="fullscreen-controls">
        <div class="controls-left">
          <button class="control-btn play-pause" @click="togglePlay">
            <img v-if="!isPlaying" src="@/assets/images/action/ic_play.svg" alt="播放">
            <img v-else src="@/assets/images/action/ic-pause.svg" alt="暂停">
          </button>
          <div class="progress-container">
            <div class="progress-bar" 
                 @click="seekVideo" 
                 @mousedown="startDrag"
                 :class="{ 'dragging': isDragging }">
              <div class="progress-filled" :style="{ width: progressPercent + '%' }"></div>
              <div class="progress-handle" 
                   :style="{ left: progressPercent + '%' }"
                   :class="{ 'active': isDragging }"></div>
            </div>
          </div>
          <span class="time-display">{{ currentPage }}/{{ totalPages }}</span>
        </div>
        
        <div class="controls-right">
          <!-- 字幕切换按钮 -->
          <button class="control-btn subtitle-btn" @click="toggleSubtitle">
            <img v-if="showSubtitle" src="@/assets/images/action/ic-subtitle.svg" alt="字幕开">
            <img v-else src="@/assets/images/action/IC-NOsubtitle.svg" alt="字幕关">
          </button>
          
          <!-- 播放速度 -->
          <button class="control-btn speed-btn" @click="cyclePlaybackSpeed">
            {{ playbackSpeed }}x
          </button>
          
          <!-- 音量 -->
          <button class="control-btn volume" @click="toggleMute">
            <img v-if="!isMuted" src="@/assets/images/action/ic_volume_on.svg" alt="音量">
            <img v-else src="@/assets/images/action/ic_volume_off.svg" alt="静音">
          </button>
          
          <!-- 退出全屏 -->
          <button class="control-btn exit-fullscreen" @click="toggleFullscreen">
            <img src="@/assets/images/action/ic-Exit Fullscreen.svg" alt="退出全屏">
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { useUserStore } from '@/stores/userStore'

// 用户信息 store
const userStore = useUserStore()

// 用户名
const userName = computed(() => userStore.userName)

// Tab配置
const tabs = [
  { id: 'ai-assistant', name: 'AI助手' },
  { id: 'history', name: '历史对话' },
  { id: 'mindmap', name: '思维导图' },
  { id: 'summary', name: '课程概要' }
]
const activeTab = ref('ai-assistant')

// 视频相关
const isPlaying = ref(false)
const isMuted = ref(false)
const currentTime = ref(25)
const duration = ref(6000)
const progressPercent = ref(0.42)
const playbackSpeed = ref(1)
const showSpeedMenu = ref(false)
const isDragging = ref(false)

// 页面数量
const currentPage = ref(1)
const totalPages = ref(10)

// 全屏模式
const isFullscreen = ref(false)

// 全新全屏界面状态
const isSidebarExpanded = ref(false)
const activeSidebarTab = ref('ai-assistant')
const showSubtitle = ref(true)
const pptScale = ref(1)

// 侧边栏宽度和拖动相关
const sidebarWidth = ref(60)
const FIXED_SIDEBAR_WIDTH = 320

// 侧边栏Tab配置
const sidebarTabs = [
  { id: 'ai-assistant', name: 'AI助手' },
  { id: 'history', name: '历史对话' },
  { id: 'mindmap', name: '思维导图' },
  { id: 'summary', name: '课程概要' }
]

// 切换侧边栏
const toggleSidebar = () => {
  isSidebarExpanded.value = !isSidebarExpanded.value
  if (isSidebarExpanded.value) {
    // 展开时固定宽度为320px
    sidebarWidth.value = FIXED_SIDEBAR_WIDTH
  } else {
    // 收起时设置为60px
    sidebarWidth.value = 60
  }
}

// 切换侧边栏Tab
const switchSidebarTab = (tabId) => {
  // 如果切换到非历史对话Tab，并且当前在查看历史对话详情，则关闭
  if (tabId !== 'history' && showHistoryDetail.value) {
    closeHistoryDetail()
  }
  activeSidebarTab.value = tabId
}

// 切换字幕显示
const toggleSubtitle = () => {
  showSubtitle.value = !showSubtitle.value
}

// 上一页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    progressPercent.value = (currentPage.value - 1) / (totalPages.value - 1) * 100
  }
}

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    progressPercent.value = (currentPage.value - 1) / (totalPages.value - 1) * 100
  }
}

// 缩放控制
const zoomIn = () => {
  if (pptScale.value < 2) {
    pptScale.value += 0.1
  }
}

const zoomOut = () => {
  if (pptScale.value > 0.5) {
    pptScale.value -= 0.1
  }
}

// 聊天相关
const inputMessage = ref('')
const messages = ref([])
const chatContainer = ref(null)
const isRecording = ref(false)
const currentConversationId = ref(null)

// 动态输入框placeholder
const inputPlaceholder = computed(() => {
  if (showHistoryDetail.value && selectedHistory.value) {
    return `继续对话：${selectedHistory.value.title}`
  }
  return '请输入你的问题'
})

// 历史对话
const showHistoryDetail = ref(false)
const selectedHistory = ref(null)
const historyMessages = ref([])
const detailChatContainer = ref(null)

// LocalStorage keys
const STORAGE_KEY = 'ai_ppt_history_conversations'

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 从localStorage加载历史对话
const loadHistoryFromStorage = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      return Array.isArray(parsed) ? parsed : []
    }
  } catch (e) {
    console.error('Failed to load history from storage:', e)
  }
  return [
    { id: generateId(), title: '如何选中目标？', messages: [
      { type: 'user', content: '如何选中目标？', timestamp: Date.now() - 86400000 },
      { type: 'ai', content: '选中目标图层，在左侧 Layers 面板里，选中你要处理的图标（比如图中的 Volume 2 或 mic 图层）。', timestamp: Date.now() - 86400000 + 1000 }
    ], createdAt: Date.now() - 86400000, updatedAt: Date.now() - 86400000 },
    { id: generateId(), title: '如何使用蒙版？', messages: [
      { type: 'user', content: '如何使用蒙版？', timestamp: Date.now() - 172800000 },
      { type: 'ai', content: '用「Frame + 遮罩」实现通用裁剪（适合所有图层）：选中要裁剪的图层，右键菜单里选择「Use as mask」（快捷键 Ctrl+Alt+M），或者先给它套一个 Frame（Ctrl+Alt+G）。', timestamp: Date.now() - 172800000 + 1000 }
    ], createdAt: Date.now() - 172800000, updatedAt: Date.now() - 172800000 }
  ]
}

const historyList = ref(loadHistoryFromStorage())

// 保存历史对话到localStorage
const saveHistoryToStorage = () => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(historyList.value))
  } catch (e) {
    console.error('Failed to save history to storage:', e)
  }
}

// 左右面板宽度
const leftWidth = ref(60)

// PPT播放器展开/收起状态
const isPptExpanded = ref(true)

// 切换PPT展开/收起状态
const togglePptExpand = () => {
  isPptExpanded.value = !isPptExpanded.value
}

// 教案展开/折叠状态
const isDocExpanded = ref(false)

// 切换教案展开/折叠状态
const toggleDocExpand = () => {
  isDocExpanded.value = !isDocExpanded.value
}

// 导出弹窗状态
const showExportDialog = ref(false)
const exportOptions = ref({
  mindmap: false,  // 思维导图（图片）
  aiLessonPlan: false,  // AI教案（word文档）
  courseSummary: false  // 课程概要（word文档）
})

// 设置弹窗状态
const showSettingsDialog = ref(false)
const settingsOptions = ref({
  model: 'chatGPT',
  python: true,
  webSearch: false,
  voice: '女声1'
})

// 打开导出弹窗
const openExportDialog = () => {
  // 重置选项
  exportOptions.value = {
    mindmap: false,
    aiLessonPlan: false,
    courseSummary: false
  }
  showExportDialog.value = true
}

// 关闭导出弹窗
const closeExportDialog = () => {
  showExportDialog.value = false
}

// 确认导出
const confirmExport = () => {
  // 检查是否有选择的选项
  const selectedOptions = Object.entries(exportOptions.value)
    .filter(([_, value]) => value)
    .map(([key, _]) => key)
  
  if (selectedOptions.length === 0) {
    alert('请至少选择一个导出选项')
    return
  }
  
  // 模拟导出过程
  console.log('开始导出:', selectedOptions)
  
  // 显示导出成功提示
  alert('导出成功！文件正在生成中，稍后将自动下载。')
  
  // 关闭弹窗
  closeExportDialog()
}

// 关闭设置弹窗
const closeSettingsDialog = () => {
  showSettingsDialog.value = false
}

// 确认设置
const confirmSettings = () => {
  // 保存设置
  console.log('保存设置:', settingsOptions.value)

  // 关闭弹窗
  closeSettingsDialog()
}

// 处理头像点击
const handleAvatarClick = () => {
  // 这里可以添加头像点击的处理逻辑
  console.log('Avatar clicked')
}
const rightWidth = computed(() => 100 - leftWidth.value)
const isResizing = ref(false)

// 播放/暂停
const togglePlay = () => {
  isPlaying.value = !isPlaying.value
}

// 静音切换
const toggleMute = () => {
  isMuted.value = !isMuted.value
}

// 拖动进度
const seekVideo = (event) => {
  if (!event) return
  
  const progressBar = event.currentTarget
  const rect = progressBar.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const progressPercentage = clickX / rect.width
  
  // 计算新的页码
  const newPage = Math.max(1, Math.min(totalPages.value, Math.ceil(progressPercentage * totalPages.value)))
  
  if (newPage !== currentPage.value) {
    currentPage.value = newPage
    // 更新进度百分比
    progressPercent.value = (newPage - 1) / (totalPages.value - 1) * 100
  }
}

// 开始拖动
const startDrag = (event) => {
  event.preventDefault()
  isDragging.value = true
  document.addEventListener('mousemove', dragProgress)
  document.addEventListener('mouseup', stopDrag)
  // 触发一次拖动事件，处理初始点击位置
  dragProgress(event)
}

// 拖动中
const dragProgress = (event) => {
  if (!isDragging.value) return
  
  // 找到触发拖动的进度条元素
  const progressBar = document.querySelector('.progress-bar.dragging')
  if (!progressBar) return
  
  const rect = progressBar.getBoundingClientRect()
  let clientX = event.clientX
  
  // 限制在进度条范围内
  clientX = Math.max(rect.left, Math.min(rect.right, clientX))
  
  const clickX = clientX - rect.left
  const progressPercentage = clickX / rect.width
  
  // 计算新的页码
  const newPage = Math.max(1, Math.min(totalPages.value, Math.ceil(progressPercentage * totalPages.value)))
  
  if (newPage !== currentPage.value) {
    currentPage.value = newPage
    // 更新进度百分比
    progressPercent.value = (newPage - 1) / (totalPages.value - 1) * 100
  }
}

// 停止拖动
const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', dragProgress)
  document.removeEventListener('mouseup', stopDrag)
}

// 设置播放速度
const setPlaybackSpeed = (speed) => {
  playbackSpeed.value = speed
  showSpeedMenu.value = false
}

// 循环切换播放速度
const cyclePlaybackSpeed = () => {
  const speeds = [1, 1.5, 2]
  const currentIndex = speeds.indexOf(playbackSpeed.value)
  const nextIndex = (currentIndex + 1) % speeds.length
  playbackSpeed.value = speeds[nextIndex]
}

// 全屏
const toggleFullscreen = () => {
  // 切换自定义全屏界面
  isFullscreen.value = !isFullscreen.value
  
  // 如果退出全屏，尝试退出原生全屏
  if (!isFullscreen.value) {
    if (document.exitFullscreen) {
      document.exitFullscreen().catch(() => {})
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen()
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen()
    }
  }
}

// 监听全屏状态变化（保留用于处理ESC键）
const handleFullscreenChange = () => {
  const isFull = document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement
  // 如果原生全屏退出，也退出自定义全屏
  if (!isFull && isFullscreen.value) {
    isFullscreen.value = false
  }
}

// 格式化时间
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 发送消息
// 保存当前对话到历史
const saveCurrentConversation = () => {
  if (messages.value.length === 0) return
  
  const title = messages.value[0]?.content?.substring(0, 30) || '新对话'
  
  if (currentConversationId.value) {
    // 更新现有对话
    const existingIndex = historyList.value.findIndex(h => h.id === currentConversationId.value)
    if (existingIndex !== -1) {
      historyList.value[existingIndex].messages = [...messages.value]
      historyList.value[existingIndex].updatedAt = Date.now()
      // 移动到最前面
      const [updated] = historyList.value.splice(existingIndex, 1)
      historyList.value.unshift(updated)
    }
  } else {
    // 创建新对话
    const newConversation = {
      id: generateId(),
      title: title,
      messages: [...messages.value],
      createdAt: Date.now(),
      updatedAt: Date.now()
    }
    historyList.value.unshift(newConversation)
    currentConversationId.value = newConversation.id
  }
  
  saveHistoryToStorage()
}

const sendMessage = () => {
  if (!inputMessage.value.trim()) return
  
  // 如果正在查看历史对话，则发送到历史对话
  if (showHistoryDetail.value && selectedHistory.value) {
    sendToHistoryMessage()
    return
  }

  const userQuestion = inputMessage.value.trim()
  
  messages.value.push({
    type: 'user',
    content: userQuestion,
    timestamp: Date.now()
  })

  inputMessage.value = ''

  setTimeout(() => {
    const aiResponse = {
      type: 'ai',
      content: `选中目标图层，在左侧 Layers 面板里，选中你要处理的图标（比如图中的 Volume 2 或 mic 图层）。<br><br>扁平化 / 轮廓化：<br>• 如果是文字 / 形状组合，先右键 → Flatten（扁平化），把组合变成单一形状。<br>• 如果要描边线条，选中线条 → 右侧面板 Stroke → 点击 Outline stroke（轮廓化描边），把线条变成可编辑的填充形状。<br><br>布尔运算合并：<br>• 选中所有组成图标的形状图层 → 顶部工具栏选择 Union selection（合并），把多个形状合并成一个大路径。<br>• 如果有镂空部分，用 Subtract selection（减去）来实现。`,
      timestamp: Date.now()
    }
    messages.value.push(aiResponse)
    scrollToBottom()
    
    // 自动保存对话
    saveCurrentConversation()
  }, 1000)
}

// 发送消息到历史对话
const sendToHistoryMessage = () => {
  if (!inputMessage.value.trim() || !selectedHistory.value) return
  
  const userQuestion = inputMessage.value.trim()
  
  // 添加用户消息到历史对话
  historyMessages.value.push({
    type: 'user',
    content: userQuestion,
    timestamp: Date.now()
  })
  
  inputMessage.value = ''
  
  // 滚动到底部
  nextTick(() => {
    if (detailChatContainer.value) {
      detailChatContainer.value.scrollTop = detailChatContainer.value.scrollHeight
    }
  })
  
  // 模拟AI回复
  setTimeout(() => {
    const aiResponse = {
      type: 'ai',
      content: '这是对您问题的回复。这个功能正在完善中，感谢您的使用！',
      timestamp: Date.now()
    }
    historyMessages.value.push(aiResponse)
    
    // 更新历史对话
    const historyIndex = historyList.value.findIndex(h => h.id === selectedHistory.value.id)
    if (historyIndex !== -1) {
      historyList.value[historyIndex].messages = [...historyMessages.value]
      historyList.value[historyIndex].updatedAt = Date.now()
      saveHistoryToStorage()
    }
    
    // 滚动到底部
    nextTick(() => {
      if (detailChatContainer.value) {
        detailChatContainer.value.scrollTop = detailChatContainer.value.scrollHeight
      }
    })
  }, 1000)
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// 格式化消息内容
const formatMessage = (content) => {
  return content.replace(/\n/g, '<br>')
}

// 格式化历史对话时间
const formatHistoryTime = (timestamp) => {
  if (!timestamp) return ''
  
  const now = Date.now()
  const diff = now - timestamp
  
  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 小于1小时
  if (diff < 3600000) {
    const mins = Math.floor(diff / 60000)
    return `${mins}分钟前`
  }
  
  // 小于24小时
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }
  
  // 小于7天
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days}天前`
  }
  
  // 显示具体日期
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  
  return `${year}-${month}-${day}`
}

// 语音输入
const startRecording = () => {
  isRecording.value = true
}

const stopRecording = () => {
  if (isRecording.value) {
    isRecording.value = false
    inputMessage.value = '语音输入的内容...'
  }
}

// 切换录音状态
const toggleRecording = () => {
  if (isRecording.value) {
    // 停止录音
    isRecording.value = false
    inputMessage.value = '语音输入的内容...'
  } else {
    // 开始录音
    isRecording.value = true
  }
}

// 开启新对话
const startNewChat = () => {
  // 保存当前对话（如果有内容）
  if (messages.value.length > 0) {
    saveCurrentConversation()
  }
  
  // 清空当前对话
  messages.value = []
  currentConversationId.value = null
  inputMessage.value = ''
}

// 打开设置
const openSettings = () => {
  showSettingsDialog.value = true
}

// 打开历史对话详情
const openHistoryDetail = (item) => {
  selectedHistory.value = item
  historyMessages.value = item.messages || []
  showHistoryDetail.value = true
  // 滚动到底部
  nextTick(() => {
    if (detailChatContainer.value) {
      detailChatContainer.value.scrollTop = detailChatContainer.value.scrollHeight
    }
  })
}

// 关闭历史对话详情
const closeHistoryDetail = () => {
  showHistoryDetail.value = false
  selectedHistory.value = null
  historyMessages.value = []
}

// 切换Tab
const switchTab = (tabId) => {
  // 如果切换到非历史对话Tab，并且当前在查看历史对话详情，则关闭
  if (tabId !== 'history' && showHistoryDetail.value) {
    closeHistoryDetail()
  }
  activeTab.value = tabId
}

// 返回
const handleBack = () => {
  window.history.back()
}

// 开始调整大小（鼠标）
const startResize = (e) => {
  e.preventDefault()
  e.stopPropagation()
  isResizing.value = true
  document.addEventListener('mousemove', resize)
  document.addEventListener('mouseup', stopResize)
}

// 开始调整大小（触摸）
const startResizeTouch = (e) => {
  e.preventDefault()
  e.stopPropagation()
  isResizing.value = true
  document.addEventListener('touchmove', resizeTouch)
  document.addEventListener('touchend', stopResizeTouch)
}

// 调整大小（鼠标）
const resize = (e) => {
  if (!isResizing.value) return
  e.preventDefault()
  e.stopPropagation()
  
  const container = document.querySelector('.main-container')
  const rect = container.getBoundingClientRect()
  let newLeftWidth = ((e.clientX - rect.left) / rect.width) * 100
  
  // 设置最小和最大宽度
  newLeftWidth = Math.max(40, Math.min(70, newLeftWidth))
  leftWidth.value = newLeftWidth
}

// 调整大小（触摸）
const resizeTouch = (e) => {
  if (!isResizing.value || e.touches.length === 0) return
  e.preventDefault()
  e.stopPropagation()
  
  const container = document.querySelector('.main-container')
  const rect = container.getBoundingClientRect()
  let newLeftWidth = ((e.touches[0].clientX - rect.left) / rect.width) * 100
  
  // 设置最小和最大宽度
  newLeftWidth = Math.max(40, Math.min(70, newLeftWidth))
  leftWidth.value = newLeftWidth
}

// 停止调整大小（鼠标）
const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
}

// 停止调整大小（触摸）
const stopResizeTouch = () => {
  isResizing.value = false
  document.removeEventListener('touchmove', resizeTouch)
  document.removeEventListener('touchend', stopResizeTouch)
}

// 监听消息变化，自动滚动
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

onMounted(() => {
  // 加载用户信息
  userStore.loadUserInfo()
  
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('msfullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('msfullscreenchange', handleFullscreenChange)
})
</script>

<style scoped>
/* 页面容器 */
.ppt-teach-page {
  height: 100vh;
  width: 100%;
  background: #FFF9F3;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* 主内容区 */
.main-container {
  flex: 1;
  display: flex;
  padding: 88px 24px 24px;
  overflow: hidden;
  height: calc(100vh - 72px);
  box-sizing: border-box;
}

/* 顶部栏 */
.header {
  height: 72px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.back-button {
  width: 48px;
  height: 48px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.2s;
}

.back-button:hover {
  background: rgba(241, 139, 91, 0.1);
}

.back-button:hover .back-icon {
  filter: none;
  opacity: 1;
}

.back-icon {
  width: 24px;
  height: 24px;
  filter: grayscale(100%) brightness(0.5);
  opacity: 0.7;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #F18B5B, #C96030);
}

.username {
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

/* 左侧：核心学习区 */
.left-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
  height: 100%;
  overflow-y: auto;
  /* 隐藏滚动条 - Firefox */
  scrollbar-width: none;
  /* 隐藏滚动条 - IE/Edge */
  -ms-overflow-style: none;
}

/* 隐藏滚动条 - Chrome/Safari/Edge */
.left-section::-webkit-scrollbar {
  display: none;
}

/* 右侧：AI助手交互区 */
.right-section {
  background: #FFFFFF;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
  height: 100%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 中间调整滑块 */
.resizer {
  width: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: col-resize;
  position: relative;
  flex-shrink: 0;
  z-index: 10;
}

.resizer-track {
  width: 2px;
  height: 100%;
  background: rgba(201, 96, 48, 0.2);
  border-radius: 1px;
  transition: background 0.2s;
}

.resizer:hover .resizer-track {
  background: rgba(241, 139, 91, 0.4);
}

.resizer-handle {
  position: absolute;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #FFFFFF;
  box-shadow: 0 2px 8px rgba(201, 96, 48, 0.3);
  transition: all 0.2s;
}

.resizer:hover .resizer-handle,
.resizer.dragging .resizer-handle {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(201, 96, 48, 0.4);
}

.resizer-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #F18B5B;
}

.resize-indicator {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: #F18B5B;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(241, 139, 91, 0.3);
  z-index: 20;
  left: 40px;
}

/* 橙色边框容器 */
.ppt-orange-container {
  border: 2px solid #FFA500;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
}

/* PPT播放器 */
.ppt-player-wrapper {
  background: white;
  display: flex;
  flex-direction: column;
}

/* PPT标题栏 - 橙色 */
.ppt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.ppt-title {
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
}

.ppt-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-btn {
  padding: 10px 18px;
  border: none;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #F18B5B;
  border-radius: 24px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.action-btn:hover {
  background: #FFF5F0;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(241, 139, 91, 0.15);
}

.action-btn.select-element {
  /* 保持默认样式 */
}

.action-btn.icon-btn {
  padding: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn.icon-btn img {
  width: 18px;
  height: 18px;
  filter: invert(55%) sepia(65%) saturate(532%) hue-rotate(333deg) brightness(98%) contrast(90%);
}

.action-btn.icon-btn img.rotate-180 {
  transform: rotate(180deg);
}

.arrow-down {
  transform: rotate(180deg);
}

/* 更多按钮 - 透明背景 */
.action-btn.icon-btn.more-btn {
  background: transparent;
  padding: 4px;
}

.action-btn.icon-btn.more-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.action-btn.icon-btn.more-btn img {
  width: 24px;
  height: 24px;
  filter: brightness(0) invert(1);
  opacity: 0.9;
}

.ppt-content {
  background: #000;
  position: relative;
  flex-shrink: 0;
}

.ppt-image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
}

.ppt-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.play-icon {
  width: 60px;
  height: 60px;
  opacity: 0.9;
  filter: grayscale(100%) brightness(0.5);
}

/* 视频控制栏 */
.video-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: #FFF9F3;
}

.control-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 6px;
  transition: all 0.2s;
  position: relative;
}

.control-btn:hover {
  background: rgba(241, 139, 91, 0.1);
}

.control-btn:hover img {
  filter: none;
  opacity: 1;
}

.control-btn img {
  width: 18px;
  height: 18px;
  object-fit: contain;
  filter: grayscale(100%) brightness(0.5);
  opacity: 0.7;
}

/* 播放图标稍微缩小 */
.control-btn.play-pause img[src*="ic_play"] {
  width: 16px;
  height: 16px;
}

/* 全屏图标稍微缩小 */
.control-btn.fullscreen img[src*="ic-fullscreen"] {
  width: 16px;
  height: 16px;
}

.progress-container {
  flex: 1;
  height: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(201, 96, 48, 0.2);
  border-radius: 2px;
  overflow: visible;
  position: relative;
  cursor: pointer;
  transition: height 0.2s ease;
}

.progress-bar:hover {
  height: 6px;
}

.progress-bar.dragging {
  height: 6px;
}

.progress-filled {
  height: 100%;
  background: linear-gradient(90deg, #F18B5B, #FF9E5F);
  border-radius: 2px;
  transition: width 0.15s ease-out;
}

.progress-bar:hover .progress-filled,
.progress-bar.dragging .progress-filled {
  border-radius: 3px;
}

.progress-handle {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: #F18B5B;
  border-radius: 50%;
  cursor: grab;
  opacity: 0;
  transition: opacity 0.2s ease, transform 0.2s ease, width 0.2s ease, height 0.2s ease;
  box-shadow: 0 2px 8px rgba(241, 139, 91, 0.4);
  z-index: 10;
}

.progress-bar:hover .progress-handle,
.progress-handle.active {
  opacity: 1;
}

.progress-handle.active {
  cursor: grabbing;
  width: 16px;
  height: 16px;
  box-shadow: 0 4px 12px rgba(241, 139, 91, 0.6);
}

.progress-bar:hover .progress-handle {
  transform: translate(-50%, -50%) scale(1.1);
}

.time-display {
  font-size: 14px;
  color: #666;
}

.speed-btn {
  padding: 4px 8px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  position: relative;
}

.speed-menu {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  margin-bottom: 8px;
  min-width: 80px;
  z-index: 100;
}

.speed-option {
  padding: 8px 16px;
  text-align: center;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.speed-option:hover {
  background: #FFF5E7;
  color: #C96030;
}

.speed-option.active {
  color: #F18B5B;
  font-weight: 500;
}

/* 课程文档包装器 */
.course-document-wrapper {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
}

/* 课程文档 */
.course-document {
  padding: 24px;
  transition: max-height 0.3s ease;
  overflow: hidden;
  max-height: 1000px; /* 足够大的高度 */
}

/* 课程文档折叠状态 */
.course-document.collapsed {
  max-height: 120px; /* 折叠到适当长度，只显示标题和部分内容 */
}

/* 展开/折叠控制 */
.doc-expand-control {
  text-align: center;
  padding: 16px;
  border-top: 1px solid rgba(201, 96, 48, 0.1);
  background: #FFF9F3;
}

/* 展开/折叠按钮 */
.doc-expand-btn {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}/* 展开/折叠按钮 */
.doc-expand-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(241, 139, 91, 0.3);
}

.doc-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(201, 96, 48, 0.1);
}

.doc-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.doc-title {
  font-size: 16px;
  font-weight: 600;
  color: #C96030;
  margin: 0 0 8px 0;
}

.doc-subtitle {
  font-size: 14px;
  color: #C96030;
  margin: 0 0 12px 0;
  font-weight: 500;
}

.doc-list {
  margin: 0;
  padding-left: 24px;
  color: #333;
  font-size: 14px;
  line-height: 1.8;
}

.doc-list li {
  margin-bottom: 8px;
}

.highlight {
  color: #F18B5B;
  font-weight: 600;
  background: rgba(241, 139, 91, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

/* 展开教室 */
.expand-classroom {
  display: flex;
  justify-content: center;
  flex-shrink: 0;
  padding-bottom: 8px;
}

.expand-btn {
  padding: 8px 24px;
  border: none;
  background: transparent;
  color: #C96030;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
  transition: all 0.2s;
}

.expand-btn:hover {
  color: #F18B5B;
}

/* Tab标签页 */
.tab-header {
  display: flex;
  background: #FFFFFF;
  padding: 0;
  gap: 0;
  flex-shrink: 0;
  border-bottom: 2px solid rgba(201, 96, 48, 0.15);
}

.tab-btn {
  flex: 1;
  padding: 16px 8px;
  border: none;
  background: transparent;
  color: #999;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  white-space: nowrap;
  position: relative;
}

.tab-btn:hover {
  color: #F18B5B;
}

.tab-btn.active {
  color: #C96030;
  font-weight: 600;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #F18B5B, #FF9E5F);
  border-radius: 2px;
}

/* Tab内容区 */
.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #FFFFFF;
  min-height: 0;
}

.tab-content::-webkit-scrollbar {
  width: 6px;
}

.tab-content::-webkit-scrollbar-track {
  background: transparent;
}

.tab-content::-webkit-scrollbar-thumb {
  background: rgba(201, 96, 48, 0.2);
  border-radius: 3px;
}

/* AI助手面板 */
.ai-chat-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 功能按钮区 */
.chat-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(201, 96, 48, 0.15);
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
  background: rgba(241, 139, 91, 0.1);
}

.action-icon-btn:hover img {
  filter: brightness(0) saturate(100%) invert(54%) sepia(22%) saturate(1764%) hue-rotate(328deg) brightness(99%) contrast(93%);
  opacity: 1;
}

.action-icon-btn img {
  width: 22px;
  height: 22px;
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
  color: #C96030;
  text-align: center;
  opacity: 0.8;
}

/* 消息气泡 */
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

.message.user-msg {
  flex-direction: row;
  justify-content: flex-end;
}

.message .avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message .ai-avatar {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-avatar-img {
  width: 24px;
  height: 24px;
}

.message .user-avatar {
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
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  color: white;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 16px rgba(241, 139, 91, 0.3);
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
  border-left: 8px solid #F18B5B;
}

.message-content {
  word-break: break-word;
}

.message-content br {
  content: '';
  display: block;
  margin-top: 8px;
}

/* 历史对话面板 */
.history-panel {
  height: 100%;
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

.history-icon {
  width: 32px;
  height: 32px;
  background: rgba(241, 139, 91, 0.1);
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

/* 历史对话详情 */
.history-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 功能按钮区 - 详情页 */
.detail-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(201, 96, 48, 0.15);
}

.detail-title-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: #C96030;
  margin: 0;
  text-align: center;
}

.detail-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-messages::-webkit-scrollbar {
  width: 6px;
}

.detail-messages::-webkit-scrollbar-track {
  background: transparent;
}

.detail-messages::-webkit-scrollbar-thumb {
  background: rgba(201, 96, 48, 0.2);
  border-radius: 3px;
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

/* 思维导图面板 */
.mindmap-panel {
  height: 100%;
}

.mindmap-container {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 12px;
}

/* 课程概要面板 */
.summary-panel {
  height: 100%;
}

.summary-content {
  background: white;
  border-radius: 12px;
  padding: 20px;
}

.summary-title {
  font-size: 16px;
  font-weight: 600;
  color: #C96030;
  margin: 0 0 16px 0;
}

.summary-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(201, 96, 48, 0.1);
}

.summary-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.summary-section h4 {
  font-size: 15px;
  font-weight: 600;
  color: #C96030;
  margin: 0 0 8px 0;
}

.summary-section p {
  font-size: 14px;
  color: #C96030;
  margin: 0 0 12px 0;
  font-weight: 500;
}

.summary-section ol {
  margin: 0;
  padding-left: 24px;
  color: #333;
  font-size: 14px;
  line-height: 1.8;
}

.summary-section li {
  margin-bottom: 8px;
}

/* 底部输入区 */
.chat-input-area {
  padding: 16px;
  background: #FFFFFF;
  flex-shrink: 0;
  border-top: 1px solid rgba(201, 96, 48, 0.1);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border-radius: 50px;
  padding: 8px 8px 8px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.input-wrapper input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #333;
  outline: none;
  padding: 8px 0;
}

.input-wrapper input::placeholder {
  color: #999;
}

.voice-btn {
  width: 44px;
  height: 44px;
  border: 2px solid transparent;
  background: rgba(241, 139, 91, 0.1);
  color: #F18B5B;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: visible;
}

.voice-btn:hover {
  background: rgba(241, 139, 91, 0.2);
  transform: scale(1.05);
}

.voice-btn .voice-icon {
  width: 28px;
  height: 28px;
  z-index: 2;
  transition: all 0.3s;
}

.voice-btn.active {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  border-color: #F18B5B;
  box-shadow: 0 4px 15px rgba(241, 139, 91, 0.4);
  animation: pulse 2s infinite;
}

.voice-btn.active:hover {
  transform: scale(1.1);
}

/* 声波动画 */
.voice-waves {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 3px;
  z-index: 1;
}

.wave {
  width: 4px;
  height: 20px;
  background: white;
  border-radius: 2px;
  animation: wave 1.2s ease-in-out infinite;
}

.wave:nth-child(1) {
  animation-delay: 0s;
}

.wave:nth-child(2) {
  animation-delay: 0.15s;
}

.wave:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes wave {
  0%, 100% {
    height: 8px;
    opacity: 0.7;
  }
  50% {
    height: 24px;
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(241, 139, 91, 0.4);
  }
  50% {
    box-shadow: 0 0 0 12px rgba(241, 139, 91, 0);
  }
}

.send-btn {
  padding: 10px 20px;
  border: none;
  background: #F18B5B;
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #C96030;
  transform: translateY(-1px);
}

.send-btn:disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
}

/* 历史对话详情 - 调整布局 */
.history-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-actions {
  flex-shrink: 0;
}

.detail-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px 0;
  min-height: 0;
}

/* 资料导出弹窗 */
.export-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.export-dialog {
  background: white;
  border-radius: 16px;
  width: 400px;
  max-width: 90vw;
  overflow: hidden;
  animation: slideIn 0.3s ease;
}

.export-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(201, 96, 48, 0.1);
  background: #FFF9F3;
}

.export-dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #C96030;
  margin: 0;
}

.export-dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.export-dialog-close:hover {
  background: rgba(201, 96, 48, 0.1);
  color: #C96030;
}

.export-dialog-content {
  padding: 24px;
}

.export-option {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.export-option input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #F18B5B;
  cursor: pointer;
}

.export-option label {
  font-size: 14px;
  color: #333;
  cursor: pointer;
  flex: 1;
}

.export-dialog-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(201, 96, 48, 0.1);
  background: #FFF9F3;
  justify-content: flex-end;
}

.export-dialog-btn {
  padding: 8px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.cancel-btn {
  background: #F5F5F5;
  color: #666;
}

.cancel-btn:hover {
  background: #E0E0E0;
}

.confirm-btn {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  color: white;
}

.confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(241, 139, 91, 0.3);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 全屏模式样式 */
.ppt-orange-container:fullscreen,
.ppt-orange-container:-webkit-full-screen,
.ppt-orange-container:-ms-fullscreen {
  background: #000;
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
}

.ppt-orange-container:fullscreen .ppt-player-wrapper,
.ppt-orange-container:-webkit-full-screen .ppt-player-wrapper,
.ppt-orange-container:-ms-fullscreen .ppt-player-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #000;
}

.ppt-orange-container:fullscreen .ppt-header,
.ppt-orange-container:-webkit-full-screen .ppt-header,
.ppt-orange-container:-ms-fullscreen .ppt-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  padding: 12px 24px;
  transition: opacity 0.3s;
}

.ppt-orange-container:fullscreen .ppt-content,
.ppt-orange-container:-webkit-full-screen .ppt-content,
.ppt-orange-container:-ms-fullscreen .ppt-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  padding: 80px 40px;
}

.ppt-orange-container:fullscreen .ppt-image-wrapper,
.ppt-orange-container:-webkit-full-screen .ppt-image-wrapper,
.ppt-orange-container:-ms-fullscreen .ppt-image-wrapper {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.ppt-orange-container:fullscreen .ppt-image,
.ppt-orange-container:-webkit-full-screen .ppt-image,
.ppt-orange-container:-ms-fullscreen .ppt-image {
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: calc(100vh - 160px);
  object-fit: contain;
}

.ppt-orange-container:fullscreen .play-overlay,
.ppt-orange-container:-webkit-full-screen .play-overlay,
.ppt-orange-container:-ms-fullscreen .play-overlay {
  background: rgba(0, 0, 0, 0.3);
}

.ppt-orange-container:fullscreen .play-icon,
.ppt-orange-container:-webkit-full-screen .play-icon,
.ppt-orange-container:-ms-fullscreen .play-icon {
  width: 100px;
  height: 100px;
}

.ppt-orange-container:fullscreen .video-controls,
.ppt-orange-container:-webkit-full-screen .video-controls,
.ppt-orange-container:-ms-fullscreen .video-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  padding: 16px 32px;
  z-index: 100;
  transition: opacity 0.3s;
}

.ppt-orange-container:fullscreen .control-btn,
.ppt-orange-container:-webkit-full-screen .control-btn,
.ppt-orange-container:-ms-fullscreen .control-btn {
  color: #fff;
}

.ppt-orange-container:fullscreen .control-btn img,
.ppt-orange-container:-webkit-full-screen .control-btn img,
.ppt-orange-container:-ms-fullscreen .control-btn img {
  filter: brightness(0) invert(1);
  opacity: 1;
}

.ppt-orange-container:fullscreen .time-display,
.ppt-orange-container:-webkit-full-screen .time-display,
.ppt-orange-container:-ms-fullscreen .time-display {
  color: #fff;
  font-weight: 500;
}

.ppt-orange-container:fullscreen .progress-bar,
.ppt-orange-container:-webkit-full-screen .progress-bar,
.ppt-orange-container:-ms-fullscreen .progress-bar {
  background: rgba(255, 255, 255, 0.3);
}

.ppt-orange-container:fullscreen .progress-filled,
.ppt-orange-container:-webkit-full-screen .progress-filled,
.ppt-orange-container:-ms-fullscreen .progress-filled {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
}

.ppt-orange-container:fullscreen .speed-btn,
.ppt-orange-container:-webkit-full-screen .speed-btn,
.ppt-orange-container:-ms-fullscreen .speed-btn {
  color: #fff;
}

/* 全屏模式鼠标移动时显示控制栏 */
.ppt-orange-container:fullscreen:hover .ppt-header,
.ppt-orange-container:fullscreen:hover .video-controls,
.ppt-orange-container:-webkit-full-screen:hover .ppt-header,
.ppt-orange-container:-webkit-full-screen:hover .video-controls,
.ppt-orange-container:-ms-fullscreen:hover .ppt-header,
.ppt-orange-container:-ms-fullscreen:hover .video-controls {
  opacity: 1;
}

.ppt-orange-container:fullscreen .ppt-header,
.ppt-orange-container:fullscreen .video-controls,
.ppt-orange-container:-webkit-full-screen .ppt-header,
.ppt-orange-container:-webkit-full-screen .video-controls,
.ppt-orange-container:-ms-fullscreen .ppt-header,
.ppt-orange-container:-ms-fullscreen .video-controls {
  opacity: 0;
  transition: opacity 0.3s;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 设置弹窗样式 */
.settings-option {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.settings-label {
  font-size: 14px;
  color: #C96030;
  font-weight: 500;
  flex: 1;
}

.settings-select {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid rgba(201, 96, 48, 0.15);
  border-radius: 8px;
  background: white;
  font-size: 14px;
  color: #333;
  outline: none;
  transition: all 0.2s ease;
}

.settings-select:focus {
  border-color: #F18B5B;
  box-shadow: 0 0 0 4px rgba(241, 139, 91, 0.1);
}

.settings-checkbox {
  width: 18px;
  height: 18px;
  accent-color: #F18B5B;
  cursor: pointer;
}

/* 全新全屏界面样式 */
.fullscreen-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #FFF9F3;
  display: flex;
  flex-direction: column;
  z-index: 9999;
}

.fullscreen-header {
  height: 80px;
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 2px solid rgba(201, 96, 48, 0.1);
}

.fullscreen-title {
  font-size: 24px;
  font-weight: 700;
  color: #FFFFFF;
}

.fullscreen-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 右侧可伸缩功能栏 */
.right-sidebar {
  width: 60px;
  background: #FFFFFF;
  border-left: 1px solid rgba(201, 96, 48, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 100;
  transition: width 0.3s ease;
}

.right-sidebar.expanded {
  width: 320px;
}

.sidebar-toggle {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #FFFFFF;
  box-shadow: 0 2px 8px rgba(201, 96, 48, 0.3);
  transition: all 0.2s;
  z-index: 101;
  cursor: pointer;
}

.sidebar-toggle:hover {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(201, 96, 48, 0.4);
}

.sidebar-toggle:hover img {
  filter: brightness(0) invert(1);
}

.sidebar-toggle img {
  transition: all 0.2s;
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-tabs {
  display: flex;
  background: #FFF9F3;
  border-bottom: 2px solid rgba(201, 96, 48, 0.15);
}

.sidebar-tab {
  flex: 1;
  padding: 12px 8px;
  border: none;
  background: transparent;
  color: #999;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  white-space: nowrap;
  position: relative;
}

.sidebar-tab:hover {
  color: #F18B5B;
}

.sidebar-tab.active {
  color: #C96030;
  font-weight: 600;
}

.sidebar-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #F18B5B, #FF9E5F);
  border-radius: 2px;
}

.sidebar-tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.sidebar-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mindmap-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}

/* PPT展示区 */
.ppt-display-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 40px 80px;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border: none;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(201, 96, 48, 0.2);
  transition: all 0.2s ease;
  opacity: 0;
  z-index: 50;
}

.ppt-display-area:hover .nav-btn {
  opacity: 1;
}

.nav-btn:hover {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(201, 96, 48, 0.3);
}

.nav-btn:hover img {
  filter: brightness(0) invert(1);
}

.nav-btn:active {
  transform: translateY(-50%) scale(0.95);
}

.nav-btn img {
  width: 22px;
  height: 22px;
  filter: grayscale(100%) brightness(0.5);
  transition: all 0.2s ease;
}

.prev-btn {
  left: 20px;
}

.next-btn {
  right: 20px;
}

.ppt-display-wrapper {
  max-width: 100%;
  max-height: 100%;
  transition: transform 0.3s ease;
}

.ppt-display-image {
  max-width: 100%;
  max-height: calc(100vh - 280px);
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

/* 缩放控制 */
.zoom-controls {
  position: absolute;
  bottom: 20px;
  right: 100px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 16px;
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(201, 96, 48, 0.15);
  z-index: 50;
}

.zoom-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  color: white;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.zoom-btn:hover {
  background: linear-gradient(135deg, #C96030, #F18B5B);
  transform: scale(1.1);
}

.zoom-level {
  font-size: 14px;
  font-weight: 600;
  color: #C96030;
  min-width: 50px;
  text-align: center;
}

/* 底部区域 */
.fullscreen-footer {
  background: linear-gradient(135deg, #FFF9F3, #FFFFFF);
  border-top: 2px solid rgba(201, 96, 48, 0.1);
}

/* 字幕区 */
.subtitle-area {
  padding: 16px 32px;
  text-align: center;
  background: rgba(0, 0, 0, 0.2);
}

.subtitle-content {
  font-size: 18px;
  color: #666;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 侧边栏底部提问框 */
.sidebar-input-area {
  padding: 16px;
  border-top: 1px solid rgba(201, 96, 48, 0.1);
  background: #FFF9F3;
}

.sidebar-input-area .input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #FFFFFF;
  border: 2px solid rgba(201, 96, 48, 0.15);
  border-radius: 50px;
  padding: 8px 12px;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.sidebar-input-area .input-wrapper:focus-within {
  border-color: #F18B5B;
  box-shadow: 0 0 0 4px rgba(241, 139, 91, 0.1);
}

.sidebar-input-area .input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  color: #333;
}

.sidebar-input-area .input-wrapper input::placeholder {
  color: #999;
}

.sidebar-input-area .voice-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(241, 139, 91, 0.1);
  border-radius: 50px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: relative;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-input-area .voice-btn:hover {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  transform: scale(1.1);
}

.sidebar-input-area .voice-btn:hover .voice-icon {
  filter: brightness(0) invert(1);
}

.sidebar-input-area .voice-btn:active {
  transform: scale(0.95);
}

.sidebar-input-area .voice-btn.active {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  animation: pulse 1.5s infinite;
}

.sidebar-input-area .voice-btn.active .voice-icon {
  filter: brightness(0) invert(1);
}

.sidebar-input-area .voice-icon {
  width: 16px;
  height: 16px;
  transition: all 0.2s ease;
}

.sidebar-input-area .voice-waves {
  position: absolute;
  display: flex;
  gap: 3px;
}

.sidebar-input-area .wave {
  width: 3px;
  height: 12px;
  background: #FFFFFF;
  border-radius: 2px;
  animation: wave 1s ease-in-out infinite;
}

.sidebar-input-area .wave:nth-child(1) {
  animation-delay: 0s;
}

.sidebar-input-area .wave:nth-child(2) {
  animation-delay: 0.2s;
}

.sidebar-input-area .wave:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes wave {
  0%, 100% {
    transform: scaleY(0.4);
  }
  50% {
    transform: scaleY(1);
  }
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(241, 139, 91, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(241, 139, 91, 0);
  }
}

.sidebar-input-area .send-btn {
  padding: 6px;
  width: 32px;
  height: 32px;
  min-width: auto;
  border: none;
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 600;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
  white-space: nowrap;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 6px;
}

.sidebar-input-area .send-btn .send-icon {
  width: 14px;
  height: 16px;
  filter: brightness(0) invert(1);
}

.sidebar-input-area .send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #C96030, #F18B5B);
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(241, 139, 91, 0.3);
}

.sidebar-input-area .send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.sidebar-input-area .send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #e0e0e0;
}

.sidebar-input-area .send-btn:disabled .send-icon {
  filter: grayscale(100%) brightness(1.5);
}

/* 播放控制区 */
.fullscreen-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.8);
}

.controls-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.controls-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.fullscreen-controls .control-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(241, 139, 91, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.fullscreen-controls .control-btn:hover {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  transform: scale(1.1);
}

.fullscreen-controls .control-btn:hover img {
  filter: brightness(0) invert(1);
}

.fullscreen-controls .control-btn img {
  width: 20px;
  height: 20px;
  filter: grayscale(100%) brightness(0.5);
}

.fullscreen-controls .progress-container {
  flex: 1;
  max-width: 600px;
}

.fullscreen-controls .progress-bar {
  height: 6px;
  background: rgba(201, 96, 48, 0.2);
  border-radius: 3px;
  overflow: visible;
  position: relative;
  cursor: pointer;
  transition: height 0.2s ease;
}

.fullscreen-controls .progress-bar:hover {
  height: 8px;
}

.fullscreen-controls .progress-bar.dragging {
  height: 8px;
}

.fullscreen-controls .progress-filled {
  height: 100%;
  background: linear-gradient(90deg, #F18B5B, #FF9E5F);
  border-radius: 3px;
  transition: width 0.15s ease-out;
}

.fullscreen-controls .progress-handle {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 14px;
  height: 14px;
  background: #F18B5B;
  border-radius: 50%;
  cursor: grab;
  opacity: 0;
  transition: opacity 0.2s ease, transform 0.2s ease, width 0.2s ease, height 0.2s ease;
  box-shadow: 0 2px 8px rgba(241, 139, 91, 0.4);
  z-index: 10;
}

.fullscreen-controls .progress-bar:hover .progress-handle,
.fullscreen-controls .progress-handle.active {
  opacity: 1;
}

.fullscreen-controls .progress-handle.active {
  cursor: grabbing;
  width: 18px;
  height: 18px;
  box-shadow: 0 4px 12px rgba(241, 139, 91, 0.6);
}

.fullscreen-controls .progress-bar:hover .progress-handle {
  transform: translate(-50%, -50%) scale(1.1);
}

.fullscreen-controls .progress-filled {
  height: 100%;
  background: linear-gradient(90deg, #F18B5B, #FF9E5F);
  border-radius: 3px;
}

.fullscreen-controls .time-display {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  min-width: 60px;
}

.fullscreen-controls .speed-btn {
  padding: 6px 12px;
  border: none;
  background: rgba(241, 139, 91, 0.1);
  color: #666;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 20px;
  transition: all 0.2s;
}

.fullscreen-controls .speed-btn:hover {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  color: white;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .right-sidebar.expanded {
    width: 280px;
  }
}

@media (max-width: 768px) {
  .fullscreen-title {
    font-size: 18px;
  }
  
  .right-sidebar {
    width: 50px;
  }
  
  .right-sidebar.expanded {
    width: 240px;
  }
  
  .ppt-display-area {
    padding: 20px 60px;
  }
  
  .nav-btn {
    width: 48px;
    height: 48px;
  }
  
  .fullscreen-controls {
    padding: 12px 16px;
  }
}

/* 消息列表样式 */
.sidebar-chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px 0;
}

.message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message.user-msg {
  flex-direction: row;
  justify-content: flex-end;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
}

.ai-avatar {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-avatar-img {
  width: 20px;
  height: 20px;
  filter: brightness(0) invert(1);
}

.user-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.message-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 16px;
  background: #f5f5f5;
}

.message.user-msg .message-bubble {
  background: linear-gradient(135deg, #F18B5B, #FF9E5F);
  color: white;
}

.message-content {
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

/* 历史对话列表样式 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background: rgba(241, 139, 91, 0.1);
}

.history-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(241, 139, 91, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.history-icon img {
  width: 20px;
  height: 20px;
}

.history-info {
  flex: 1;
  overflow: hidden;
}

.history-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 历史对话详情样式 */
.history-detail {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.detail-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(201, 96, 48, 0.1);
}

.detail-title-wrapper {
  flex: 1;
  text-align: center;
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.detail-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

</style>
