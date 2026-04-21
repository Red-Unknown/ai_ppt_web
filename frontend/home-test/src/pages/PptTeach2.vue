<template>
  <div class="ppt-teach-page">
    <!-- 背景 -->
    <div class="bg-gradient"></div>
    
    <!-- 顶部栏 -->
    <header class="header" :class="{ 'header-shadow': isScrolled }">
      <button class="back-button" @click="handleBack" aria-label="返回">
        <img src="@/assets/images/action/ic-arrow_left2.svg" alt="返回" class="back-icon">
      </button>
      <div class="user-info">
        <div class="avatar" @click="handleAvatarClick" aria-label="用户信息">
          <span class="avatar-text">小</span>
        </div>
        <span class="username">你好，老师老师</span>
      </div>
    </header>
    
    <!-- 主内容区 -->
    <main class="main-content" :class="{ 'preview-mode': !isEditMode }">
      <!-- 内容区域 -->
      <div class="content-area" :class="{ 'ppt-collapsed': pptCollapsed, 'preview-mode': !isEditMode }">
        <!-- 编辑模式布局 -->
        <template v-if="isEditMode">
          <!-- 教案区 -->
          <div class="lesson-panel" :style="{ width: lessonWidth + '%' }">
            <!-- 编辑器工具栏 -->
            <EditorToolbar 
              :is-edit-mode="isEditMode"
              :can-undo="canUndo"
              :can-redo="canRedo"
              :selected-option="selectedOption"
              @undo="handleUndo"
              @redo="handleRedo"
              @save="handleSave"
              @select-element="handleSelectElement"
              @toggle-edit-mode="toggleEditMode"
              @option-change="handleOptionChange"
              @bold="handleBold"
            />

            <!-- PPT解析状态栏 -->
            <div class="ppt-parser-control">
              <div class="parser-status">
                <span class="status-label">PPT解析状态:</span>
                <span class="status-value" :class="{ 'parsing': isParsingPPT, 'connected': pptParser?.isConnected() }">
                  {{ parseStatusText }}
                </span>
                <span v-if="isParsingPPT" class="progress-value">{{ parseProgress }}%</span>
              </div>
            </div>
            
            <!-- 教案内容 -->
            <div class="panel-content">
              <LoadingState 
                v-if="isLoading" 
                type="loading" 
                :text="parseStatusText + ' ' + parseProgress + '%'"
              />
              <LessonPlanContent 
                v-else 
                ref="lessonPlanContentRef"
                :content="currentContent"
                :is-edit-mode="isEditMode"
                :content-type="selectedOption === '思维导图编辑区' ? 'mindmap' : selectedOption === '课程概要编辑区' ? 'summary' : 'lesson'"
                @content-change="handleContentChange"
              />
            </div>
          </div>
          
          <!-- 滑块 -->
          <div class="resizer" @mousedown="startResize" :class="{ dragging: isResizing }" 
               @touchstart="startResizeTouch" 
               :style="{ cursor: isResizing ? 'grabbing' : 'grab' }"
               unselectable="on"
               onselectstart="return false;"
               onmousedown="return false;"
               aria-label="调整面板大小">
            <div class="resizer-track"></div>
            <div class="resizer-handle">
              <div class="resizer-dot"></div>
            </div>
            <!-- 位置指示 -->
            <div v-if="isResizing" class="resize-indicator">
              {{ Math.round(lessonWidth) }}% / {{ Math.round(pptWidth) }}%
            </div>
          </div>
          
          <!-- PPT区 - 使用新组件 -->
          <div class="ppt-panel" :class="{ collapsed: pptCollapsed }" :style="{ width: pptWidth + '%' }">
            <AIAssistantPanel
              theme="blue"
              :tabs="[
                { id: 'courseware', name: '课件' },
                { id: 'ai-assistant', name: 'AI助手' },
                { id: 'history', name: '历史对话' }
              ]"
              empty-text="老师您好，若有任何想法，欢迎随时与我沟通"
              v-model:messages="aiMessages"
              v-model:history-list="historyList"
              v-model:history-messages="historyDetailMessages"
              v-model:selected-history="selectedHistoryItem"
              v-model:show-history-detail="showHistoryDetail"
              v-model="questionText"
              v-model:is-recording="isVoiceInputActive"
              @new-chat="createNewChat"
              @open-settings="toggleSettingsModal"
              @send-message="handleSendMessage"
              @toggle-recording="handleToggleRecording"
              @open-history-detail="openHistoryDetail"
              @close-history-detail="closeHistoryDetail"
              @update:active-tab="handleActiveTabChange"
            >
              <!-- 自定义课件标签 -->
              <template #tab-courseware>
                <div v-if="panelActiveTab === 'courseware'" class="courseware-panel">
                  <div class="courseware-content">
                    <CoursewarePreview 
                      :slides="slides"
                      :selected-slide="currentSlide"
                      :bboxes="currentBboxes"
                      @slide-click="handleSlideClick"
                      @select-element="handleSelectElement"
                      @add-to-chat="handleAddToChat"
                    />
                    <div class="courseware-input-wrapper">
                      <AIChatInput 
                        v-model="questionText"
                        @send="handleSendQuestion"
                        @switch-to-ai="switchToAITab"
                        :ppt-content="{ slides, lessonContent }"
                        :added-contents="addedContents"
                        @remove-content="handleRemoveContent"
                      />
                    </div>
                  </div>
                </div>
              </template>


            </AIAssistantPanel>
          </div>
        </template>

        <!-- 预览模式布局 - 参考学生端 -->
        <template v-else>
          <!-- 左侧：核心预览区 -->
          <div class="left-section" :style="{ width: lessonWidth + '%' }">
            <!-- PPT预览容器 - 蓝色 -->
            <div class="ppt-blue-container">
              <div class="ppt-player-wrapper">
                <!-- PPT标题栏 - 蓝色 -->
                <div class="ppt-header-preview">
                  <span class="ppt-title-preview">PPT标题</span>
                  <div class="ppt-right-section-preview">
                    <div class="edit-preview-tabs-preview">
                      <button 
                        class="tab-button-preview" 
                        :class="{ active: isEditMode }"
                        @click="toggleEditMode"
                      >
                        编辑
                      </button>
                      <button 
                        class="tab-button-preview" 
                        :class="{ active: !isEditMode }"
                        @click="toggleEditMode"
                      >
                        预览
                      </button>
                    </div>
                    <div class="ppt-actions-preview">
                      <button class="action-btn-preview select-element-preview">选择元素</button>
                      <button class="action-btn-preview icon-btn-preview">
                        <img src="@/assets/images/action/ic-share.svg" alt="分享">
                      </button>
                      <button class="action-btn-preview icon-btn-preview more-btn-preview" @click="togglePptExpand">
                        <img src="@/assets/images/action/ic-arrow_down.svg" alt="更多" :class="{ 'rotate-180': !isPptExpanded }">
                      </button>
                    </div>
                  </div>
                </div>
                
                <!-- PPT内容区 -->
                <div v-if="isPptExpanded" class="ppt-content-preview">
                  <div class="ppt-image-wrapper-preview">
                    <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Great%20Wall%20of%20China%20landscape%20with%20mountains&image_size=landscape_16_9" alt="PPT" class="ppt-image-preview">
                    <div class="play-overlay-preview" @click="togglePlay">
                      <img src="@/assets/images/action/ic_play.svg" alt="播放" class="play-icon-preview">
                    </div>
                  </div>
                </div>
                
                <!-- 视频控制栏 -->
                <div v-if="isPptExpanded" class="video-controls-preview">
                  <button class="control-btn-preview play-pause-preview" @click="togglePlay">
                    <img v-if="!isPlaying" src="@/assets/images/action/ic_play.svg" alt="播放">
                    <img v-else src="@/assets/images/action/ic-pause.svg" alt="暂停">
                  </button>
                  <div class="progress-container-preview">
                    <div class="progress-bar-preview" 
                         @click="seekVideo" 
                         @mousedown="startDrag"
                         :class="{ 'dragging': isDragging }">
                      <div class="progress-filled-preview" :style="{ width: progressPercent + '%' }"></div>
                      <div class="progress-handle-preview" 
                           :style="{ left: progressPercent + '%' }"
                           :class="{ 'active': isDragging }"></div>
                    </div>
                  </div>
                  <span class="time-display-preview">{{ currentPage }}/{{ totalPages }}</span>
                  <button class="control-btn-preview speed-btn-preview" @click="cyclePlaybackSpeed">
                    {{ playbackSpeed }}x
                  </button>
                  <button class="control-btn-preview volume-preview" @click="toggleMute">
                    <img v-if="!isMuted" src="@/assets/images/action/ic_volume_on.svg" alt="音量">
                    <img v-else src="@/assets/images/action/ic_volume_off.svg" alt="静音">
                  </button>
                  <button class="control-btn-preview fullscreen-preview" @click="toggleFullscreen">
                    <img src="@/assets/images/action/ic-fullscreen.svg" alt="全屏">
                  </button>
                </div>
              </div>
            </div>

            <!-- 课程文档 -->
            <div class="course-document-wrapper-preview">
              <div class="course-document-preview" :class="{ 'collapsed': !isDocExpanded }">
                <div class="doc-section-preview">
                  <h3 class="doc-title-preview">方法 2：</h3>
                  <p class="doc-subtitle-preview">用「Frame + 遮罩」实现通用裁剪（适合所有图层）</p>
                  <ol class="doc-list-preview">
                    <li>选中要裁剪的图层，右键菜单里选择 <span class="highlight-preview">「Use as mask」</span>（快捷键 Ctrl+Alt+M），或者先给它套一个 Frame（Ctrl+Alt+G）。</li>
                    <li>调整 Frame 的大小和位置，超出 Frame 的部分会被自动隐藏，实现和裁剪一样的效果。</li>
                    <li>这种方法不会破坏原图层，随时可以调整裁剪范围</li>
                  </ol>
                </div>
              </div>
              
              <!-- 展开/折叠教案按钮 -->
              <div class="doc-expand-control-preview">
                <button class="doc-expand-btn-preview" @click="toggleDocExpand">
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
              {{ Math.round(lessonWidth) }}% / {{ Math.round(pptWidth) }}%
            </div>
          </div>

          <!-- 右侧：AI助手交互区 -->
          <div class="right-section-preview" :style="{ width: pptWidth + '%' }">
            <AIAssistantPanel
              theme="blue"
              :tabs="[
                { id: 'ai-assistant', name: 'AI助手' },
                { id: 'history', name: '历史对话' },
                { id: 'mindmap', name: '思维导图' },
                { id: 'summary', name: '课程概要' }
              ]"
              empty-text="老师您好，若有任何想法，欢迎随时与我沟通"
              v-model:messages="aiMessages"
              v-model:history-list="historyList"
              v-model:history-messages="historyDetailMessages"
              v-model:selected-history="selectedHistoryItem"
              v-model:show-history-detail="showHistoryDetail"
              v-model="questionText"
              v-model:is-recording="isVoiceInputActive"
              @new-chat="createNewChat"
              @open-settings="toggleSettingsModal"
              @send-message="handleSendMessage"
              @toggle-recording="handleToggleRecording"
              @open-history-detail="openHistoryDetail"
              @close-history-detail="closeHistoryDetail"
              @update:active-tab="handleActiveTabChange"
            />
          </div>
        </template>
      </div>
    </main>
    
    <!-- 全局加载 -->
    <Loading :visible="isGlobalLoading" :text="loadingText" />
    
    <!-- 设置弹窗 -->
    <div v-if="showSettingsModal" class="export-dialog-overlay" @click="toggleSettingsModal">
      <div class="export-dialog" @click.stop>
        <div class="export-dialog-header">
          <h3 class="export-dialog-title">对话设置</h3>
          <button class="export-dialog-close" @click="toggleSettingsModal">×</button>
        </div>
        <div class="export-dialog-content">
          <div class="settings-option">
            <label for="model-select" class="settings-label">模型选择</label>
            <select id="model-select" v-model="aiSettings.model" class="settings-select">
              <option value="chatGPT">chatGPT</option>
              <option value="GPT-4">GPT-4</option>
              <option value="Claude">Claude</option>
            </select>
          </div>
          <div class="settings-option">
            <label for="python-checkbox" class="settings-label">Python计算</label>
            <input type="checkbox" id="python-checkbox" v-model="aiSettings.usePython" class="settings-checkbox">
          </div>
          <div class="settings-option">
            <label for="websearch-checkbox" class="settings-label">联网搜索</label>
            <input type="checkbox" id="websearch-checkbox" v-model="aiSettings.useInternet" class="settings-checkbox">
          </div>
          <div class="settings-option">
            <label for="voice-select" class="settings-label">对话声音</label>
            <select id="voice-select" v-model="aiSettings.voice" class="settings-select">
              <option value="女声1">女声1</option>
              <option value="女声2">女声2</option>
              <option value="男声1">男声1</option>
              <option value="男声2">男声2</option>
            </select>
          </div>
        </div>
        <div class="export-dialog-footer">
          <button class="export-dialog-btn cancel-btn" @click="toggleSettingsModal">取消</button>
          <button class="export-dialog-btn confirm-btn" @click="saveSettings">确认设置</button>
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
                <div v-if="aiMessages.length === 0" class="empty-chat">
                  <div class="empty-icon">
                    <img src="@/assets/images/logo/ic-AI.svg" alt="AI" class="ai-icon">
                  </div>
                  <p class="empty-text">老师您好，若有任何想法，欢迎随时与我沟通</p>
                </div>
                <div v-else class="message-list">
                  <div v-for="(msg, index) in aiMessages" :key="index" class="message" :class="msg.type === 'user' ? 'user-msg' : 'ai-msg'">
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
                    <h3 class="detail-title">{{ selectedHistoryItem?.title }}</h3>
                  </div>
                  <button class="action-icon-btn" @click="openSettings" title="设置">
                    <img src="@/assets/images/action/ic-set.svg" alt="设置">
                  </button>
                </div>
                <div class="detail-messages" ref="detailChatContainer">
                  <div v-for="(msg, index) in historyDetailMessages" :key="index" class="message" :class="msg.type === 'user' ? 'user-msg' : 'ai-msg'">
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
                v-model="questionText"
                :placeholder="inputPlaceholder"
                @keyup.enter="handleSendMessage"
              />
              <button
                class="voice-btn"
                :class="{ active: isVoiceInputActive }"
                @click="handleToggleRecording"
              >
                <img v-if="!isVoiceInputActive" src="@/assets/images/action/ic_mic_off.svg" alt="语音" class="voice-icon">
                <img v-else src="@/assets/images/action/ic_mic_active.svg" alt="录音中" class="voice-icon">
                <div v-if="isVoiceInputActive" class="voice-waves">
                  <span class="wave"></span>
                  <span class="wave"></span>
                  <span class="wave"></span>
                </div>
              </button>
              <button
                class="send-btn"
                @click="handleSendMessage"
                :disabled="!questionText.trim()"
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
                   :class="{ 'active': isDragging }">
              </div>
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
  </div>
  
  <!-- 用户信息弹窗 -->
  <UserInfoPopup
    v-if="showUserInfoPopup"
    :user-info="userInfo"
    theme="blue"
    @close="showUserInfoPopup = false"
    @menu-click="handleMenuClick"
    @logout="handleLogout"
    @save-profile="handleSaveProfile"
  />
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import EditorToolbar from '../components/EditorToolbar.vue'
import LoadingState from '../components/LoadingState.vue'
import LessonPlanContent from '../components/LessonPlanContent.vue'
import CoursewarePreview from '../components/CoursewarePreview.vue'
import AIChatInput from '../components/AIChatInput.vue'
import Loading from '../components/Loading.vue'
import AIAssistantPanel from '../components/AIAssistantPanel.vue'
import UserInfoPopup from '../components/UserInfoPopup.vue'
import { startChatSession, createChatSSE, sendChatMessage } from '../services/apiService.js'
import { mockBboxService } from '../services/bboxService.js'
import { PPTParserService } from '../services/pptParserService.js'

