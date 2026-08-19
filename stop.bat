@echo off
title AI学习资料智能问答系统 - 停止服务

echo 正在停止项目服务 (端口 8000 / 5173)...

REM 找出占用 8000 和 5173 端口的进程并结束
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173 " ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo 已停止所有服务。
echo.
pause