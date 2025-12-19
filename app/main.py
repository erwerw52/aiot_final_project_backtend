from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from app.tts_service import TTSService
from app.webhook_service import WebhookService
import logging
import base64

app = FastAPI(title="TTS API", description="CQRS-based TTS API with Edge TTS")

@app.get("/")
def read_root():
    return {"message": "Hello"}

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 請求模型
class UserInputRequest(BaseModel):
    input: str

# Command: 串接使用者輸入（預留接口，目前僅記錄）
@app.post("/commands/user-input")
async def handle_user_input(request: UserInputRequest):
    logger.info(f"User input received: {request.input}")
    # 後續可擴展處理邏輯
    return {"status": "received", "input": request.input}

# Webhook: 發送文字到 n8n webhook
@app.post("/webhook/send")
async def send_to_webhook(request: UserInputRequest):
    """
    發送文字到 n8n webhook 服務
    """
    if not request.input.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        result = await WebhookService.send_webhook(request.input)
        
        if result["success"]:
            return {
                "status": "success",
                "message": "Webhook sent successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Webhook failed: {result.get('error', 'Unknown error')}"
            )
    except Exception as e:
        logger.error(f"Webhook sending error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send webhook: {str(e)}")

# Query: 獲取 WAV 和時間軸
@app.get("/queries/get-tts-wav")
async def get_tts_wav(text: str, voice: int = 0):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if voice not in [0, 1]:
        raise HTTPException(status_code=400, detail="Voice must be 0 (male) or 1 (female)")

    try:
        wav_data, timeline, response_url = await TTSService.generate_wav_with_timeline(text, voice)
        # 將 WAV 編碼為 base64
        wav_base64 = base64.b64encode(wav_data).decode('utf-8')
        return {
            "audioData": wav_base64,
            "timeLines": [item.to_dict() for item in timeline],
            "url": response_url
        }
    except Exception as e:
        logger.error(f"WAV and timeline generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"WAV and timeline generation failed: {str(e)}")