// 用户信息
const userInfo = ref({
  name: '老师',
  teacherId: '',
  title: '',
  email: '',
  phone: '',
  major: '',
  researchArea: '',
  education: '',
  university: ''
})

// 状态
const panelActiveTab = ref('courseware')
const pptCollapsed = ref(false)
const lessonWidth = ref(50)
const pptWidth = ref(50)
const isResizing = ref(false)
const questionText = ref('')
const showPresetQuestions = ref(false)
const zoomLevel = ref(1)
const selectedOption = ref('教案编辑区')
// 语音输入状态
const isVoiceInputActive = ref(false)
let recognition = null
// PPT进度条状态
const currentSlide = ref(0)
const totalSlides = ref(5)
const progressPercentage = ref(0)
const isDragging = ref(false)
// 答疑集弹窗状态
const anserPopupVisible = ref(false)
const conversations = ref([])
// AI聊天消息 - 适配新组件格式
const aiMessages = ref([])
// 历史对话列表 - 适配新组件格式
const historyList = ref([])
// 历史对话详情消息
const historyDetailMessages = ref([])
// 当前查看的历史对话详情
const selectedHistoryItem = ref(null)
const showHistoryDetail = ref(false)
// SSE连接
const sseConnection = ref(null)

// PPT解析服务
const pptParser = ref(null)
const isParsingPPT = ref(false)
const parseProgress = ref(0)
const parseStatus = ref('')
const parseStatusText = ref('等待解析...')

// 教案区状态切换按钮
const lessonPanelState = ref(localStorage.getItem('lessonPanelState') === 'true')
// 导航栏状态
const isScrolled = ref(false)
const showUserInfoPopup = ref(false)
// Bbox状态
const currentBboxes = ref([])
// 编辑模式状态
const isEditMode = ref(true)

// 预览模式状态
const isPlaying = ref(false)
const isMuted = ref(false)
const playbackSpeed = ref(1)
const currentPage = ref(1)
const totalPages = ref(10)
const isDocExpanded = ref(true)
const progressPercent = ref(0)
const isPptExpanded = ref(true)

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

// 动态输入框placeholder
const inputPlaceholder = computed(() => {
  if (showHistoryDetail.value && selectedHistoryItem.value) {
    return `继续对话：${selectedHistoryItem.value.title}`
  }
  return '请输入你的问题'
})
// 操作历史栈，用于撤销功能
// 注意：内容编辑的历史记录现在由LessonPlanContent组件管理
const historyStack = ref([])
const historyIndex = ref(-1)
// 加载状态
const isLoading = ref(true)
const isGlobalLoading = ref(false)
const loadingText = ref('')

// 设置弹窗状态
const showSettingsModal = ref(false)
// AI设置
const aiSettings = ref({
  model: 'chatGPT',
  python: true,
  webSearch: true,
  voice: '女声1'
})

// 选择元素状态
const isSelectMode = ref(false)
const selectedContent = ref(null)
const addedContents = ref([])

// 教案内容
const lessonContent = ref({
  objectives: [
    '理解三角形的基本性质',
    '掌握三角形面积计算方法',
    '能够应用三角形知识解决实际问题'
  ],
  keyPoints: [
    '三角形的面积计算公式：S = 1/2 × 底 × 高'
  ],
  teachingSteps: [
    '导入：通过生活中的三角形实例引入课题',
    '讲解：详细解释三角形的基本概念和性质',
    '演示：通过PPT展示三角形面积计算的具体步骤',
    '练习：让学生完成相关练习题',
    '总结：回顾本节课的重点内容'
  ],
  exercises: [
    '计算底为10cm，高为8cm的三角形面积',
    '已知三角形面积为24cm²，底为8cm，求高',
    '应用三角形知识解决实际问题'
  ]
})

// 思维导图内容
const mindMapContent = ref({
  objectives: [],
  keyPoints: [],
  teachingSteps: [],
  exercises: []
})

// 课程概要内容
const courseSummaryContent = ref({
  objectives: [],
  keyPoints: [],
  teachingSteps: [],
  exercises: []
})

