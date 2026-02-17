@echo off
chcp 65001 > nul
title 🚀 太空 AI 發射站 (零秒啟動)

:: 1. 定位到桌面
cd /d "C:\Users\yangy\OneDrive\桌面"

:: 2. 啟動 Ollama
echo [1/3] 啟動 Ollama...
start "" "ollama" app

:: 3. 啟動 Streamlit (直接背景發射)
echo [2/3] 啟動 AI 介面...
start /min "AI_ENGINE" "C:\Users\yangy\AppData\Local\Programs\Python\Python313\python.exe" -m streamlit run "app.py" --server.port 8501

:: 4. 直接啟動 Ngrok (完全不等待)
echo [3/3] 全球連線啟動：dynastic-antone-synclinal.ngrok-free.dev
"C:\Users\yangy\OneDrive\桌面\ngrok.exe" http 8501 --domain=dynastic-antone-synclinal.ngrok-free.dev

pause