@echo off
title AI学习资料智能问答系统 - 一键启动
color 0A

echo ================================================
echo   AI 学习资料智能问答系统 - 一键启动
echo ================================================
echo.

set ROOT=%~dp0

REM ========== 启动后端 (FastAPI, 端口 8000) ==========
echo [1/2] 启动后端  http://127.0.0.1:8000
cd /d "%ROOT%backend"
start "AI问答-后端 FastAPI" cmd /k "venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

REM ========== 启动前端 (Vue3, 端口 5173) ==========
echo [2/2] 启动前端  http://localhost:5173
cd /d "%ROOT%frontend"
start "AI问答-前端 Vue3" cmd /k "npm run dev"

echo.
echo 启动完成！请稍等几秒让服务就绪...
echo   后端接口文档: http://127.0.0.1:8000/docs
echo   前端页面:     http://localhost:5173
echo.
timeout /t 3 /nobreak >nul
start http://localhost:5173
exit