// 计算当前显示的内容
const currentContent = computed(() => {
  switch (selectedOption.value) {
    case '思维导图编辑区':
      return mindMapContent.value
    case '课程概要编辑区':
      return courseSummaryContent.value
    default:
      return lessonContent.value
  }
})

// 组件引用
const lessonPlanContentRef = ref(null)
// 撤销/重做状态 - 从LessonPlanContent获取
const canUndo = computed(() => {
  return lessonPlanContentRef.value ? lessonPlanContentRef.value.canUndo.value : false
})
const canRedo = computed(() => {
  return lessonPlanContentRef.value ? lessonPlanContentRef.value.canRedo.value : false
})
// PPT幻灯片数据
const slides = ref([
  {
    imageUrl: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Great%20Wall%20of%20China%20landscape%20with%20mountains&image_size=landscape_16_9'
  },
  {
    imageUrl: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Great%20Wall%20of%20China%20architecture%20details&image_size=landscape_16_9'
  }
])

// 初始化历史对话列表 - 适配新组件格式
const initHistoryList = () => {
  const originalHistory = [
    { 
      id: 1,
      question: '如何选中目标？',
      answer: '选中目标图层：在左侧 Layers 面板里，选中你要处理的图标（比如图中的 Volume 2 或 mic 图层）。\n扁平化 / 轮廓化：\n• 如果是文字 / 形状组合：先右键 → Flatten（扁平化），把组合变成单一形状。\n• 如果是描边线条：选中线条 → 右侧面板 Stroke → 点击 Outline stroke（轮廓化描边），把线条变成可编辑的填充形状。\n布尔运算合并：\n• 选中所有组成图标的形状图层 → 顶部工具栏选择 Union selection（合并），把多个形状合并成一个矢量路径。\n• 如果有镂空部分，用 Subtract selection（减去）来实现。',
      time: '今天 10:30',
      updatedAt: Date.now() - 30 * 60 * 1000
    },
    { 
      id: 2,
      question: '如何选中目标？',
      answer: '选中目标图层：在左侧 Layers 面板里，选中你要处理的图标（比如图中的 Volume 2 或 mic 图层）。\n扁平化 / 轮廓化：\n• 如果是文字 / 形状组合：先右键 → Flatten（扁平化），把组合变成单一形状。\n• 如果是描边线条：选中线条 → 右侧面板 Stroke → 点击 Outline stroke（轮廓化描边），把线条变成可编辑的填充形状。\n布尔运算合并：\n• 选中所有组成图标的形状图层 → 顶部工具栏选择 Union selection（合并），把多个形状合并成一个矢量路径。\n• 如果有镂空部分，用 Subtract selection（减去）来实现。',
      time: '今天 10:25',
      updatedAt: Date.now() - 35 * 60 * 1000
    }
  ]
  
  historyList.value = originalHistory.map(item => ({
    id: item.id,
    title: item.question,
    messages: [
      { type: 'user', content: item.question },
      { type: 'ai', content: item.answer }
    ],
    createdAt: item.updatedAt,
    updatedAt: item.updatedAt
  }))
}

// 切换教案区状态
const toggleLessonPanelState = () => {
  lessonPanelState.value = !lessonPanelState.value
  localStorage.setItem('lessonPanelState', lessonPanelState.value.toString())
}

// 切换倍率
const toggleZoom = () => {
  if (zoomLevel.value === 1) {
    zoomLevel.value = 2
  } else if (zoomLevel.value === 2) {
    zoomLevel.value = 3
  } else {
    zoomLevel.value = 1
  }
}

// 初始化语音识别
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
    }
    
    recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error)
    }
    
    recognition.onend = () => {
    }
  }
}

// 切换语音输入
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

// 处理语音切换
const handleToggleRecording = (recording) => {
  isVoiceInputActive.value = recording
  if (recording) {
    toggleVoiceInput()
  } else {
    if (recognition) {
      recognition.stop()
      isVoiceInputActive.value = false
    }
  }
}

// 计算进度百分比
const calculateProgress = () => {
  if (totalSlides.value > 0) {
    progressPercentage.value = Math.round((currentSlide.value / (totalSlides.value - 1)) * 100 * 100) / 100
  } else {
    progressPercentage.value = 0
  }
}

// 切换到下一张幻灯片
const nextSlide = () => {
  if (currentSlide.value < totalSlides.value - 1) {
    currentSlide.value++
    calculateProgress()
  }
}

// 切换到上一张幻灯片
const prevSlide = () => {
  if (currentSlide.value > 0) {
    currentSlide.value--
    calculateProgress()
  }
}

// 跳转到指定幻灯片
const seekToSlide = (event) => {
  const progressBar = event.currentTarget
  const rect = progressBar.getBoundingClientRect()
  const clickPosition = (event.clientX - rect.left) / rect.width
  const slideIndex = Math.round(clickPosition * (totalSlides.value - 1))
  currentSlide.value = Math.max(0, Math.min(totalSlides.value - 1, slideIndex))
  calculateProgress()
}

// 开始拖拽进度条（合并函数）
const startDrag = (event) => {
  isDragging.value = true
  document.addEventListener('mousemove', dragProgress)
  document.addEventListener('mouseup', stopDrag)
  if (event.preventDefault) event.preventDefault()
}

// 开始触摸拖拽（合并函数）
const startDragTouch = (event) => {
  isDragging.value = true
  document.addEventListener('touchmove', dragProgressTouch)
  document.addEventListener('touchend', stopDrag)
  if (event.preventDefault) event.preventDefault()
}

// 拖拽进度条（合并函数）
const dragProgress = (event) => {
  if (!isDragging.value) return
  
  // 优先查找预览模式的进度条，如果没有则查找编辑模式的
  let progressBar = document.querySelector('.progress-bar-preview')
  if (!progressBar) {
    progressBar = document.querySelector('.progress-bar')
  }
  
  if (progressBar) {
    const rect = progressBar.getBoundingClientRect()
    const dragPosition = (event.clientX - rect.left) / rect.width
    
    // 根据进度条类型更新不同的状态
    if (progressBar.classList.contains('progress-bar-preview')) {
      progressPercent.value = Math.max(0, Math.min(100, dragPosition * 100))
      currentPage.value = Math.ceil(progressPercent.value / 100 * totalPages.value)
    } else {
      const slideIndex = Math.round(dragPosition * (totalSlides.value - 1))
      currentSlide.value = Math.max(0, Math.min(totalSlides.value - 1, slideIndex))
      calculateProgress()
    }
  }
}

// 触摸拖拽进度条（合并函数）
const dragProgressTouch = (event) => {
  if (!isDragging.value) return
  if (!event.touches || event.touches.length === 0) return
  
  // 优先查找预览模式的进度条，如果没有则查找编辑模式的
  let progressBar = document.querySelector('.progress-bar-preview')
  if (!progressBar) {
    progressBar = document.querySelector('.progress-bar')
  }
  
  if (progressBar) {
    const rect = progressBar.getBoundingClientRect()
    const dragPosition = (event.touches[0].clientX - rect.left) / rect.width
    
    // 根据进度条类型更新不同的状态
    if (progressBar.classList.contains('progress-bar-preview')) {
      progressPercent.value = Math.max(0, Math.min(100, dragPosition * 100))
      currentPage.value = Math.ceil(progressPercent.value / 100 * totalPages.value)
    } else {
      const slideIndex = Math.round(dragPosition * (totalSlides.value - 1))
      currentSlide.value = Math.max(0, Math.min(totalSlides.value - 1, slideIndex))
      calculateProgress()
    }
  }
}

// 停止拖拽（合并函数）
const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', dragProgress)
  document.removeEventListener('touchmove', dragProgressTouch)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchend', stopDrag)
}

// 处理返回
const handleBack = () => {
  window.history.back()
}

// 处理保存
const handleSave = () => {
  console.log('保存教案')
  addToHistory('save', {})
}

// 切换编辑/预览模式
const toggleEditMode = () => {
  isEditMode.value = !isEditMode.value
  console.log('切换到', isEditMode.value ? '编辑' : '预览', '模式')
  addToHistory('toggleEditMode', { isEditMode: isEditMode.value })
}

// ============== 预览模式控制函数 ==============

// 切换播放/暂停
const togglePlay = () => {
  isPlaying.value = !isPlaying.value
  console.log(isPlaying.value ? '开始播放' : '暂停播放')
}

// 切换静音
const toggleMute = () => {
  isMuted.value = !isMuted.value
  console.log(isMuted.value ? '已静音' : '取消静音')
}

// 循环播放速度
const cyclePlaybackSpeed = () => {
  const speeds = [0.5, 1, 1.5, 2]
  const currentIndex = speeds.indexOf(playbackSpeed.value)
  playbackSpeed.value = speeds[(currentIndex + 1) % speeds.length]
  console.log('播放速度:', playbackSpeed.value, 'x')
}

// 切换全屏
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

// 跳转到指定位置
const seekVideo = (event) => {
  const progressBar = event.currentTarget
  const rect = progressBar.getBoundingClientRect()
  const clickPosition = (event.clientX - rect.left) / rect.width
  progressPercent.value = Math.max(0, Math.min(100, clickPosition * 100))
  currentPage.value = Math.ceil(progressPercent.value / 100 * totalPages.value)
  console.log('跳转到', progressPercent.value.toFixed(0) + '%，第', currentPage.value, '页')
}

// 切换教案展开/折叠
const toggleDocExpand = () => {
  isDocExpanded.value = !isDocExpanded.value
  console.log(isDocExpanded.value ? '展开教案' : '折叠教案')
}

// 切换PPT展开/折叠
const togglePptExpand = () => {
  isPptExpanded.value = !isPptExpanded.value
  console.log(isPptExpanded.value ? '展开PPT' : '折叠PPT')
}

// 添加操作到历史栈
const addToHistory = (action, data) => {
  if (historyIndex.value < historyStack.value.length - 1) {
    historyStack.value = historyStack.value.slice(0, historyIndex.value + 1)
  }
  
  historyStack.value.push({ action, data, timestamp: Date.now() })
  
  const maxHistorySize = 50
  if (historyStack.value.length > maxHistorySize) {
    historyStack.value.shift()
  } else {
    historyIndex.value++
  }
}

