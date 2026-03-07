\# 语音服务 WebSocket 接口文档



\## 一、接口基本信息



\### 1.1 服务概述

本服务提供两个功能：

\- \*\*文字转语音（TTS）\*\*：输入文字，返回语音音频。

\- \*\*语音转文字（ASR）\*\*：输入录音音频，返回识别出的文字。



\### 1.2 连接信息

\- \*\*地址\*\*：`ws://localhost:8765`（开发环境）

\- \*\*协议\*\*：WebSocket



---



\## 二、通用规则

1\. 连接成功后，\*\*必须立即发送一条 JSON 消息\*\*，包含 `service` 字段，指定要使用 TTS 还是 ASR。

2\. 所有控制消息均为 JSON 字符串。

3\. 音频数据使用二进制格式发送/接收。

4\. 传输结束标志：发送一个长度为 \*\*0 的空字节数组\*\*。



---



\## 三、TTS（文字转语音）



\### 3.1 请求格式（JSON）

```json

{

&nbsp; "service": "tts",

&nbsp; "text": "你要合成的文字",

&nbsp; "voice": "zh-CN-XiaoxiaoNeural"

}

可用语音列表：



语音标识	描述

zh-CN-XiaoxiaoNeural	晓晓（女声，推荐）

zh-CN-YunxiNeural	云希（男声，推荐）

zh-CN-YunyangNeural	云扬（男声，新闻）

zh-CN-XiaoyiNeural	晓伊（女声，活泼）

zh-CN-YunjianNeural	云健（男声，深沉）

zh-HK-HiuGaaiNeural	晓佳（粤语，女声）

zh-HK-HiuMaanNeural	晓曼（粤语，女声）

zh-HK-WanLungNeural	云龙（粤语，男声）

zh-TW-HsiaoChenNeural	晓臻（台湾，女声）

zh-TW-HsiaoYuNeural	晓雨（台湾，女声）

zh-TW-YunJheNeural	云哲（台湾，男声）

zh-CN-liaoning-XiaobeiNeural	晓北（辽宁，女声）

zh-CN-shaanxi-XiaoniNeural	晓妮（陕西，女声）

3.2 响应

成功响应

服务器将合成的 MP3 音频数据分块发送，每个数据块为二进制格式。



客户端处理流程：



依次接收所有数据块并暂存。



当收到一个长度为 0 的空字节数组时，表示音频传输结束。



将所有数据块合并成完整的 MP3 音频数据，即可播放或保存为文件。



错误响应

{

&nbsp; "error": "TTS 合成失败: No audio was received..."

}

3.3 接收音频示例（JavaScript）

let audioChunks = \[];



ws.onmessage = (event) => {

&nbsp; if (event.data instanceof ArrayBuffer) {

&nbsp;   const chunk = new Uint8Array(event.data);

&nbsp;   if (chunk.length === 0) {

&nbsp;     console.log('音频传输结束');

&nbsp;     const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });

&nbsp;     const audioUrl = URL.createObjectURL(audioBlob);

&nbsp;     new Audio(audioUrl).play();

&nbsp;     audioChunks = \[];

&nbsp;   } else {

&nbsp;     audioChunks.push(chunk);

&nbsp;   }

&nbsp; } else {

&nbsp;   try {

&nbsp;     const error = JSON.parse(event.data);

&nbsp;     console.error('TTS错误:', error.error);

&nbsp;   } catch (e) {

&nbsp;     console.log('收到非JSON消息:', event.data);

&nbsp;   }

&nbsp; }

};

3.4 接收音频示例（Python）

audio\_chunks = \[]



while True:

&nbsp;   msg = await websocket.recv()

&nbsp;   if isinstance(msg, bytes):

&nbsp;       if len(msg) == 0:

&nbsp;           break

&nbsp;       audio\_chunks.append(msg)

&nbsp;   else:

&nbsp;       error = json.loads(msg)

&nbsp;       print("错误:", error.get("error"))

&nbsp;       break



with open("output.mp3", "wb") as f:

&nbsp;   for chunk in audio\_chunks:

&nbsp;       f.write(chunk)

四、ASR（语音转文字）

4.1 请求格式（JSON）

{

&nbsp; "service": "asr"

}

4.2 音频格式要求

目前只支持浏览器 MediaRecorder 默认输出的 audio/webm 格式。



4.3 响应格式

成功响应

{

&nbsp; "text": "识别出的文字"

}

错误响应

{

&nbsp; "error": "描述错误"

}



4.4 JavaScript 示例



const arrayBuffer = await audioBlob.arrayBuffer();

const ws = new WebSocket('ws://localhost:8765');

ws.binaryType = 'arraybuffer';



ws.onopen = () => {

&nbsp; ws.send(JSON.stringify({ service: 'asr' }));

&nbsp; ws.send(arrayBuffer);

&nbsp; ws.send(new Uint8Array(0));

};



ws.onmessage = (event) => {

&nbsp; if (typeof event.data === 'string') {

&nbsp;   try {

&nbsp;     const resp = JSON.parse(event.data);

&nbsp;     if (resp.text) {

&nbsp;       console.log('识别结果:', resp.text);

&nbsp;       document.getElementById('result').innerText = resp.text;

&nbsp;     } else if (resp.error) {

&nbsp;       console.error('ASR错误:', resp.error);

&nbsp;     }

&nbsp;   } catch (e) {

&nbsp;     console.log('收到非JSON消息:', event.data);

&nbsp;   }

&nbsp; }

};



ws.onerror = (err) => console.error('WebSocket错误:', err);

ws.onclose = () => console.log('ASR连接关闭');



4.5 Python 示例



import asyncio

import websockets

import json



async def asr\_example(audio\_file\_path):

&nbsp;   uri = "ws://localhost:8765"

&nbsp;   async with websockets.connect(uri) as websocket:

&nbsp;       await websocket.send(json.dumps({"service": "asr"}))

&nbsp;       with open(audio\_file\_path, "rb") as f:

&nbsp;           audio\_data = f.read()

&nbsp;       await websocket.send(audio\_data)

&nbsp;       await websocket.send(b"")

&nbsp;       response = await websocket.recv()

&nbsp;       result = json.loads(response)

&nbsp;       if "text" in result:

&nbsp;           print("识别结果:", result\["text"])

&nbsp;       else:

&nbsp;           print("错误:", result.get("error"))



asyncio.run(asr\_example("test.webm"))



五、注意事项



5.1 常见错误

错误信息	错误原因	处理建议

{"error": "text is required"}	TTS 请求中文字内容为空	检查并补充 text 字段

{"error": "TTS 合成失败: ..."}	语音合成服务异常、语音类型无效或网络问题	检查语音类型，重试请求

{"error": "第一条消息必须是 JSON 格式"}	首次发送的不是合法 JSON 消息	确保首次发送的是 JSON 字符串

{"error": "未知服务: xxx"}	service 字段值不是 tts 或 asr	修正 service 字段

语音识别无结果 / 结果错误	音频格式非 audio/webm、音频模糊或时长过长	确保音频为 audio/webm，优化录音，单次不超过 1 分钟

连接建立失败	服务器地址/端口错误、服务器未启动	检查地址和端口，确认服务运行

5.2 ASR 录音时长建议

单次录音建议不超过一分钟，避免超时。若需长时间录音，请分多次发送。



text



---



\### 第六步：确认文件已创建



```powershell

dir docs\\api

