# AIoT Final Project - Backend

基於 FastAPI 的文字轉語音（TTS）服務後端，整合 Edge TTS 和 n8n Webhook 服務。

## 📋 專案簡介

本專案提供 TTS（Text-to-Speech）API 服務，採用 CQRS（Command Query Responsibility Segregation）架構設計，支援：

- 🎤 即時文字轉語音功能（使用 Microsoft Edge TTS）
- 🕐 語音時間軸生成（Word Boundary）
- 🔗 與 n8n Webhook 整合進行文字預處理
- 🎭 支援多種中文語音（男聲/女聲）
- 📊 返回 base64 編碼的 WAV 音頻數據

## 🚀 功能特點

- **CQRS 架構**: 分離命令（Command）和查詢（Query）操作
- **非同步處理**: 使用 FastAPI 的 async/await 特性
- **高品質音頻**: 輸出 16kHz, mono, 16-bit PCM WAV 格式
- **精準時間軸**: 提供每個單詞的開始和結束時間
- **Webhook 整合**: 支援文字預處理和外部服務整合
- **Zeabur 架構**:
   -<img width="278" height="303" alt="image" src="https://github.com/user-attachments/assets/9f7d478a-28bd-4c61-a4db-4676b545d040" />
 
## 📦 技術棧

- **FastAPI** (0.115.6) - 現代化的 Web 框架
- **Uvicorn** (0.34.0) - ASGI 伺服器
- **Edge-TTS** (7.2.7) - Microsoft Edge 文字轉語音引擎
- **Pydub** (0.25.1) - 音頻處理庫
- **HTTPX** (0.27.2) - 非同步 HTTP 客戶端

## 📁 專案結構

```
aiot_final_project_backtend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用主程式
│   ├── tts_service.py       # TTS 服務邏輯
│   ├── webhook_service.py   # Webhook 服務邏輯
│   └── model/
│       ├── time_line_dto.py # 時間軸數據傳輸物件
│       └── enum/
├── requirements.txt         # Python 依賴套件
└── README.md               # 專案說明文檔
```

## 🔧 安裝與設置

### 環境需求

- Python 3.8+
- pip

## 訪問 API 文檔
   - Swagger UI: https://aiot-backend.zeabur.app/docs

### 主要端點概覽

- `GET /` - 健康檢查
- `POST /webhook/send` - 發送文字到 n8n webhook 進行處理
- `GET /queries/get-tts-wav` - 文字轉語音（TTS），返回 WAV 音頻和時間軸
- `POST /commands/user-input` - 使用者輸入命令（預留接口）

### 語音選項

系統支援以下中文語音：
- `voice=0`: 女聲 (zh-TW-HsiaoChenNeural)
- `voice=1`: 男聲 (zh-TW-HsiaoYuNeural)

更多語音選項請參考 [Edge TTS 文檔](https://github.com/rany2/edge-tts#voices)。

## 📝 架構說明

### CQRS 設計模式

本專案採用 CQRS（Command Query Responsibility Segregation）架構：

- **Command (命令)**: `/commands/*` - 用於寫入操作
- **Query (查詢)**: `/queries/*` - 用於讀取操作  
- **Webhook**: `/webhook/*` - 用於外部服務整合

### 核心組件

- **TTS Service**: 負責文字轉語音和時間軸生成
- **Webhook Service**: 負責與 n8n 服務通信
- **Timeline DTO**: 封裝時間軸數據結構

### 錯誤處理

系統使用 FastAPI 的標準錯誤處理機制：
- `400 Bad Request`: 無效的輸入參數
- `500 Internal Server Error`: 服務器內部錯誤

所有關鍵操作均有日誌記錄，便於追蹤和除錯。

### 開發團隊
   AIOT Final Project Team 12
   最後更新: 2025/12/24

### 授權
   本專案僅供學習和研究使用。