// 撤销操作
const handleUndo = () => {
  if (historyIndex.value >= 0) {
    const lastAction = historyStack.value[historyIndex.value]
    console.log('撤销操作:', lastAction.action)
    switch (lastAction.action) {
      case 'toggleEditMode':
        isEditMode.value = !lastAction.data.isEditMode
        break
      default:
        break
    }
    historyIndex.value--
  }
  if (lessonPlanContentRef.value) {
    lessonPlanContentRef.value.undo()
  }
}

// 重做操作
const handleRedo = () => {
  if (historyIndex.value < historyStack.value.length - 1) {
    historyIndex.value++
    const nextAction = historyStack.value[historyIndex.value]
    console.log('重做操作:', nextAction.action)
    switch (nextAction.action) {
      case 'toggleEditMode':
        isEditMode.value = nextAction.data.isEditMode
        break
      default:
        break
    }
  }
  if (lessonPlanContentRef.value) {
    lessonPlanContentRef.value.redo()
  }
}

// 处理文字加粗变色
const handleBold = () => {
  if (lessonPlanContentRef.value) {
    lessonPlanContentRef.value.handleBold()
  }
}

// 处理头像点击
const handleAvatarClick = () => {
  showUserInfoPopup.value = true
}

// 处理菜单项点击
const handleMenuClick = (menuItem) => {
  console.log('点击菜单项:', menuItem)
  // 这里可以添加相应的处理逻辑
}

// 处理退出登录
const handleLogout = () => {
  console.log('退出登录')
  // 这里可以添加退出登录的逻辑
  // 例如清除localStorage中的session_id
  localStorage.removeItem('session_id')
  // 跳转到登录页面
  window.location.href = '/'
}

// 处理保存个人资料
const handleSaveProfile = (profileData) => {
  console.log('保存个人资料:', profileData)
  // 更新本地用户信息
  userInfo.value = {
    ...userInfo.value,
    ...profileData
  }
  // 这里可以添加保存到服务器的逻辑
  // 例如发送API请求
  // saveProfileToServer(profileData)
  // 显示保存成功的提示
  alert('个人资料保存成功！')
}

// 处理标签页切换
const handleActiveTabChange = (tabId) => {
  panelActiveTab.value = tabId
}

// 处理幻灯片点击
const handleSlideClick = (index) => {
  currentSlide.value = index
  calculateProgress()
}

// 处理元素选择
const handleSelectElement = (isSelecting) => {
  console.log('选择元素模式:', isSelecting)
  isSelectMode.value = isSelecting
}

// 处理选项更改
const handleOptionChange = (option) => {
  console.log('选择的选项:', option)
  selectedOption.value = option
}

// 处理添加到对话
const handleAddToChat = (content) => {
  console.log('添加到对话:', content)
  addedContents.value.push(content)
}

// 处理移除内容
const handleRemoveContent = (index) => {
  console.log('移除内容:', index)
  addedContents.value.splice(index, 1)
}

// 处理发送问题（课件标签）
const handleSendQuestion = async (text) => {
  console.log('发送问题:', text)
  console.log('添加的内容:', addedContents.value)
  
  switchToAITab()
  
  const messageContent = {
    text: text,
    addedContents: [...addedContents.value]
  }
  
  aiMessages.value.push({
    type: 'user',
    content: messageContent
  })
  
  questionText.value = ''
  addedContents.value = []
  
  await simulateAIResponse()
}

// 处理发送消息（通用）
const handleSendMessage = async (text) => {
  if (!text.trim()) return
  
  if (showHistoryDetail.value && selectedHistoryItem.value) {
    historyDetailMessages.value.push({
      type: 'user',
      content: text
    })
    
    setTimeout(() => {
      historyDetailMessages.value.push({
        type: 'ai',
        content: '这是对历史对话的回复：' + text
      })
    }, 1000)
  } else {
    aiMessages.value.push({
      type: 'user',
      content: text
    })
    
    await simulateAIResponse()
  }
  
  questionText.value = ''
}

// 从输入框发送消息
const sendMessageFromInput = () => {
  handleSendMessage(questionText.value)
}

// 发送消息到后端并获取AI回复
const simulateAIResponse = async () => {
  try {
    isGlobalLoading.value = true
    loadingText.value = 'AI正在思考...'
    
    // 启动聊天会话
    await startChatSession()
    
    // 发送消息
    const lastUserMessage = aiMessages.value.filter(msg => msg.type === 'user').pop()
    if (lastUserMessage) {
      const messageContent = typeof lastUserMessage.content === 'object' 
        ? lastUserMessage.content.text 
        : lastUserMessage.content
      
      await sendChatMessage(messageContent)
    }
    
    // 建立SSE连接获取响应
    if (sseConnection.value) {
      sseConnection.value.close()
    }
    
    let fullAnswer = ''
    
    sseConnection.value = createChatSSE((data) => {
      if (data.answer) {
        fullAnswer += data.answer
        aiMessages.value.push({
          type: 'ai',
          content: data.answer
        })
      }
      
      // 模拟获取bboxes（根据AI回答内容获取相关的bbox）
      if (fullAnswer && data.type === 'end') {
        const bboxes = mockBboxService.getBboxesForAnswer(fullAnswer)
        if (bboxes && bboxes.length > 0) {
          currentBboxes.value = bboxes
        }
      }
    })
  } catch (error) {
    console.error('获取AI回复失败:', error)
    // 失败时使用模拟回复
    const mockAnswer = '选中目标图层：在左侧 Layers 面板里，选中你要处理的图标（比如图中的 Volume 2 或 mic 图层）。\n扁平化 / 轮廓化：\n• 如果是文字 / 形状组合：先右键 → Flatten（扁平化），把组合变成单一形状。\n• 如果是描边线条：选中线条 → 右侧面板 Stroke → 点击 Outline stroke（轮廓化描边），把线条变成可编辑的填充形状。\n布尔运算合并：\n• 选中所有组成图标的形状图层 → 顶部工具栏选择 Union selection（合并），把多个形状合并成一个矢量路径。\n• 如果有镂空部分，用 Subtract selection（减去）来实现。'
    
    setTimeout(() => {
      aiMessages.value.push({
        type: 'ai',
        content: mockAnswer
      })
      
      // 模拟获取bboxes
      const bboxes = mockBboxService.getBboxesForAnswer(mockAnswer)
      if (bboxes && bboxes.length > 0) {
        currentBboxes.value = bboxes
      }
    }, 1000)
  } finally {
    isGlobalLoading.value = false
  }
}

// 打开历史对话详情
const openHistoryDetail = (item) => {
  selectedHistoryItem.value = item
  showHistoryDetail.value = true
  historyDetailMessages.value = item.messages || []
}

// 关闭历史对话详情
const closeHistoryDetail = () => {
  selectedHistoryItem.value = null
  showHistoryDetail.value = false
  historyDetailMessages.value = []
}

// 切换到AI助手标签
const switchToAITab = () => {
  panelActiveTab.value = 'ai-assistant'
}

// 新建对话
const createNewChat = () => {
  if (aiMessages.value.length > 0) {
    const userMessage = aiMessages.value.find(msg => msg.type === 'user')
    const aiMessage = aiMessages.value.filter(msg => msg.type === 'ai').pop()
    
    if (userMessage && aiMessage) {
      const now = new Date()
      const newId = historyList.value.length > 0 
        ? Math.max(...historyList.value.map(item => item.id)) + 1 
        : 1
      
      const newHistoryItem = {
        id: newId,
        title: typeof userMessage.content === 'object' ? userMessage.content.text : userMessage.content,
        messages: [...aiMessages.value],
        createdAt: Date.now(),
        updatedAt: Date.now()
      }
      
      historyList.value.unshift(newHistoryItem)
    }
  }
  
  aiMessages.value = []
}

// 切换设置弹窗
const toggleSettingsModal = () => {
  showSettingsModal.value = !showSettingsModal.value
}

// 保存设置
const saveSettings = () => {
  localStorage.setItem('aiSettings', JSON.stringify(aiSettings.value))
  showSettingsModal.value = false
  console.log('设置已保存:', aiSettings.value)
}

// 处理内容变化
const handleContentChange = (content) => {
  console.log('内容变化:', content)
  if (content.html) {
    lessonContent.value.html = content.html
  } else {
    lessonContent.value = content
  }
}

// 模拟PPT解析完成
setTimeout(() => {
  isLoading.value = false
}, 2000)

// 滑动状态
const startX = ref(0)
const startWidth = ref(0)
const velocity = ref(0)
const lastX = ref(0)
const lastTime = ref(0)
const animationFrameId = ref(null)

// 开始调整大小（鼠标）
const startResize = (e) => {
  e.preventDefault()
  e.stopPropagation()
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'grabbing'
  isResizing.value = true
  startX.value = e.clientX
  startWidth.value = lessonWidth.value
  lastX.value = e.clientX
  lastTime.value = performance.now()
  velocity.value = 0
  document.addEventListener('mousemove', resize)
  document.addEventListener('mouseup', stopResize)
  document.addEventListener('mouseleave', stopResize)
}

// 开始调整大小（触摸）
const startResizeTouch = (e) => {
  e.preventDefault()
  e.stopPropagation()
  document.body.style.userSelect = 'none'
  isResizing.value = true
  const touch = e.touches[0]
  startX.value = touch.clientX
  startWidth.value = lessonWidth.value
  lastX.value = touch.clientX
  lastTime.value = performance.now()
  velocity.value = 0
  document.addEventListener('touchmove', resizeTouch)
  document.addEventListener('touchend', stopResizeTouch)
  document.addEventListener('touchcancel', stopResizeTouch)
}

