import io
import edge_tts
from pydub import AudioSegment
import base64
import json
from app.model.time_line_dto import TimelineDTO

class TTSService:
    @staticmethod
    async def generate_wav_with_timeline(text: str, voice: str = "zh-TW-HsiaoChenNeural") -> tuple[bytes, list]:
        """
        即時生成 WAV 數據和時間軸 JSON 並返回。
        """
        try:
            communicate = edge_tts.Communicate(text, voice, boundary="WordBoundary")
            audio_data = b""
            timeline = []
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
                elif chunk["type"] == "WordBoundary":
                    # 轉換時間軸：offset 和 duration 為 100ns 單位，轉為秒
                    start = chunk["offset"] / 10_000_000
                    end = (chunk["offset"] + chunk["duration"]) / 10_000_000
                    timeline.append(TimelineDTO(
                        start=round(start, 3),
                        end=round(end, 3),
                        text=chunk["text"]
                    ))

            # 用 pydub 處理音頻：確保 16kHz, mono, 16-bit PCM
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

            # 導出為 WAV bytes
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_data = wav_buffer.getvalue()

            return wav_data, timeline
        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")