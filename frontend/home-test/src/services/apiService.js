// API服务文件，处理与后端的通信

const API_BASE_URL = 'http://localhost:8000'; // 后端API地址

// 启动聊天会话
export const startChatSession = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/session/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('启动聊天会话失败:', error);
    throw error;
  }
};

// 建立SSE连接获取流式聊天响应
export const createChatSSE = (callback) => {
  const url = `${API_BASE_URL}/api/v1/chat/sse`;
  const eventSource = new EventSource(url);
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      callback(data);
    } catch (error) {
      console.error('解析SSE消息失败:', error);
    }
  };
  
  eventSource.onerror = (error) => {
    console.error('SSE连接错误:', error);
    eventSource.close();
  };
  
  return eventSource;
};

// 发送消息到聊天会话
export const sendChatMessage = async (message) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/session/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('发送消息失败:', error);
    throw error;
  }
};