// 调整大小（鼠标）
const resize = (e) => {
  if (!isResizing.value) return
  e.preventDefault()
  e.stopPropagation()
  const currentTime = performance.now()
  const deltaTime = currentTime - lastTime.value
  const deltaX = e.clientX - lastX.value
  if (deltaTime > 0) {
    velocity.value = deltaX / deltaTime
  }
  lastX.value = e.clientX
  lastTime.value = currentTime
  if (!animationFrameId.value) {
    animationFrameId.value = requestAnimationFrame(() => {
      const contentArea = document.querySelector('.content-area')
      const rect = contentArea.getBoundingClientRect()
      let width = e.clientX - rect.left
      let percentage = (width / rect.width) * 100
      const minWidth = 45
      const maxWidth = 55
      if (percentage < minWidth) {
        const distance = minWidth - percentage
        const resistance = 1 + (distance / 10)
        percentage = minWidth - (distance / resistance)
      } else if (percentage > maxWidth) {
        const distance = percentage - maxWidth
        const resistance = 1 + (distance / 10)
        percentage = maxWidth + (distance / resistance)
      }
      percentage = Math.max(minWidth, Math.min(maxWidth, percentage))
      let newWidth = percentage
      if (Math.abs(newWidth - 50) < 5) {
        newWidth = 50
      }
      lessonWidth.value = newWidth
      pptWidth.value = 100 - newWidth
      pptCollapsed.value = false
      animationFrameId.value = null
    })
  }
}

// 调整大小（触摸）
const resizeTouch = (e) => {
  if (!isResizing.value) return
  e.preventDefault()
  e.stopPropagation()
  const touch = e.touches[0]
  const currentTime = performance.now()
  const deltaTime = currentTime - lastTime.value
  const deltaX = touch.clientX - lastX.value
  if (deltaTime > 0) {
    velocity.value = deltaX / deltaTime
  }
  lastX.value = touch.clientX
  lastTime.value = currentTime
  if (!animationFrameId.value) {
    animationFrameId.value = requestAnimationFrame(() => {
      const contentArea = document.querySelector('.content-area')
      const rect = contentArea.getBoundingClientRect()
      let width = touch.clientX - rect.left
      let percentage = (width / rect.width) * 100
      const minWidth = 45
      const maxWidth = 55
      if (percentage < minWidth) {
        const distance = minWidth - percentage
        const resistance = 1 + (distance / 10)
        percentage = minWidth - (distance / resistance)
      } else if (percentage > maxWidth) {
        const distance = percentage - maxWidth
        const resistance = 1 + (distance / 10)
        percentage = maxWidth + (distance / resistance)
      }
      percentage = Math.max(minWidth, Math.min(maxWidth, percentage))
      let newWidth = percentage
      if (Math.abs(newWidth - 50) < 5) {
        newWidth = 50
      }
      lessonWidth.value = newWidth
      pptWidth.value = 100 - newWidth
      pptCollapsed.value = false
      animationFrameId.value = null
    })
  }
}

// 停止调整大小（鼠标）
const stopResize = () => {
  if (!isResizing.value) return
  isResizing.value = false
  document.body.style.userSelect = ''
  document.body.style.cursor = ''
  applyInertia()
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
  document.removeEventListener('mouseleave', stopResize)
}

// 停止调整大小（触摸）
const stopResizeTouch = () => {
  if (!isResizing.value) return
  isResizing.value = false
  document.body.style.userSelect = ''
  applyInertia()
  document.removeEventListener('touchmove', resizeTouch)
  document.removeEventListener('touchend', stopResizeTouch)
  document.removeEventListener('touchcancel', stopResizeTouch)
}

// 应用惯性效果
const applyInertia = () => {
  const contentArea = document.querySelector('.content-area')
  const rect = contentArea.getBoundingClientRect()
  let currentWidth = lessonWidth.value
  let currentVelocity = velocity.value * 10
  const friction = 0.9
  const minVelocity = 0.1
  const minWidth = 45
  const maxWidth = 55
  const animateInertia = () => {
    if (Math.abs(currentVelocity) < minVelocity) {
      if (Math.abs(currentWidth - 50) < 5) {
        currentWidth = 50
      }
      currentWidth = Math.max(minWidth, Math.min(maxWidth, currentWidth))
      lessonWidth.value = currentWidth
      pptWidth.value = 100 - currentWidth
      pptCollapsed.value = false
      return
    }
    currentVelocity *= friction
    const deltaWidth = (currentVelocity / rect.width) * 100
    currentWidth += deltaWidth
    if (currentWidth < minWidth) {
      const distance = minWidth - currentWidth
      const resistance = 1 + (distance / 10)
      currentWidth = minWidth - (distance / resistance)
      currentVelocity *= 0.8
    } else if (currentWidth > maxWidth) {
      const distance = currentWidth - maxWidth
      const resistance = 1 + (distance / 10)
      currentWidth = maxWidth + (distance / resistance)
      currentVelocity *= 0.8
    }
    currentWidth = Math.max(minWidth, Math.min(maxWidth, currentWidth))
    lessonWidth.value = currentWidth
    pptWidth.value = 100 - currentWidth
    pptCollapsed.value = false
    requestAnimationFrame(animateInertia)
  }
  if (Math.abs(currentVelocity) > minVelocity) {
    requestAnimationFrame(animateInertia)
  }
}

// 挂载时
onMounted(() => {
  const savedSettings = localStorage.getItem('aiSettings')
  if (savedSettings) {
    try {
      aiSettings.value = JSON.parse(savedSettings)
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }
  
  initHistoryList()
  calculateProgress()
  initVoiceRecognition()
  
  // 初始化PPT解析服务
  initPPTParser()
  
  const handleScroll = () => {
    isScrolled.value = window.scrollY > 10
  }
  
  window.addEventListener('scroll', handleScroll)
  
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('msfullscreenchange', handleFullscreenChange)
  
  return () => {
    // 关闭SSE连接
    if (sseConnection.value) {
      sseConnection.value.close()
    }
    
    window.removeEventListener('scroll', handleScroll)
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
    document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.removeEventListener('msfullscreenchange', handleFullscreenChange)
  }
})

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

// 监听全屏状态变化（保留用于处理ESC键）
const handleFullscreenChange = () => {
  const isFull = document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement
  // 如果原生全屏退出，也退出自定义全屏
  if (!isFull && isFullscreen.value) {
    isFullscreen.value = false
  }
}

// 初始化PPT解析服务
const initPPTParser = async () => {
  pptParser.value = new PPTParserService()
  
  // 监听状态事件
  pptParser.value.on('status', (data) => {
    parseStatus.value = data.step
    parseStatusText.value = getStatusText(data.step)
    console.log('[PPTParser] 状态:', data.step)
    
    // 更新总页数
    if (data.total_pages) {
      totalSlides.value = data.total_pages
      totalPages.value = data.total_pages
    }
  })
  
  // 监听进度事件
  pptParser.value.on('progress', (data) => {
    if (data.step === 'tts') {
      parseProgress.value = Math.round((data.current / data.total) * 100)
      currentSlide.value = data.current - 1
      currentPage.value = data.current
      progressPercentage.value = parseProgress.value
      progressPercent.value = parseProgress.value
      console.log('[PPTParser] 进度:', data.current + '/' + data.total)
    }
  })
  
  // 监听完成事件
  pptParser.value.on('done', (data) => {
    isParsingPPT.value = false
    isLoading.value = false
    parseStatusText.value = '解析完成'
    console.log('[PPTParser] 完成，耗时:', data.elapsed_seconds + '秒')
    
    // 处理解析结果
    if (data.output) {
      handleParseResult(data.output)
    }
  })
  
  // 监听错误事件
  pptParser.value.on('error', (data) => {
    isParsingPPT.value = false
    isLoading.value = false
    parseStatusText.value = '解析失败'
    console.error('[PPTParser] 错误:', data.error)
    alert('PPT解析失败: ' + data.error)
  })
  
  // 监听连接事件
  pptParser.value.on('connection', (data) => {
    console.log('[PPTParser] 连接ID:', data.connection_id)
  })
  
  // 建立连接
  try {
    await pptParser.value.connect()
    console.log('[PPTParser] 连接成功')
  } catch (error) {
    console.error('[PPTParser] 连接失败:', error)
  }
}

// 获取状态文本
const getStatusText = (step) => {
  const statusMap = {
    'start': '开始解析...',
    'extract': '提取PPT内容...',
    'convert': '转换格式...',
    'script': '生成教案...',
    'tts': '生成语音...',
    'vector': '构建向量索引...',
    'done': '解析完成'
  }
  return statusMap[step] || '处理中...'
}

// 发送PPT解析请求
const startPPTParse = (filePath, fileType = 'ppt', courseId = 'course_mechanics_001') => {
  if (!pptParser.value || !pptParser.value.isConnected()) {
    console.error('[PPTParser] 服务未连接')
    alert('PPT解析服务未连接，请稍后重试')
    return
  }
  
  isParsingPPT.value = true
  isLoading.value = true
  parseProgress.value = 0
  parseStatusText.value = '开始解析...'
  
  pptParser.value.parsePPT({
    service: 'full_pipeline',
    file_path: filePath,
    file_type: fileType,
    course_id: courseId
  })
}

// 处理解析结果
const handleParseResult = (output) => {
  // 更新教案内容
  if (output.lesson_plan) {
    lessonContent.value = {
      objectives: output.lesson_plan.objectives || [],
      keyPoints: output.lesson_plan.key_points || [],
      teachingSteps: output.lesson_plan.teaching_steps || [],
      exercises: output.lesson_plan.exercises || []
    }
  }
  
  // 更新幻灯片数据
  if (output.slides && Array.isArray(output.slides)) {
    slides.value = output.slides.map((slide, index) => ({
      imageUrl: slide.image_url || slide.imageUrl || '',
      pageNumber: slide.page_number || index + 1,
      elements: slide.elements || []
    }))
  }
  
  // 更新思维导图
  if (output.mindmap) {
    mindMapContent.value = output.mindmap
  }
  
  // 更新课程概要
  if (output.summary) {
    courseSummaryContent.value = output.summary
  }
}

// 清理
onUnmounted(() => {
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
  
  // 断开PPT解析服务
  if (pptParser.value) {
    pptParser.value.disconnect()
    console.log('[PPTParser] 连接已断开')
  }
})
</script>

<style scoped>
/* PPT教学页面容器 */
.ppt-teach-page {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
  background: #F5FBFF;
  font-family: 'PingFang SC', 'Segoe UI', system-ui, -apple-system, sans-serif;
}

/* 背景渐变 */
.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #CDF4FF, #50C878, #CDF4FF);
  background-size: 400% 400%;
  animation: gradientFlow 15s ease infinite;
  z-index: 1;
  opacity: 0.1;
}

