from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from app.tts_service import TTSService
from app.webhook_service import WebhookService
import logging
import base64

app = FastAPI(
    title="AIoT TTS API",
    description="基於 CQRS 架構的文字轉語音服務，整合 Edge TTS 和 n8n Webhook",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get(
    "/",
    summary="健康檢查",
    description="確認 API 服務是否正常運行",
    tags=["系統"]
)
def read_root():
    """
    ## 健康檢查端點
    
    用於確認 API 服務是否正常運行。
    
    ### 回應
    - 返回簡單的歡迎訊息
    """
    return {"message": "Hello"}

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 請求模型
class UserInputRequest(BaseModel):
    input: str = Field(
        ...,
        description="使用者輸入的文字內容",
        example="你好，這是測試文字",
        min_length=1
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "input": "歡迎使用 TTS 服務"
            }
        }

# Command: 串接使用者輸入（預留接口，目前僅記錄）
@app.post(
    "/commands/user-input",
    summary="使用者輸入命令（預留接口）",
    description="接收使用者輸入並記錄，預留供未來擴展處理邏輯使用",
    tags=["Command"]
)
async def handle_user_input(request: UserInputRequest):
    """
    ## 使用者輸入命令端點
    
    此端點為預留接口，目前僅記錄使用者輸入的內容。
    未來可擴展為處理各種使用者命令的邏輯。
    
    ### 參數
    - **input**: 使用者輸入的文字內容（必填）
    
    ### 回應
    - **status**: 處理狀態
    - **input**: 接收到的輸入內容
    """
    logger.info(f"User input received: {request.input}")
    # 後續可擴展處理邏輯
    return {"status": "received", "input": request.input}

# Webhook: 發送文字到 n8n webhook
@app.post(
    "/webhook/send",
    summary="發送文字到 n8n Webhook",
    description="將文字發送到 n8n webhook 服務進行處理，並返回處理結果",
    tags=["Webhook"],
    responses={
        200: {
            "description": "成功發送並獲得回應",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Webhook sent successfully",
                        "data": {
                            "success": True,
                            "status_code": 200,
                            "response": {"text": "處理後的文字", "url": "https://example.com"}
                        }
                    }
                }
            }
        },
        400: {"description": "文字內容為空"},
        500: {"description": "Webhook 發送失敗"}
    }
)
async def send_to_webhook(request: UserInputRequest):
    """
    ## 發送 Webhook 端點
    
    將使用者輸入的文字發送到 n8n webhook 服務進行預處理。
    
    ### 參數
    - **input**: 要發送的文字內容（必填，不可為空）
    
    ### 處理流程
    1. 驗證輸入文字不為空
    2. 發送到 n8n webhook 服務
    3. 等待並接收處理結果
    4. 返回處理狀態和結果數據
    
    ### 回應
    - **status**: 發送狀態（success/error）
    - **message**: 狀態訊息
    - **data**: webhook 回應數據，包含處理後的文字和相關 URL
    
    ### 錯誤處理
    - 400: 輸入文字為空
    - 500: Webhook 服務連線失敗或處理錯誤
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
@app.get(
    "/queries/get-tts-wav",
    summary="文字轉語音（TTS）",
    description="將文字轉換為語音，返回 WAV 音頻數據（base64 編碼）和時間軸資訊",
    tags=["Query"],
    responses={
        200: {
            "description": "成功生成音頻和時間軸",
            "content": {
                "application/json": {
                    "example": {
                        "audioData": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
                        "timeLines": [
                            {"start": 0.0, "end": 0.3, "text": "你好"},
                            {"start": 0.3, "end": 0.6, "text": "世界"}
                        ],
                        "originalText": "你好世界",
                        "url": "https://example.com/resource"
                    }
                }
            }
        },
        400: {"description": "文字為空或語音參數無效"},
        500: {"description": "TTS 生成失敗"}
    }
)
async def get_tts_wav(
    text: str = Query(
        ...,
        description="要轉換為語音的文字內容",
        example="你好世界",
        min_length=1
    ),
    voice: int = Query(
        0,
        description="語音類型選擇：0=女聲 (zh-TW-HsiaoChenNeural), 1=男聲 (zh-TW-HsiaoYuNeural)",
        ge=0,
        le=1,
        example=0
    )
):
    """
    ## 文字轉語音端點
    
    將輸入的文字轉換為語音（WAV 格式），並提供每個單詞的時間軸資訊。
    
    ### 處理流程
    1. 將文字發送到 n8n webhook 進行預處理
    2. 使用 Microsoft Edge TTS 引擎生成語音
    3. 轉換為 16kHz, mono, 16-bit PCM WAV 格式
    4. 提取單詞邊界時間軸資訊
    5. 將 WAV 數據編碼為 base64 字符串返回
    
    ### 參數
    - **text**: 要轉換的文字內容（必填，不可為空）
    - **voice**: 語音類型（選填，預設為 0）
      - `0`: 女聲 - zh-TW-HsiaoChenNeural
      - `1`: 男聲 - zh-TW-HsiaoYuNeural
    
    ### 回應
    - **audioData**: base64 編碼的 WAV 音頻數據
    - **timeLines**: 時間軸陣列，包含每個單詞的開始時間、結束時間和文字
      - **start**: 開始時間（秒）
      - **end**: 結束時間（秒）
      - **text**: 對應的文字內容
    - **originalText**: 經過 webhook 處理後的原始文字
    - **url**: webhook 返回的資源 URL
    
    ### 音頻規格
    - 格式: WAV
    - 採樣率: 16kHz
    - 聲道: Mono (單聲道)
    - 位元深度: 16-bit PCM
    
    ### 錯誤處理
    - 400: 文字為空或語音參數不在有效範圍內（0-1）
    - 500: TTS 生成失敗（可能是 webhook 錯誤或 Edge TTS 服務問題）
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if voice not in [0, 1]:
        raise HTTPException(status_code=400, detail="Voice must be 0 (female) or 1 (male)")

    try:
        wav_data, timeline, response_text, response_url = await TTSService.generate_wav_with_timeline(text, voice)
        # 將 WAV 編碼為 base64
        wav_base64 = base64.b64encode(wav_data).decode('utf-8')
        return {
            "audioData": wav_base64,
            "timeLines": [item.to_dict() for item in timeline],
            "originalText": response_text,
            "url": response_url
        }
    except Exception as e:
        logger.error(f"WAV and timeline generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"WAV and timeline generation failed: {str(e)}")