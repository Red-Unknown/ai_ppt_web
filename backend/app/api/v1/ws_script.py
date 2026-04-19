from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from backend.app.services.script.tts import TTSService
from backend.app.services.script.asr import ASRService
from backend.app.services.parser.cir_pipeline import run_cir_pipeline
from backend.app.services.parser.full_pipeline import run_full_pipeline

router = APIRouter()

@router.websocket("/ws/script")
async def websocket_script(websocket: WebSocket):
    await websocket.accept()
    try:
        # 接收第一条消息（必须是 JSON）
        message = await websocket.receive_text()
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            await websocket.send_json({"error": "第一条消息必须是 JSON 格式"})
            await websocket.close()
            return

        service = data.get("service")
        if service == "tts":
            await handle_tts(websocket, data)
        elif service == "asr":
            await handle_asr(websocket)
        elif service == "cir_pipeline":
            await handle_cir_pipeline(websocket, data)
        elif service == "full_pipeline":
            await handle_full_pipeline(websocket, data)
        else:
            await websocket.send_json({"error": f"未知服务: {service}"})
            await websocket.close()
    except WebSocketDisconnect:
        print("客户端断开连接")
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        await websocket.close()

async def handle_tts(websocket: WebSocket, data: dict):
    text = data.get("text")
    voice = data.get("voice", "zh-CN-XiaoxiaoNeural")
    if not text:
        await websocket.send_json({"error": "text is required"})
        await websocket.close()
        return

    try:
        # 调用 TTS 服务获取完整音频
        audio_data = await TTSService.synthesize(text, voice)

        # 分块发送音频（与原代码一致）
        chunk_size = 4096
        for i in range(0, len(audio_data), chunk_size):
            await websocket.send_bytes(audio_data[i:i+chunk_size])
            await asyncio.sleep(0.01)  # 保持原样，避免发送过快

        # 发送结束标志（空字节）
        await websocket.send_bytes(b"")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

async def handle_asr(websocket: WebSocket):
    # 接收音频数据块
    audio_chunks = []
    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.receive":
                if "bytes" in message:
                    chunk = message["bytes"]
                    if len(chunk) == 0:
                        break  # 结束标志
                    audio_chunks.append(chunk)
                elif "text" in message:
                    # 忽略非二进制消息
                    pass
    except WebSocketDisconnect:
        pass

    if not audio_chunks:
        await websocket.send_json({"error": "未接收到音频数据"})
        await websocket.close()
        return

    audio_data = b"".join(audio_chunks)

    try:
        text = await ASRService.recognize(audio_data)
        await websocket.send_json({"text": text})
    except Exception as e:
        await websocket.send_json({"error": f"ASR识别失败: {str(e)}"})
    finally:
        await websocket.close()


async def handle_cir_pipeline(websocket: WebSocket, data: dict):
    json_path = data.get("json_path")
    output_text_path = data.get("output_text_path")
    if not json_path or not output_text_path:
        await websocket.send_json({"error": "json_path 和 output_text_path 为必填"})
        await websocket.close()
        return

    try:
        async for event in run_cir_pipeline(
            json_path=json_path,
            output_text_path=output_text_path,
            lesson_id=data.get("lesson_id"),
            course_id=data.get("course_id"),
            school_id=data.get("school_id", "default_school"),
            title=data.get("title"),
            voice=data.get("voice", "zh-CN-XiaoxiaoNeural"),
        ):
            await websocket.send_json(event)
    except Exception as e:
        await websocket.send_json({"type": "error", "error": str(e)})
    finally:
        await websocket.close()


async def handle_full_pipeline(websocket: WebSocket, data: dict):
    file_path = data.get("file_path")
    file_type = data.get("file_type")
    output_raw_json_path = data.get("output_raw_json_path")
    output_text_path = data.get("output_text_path")
    if not file_path or not file_type or not output_raw_json_path or not output_text_path:
        await websocket.send_json({"error": "file_path/file_type/output_raw_json_path/output_text_path 为必填"})
        await websocket.close()
        return

    try:
        async for event in run_full_pipeline(
            file_path=file_path,
            file_type=file_type,
            output_raw_json_path=output_raw_json_path,
            output_text_path=output_text_path,
            lesson_id=data.get("lesson_id"),
            course_id=data.get("course_id"),
            school_id=data.get("school_id", "default_school"),
            title=data.get("title"),
            voice=data.get("voice", "zh-CN-XiaoxiaoNeural"),
            enable_script_llm=bool(data.get("enable_script_llm", True)),
        ):
            await websocket.send_json(event)
    except Exception as e:
        await websocket.send_json({"type": "error", "error": str(e)})
    finally:
        await websocket.close()