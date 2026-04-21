/**
 * PPT解析服务
 * 用于与后端WebSocket API通信，支持真实后端和Mock服务
 * 
 * 使用方法：
 * 1. 引入服务: import { PPTParserService } from '@/services/pptParserService'
 * 2. 创建实例: const parser = new PPTParserService()
 * 3. 连接: await parser.connect()
 * 4. 监听事件: parser.on('status', callback)
 * 5. 发送请求: parser.parsePPT(requestData)
 */

// API配置
const API_CONFIG = {
  // WebSocket地址 - 根据环境自动切换
  WS_URL: process.env.VUE_APP_MOCK_MODE === 'true' 
    ? 'ws://127.0.0.1:8001/api/v1/ws/script'  // Mock服务
    : 'ws://localhost:8001/api/v1/ws/script', // 真实后端
  
  // 默认请求参数
  defaults: {
    service: 'full_pipeline',
    output_raw_json_path: 'sandbox/output.json',
    output_text_path: 'sandbox/output.txt',
    voice: 'zh-CN-XiaoxiaoNeural',
    enable_script_llm: true
  }
};

/**
 * PPT解析服务类
 */
export class PPTParserService {
  constructor(options = {}) {
    this.ws = null;
    this.url = options.url || API_CONFIG.WS_URL;
    this.messageHandlers = new Map();
    this.connectionState = 'disconnected'; // disconnected, connecting, connected, error
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 3;
    this.reconnectDelay = options.reconnectDelay || 3000;
    this.connectionId = null;
    this.startTime = null;
  }

  /**
   * 建立WebSocket连接
   */
  connect() {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        console.log('[PPTParser] 已经连接');
        resolve();
        return;
      }

      this.connectionState = 'connecting';
      console.log(`[PPTParser] 正在连接到 ${this.url}`);

      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          this.connectionState = 'connected';
          this.reconnectAttempts = 0;
          console.log('[PPTParser] WebSocket连接已建立');
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('[PPTParser] 解析消息失败:', error);
            this.emit('error', { error: '消息解析失败', details: error.message });
          }
        };

        this.ws.onclose = (event) => {
          this.connectionState = 'disconnected';
          console.log(`[PPTParser] WebSocket连接已关闭: code=${event.code}`);
          this.emit('disconnected', { code: event.code });
          
          // 尝试重连
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`[PPTParser] ${this.reconnectDelay}ms后尝试第${this.reconnectAttempts}次重连...`);
            setTimeout(() => this.connect(), this.reconnectDelay);
          }
        };

        this.ws.onerror = (error) => {
          this.connectionState = 'error';
          console.error('[PPTParser] WebSocket错误:', error);
          this.emit('error', { error: '连接错误', details: error });
          reject(error);
        };

        // 等待连接成功消息
        const checkConnection = (data) => {
          if (data.type === 'connection' && data.status === 'connected') {
            this.connectionId = data.connection_id;
            this.off('connection', checkConnection);
            resolve(data);
          }
        };
        this.on('connection', checkConnection);

      } catch (error) {
        this.connectionState = 'error';
        console.error('[PPTParser] 创建连接失败:', error);
        reject(error);
      }
    });
  }

  /**
   * 处理收到的消息
   */
  handleMessage(data) {
    // 触发对应类型的处理器
    const handler = this.messageHandlers.get(data.type);
    if (handler) {
      handler.forEach(cb => cb(data));
    }

    // 触发通用消息处理器
    const allHandler = this.messageHandlers.get('*');
    if (allHandler) {
      allHandler.forEach(cb => cb(data));
    }

    // 记录处理时间
    if (data.type === 'done') {
      const elapsed = this.startTime ? ((Date.now() - this.startTime) / 1000).toFixed(2) : null;
      console.log(`[PPTParser] 流程完成，总耗时: ${elapsed}s`);
    }
  }

  /**
   * 注册事件监听器
   * @param {string} type - 事件类型: 'connection' | 'status' | 'progress' | 'done' | 'error' | '*'
   * @param {function} callback - 回调函数
   */
  on(type, callback) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }
    this.messageHandlers.get(type).add(callback);
    
    // 返回取消订阅函数
    return () => this.off(type, callback);
  }

  /**
   * 移除事件监听器
   */
  off(type, callback) {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.delete(callback);
    }
  }

  /**
   * 触发事件
   */
  emit(type, data) {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.forEach(cb => cb(data));
    }
  }

  /**
   * 发送PPT解析请求
   * @param {Object} requestData - 请求参数
   */
  parsePPT(requestData) {
    if (!this.isConnected()) {
      console.error('[PPTParser] WebSocket未连接');
      this.emit('error', { error: 'WebSocket未连接' });
      return false;
    }

    // 合并默认参数
    const fullRequest = {
      ...API_CONFIG.defaults,
      ...requestData,
      lesson_id: requestData.lesson_id || `lesson_${Date.now()}`
    };

    this.startTime = Date.now();
    console.log('[PPTParser] 发送解析请求:', fullRequest);
    
    this.ws.send(JSON.stringify(fullRequest));
    return true;
  }

  /**
   * 快速测试模式（5页）
   */
  parsePPTFast(requestData) {
    return this.parsePPT({
      ...requestData,
      mode: 'fast'
    });
  }

  /**
   * 模拟特定错误场景（仅用于测试）
   * @param {string} errorType - 错误类型: 'validation' | 'parse' | 'tts' | 'qdrant'
   */
  simulateError(errorType, requestData = {}) {
    return this.parsePPT({
      ...requestData,
      simulate_error: errorType
    });
  }

  /**
   * 检查连接状态
   */
  isConnected() {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * 获取连接状态
   */
  getState() {
    return {
      state: this.connectionState,
      connectionId: this.connectionId,
      isConnected: this.isConnected()
    };
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connectionState = 'disconnected';
    this.connectionId = null;
    this.messageHandlers.clear();
    console.log('[PPTParser] 连接已断开');
  }
}

