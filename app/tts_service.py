import asyncio
import io
import uuid
from typing import Dict, Optional
import edge_tts
from pydub import AudioSegment

# 儲存生成的 PCM 數據（記憶體字典，生產環境可改用 Redis 或 DB）
pcm_storage: Dict[str, bytes] = {}

class TTSService:
    @staticmethod
    async def generate_pcm(text: str, voice: str = "zh-TW-HsiaoChenNeural") -> str:
        """
        生成 PCM 數據並儲存，返回唯一 ID。
        """
        tts_id = str(uuid.uuid4())

        try:
            # 使用 edge-tts 生成 WAV
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            # 用 pydub 處理音頻：確保 16kHz, mono, 16-bit PCM
            # edge-tts 輸出 MP3，所以用 from_mp3
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # 16kHz, mono, 16-bit

            # 提取 PCM (raw bytes)
            pcm_data = audio.raw_data

            # 儲存到記憶體
            pcm_storage[tts_id] = pcm_data

            return tts_id
        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")

    @staticmethod
    def get_pcm(tts_id: str) -> Optional[bytes]:
        """
        根據 ID 獲取 PCM 數據。
        """
        return pcm_storage.get(tts_id)

    @staticmethod
    def convert_pcm_to_wav(pcm_data: bytes) -> bytes:
        """
        將 PCM 數據轉換為 WAV 格式。
        """
        # 從 raw PCM 創建 AudioSegment（16kHz, mono, 16-bit）
        audio = AudioSegment.from_raw(io.BytesIO(pcm_data), sample_width=2, frame_rate=16000, channels=1)
        # 導出為 WAV
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        return wav_buffer.getvalue()