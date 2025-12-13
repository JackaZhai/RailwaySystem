#!/usr/bin/env python3
"""
一键启动脚本 - 铁路乘客分析系统
同时启动 Django 后端服务器和 React 前端开发服务器。

使用方法:
    python start_dev.py

停止: Ctrl+C
"""

import os
import sys
import subprocess
import signal
import time
import argparse
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# 服务器配置
DJANGO_HOST = "0.0.0.0"
DJANGO_PORT = 8000
VITE_PORT = 5173

# 全局存储子进程引用
backend_process = None
frontend_process = None


def check_npm_available():
    """检查 npm 是否可用"""
    npm_cmd = None
    npm_paths = []

    if sys.platform == "win32":
        npm_paths = [
            "npm.cmd",
            "npm",
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            r"C:\Users\{}\AppData\Roaming\npm\npm.cmd".format(os.environ.get("USERNAME", ""))
        ]
    else:
        npm_paths = ["npm", "/usr/local/bin/npm", "/usr/bin/npm"]

    for candidate in npm_paths:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return candidate, result.stdout.strip()
        except FileNotFoundError:
            continue

    return None, None


def check_dependencies():
    """检查基本依赖"""
    print("=" * 60)
    print("检查项目依赖...")

    # 检查后端目录
    if not BACKEND_DIR.exists():
        print(f"错误: 后端目录不存在: {BACKEND_DIR}")
        return False

    # 检查前端目录
    if not FRONTEND_DIR.exists():
        print(f"错误: 前端目录不存在: {FRONTEND_DIR}")
        return False

    # 检查虚拟环境（可选）
    if "VIRTUAL_ENV" not in os.environ:
        print("警告: 未检测到 Python 虚拟环境，建议先激活虚拟环境")
        print("      使用命令: python -m venv .venv")
        print("      Windows: .venv\\Scripts\\activate")
        print("      Linux/macOS: source .venv/bin/activate")
        print("      或者直接运行 pip install -r backend/requirements.txt")

    # 检查 npm（警告级别）
    npm_cmd, npm_version = check_npm_available()
    if npm_cmd:
        print(f"npm 检查通过: {npm_cmd} (版本: {npm_version})")
    else:
        print("警告: 找不到 npm，前端服务器可能无法启动")
        print("      请确保 Node.js 已安装并添加到系统 PATH")

    print("项目结构检查通过!")
    return True


def start_backend_server():
    """启动 Django 后端服务器"""
    global backend_process

    print("=" * 60)
    print("启动 Django 后端服务器...")

    # 切换到后端目录
    os.chdir(BACKEND_DIR)

    # 检查数据库迁移（可选）
    print("检查数据库迁移...")
    try:
        subprocess.run(
            [sys.executable, "manage.py", "migrate", "--check"],
            capture_output=True,
            text=True,
            check=False
        )
    except Exception as e:
        print(f"迁移检查时出错: {e}")

    # 启动 Django 开发服务器
    backend_cmd = [
        sys.executable,
        "manage.py",
        "runserver",
        f"{DJANGO_HOST}:{DJANGO_PORT}"
    ]

    print(f"执行命令: {' '.join(backend_cmd)}")
    print(f"后端地址: http://localhost:{DJANGO_PORT}/")
    print(f"API 地址: http://localhost:{DJANGO_PORT}/api/")

    # 启动进程
    backend_process = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    # 返回到根目录
    os.chdir(ROOT_DIR)

    # 等待服务器启动（检查输出）
    print("等待后端服务器启动...")
    time.sleep(2)

    return backend_process


def start_frontend_server():
    """启动 React 前端开发服务器"""
    global frontend_process

    print("=" * 60)
    print("启动 React 前端开发服务器...")

    # 切换到前端目录
    os.chdir(FRONTEND_DIR)

    # 检查 node_modules（可选）
    node_modules_dir = FRONTEND_DIR / "node_modules"
    if not node_modules_dir.exists():
        print("警告: node_modules 目录不存在，前端依赖可能未安装")
        print("      使用命令: cd frontend && npm install")
        print("      继续启动，如果失败请手动安装依赖")

    # 检查 npm 是否可用
    npm_cmd, npm_version = check_npm_available()
    if not npm_cmd:
        print("错误: 找不到 npm 可执行文件")
        print("      请确保 Node.js 已安装并添加到系统 PATH")
        if sys.platform == "win32":
            print("      Windows 用户可以从 https://nodejs.org/ 下载安装 Node.js")
        else:
            print("      Linux/macOS 用户可以使用包管理器安装: sudo apt install nodejs npm")
        raise FileNotFoundError("找不到 npm 可执行文件")

    print(f"找到 npm: {npm_cmd} (版本: {npm_version})")

    # 启动 Vite 开发服务器
    frontend_cmd = [npm_cmd, "run", "dev"]

    print(f"执行命令: {' '.join(frontend_cmd)}")
    print(f"前端地址: http://localhost:{VITE_PORT}/")

    # 在 Windows 上使用 shell=True 以正确执行 .cmd 文件
    use_shell = sys.platform == "win32"

    # 启动进程
    try:
        frontend_process = subprocess.Popen(
            frontend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            shell=use_shell
        )
    except FileNotFoundError as e:
        print(f"错误: 无法执行命令 {' '.join(frontend_cmd)}")
        print(f"      错误信息: {e}")
        print("      尝试使用 shell=True...")
        # 如果失败，尝试强制使用 shell=True
        try:
            frontend_process = subprocess.Popen(
                frontend_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True
            )
        except Exception as e2:
            print(f"再次失败: {e2}")
            print("请手动检查 npm 安装和 PATH 配置")
            raise

    # 返回到根目录
    os.chdir(ROOT_DIR)

    # 等待服务器启动
    print("等待前端服务器启动...")
    time.sleep(3)

    return frontend_process


