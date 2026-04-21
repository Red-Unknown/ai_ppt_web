/**
 * PPT解析API Mock服务器
 * 实现 WebSocket 接口: ws://127.0.0.1:8001/api/v1/ws/script
 * 服务名: full_pipeline
 */

const WebSocket = require('ws');
const http = require('http');
const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const path = require('path');

const {
  MOCK_CONFIG,
  generateParseResult,
  generateTextContent,
  generateScriptContent,
  generateMindMapData,
  generateTTSTasks,
  generatePostgresResult,
  generateQdrantResult,
  generateErrorResponse
} = require('./data/mockData');

// 配置
const PORT = process.env.MOCK_PORT || 8001;
const HOST = process.env.MOCK_HOST || '127.0.0.1';

// 创建Express应用
const app = express();
app.use(cors());
app.use(express.json());

// 静态文件服务（用于测试页面）
app.use('/test', express.static(path.join(__dirname, 'public')));

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'ppt-parser-mock', timestamp: new Date().toISOString() });
});

// API信息端点
app.get('/api/v1/info', (req, res) => {
  res.json({
    name: 'PPT Parser Mock API',
    version: '1.0.0',
    endpoints: {
      websocket: '/api/v1/ws/script',
      health: '/health',
      upload: '/api/v1/lesson/upload'
    },
    services: ['full_pipeline']
  });
});

// 文件上传端点 - 根据接口文档实现
app.post('/api/v1/lesson/upload', (req, res) => {
  // 模拟文件上传处理
  const fileName = req.headers['x-file-name'] || 'uploaded_file.ppt';
  const fileId = uuidv4().replace(/-/g, '');
  const fileExt = fileName.split('.').pop().toLowerCase();
  
  // 支持的文件类型
  const allowedTypes = ['ppt', 'pptx', 'pdf'];
  
  if (!allowedTypes.includes(fileExt)) {
    return res.status(400).json({
      detail: `Unsupported file type: .${fileExt}. Allowed: ['.pdf', '.ppt', '.pptx']`
    });
  }
  
  // 生成模拟响应 - 根据 file-upload-api.md 文档
  const response = {
    code: 200,
    msg: 'Upload successful',
    data: {
      fileId: fileId,
      fileName: fileName,
      fileType: fileExt,
      fileSize: 14381283, // 模拟文件大小
      fileUrl: `uploads/lesson_files/${fileId}.${fileExt}`,
      courseId: req.body?.course_id || 'course_mechanics_001',
      schoolId: req.body?.school_id || 'SCH001',
      uploadedAt: new Date().toISOString()
    }
  };
  
  console.log(`[Upload] 文件上传成功: ${fileName} -> ${response.data.fileUrl}`);
  
  res.json(response);
});

// 创建HTTP服务器
const server = http.createServer(app);

// 创建WebSocket服务器
const wss = new WebSocket.Server({ 
  server,
  path: '/api/v1/ws/script'
});

// 存储活跃连接
const activeConnections = new Map();

/**
 * 发送消息到客户端
 */
function sendMessage(ws, data) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
  }
}

/**
 * 延迟函数
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 验证请求参数
 */
function validateRequest(data) {
  const errors = [];
  
  if (!data.service || data.service !== 'full_pipeline') {
    errors.push('service 必须是 "full_pipeline"');
  }
  
  if (!data.file_path) {
    errors.push('file_path 是必填字段');
  }
  
  if (!data.file_type || !['ppt', 'pptx', 'pdf'].includes(data.file_type)) {
    errors.push('file_type 必须是 ppt/pptx/pdf 之一');
  }
  
  if (!data.output_raw_json_path) {
    errors.push('output_raw_json_path 是必填字段');
  }
  
  if (!data.output_text_path) {
    errors.push('output_text_path 是必填字段');
  }
  
  if (!data.course_id) {
    errors.push('course_id 是必填字段');
  }
  
  return errors;
}

/**
 * 模拟全流程处理
 */
