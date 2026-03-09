import asyncio
from edge_tts import Communicate

class TTSService:
    @staticmethod
    async def synthesize(text: str, voice: str) -> bytes:
        """
        合成语音，返回完整的 MP3 音频数据（bytes）。
        """
        communicate = Communicate(text, voice)
        audio_data = b""
        try:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
        except Exception as e:
            raise RuntimeError(f"TTS 合成失败: {str(e)}") from e

        if not audio_data:
            raise RuntimeError("没有生成音频数据，请检查语音参数")

        return audio_data