/**
 * 便捷的解析函数（一次性使用）
 * @param {Object} requestData - 请求参数
 * @param {Object} callbacks - 回调函数 { onStatus, onProgress, onDone, onError }
 * @returns {Promise} - 解析完成的Promise
 */
export function parsePPT(requestData, callbacks = {}) {
  return new Promise((resolve, reject) => {
    const parser = new PPTParserService();
    
    parser.on('status', (data) => {
      callbacks.onStatus?.(data);
    });
    
    parser.on('progress', (data) => {
      callbacks.onProgress?.(data);
    });
    
    parser.on('done', (data) => {
      callbacks.onDone?.(data);
      parser.disconnect();
      resolve(data);
    });
    
    parser.on('error', (data) => {
      callbacks.onError?.(data);
      parser.disconnect();
      reject(new Error(data.error));
    });
    
    parser.connect()
      .then(() => parser.parsePPT(requestData))
      .catch(reject);
  });
}

/**
 * 创建带进度追踪的解析器
 * 适用于需要实时显示进度的场景
 */
export function createProgressTracker() {
  const progress = {
    totalPages: 0,
    currentPage: 0,
    ttsProgress: 0,
    currentStep: '',
    startTime: null,
    elapsedTime: 0,
    isComplete: false,
    error: null
  };

  const service = new PPTParserService();

  service.on('status', (data) => {
    progress.currentStep = data.step;
    
    if (data.step === 'start') {
      progress.startTime = Date.now();
    }
    
    if (data.total_pages) {
      progress.totalPages = data.total_pages;
    }
  });

  service.on('progress', (data) => {
    if (data.step === 'tts') {
      progress.currentPage = data.current;
      progress.totalPages = data.total;
      progress.ttsProgress = Math.round((data.current / data.total) * 100);
    }
  });

  service.on('done', () => {
    progress.isComplete = true;
    if (progress.startTime) {
      progress.elapsedTime = (Date.now() - progress.startTime) / 1000;
    }
  });

  service.on('error', (data) => {
    progress.error = data.error;
  });

  return {
    service,
    progress,
    getProgress() {
      if (progress.startTime && !progress.isComplete) {
        progress.elapsedTime = (Date.now() - progress.startTime) / 1000;
      }
      return { ...progress };
    }
  };
}

export default PPTParserService;