/* 背景流动动画 */
@keyframes gradientFlow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* 顶部栏 */
.header {
  height: 60px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  transition: all 0.3s ease;
}

.header-shadow {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.back-button {
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  border-radius: 50%;
}

.back-button:hover {
  transform: translateX(-2px);
  background: rgba(0, 138, 197, 0.05);
}

.back-icon {
  width: 20px;
  height: 20px;
  transition: all 0.2s ease;
}

.back-button:hover .back-icon {
  filter: brightness(0) saturate(100%) invert(29%) sepia(62%) saturate(1865%) hue-rotate(176deg) brightness(93%) contrast(101%);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #008AC5;
  transition: all 0.2s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
}

.avatar:hover {
  box-shadow: 0 0 0 4px rgba(0, 138, 197, 0.2);
  transform: scale(1.05);
}

.avatar-text {
  font-size: 16px;
}

.username {
  font-size: 16px;
  color: #008AC5;
  font-weight: 400;
  font-family: 'PingFang SC', 'Segoe UI', sans-serif;
  white-space: nowrap;
}

/* 主内容区 */
.main-content {
  position: relative;
  z-index: 3;
  flex: 1;
  padding-top: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  overflow: hidden;
}

/* 内容区域 */
.content-area {
  flex: 1;
  display: flex;
  height: 100%;
  position: relative;
  transition: all 0.4s ease;
  order: 1;
  transform: translateZ(0);
  will-change: transform;
  margin: 16px;
  gap: 16px;
}

.content-area.ppt-collapsed {
  flex-direction: column;
}

.main-content .content-area.preview-mode {
  padding: 0;
  margin: 0;
  gap: 0;
  transition: none;
  transform: none;
  will-change: auto;
}

.main-content.preview-mode {
  padding: 16px;
  height: auto;
}

.main-content.preview-mode .content-area {
  margin: 0;
  gap: 16px;
  padding: 0;
  transform: none;
  will-change: auto;
}

.main-content.preview-mode .content-area > .left-section,
.main-content.preview-mode .content-area > .right-section-preview {
  margin: 0;
}

.main-content.preview-mode .content-area > .resizer {
  margin: 0;
}

/* PPT解析控制栏 */
.ppt-parser-control {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: linear-gradient(135deg, #f0f8ff, #e6f3ff);
  border-bottom: 1px solid rgba(0, 138, 197, 0.15);
  gap: 16px;
}

.parser-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.status-label {
  color: #666;
  font-weight: 500;
}

.status-value {
  color: #008AC5;
  font-weight: 600;
  padding: 4px 12px;
  background: rgba(0, 138, 197, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.status-value.parsing {
  color: #ff6b35;
  background: rgba(255, 107, 53, 0.1);
  animation: pulse-status 1.5s ease-in-out infinite;
}

.status-value.connected {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

.progress-value {
  color: #ff6b35;
  font-weight: 700;
  font-size: 13px;
}

@keyframes pulse-status {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.parser-actions {
  display: flex;
  gap: 8px;
}

.parser-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  background: linear-gradient(135deg, #008AC5, #006699);
  color: white;
}

.parser-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.3);
}

.parser-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.7;
}

.parser-btn.secondary {
  background: white;
  color: #008AC5;
  border: 1px solid #008AC5;
}

.parser-btn.secondary:hover:not(:disabled) {
  background: rgba(0, 138, 197, 0.05);
  box-shadow: 0 2px 8px rgba(0, 138, 197, 0.15);
}

/* 面板通用样式 */
.lesson-panel, .ppt-panel {
  background: #FFFFFF;
  border-radius: 12px;
  margin: 0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid #E0F0FF;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  transform: translateZ(0);
  will-change: width;
}

.lesson-panel {
  flex-shrink: 0;
  transition: width 0.3s ease;
}

.ppt-panel {
  flex-shrink: 0;
  transition: all 0.4s ease;
  position: relative;
}

.ppt-panel.collapsed {
  width: 60px !important;
}

/* 面板内容 */
.panel-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  position: relative;
}

.panel-content::-webkit-scrollbar {
  width: 8px;
}

.panel-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.panel-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 课件面板样式 */
.courseware-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #FFFFFF;
}

.courseware-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.courseware-input-wrapper {
  padding: 16px;
  background: #FAFAFA;
  border-top: 1px solid #E8E8E8;
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
  background: rgba(0, 138, 197, 0.2);
  border-radius: 1px;
  transition: background 0.2s;
}

.resizer:hover .resizer-track {
  background: rgba(0, 138, 197, 0.4);
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
  box-shadow: 0 2px 8px rgba(0, 138, 197, 0.3);
  transition: all 0.2s;
}

.resizer:hover .resizer-handle,
.resizer.dragging .resizer-handle {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.4);
}

.resizer-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #008AC5;
}

.resize-indicator {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: #008AC5;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 138, 197, 0.3);
  z-index: 20;
  left: 40px;
}

/* 设置弹窗 - 参考学生端设计，蓝色主题 */
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
  border-bottom: 1px solid rgba(0, 138, 197, 0.1);
  background: #F2FCFF;
}

.export-dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #008AC5;
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
  background: rgba(0, 138, 197, 0.1);
  color: #008AC5;
}

.export-dialog-content {
  padding: 24px;
}

.settings-option {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.settings-label {
  font-size: 14px;
  color: #333;
  cursor: pointer;
  flex: 1;
}

.settings-select {
  padding: 10px 16px;
  border: 2px solid rgba(0, 138, 197, 0.2);
  border-radius: 8px;
  background: white;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
  min-width: 150px;
}

.settings-select:hover {
  border-color: rgba(0, 138, 197, 0.4);
}

.settings-select:focus {
  border-color: #008AC5;
  box-shadow: 0 0 0 4px rgba(0, 138, 197, 0.1);
}

.settings-checkbox {
  width: 18px;
  height: 18px;
  accent-color: #008AC5;
  cursor: pointer;
}

.export-dialog-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(0, 138, 197, 0.1);
  background: #F2FCFF;
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
  background: linear-gradient(135deg, #008AC5, #00A5D8);
  color: white;
}

.confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.3);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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

.setting-item select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.setting-item select:hover {
  border-color: #008AC5;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-label {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.toggle-label:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-label {
  background-color: #008AC5;
}

input:checked + .toggle-label:before {
  transform: translateX(26px);
}

.settings-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.cancel-button {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-button:hover {
  background: #f8f9fa;
  border-color: #ccc;
}

.save-button {
  padding: 8px 16px;
  border: 1px solid #008AC5;
  background: #008AC5;
  color: white;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.save-button:hover {
  background: #006699;
  border-color: #006699;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-area {
    margin: 16px;
    gap: 16px;
  }
  
  .panel-content {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }
  
  .username {
    font-size: 14px;
  }
  
  .avatar {
    width: 36px;
    height: 36px;
  }
  
  .back-button {
    width: 36px;
    height: 36px;
  }
  
  .back-icon {
    width: 18px;
    height: 18px;
  }
  
  .main-content {
    padding-top: 0;
  }
  
  .content-area {
    margin: 12px;
    gap: 12px;
  }
  
  .panel-content {
    padding: 16px;
  }
  
  .content-area {
    flex-direction: column;
    height: calc(100vh - 60px);
    margin: 8px;
    gap: 8px;
  }
  
  .lesson-panel, .ppt-panel {
    width: 100% !important;
    margin: 0;
  }
  
  .resizer {
    width: 100%;
    height: 24px;
    cursor: row-resize;
  }

  .resizer-track {
    width: 100%;
    height: 2px;
  }

  .resize-indicator {
    left: 50%;
    top: 40px;
    transform: translateX(-50%);
  }
}

@media (max-width: 480px) {
  .header {
    padding: 0 12px;
  }
  
  .username {
    font-size: 12px;
  }
  
  .user-info {
    gap: 8px;
  }
  
  .avatar {
    width: 32px;
    height: 32px;
  }
  
  .back-button {
    width: 32px;
    height: 32px;
  }
  
  .back-icon {
    width: 16px;
    height: 16px;
  }
  
  .content-area {
    margin: 8px;
    gap: 8px;
  }
  
  .panel-content {
    padding: 12px;
  }
}

/* 预览模式样式 */
.content-area.preview-mode {
  display: flex;
  flex-direction: row;
  gap: 20px;
}

/* 预览模式 - 左侧区域 */
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

/* PPT预览容器 - 蓝色 */
.ppt-blue-container {
  border: 2px solid #008AC5;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
}

/* PPT播放器包装器 */
.ppt-player-wrapper {
  background: white;
  display: flex;
  flex-direction: column;
}

/* PPT标题栏 - 蓝色 */
.ppt-header-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #008AC5, #006699);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  gap: 16px;
}

.ppt-title-preview {
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
  flex-shrink: 0;
}

