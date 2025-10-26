#!/bin/bash
# Backend'i temiz bir şekilde yeniden başlat

cd /Users/berkeseker/Documents/Repositories/Llama-Hackathon-Lambda/backend

# Eski process'i öldür
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# 1 saniye bekle
sleep 1

# Yeniden başlat
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

