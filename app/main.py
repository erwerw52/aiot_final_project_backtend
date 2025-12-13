from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from app.tts_service import TTSService
import logging

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

# Query: 獲取 PCM
@app.get("/queries/get-tts-pcm")
async def get_tts_pcm(text: str, voice: str = "zh-TW-HsiaoChenNeural"):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        pcm_data = await TTSService.generate_pcm_sync(text, voice)
        return Response(content=pcm_data, media_type="audio/pcm")
    except Exception as e:
        logger.error(f"PCM generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PCM generation failed: {str(e)}")

# Query: 獲取 WAV
@app.get("/queries/get-tts-wav")
async def get_tts_wav(text: str, voice: str = "zh-TW-HsiaoChenNeural"):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        wav_data = await TTSService.generate_wav_sync(text, voice)
        return Response(content=wav_data, media_type="audio/wav")
    except Exception as e:
        logger.error(f"WAV generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"WAV generation failed: {str(e)}")