import io
import edge_tts
import logging
from pydub import AudioSegment
from app.model.time_line_dto import TimelineDTO
from app.webhook_service import WebhookService

logger = logging.getLogger(__name__)


class TTSService:
    VOICE_MAPPING = {
        0: "zh-TW-HsiaoChenNeural",  # Female
        1: "zh-TW-HsiaoYuNeural"  # Male
    }

    @staticmethod
    async def generate_wav_with_timeline(text: str, voice: int) -> tuple[bytes, list]:
        """
        即時生成 WAV 數據和時間軸 JSON 並返回。
        """
        if voice not in TTSService.VOICE_MAPPING:
            raise ValueError("Invalid voice: must be 0 (male) or 1 (female)")
        
        """ 呼叫 n8n webhook 獲取處理後的文本 (TODO 這邊要討論回傳的格式，現在先做測試) """
        result = await WebhookService.send_webhook(text)

        response_message = ''
        response_url = ''

        if result["success"] is False:
            raise ValueError("Webhook service failed to process the text.")
        else:
            response_message = result.get("response")['message']
            response_url = result.get("response")['html']
        
        logger.info(f"Processed text from webhook: {response_message}")

        actual_voice = TTSService.VOICE_MAPPING[voice]
        try:
            communicate = edge_tts.Communicate(response_message, actual_voice, boundary="WordBoundary")
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

            return wav_data, timeline, response_message, response_url
        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")