def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    print("\n" + "=" * 60)
    print("收到停止信号，正在关闭服务器...")
    cleanup()
    sys.exit(0)


def cleanup():
    """清理子进程"""
    global backend_process, frontend_process

    print("正在停止子进程...")

    # 停止前端服务器
    if frontend_process and frontend_process.poll() is None:
        print("停止前端服务器...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
        frontend_process = None

    # 停止后端服务器
    if backend_process and backend_process.poll() is None:
        print("停止后端服务器...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        backend_process = None

    print("所有服务器已停止!")


def monitor_processes():
    """监控子进程并打印输出"""
    print("=" * 60)
    print("服务器启动完成!")
    print("=" * 60)
    print("后端: http://localhost:8000/")
    print("前端: http://localhost:5173/")
    print("API:  http://localhost:8000/api/")
    print("=" * 60)
    print("按 Ctrl+C 停止所有服务器")
    print("=" * 60)

    try:
        # 简单轮询输出
        while True:
            time.sleep(1)

            # 检查进程状态
            if backend_process and backend_process.poll() is not None:
                print("后端服务器已停止!")
                break

            if frontend_process and frontend_process.poll() is not None:
                print("前端服务器已停止!")
                break

    except KeyboardInterrupt:
        pass


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="铁路乘客分析系统 - 一键启动脚本",
        epilog="默认同时启动后端和前端开发服务器。使用 --check 只验证环境。"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="只检查依赖和环境，不启动服务器"
    )
    parser.add_argument(
        "--no-backend",
        action="store_true",
        help="不启动后端服务器"
    )
    parser.add_argument(
        "--no-frontend",
        action="store_true",
        help="不启动前端服务器"
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="只启动后端服务器"
    )
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="只启动前端服务器"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("铁路乘客分析系统 - 一键启动脚本")
    print("=" * 60)

    # 检查模式
    if args.check:
        print("运行环境检查模式...")
        if check_dependencies():
            print("\n" + "=" * 60)
            print("环境检查通过!")
            print("项目结构完整，可以正常启动。")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("环境检查失败，请修复上述问题。")
            print("=" * 60)
            sys.exit(1)

    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，请检查项目结构!")
        sys.exit(1)

    try:
        backend_proc = None
        frontend_proc = None

        # 启动后端服务器
        if not args.no_frontend and not args.frontend_only:
            if not args.no_backend and not args.frontend_only:
                backend_proc = start_backend_server()
                if backend_proc.poll() is not None:
                    print("后端服务器启动失败!")
                    if backend_proc.stdout:
                        print(backend_proc.stdout.read())
                    cleanup()
                    sys.exit(1)
            else:
                print("跳过后端服务器启动")
        else:
            if args.backend_only or not args.no_backend:
                backend_proc = start_backend_server()
                if backend_proc.poll() is not None:
                    print("后端服务器启动失败!")
                    if backend_proc.stdout:
                        print(backend_proc.stdout.read())
                    cleanup()
                    sys.exit(1)

        # 启动前端服务器
        if not args.no_backend and not args.backend_only:
            if not args.no_frontend and not args.backend_only:
                frontend_proc = start_frontend_server()
                if frontend_proc.poll() is not None:
                    print("前端服务器启动失败!")
                    if frontend_proc.stdout:
                        print(frontend_proc.stdout.read())
                    cleanup()
                    sys.exit(1)
            else:
                print("跳过前端服务器启动")
        else:
            if args.frontend_only or not args.no_frontend:
                frontend_proc = start_frontend_server()
                if frontend_proc.poll() is not None:
                    print("前端服务器启动失败!")
                    if frontend_proc.stdout:
                        print(frontend_proc.stdout.read())
                    cleanup()
                    sys.exit(1)

        # 监控进程
        monitor_processes()

    except Exception as e:
        print(f"启动过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()