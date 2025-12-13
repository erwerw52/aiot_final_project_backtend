from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from app.tts_service import TTSService
import logging

app = FastAPI(title="TTS API", description="CQRS-based TTS API with Edge TTS")

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 請求模型
class GenerateTTSRequest(BaseModel):
    text: str
    voice: str = "zh-TW-HsiaoChenNeural"

class UserInputRequest(BaseModel):
    input: str

# Command: 生成 TTS
@app.post("/commands/generate-tts")
async def generate_tts(request: GenerateTTSRequest, background_tasks: BackgroundTasks):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # 異步生成 PCM
        tts_id = await TTSService.generate_pcm(request.text, request.voice)

        logger.info(f"TTS generated with ID: {tts_id}")
        return {"id": tts_id, "status": "processing"}
    except Exception as e:
        logger.error(f"TTS generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

# Query: 獲取 PCM
@app.get("/queries/get-tts-pcm")
async def get_tts_pcm(tts_id: str):
    pcm_data = TTSService.get_pcm(tts_id)
    if pcm_data is None:
        raise HTTPException(status_code=404, detail="TTS not found or not ready")

    return Response(content=pcm_data, media_type="audio/pcm")

# Query: 獲取 WAV（從 PCM 轉換）
@app.get("/queries/get-tts-wav")
async def get_tts_wav(tts_id: str):
    pcm_data = TTSService.get_pcm(tts_id)
    if pcm_data is None:
        raise HTTPException(status_code=404, detail="TTS not found or not ready")

    wav_data = TTSService.convert_pcm_to_wav(pcm_data)
    return Response(content=wav_data, media_type="audio/wav")

# Command: 串接使用者輸入（預留接口，目前僅記錄）
@app.post("/commands/user-input")
async def handle_user_input(request: UserInputRequest):
    logger.info(f"User input received: {request.input}")
    # 後續可擴展處理邏輯
    return {"status": "received", "input": request.input}