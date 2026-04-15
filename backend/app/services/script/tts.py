import asyncio
from edge_tts import Communicate
from .text_preprocessor import preprocess_text_for_tts

class TTSService:
    @staticmethod
    async def synthesize(text: str, voice: str, preprocess: bool = True) -> bytes:
        """
        合成语音，返回完整的 MP3 音频数据（bytes）。
        
        Args:
            text: 要合成的文本
            voice: 语音标识（如 zh-CN-XiaoxiaoNeural）
            preprocess: 是否对文本进行预处理（包括数学公式转换）
        
        Returns:
            音频数据（MP3格式）
        """
        if preprocess:
            text = preprocess_text_for_tts(text)
        
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