.ppt-actions-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.ppt-right-section-preview {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

/* 编辑/预览切换按钮 - 预览模式 */
.edit-preview-tabs-preview {
  display: flex;
  background: white;
  border-radius: 24px;
  padding: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.tab-button-preview {
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

.tab-button-preview.active {
  background: linear-gradient(135deg, #008AC5, #006699);
  color: white;
  box-shadow: 0 2px 4px rgba(0, 138, 197, 0.3);
}

.tab-button-preview:hover:not(.active) {
  background: #f0f8ff;
}

.action-btn-preview {
  padding: 10px 18px;
  border: none;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #008AC5;
  border-radius: 24px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.action-btn-preview:hover {
  background: #f0f8ff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.15);
}

.action-btn-preview.select-element-preview {
  /* 保持默认样式 */
}

.action-btn-preview.icon-btn-preview {
  padding: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn-preview.icon-btn-preview img {
  width: 18px;
  height: 18px;
  filter: invert(38%) sepia(66%) saturate(3865%) hue-rotate(182deg) brightness(92%) contrast(101%);
}

.action-btn-preview.icon-btn-preview img.rotate-180 {
  transform: rotate(180deg);
}

/* 更多按钮 - 透明背景 */
.action-btn-preview.icon-btn-preview.more-btn-preview {
  background: transparent;
  padding: 4px;
}

.action-btn-preview.icon-btn-preview.more-btn-preview:hover {
  background: rgba(255, 255, 255, 0.15);
}

.action-btn-preview.icon-btn-preview.more-btn-preview img {
  width: 24px;
  height: 24px;
  filter: brightness(0) invert(1);
  opacity: 0.9;
}

/* PPT内容区 */
.ppt-content-preview {
  background: #000;
  position: relative;
  flex-shrink: 0;
  padding: 20px;
}

.ppt-image-wrapper-preview {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  border-radius: 12px;
  overflow: hidden;
}

.ppt-image-preview {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 播放覆盖层 */
.play-overlay-preview {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.play-overlay-preview:hover {
  background: rgba(0, 0, 0, 0.4);
}

.play-icon-preview {
  width: 64px;
  height: 64px;
  filter: brightness(0) invert(1);
}

/* 视频控制栏 - 蓝色主题 */
.video-controls-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: #F2FCFF;
}

.control-btn-preview {
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

.control-btn-preview:hover {
  background: rgba(0, 138, 197, 0.1);
}

.control-btn-preview:hover img {
  filter: none;
  opacity: 1;
}

.control-btn-preview img {
  width: 18px;
  height: 18px;
  object-fit: contain;
  filter: grayscale(100%) brightness(0.5);
  opacity: 0.7;
}

/* 播放图标稍微缩小 */
.control-btn-preview.play-pause-preview img[src*="ic_play"] {
  width: 16px;
  height: 16px;
}

/* 全屏图标稍微缩小 */
.control-btn-preview.fullscreen-preview img[src*="ic-fullscreen"] {
  width: 16px;
  height: 16px;
}

/* 进度条容器 */
.progress-container-preview {
  flex: 1;
  height: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.progress-bar-preview {
  width: 100%;
  height: 4px;
  background: rgba(0, 138, 197, 0.2);
  border-radius: 2px;
  overflow: visible;
  position: relative;
  cursor: pointer;
  transition: height 0.2s ease;
}

.progress-bar-preview:hover {
  height: 6px;
}

.progress-bar-preview.dragging {
  height: 6px;
}

.progress-filled-preview {
  height: 100%;
  background: linear-gradient(90deg, #008AC5, #00A3E0);
  border-radius: 2px;
  transition: width 0.15s ease-out;
}

.progress-bar-preview:hover .progress-filled-preview,
.progress-bar-preview.dragging .progress-filled-preview {
  border-radius: 3px;
}

.progress-handle-preview {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: #008AC5;
  border-radius: 50%;
  cursor: grab;
  opacity: 0;
  transition: opacity 0.2s;
  box-shadow: 0 2px 6px rgba(0, 138, 197, 0.3);
  z-index: 1;
}

.progress-bar-preview:hover .progress-handle-preview,
.progress-bar-preview.dragging .progress-handle-preview {
  opacity: 1;
}

/* 时间显示 */
.time-display-preview {
  font-size: 14px;
  color: #008AC5;
  font-weight: 500;
  user-select: none;
}

/* 速度按钮 */
.speed-btn-preview {
  font-size: 12px;
  font-weight: 600;
  color: #008AC5;
  width: auto;
  min-width: 44px;
  padding: 0 8px;
}

.speed-btn-preview:hover {
  background: rgba(0, 138, 197, 0.1);
  color: #008AC5;
}

/* 课程文档包装器 */
.course-document-wrapper-preview {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
}

/* 课程文档 */
.course-document-preview {
  padding: 24px;
  transition: max-height 0.3s ease;
}

.course-document-preview.collapsed {
  max-height: 0;
  padding: 0;
  overflow: hidden;
}

.doc-section-preview {
  margin-bottom: 24px;
}

.doc-title-preview {
  font-size: 18px;
  font-weight: 600;
  color: #008AC5;
  margin: 0 0 8px 0;
}

.doc-subtitle-preview {
  font-size: 14px;
  color: #333;
  margin: 0 0 12px 0;
  line-height: 1.6;
}

.doc-list-preview {
  margin: 0;
  padding-left: 20px;
}

.doc-list-preview li {
  font-size: 14px;
  color: #555;
  line-height: 1.8;
  margin-bottom: 8px;
}

.highlight-preview {
  color: #008AC5;
  font-weight: 600;
}

/* 展开/折叠控制 */
.doc-expand-control-preview {
  text-align: center;
  padding: 16px;
  border-top: 1px solid rgba(0, 138, 197, 0.1);
  background: #F2FCFF;
}

/* 展开/折叠按钮 */
.doc-expand-btn-preview {
  background: linear-gradient(135deg, #008AC5, #006699);
  color: white;
  border: none;
  padding: 8px 24px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 138, 197, 0.2);
}

.doc-expand-btn-preview:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.3);
}

/* 预览模式 - 右侧区域 */
.right-section-preview {
  background: #FFFFFF;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
  height: 100%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: none;
  transition: none;
}

/* 全屏模式样式 */
.ppt-blue-container:fullscreen,
.ppt-blue-container:-webkit-full-screen,
.ppt-blue-container:-ms-fullscreen {
  background: #000;
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
}

.ppt-blue-container:fullscreen .ppt-player-wrapper,
.ppt-blue-container:-webkit-full-screen .ppt-player-wrapper,
.ppt-blue-container:-ms-fullscreen .ppt-player-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #000;
}

.ppt-blue-container:fullscreen .ppt-header-preview,
.ppt-blue-container:-webkit-full-screen .ppt-header-preview,
.ppt-blue-container:-ms-fullscreen .ppt-header-preview {
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

.ppt-blue-container:fullscreen .edit-preview-tabs-preview,
.ppt-blue-container:-webkit-full-screen .edit-preview-tabs-preview,
.ppt-blue-container:-ms-full-screen .edit-preview-tabs-preview {
  background: rgba(255, 255, 255, 0.2);
}

.ppt-blue-container:fullscreen .tab-button-preview,
.ppt-blue-container:-webkit-full-screen .tab-button-preview,
.ppt-blue-container:-ms-full-screen .tab-button-preview {
  color: rgba(255, 255, 255, 0.8);
}

.ppt-blue-container:fullscreen .action-btn-preview,
.ppt-blue-container:-webkit-full-screen .action-btn-preview,
.ppt-blue-container:-ms-full-screen .action-btn-preview {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.ppt-blue-container:fullscreen .action-btn-preview:hover,
.ppt-blue-container:-webkit-full-screen .action-btn-preview:hover,
.ppt-blue-container:-ms-full-screen .action-btn-preview:hover {
  background: rgba(255, 255, 255, 0.25);
}

.ppt-blue-container:fullscreen .action-btn-preview.icon-btn-preview img,
.ppt-blue-container:-webkit-full-screen .action-btn-preview.icon-btn-preview img,
.ppt-blue-container:-ms-full-screen .action-btn-preview.icon-btn-preview img {
  filter: brightness(0) invert(1);
  opacity: 1;
}

.ppt-blue-container:fullscreen .tab-button-preview.active,
.ppt-blue-container:-webkit-full-screen .tab-button-preview.active,
.ppt-blue-container:-ms-full-screen .tab-button-preview.active {
  background: linear-gradient(135deg, #008AC5, #006699);
  color: white;
  box-shadow: 0 2px 4px rgba(0, 138, 197, 0.3);
}

.ppt-blue-container:fullscreen .tab-button-preview:hover:not(.active),
.ppt-blue-container:-webkit-full-screen .tab-button-preview:hover:not(.active),
.ppt-blue-container:-ms-full-screen .tab-button-preview:hover:not(.active) {
  background: rgba(255, 255, 255, 0.1);
}

.ppt-blue-container:fullscreen .ppt-content-preview,
.ppt-blue-container:-webkit-full-screen .ppt-content-preview,
.ppt-blue-container:-ms-fullscreen .ppt-content-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  padding: 80px 40px;
}

.ppt-blue-container:fullscreen .ppt-image-wrapper-preview,
.ppt-blue-container:-webkit-full-screen .ppt-image-wrapper-preview,
.ppt-blue-container:-ms-fullscreen .ppt-image-wrapper-preview {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.ppt-blue-container:fullscreen .ppt-image-preview,
.ppt-blue-container:-webkit-full-screen .ppt-image-preview,
.ppt-blue-container:-ms-fullscreen .ppt-image-preview {
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: calc(100vh - 160px);
  object-fit: contain;
}

.ppt-blue-container:fullscreen .play-overlay-preview,
.ppt-blue-container:-webkit-full-screen .play-overlay-preview,
.ppt-blue-container:-ms-fullscreen .play-overlay-preview {
  background: rgba(0, 0, 0, 0.3);
}

.ppt-blue-container:fullscreen .play-icon-preview,
.ppt-blue-container:-webkit-full-screen .play-icon-preview,
.ppt-blue-container:-ms-fullscreen .play-icon-preview {
  width: 100px;
  height: 100px;
}

.ppt-blue-container:fullscreen .video-controls-preview,
.ppt-blue-container:-webkit-full-screen .video-controls-preview,
.ppt-blue-container:-ms-fullscreen .video-controls-preview {
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

.ppt-blue-container:fullscreen .control-btn-preview,
.ppt-blue-container:-webkit-full-screen .control-btn-preview,
.ppt-blue-container:-ms-fullscreen .control-btn-preview {
  color: #fff;
}

.ppt-blue-container:fullscreen .control-btn-preview:hover,
.ppt-blue-container:-webkit-full-screen .control-btn-preview:hover,
.ppt-blue-container:-ms-fullscreen .control-btn-preview:hover {
  background: rgba(255, 255, 255, 0.1);
}

.ppt-blue-container:fullscreen .control-btn-preview img,
.ppt-blue-container:-webkit-full-screen .control-btn-preview img,
.ppt-blue-container:-ms-fullscreen .control-btn-preview img {
  filter: brightness(0) invert(1);
  opacity: 1;
}

.ppt-blue-container:fullscreen .time-display-preview,
.ppt-blue-container:-webkit-full-screen .time-display-preview,
.ppt-blue-container:-ms-fullscreen .time-display-preview {
  color: #fff;
  font-weight: 500;
}

.ppt-blue-container:fullscreen .progress-bar-preview,
.ppt-blue-container:-webkit-full-screen .progress-bar-preview,
.ppt-blue-container:-ms-fullscreen .progress-bar-preview {
  background: rgba(255, 255, 255, 0.3);
}

.ppt-blue-container:fullscreen .progress-filled-preview,
.ppt-blue-container:-webkit-full-screen .progress-filled-preview,
.ppt-blue-container:-ms-fullscreen .progress-filled-preview {
  background: linear-gradient(90deg, #008AC5, #00A3E0);
}

.ppt-blue-container:fullscreen .speed-btn-preview,
.ppt-blue-container:-webkit-full-screen .speed-btn-preview,
.ppt-blue-container:-ms-fullscreen .speed-btn-preview {
  color: #fff;
}

.ppt-blue-container:fullscreen .speed-btn-preview:hover,
.ppt-blue-container:-webkit-full-screen .speed-btn-preview:hover,
.ppt-blue-container:-ms-full-screen .speed-btn-preview:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 全屏模式鼠标移动时显示控制栏 */
.ppt-blue-container:fullscreen:hover .ppt-header-preview,
.ppt-blue-container:fullscreen:hover .video-controls-preview,
.ppt-blue-container:-webkit-full-screen:hover .ppt-header-preview,
.ppt-blue-container:-webkit-full-screen:hover .video-controls-preview,
.ppt-blue-container:-ms-full-screen:hover .ppt-header-preview,
.ppt-blue-container:-ms-full-screen:hover .video-controls-preview {
  opacity: 1;
}

.ppt-blue-container:fullscreen .ppt-header-preview,
.ppt-blue-container:fullscreen .video-controls-preview,
.ppt-blue-container:-webkit-full-screen .ppt-header-preview,
.ppt-blue-container:-webkit-full-screen .video-controls-preview,
.ppt-blue-container:-ms-full-screen .ppt-header-preview,
.ppt-blue-container:-ms-full-screen .video-controls-preview {
  opacity: 0;
  transition: opacity 0.3s;
}

/* 预览模式响应式设计 */
@media (max-width: 768px) {
  .content-area.preview-mode {
    flex-direction: column;
    height: calc(100vh - 60px);
    margin: 8px;
    gap: 8px;
  }

  .left-section,
  .right-section-preview {
    width: 100% !important;
  }

  .resizer {
    width: 100%;
    height: 24px;
    cursor: row-resize;
  }

  .resizer-track {
    width: 100%;
    height: 2px;
  }

  .resize-indicator {
    left: 50%;
    top: 40px;
    transform: translateX(-50%);
  }

  .ppt-header-preview {
    padding: 12px 16px;
  }

  .ppt-title-preview {
    font-size: 14px;
  }

  .action-btn-preview {
    padding: 6px 12px;
    font-size: 13px;
  }

  .action-btn-preview.icon-btn-preview {
    width: 36px;
    height: 36px;
  }

  .course-document-preview {
    padding: 16px;
  }

  .doc-title-preview {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .ppt-header-preview {
    padding: 10px 12px;
  }

  .ppt-actions-preview {
    gap: 8px;
  }

  .action-btn-preview {
    padding: 6px 10px;
    font-size: 12px;
  }

  .action-btn-preview.icon-btn-preview {
    width: 32px;
    height: 32px;
  }
}

/* 全新全屏界面样式 */
.fullscreen-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #F0F8FF;
  display: flex;
  flex-direction: column;
  z-index: 9999;
}

.fullscreen-header {
  height: 80px;
  background: linear-gradient(135deg, #008AC5, #006699);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 2px solid rgba(0, 138, 197, 0.1);
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
  border-left: 1px solid rgba(0, 138, 197, 0.1);
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
  box-shadow: 0 2px 8px rgba(0, 138, 197, 0.3);
  transition: all 0.2s;
  z-index: 101;
  cursor: pointer;
}

.sidebar-toggle:hover {
  background: linear-gradient(135deg, #008AC5, #006699);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.4);
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
  background: #F0F8FF;
  border-bottom: 2px solid rgba(0, 138, 197, 0.15);
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
  color: #008AC5;
}

.sidebar-tab.active {
  color: #006699;
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
  background: linear-gradient(90deg, #008AC5, #006699);
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

.sidebar-chat-messages::-webkit-scrollbar {
  width: 6px;
}

.sidebar-chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-chat-messages::-webkit-scrollbar-thumb {
  background: rgba(0, 138, 197, 0.2);
  border-radius: 3px;
}

/* 功能按钮区 */
.chat-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 138, 197, 0.15);
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
  background: rgba(0, 138, 197, 0.1);
}

.action-icon-btn:hover img {
  filter: brightness(0) saturate(100%) invert(31%) sepia(92%) saturate(1783%) hue-rotate(179deg) brightness(98%) contrast(101%);
  opacity: 1;
}

.action-icon-btn img {
  width: 22px;
  height: 22px;
  filter: grayscale(100%) brightness(0.5);
  opacity: 0.7;
}

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
  color: #006699;
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
  background: linear-gradient(135deg, #008AC5, #006699);
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
  background: linear-gradient(135deg, #FFFFFF, #F0F8FF);
  color: #333;
  border-top-left-radius: 4px;
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
  background: linear-gradient(135deg, #008AC5, #006699);
  color: white;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 138, 197, 0.2);
}

.user-msg .message-bubble::after {
  content: '';
  position: absolute;
  right: -8px;
  top: 16px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 8px solid #008AC5;
}

/* 历史对话列表 */
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
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.15);
}

.history-icon {
  width: 32px;
  height: 32px;
  background: rgba(0, 138, 197, 0.1);
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
  border-bottom: 1px solid rgba(0, 138, 197, 0.15);
}

.detail-title-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: #006699;
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
  background: rgba(0, 138, 197, 0.2);
  border-radius: 3px;
}

/* 课程概要内容 */
.summary-content {
  background: white;
  border-radius: 12px;
  padding: 20px;
}

.summary-title {
  font-size: 16px;
  font-weight: 600;
  color: #006699;
  margin: 0 0 16px 0;
}

.summary-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0, 138, 197, 0.1);
}

.summary-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.summary-section h4 {
  font-size: 15px;
  font-weight: 600;
  color: #006699;
  margin: 0 0 8px 0;
}

.summary-section p {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.8;
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
  box-shadow: 0 2px 8px rgba(0, 138, 197, 0.2);
  transition: all 0.2s ease;
  opacity: 0;
  z-index: 50;
}

.ppt-display-area:hover .nav-btn {
  opacity: 1;
}

.nav-btn:hover {
  background: linear-gradient(135deg, #008AC5, #006699);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.3);
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
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.15);
  z-index: 50;
}

.zoom-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: linear-gradient(135deg, #008AC5, #006699);
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
  background: linear-gradient(135deg, #006699, #004C6E);
  transform: scale(1.1);
}

.zoom-level {
  font-size: 14px;
  font-weight: 600;
  color: #006699;
  min-width: 50px;
  text-align: center;
}

/* 底部区域 */
.fullscreen-footer {
  background: linear-gradient(135deg, #F0F8FF, #FFFFFF);
  border-top: 2px solid rgba(0, 138, 197, 0.1);
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
  border-top: 1px solid rgba(0, 138, 197, 0.1);
  background: #F0F8FF;
}

.sidebar-input-area .input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #FFFFFF;
  border: 2px solid rgba(0, 138, 197, 0.15);
  border-radius: 50px;
  padding: 8px 12px;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.sidebar-input-area .input-wrapper:focus-within {
  border-color: #008AC5;
  box-shadow: 0 0 0 4px rgba(0, 138, 197, 0.1);
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
  background: rgba(0, 138, 197, 0.1);
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
  background: linear-gradient(135deg, #008AC5, #006699);
  transform: scale(1.1);
}

.sidebar-input-area .voice-btn:hover .voice-icon {
  filter: brightness(0) invert(1);
}

.sidebar-input-area .voice-btn:active {
  transform: scale(0.95);
}

.sidebar-input-area .voice-btn.active {
  background: linear-gradient(135deg, #008AC5, #006699);
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
    box-shadow: 0 0 0 0 rgba(0, 138, 197, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(0, 138, 197, 0);
  }
}

.sidebar-input-area .send-btn {
  padding: 6px;
  width: 32px;
  height: 32px;
  min-width: auto;
  border: none;
  background: linear-gradient(135deg, #008AC5, #006699);
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
  background: linear-gradient(135deg, #006699, #004C6E);
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.3);
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
  background: rgba(0, 138, 197, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.fullscreen-controls .control-btn:hover {
  background: linear-gradient(135deg, #008AC5, #006699);
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
  background: rgba(0, 138, 197, 0.2);
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
  background: linear-gradient(90deg, #008AC5, #006699);
  border-radius: 3px;
  transition: width 0.15s ease-out;
}

.fullscreen-controls .progress-handle {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 14px;
  height: 14px;
  background: #008AC5;
  border-radius: 50%;
  cursor: grab;
  opacity: 0;
  transition: opacity 0.2s ease, transform 0.2s ease, width 0.2s ease, height 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 138, 197, 0.4);
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
  box-shadow: 0 4px 12px rgba(0, 138, 197, 0.6);
}

.fullscreen-controls .progress-bar:hover .progress-handle {
  transform: translate(-50%, -50%) scale(1.1);
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
  background: rgba(0, 138, 197, 0.1);
  color: #666;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 20px;
  transition: all 0.2s;
}

.fullscreen-controls .speed-btn:hover {
  background: linear-gradient(135deg, #008AC5, #006699);
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
}
</style>