async function simulateFullPipeline(ws, requestData, connectionId) {
  const startTime = Date.now();
  const pageCount = requestData.simulate_pages || MOCK_CONFIG.defaultPages;
  const shouldError = requestData.simulate_error || null;
  
  try {
    // 1. 发送开始状态
    await delay(MOCK_CONFIG.delays.statusStart);
    sendMessage(ws, {
      type: 'status',
      step: 'start',
      message: '开始执行全流程',
      lesson_id: requestData.lesson_id,
      timestamp: new Date().toISOString()
    });

    // 检查是否模拟验证错误
    if (shouldError === 'validation') {
      await delay(500);
      sendMessage(ws, {
        type: 'error',
        step: 'validate_course',
        error: 'course_id 不存在: course_xxx。请先在 courses 表创建该课程。',
        error_type: 'CourseNotFoundError'
      });
      return;
    }

    // 2. VL LLM解析完成
    await delay(MOCK_CONFIG.delays.vlLLMParse);
    const parseResult = generateParseResult(requestData.file_path, pageCount);
    sendMessage(ws, {
      type: 'status',
      step: 'vl_llm_parse_complete',
      path: requestData.output_raw_json_path,
      lesson_id: requestData.lesson_id,
      message: '课件解析完成（含图片理解）',
      total_pages: pageCount,
      timestamp: new Date().toISOString()
    });

    // 检查是否模拟解析错误
    if (shouldError === 'parse') {
      await delay(500);
      sendMessage(ws, {
        type: 'error',
        ...generateErrorResponse('vl_llm_parse', 'parse_error')
      });
      return;
    }

    // 3. 文本提取完成
    await delay(MOCK_CONFIG.delays.contentText);
    const textContent = generateTextContent(requestData.output_text_path, pageCount);
    sendMessage(ws, {
      type: 'status',
      step: 'content_text',
      pages: pageCount,
      path: requestData.output_text_path,
      timestamp: new Date().toISOString()
    });

    // 4. 讲稿生成完成
    await delay(MOCK_CONFIG.delays.script);
    const scriptContent = generateScriptContent(pageCount, requestData.enable_script_llm !== false);
    sendMessage(ws, {
      type: 'status',
      step: 'script',
      generated: scriptContent.generated,
      llm: scriptContent.llm,
      timestamp: new Date().toISOString()
    });

    // 5. PostgreSQL插入完成
    await delay(MOCK_CONFIG.delays.postgres);
    const postgresResult = generatePostgresResult(pageCount);
    sendMessage(ws, {
      type: 'status',
      step: 'postgres_cir_base',
      inserted_nodes: postgresResult.inserted_nodes,
      timestamp: new Date().toISOString()
    });

    // 6. 思维导图生成完成
    await delay(MOCK_CONFIG.delays.mindMap);
    const mindMapData = generateMindMapData(pageCount);
    sendMessage(ws, {
      type: 'status',
      step: 'mind_map',
      keywords_count: mindMapData.keywords_count,
      timestamp: new Date().toISOString()
    });

    // 7. TTS进度（逐页发送）
    const ttsTasks = generateTTSTasks(pageCount, requestData.voice || 'zh-CN-XiaoxiaoNeural');
    
    // 检查是否模拟TTS错误
    if (shouldError === 'tts') {
      await delay(MOCK_CONFIG.delays.ttsPerPage);
      sendMessage(ws, {
        type: 'progress',
        step: 'tts',
        current: 1,
        total: pageCount
      });
      await delay(MOCK_CONFIG.delays.ttsPerPage);
      sendMessage(ws, {
        type: 'error',
        ...generateErrorResponse('tts', 'tts_error')
      });
      return;
    }

    for (let i = 1; i <= pageCount; i++) {
      await delay(MOCK_CONFIG.delays.ttsPerPage);
      sendMessage(ws, {
        type: 'progress',
        step: 'tts',
        current: i,
        total: pageCount,
        page_info: {
          page_number: i,
          task_id: ttsTasks[i - 1].task_id,
          audio_url: ttsTasks[i - 1].audio_url
        }
      });
    }

    // 8. TTS完成
    sendMessage(ws, {
      type: 'status',
      step: 'tts_done',
      total_tasks: pageCount,
      timestamp: new Date().toISOString()
    });

    // 9. Qdrant索引完成
    await delay(MOCK_CONFIG.delays.qdrant);
    
    // 检查是否模拟Qdrant错误
    if (shouldError === 'qdrant') {
      sendMessage(ws, {
        type: 'error',
        ...generateErrorResponse('qdrant', 'qdrant_error')
      });
      return;
    }

    const qdrantResult = generateQdrantResult(pageCount);
    sendMessage(ws, {
      type: 'status',
      step: 'qdrant',
      ok: qdrantResult.ok,
      log: qdrantResult.log,
      points_count: qdrantResult.points_count,
      timestamp: new Date().toISOString()
    });

    // 10. 流程完成
    const elapsedSeconds = (Date.now() - startTime) / 1000;
    sendMessage(ws, {
      type: 'done',
      step: 'end',
      lesson_id: requestData.lesson_id,
      elapsed_seconds: parseFloat(elapsedSeconds.toFixed(3)),
      summary: {
        total_pages: pageCount,
        nodes_inserted: postgresResult.inserted_nodes,
        keywords_extracted: mindMapData.keywords_count,
        tts_tasks: pageCount,
        vectors_indexed: qdrantResult.points_count
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error(`[${connectionId}] 处理错误:`, error);
    sendMessage(ws, {
      type: 'error',
      step: 'internal',
      error: error.message,
      error_type: error.name || 'InternalError',
      timestamp: new Date().toISOString()
    });
  }
}

/**
 * 模拟快速测试模式（用于快速验证前端逻辑）
 */
async function simulateFastMode(ws, requestData, connectionId) {
  const startTime = Date.now();
  const pageCount = 5; // 快速模式只处理5页
  
  sendMessage(ws, {
    type: 'status',
    step: 'start',
    message: '开始执行全流程（快速测试模式）',
    lesson_id: requestData.lesson_id,
    timestamp: new Date().toISOString()
  });

  // 快速完成各阶段
  const fastDelay = 200;
  
  await delay(fastDelay);
  sendMessage(ws, {
    type: 'status',
    step: 'vl_llm_parse_complete',
    path: requestData.output_raw_json_path,
    lesson_id: requestData.lesson_id,
    message: '课件解析完成（含图片理解）',
    total_pages: pageCount
  });

  await delay(fastDelay);
  sendMessage(ws, {
    type: 'status',
    step: 'content_text',
    pages: pageCount,
    path: requestData.output_text_path
  });

  await delay(fastDelay);
  sendMessage(ws, {
    type: 'status',
    step: 'script',
    generated: pageCount,
    llm: true
  });

  await delay(fastDelay);
  sendMessage(ws, {
    type: 'status',
    step: 'postgres_cir_base',
    inserted_nodes: pageCount + 5
  });

  await delay(fastDelay);
  sendMessage(ws, {
    type: 'status',
    step: 'mind_map',
    keywords_count: 15
  });

  for (let i = 1; i <= pageCount; i++) {
    await delay(100);
    sendMessage(ws, {
      type: 'progress',
      step: 'tts',
      current: i,
      total: pageCount
    });
  }

  sendMessage(ws, { type: 'status', step: 'tts_done' });

  await delay(fastDelay);
  sendMessage(ws, {
    type: 'status',
    step: 'qdrant',
    ok: true,
    log: '[INFO] Fast mode Qdrant ingestion finished.'
  });

  const elapsedSeconds = (Date.now() - startTime) / 1000;
  sendMessage(ws, {
    type: 'done',
    step: 'end',
    lesson_id: requestData.lesson_id,
    elapsed_seconds: parseFloat(elapsedSeconds.toFixed(3)),
    mode: 'fast'
  });
}

// WebSocket连接处理
wss.on('connection', (ws, req) => {
  const connectionId = uuidv4().slice(0, 8);
  console.log(`[${connectionId}] WebSocket连接已建立: ${req.url}`);
  
  activeConnections.set(connectionId, {
    ws,
    connectedAt: new Date(),
    status: 'connected'
  });

  // 发送连接成功消息
  sendMessage(ws, {
    type: 'connection',
    status: 'connected',
    connection_id: connectionId,
    message: 'WebSocket连接已建立，请发送请求数据',
    timestamp: new Date().toISOString()
  });

  // 消息处理
  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      console.log(`[${connectionId}] 收到请求:`, JSON.stringify(data, null, 2));

      // 验证请求
      const validationErrors = validateRequest(data);
      if (validationErrors.length > 0) {
        sendMessage(ws, {
          type: 'error',
          step: 'validation',
          error: '请求参数验证失败',
          error_type: 'ValidationError',
          details: validationErrors
        });
        return;
      }

      // 更新连接状态
      activeConnections.get(connectionId).status = 'processing';
      activeConnections.get(connectionId).requestData = data;

      // 根据模式选择处理方式
      if (data.mode === 'fast') {
        await simulateFastMode(ws, data, connectionId);
      } else {
        await simulateFullPipeline(ws, data, connectionId);
      }

      const connection = activeConnections.get(connectionId);
      if (connection) {
        connection.status = 'completed';
      }

    } catch (error) {
      console.error(`[${connectionId}] 消息处理错误:`, error);
      sendMessage(ws, {
        type: 'error',
        step: 'message_parse',
        error: '无法解析请求消息',
        error_type: 'ParseError',
        details: error.message
      });
    }
  });

  // 连接关闭处理
  ws.on('close', (code, reason) => {
    console.log(`[${connectionId}] WebSocket连接已关闭: code=${code}, reason=${reason}`);
    activeConnections.delete(connectionId);
  });

  // 错误处理
  ws.on('error', (error) => {
    console.error(`[${connectionId}] WebSocket错误:`, error);
    activeConnections.get(connectionId).status = 'error';
  });
});

// 启动服务器
server.listen(PORT, HOST, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║          PPT Parser Mock Server 启动成功                     ║
╠══════════════════════════════════════════════════════════════╣
║  WebSocket: ws://${HOST}:${PORT}/api/v1/ws/script            ║
║  HTTP API:  http://${HOST}:${PORT}/health                    ║
║  测试页面:  http://${HOST}:${PORT}/test/                     ║
╚══════════════════════════════════════════════════════════════╝
  `);
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing server...');
  wss.close(() => {
    server.close(() => {
      process.exit(0);
    });
  });
});

process.on('SIGINT', () => {
  console.log('\nSIGINT received, closing server...');
  wss.close(() => {
    server.close(() => {
      process.exit(0);
    });
  });
});

module.exports = { server, wss };
