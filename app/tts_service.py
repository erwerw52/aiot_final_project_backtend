import io
import edge_tts
from pydub import AudioSegment

class TTSService:
    @staticmethod
    async def generate_pcm_sync(text: str, voice: str = "zh-TW-HsiaoChenNeural") -> bytes:
        """
        即時生成 PCM 數據並返回。
        """
        try:
            # 使用 edge-tts 生成 MP3
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            # 用 pydub 處理音頻：確保 16kHz, mono, 16-bit PCM
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

            # 提取 PCM (raw bytes)
            pcm_data = audio.raw_data

            return pcm_data
        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")

    @staticmethod
    async def generate_wav_sync(text: str, voice: str = "zh-TW-HsiaoChenNeural") -> bytes:
        """
        即時生成 WAV 數據並返回。
        """
        try:
            # 使用 edge-tts 生成 MP3
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            # 用 pydub 處理音頻：確保 16kHz, mono, 16-bit PCM
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

            # 導出為 WAV bytes
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_data = wav_buffer.getvalue()

            return wav_data
        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")