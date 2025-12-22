import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebhookService:
    """ 負責與 n8n webhook 服務進行通信的服務類別"""
    WEBHOOK_URL = "https://n8n-projects-aiot.zeabur.app/webhook/travel_planner"
    TIMEOUT = 120.0  # 120 秒超時
    
    @staticmethod
    async def send_webhook(text: str) -> Dict[str, Any]:
        """
        發送 webhook 到 n8n 服務
        
        Args:
            text: 要傳送的文字內容
            
        Returns:
            Dict 包含狀態和回應資料
        """
        payload = {
            "text": text
        }
        
        try:
            async with httpx.AsyncClient(timeout=WebhookService.TIMEOUT) as client:
                response = await client.post(
                    WebhookService.WEBHOOK_URL,
                    json=payload
                )
                
                # 記錄請求資訊
                logger.info(f"Webhook sent to {WebhookService.WEBHOOK_URL}")
                logger.info(f"Payload: {payload}")
                logger.info(f"Response status: {response.status_code}")
                
                # 檢查回應狀態
                response.raise_for_status()
                
                # 嘗試解析 JSON 回應
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response_data
                }
                
        except httpx.TimeoutException as e:
            logger.error(f"Webhook timeout: {str(e)}")
            return {
                "success": False,
                "error": "Request timeout",
                "details": str(e)
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Webhook HTTP error: {str(e)}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return {
                "success": False,
                "error": "Unknown error",
                "details": str(e)
            }
