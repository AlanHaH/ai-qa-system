"""一键启动脚本：后端 + 前端 + 自动打开浏览器
用法：
    终端运行：python start.py
说明：
    后端强制使用项目 venv 里的 Python（避免用系统 Python 缺依赖报错）
"""
import os
import subprocess
import sys
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
FRONTEND = os.path.join(ROOT, "frontend")

# 项目 venv 的 Python（后端依赖都装在这里）
VENV_PYTHON = os.path.join(BACKEND, "venv", "Scripts", "python.exe")


def stop_proc(proc, name):
    """结束进程（含子进程树），Windows 用 taskkill /T /F"""
    if proc.poll() is None:
        try:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                           capture_output=True)
        except Exception:
            proc.terminate()
        print(f"已停止 {name}")


def main():
    if not os.path.exists(VENV_PYTHON):
        print(f"[错误] 找不到 venv Python: {VENV_PYTHON}")
        sys.exit(1)

    print("=" * 50)
    print("  AI 学习资料智能问答系统 - 一键启动")
    print("=" * 50)

    # 1. 启动后端 (FastAPI, 端口 8000)
    print("[1/2] 启动后端  http://127.0.0.1:8000")
    backend_proc = subprocess.Popen(
        [VENV_PYTHON, "-m", "uvicorn", "main:app", "--reload",
         "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND,
    )

    # 2. 启动前端 (Vue3, 端口 5173)
    print("[2/2] 启动前端  http://localhost:5173")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND,
        shell=True,  # Windows 下 npm 是 npm.cmd，需要 shell 才能找到
    )

    # 3. 等待几秒后打开浏览器
    print("\n正在等待服务启动...")
    time.sleep(5)
    webbrowser.open("http://localhost:5173")

    print("\n服务已启动：")
    print("  接口文档: http://127.0.0.1:8000/docs")
    print("  前端页面: http://localhost:5173")
    print("\n按 Ctrl+C 停止前后端进程...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        stop_proc(backend_proc, "后端")
        stop_proc(frontend_proc, "前端")
        print("已全部关闭")


if __name__ == "__main__":
    main()
