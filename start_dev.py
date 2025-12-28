#!/usr/bin/env python3
"""
铁路客运智能分析与可视化系统 - 一键启动脚本 (Python版本)
启动后端Django服务器，等待5秒后启动前端Vite开发服务器
"""

import os
import sys
import time
import subprocess
import signal
import atexit
from pathlib import Path

def print_header():
    """打印标题"""
    print("🚂 铁路客运智能分析与可视化系统 - 一键启动")
    print("=" * 50)

def cleanup(backend_proc, frontend_proc):
    """清理函数，用于优雅地关闭进程"""
    print("\n🛑 正在关闭服务器...")

    if frontend_proc and frontend_proc.poll() is None:
        print("  关闭前端服务器...")
        frontend_proc.terminate()
        try:
            frontend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_proc.kill()

    if backend_proc and backend_proc.poll() is None:
        print("  关闭后端服务器...")
        backend_proc.terminate()
        try:
            backend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_proc.kill()

    print("✅ 服务器已关闭")

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")

    # 检查Python
    try:
        subprocess.run([sys.executable, "--version"], capture_output=True, check=True)
        print("  ✅ Python可用")
    except:
        print("  ❌ Python不可用")
        return False

    # 检查npm
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        print("  ✅ npm可用")
    except:
        print("  ❌ npm不可用")
        return False

    return True

def start_backend(backend_dir):
    """启动后端服务器"""
    print("\n🚀 启动后端Django服务器...")

    # 切换到后端目录
    os.chdir(backend_dir)

    # 启动Django服务器
    backend_proc = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "0.0.0.0:8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    print(f"  后端服务器启动中 (PID: {backend_proc.pid}, 端口: 8080)")

    # 等待后端启动
    print("⏳ 等待后端服务器启动...")
    time.sleep(5)

    # 检查后端是否在运行
    if backend_proc.poll() is not None:
        print("❌ 错误: 后端服务器启动失败")
        # 打印输出
        output, _ = backend_proc.communicate()
        if output:
            print("后端输出:")
            print(output[:500])  # 只打印前500字符
        return None

    # 测试后端API
    print("🔍 测试后端API连接...")
    try:
        import urllib.request
        import urllib.error
        response = urllib.request.urlopen("http://localhost:8080/api/stations/?format=json", timeout=5)
        if response.status == 200:
            print("✅ 后端API连接成功")
        else:
            print("⚠️  后端API返回非200状态码")
    except Exception as e:
        print(f"⚠️  后端API连接测试失败: {e}")
        print("   但继续启动前端...")

    return backend_proc

def start_frontend(frontend_dir):
    """启动前端服务器"""
    print("\n🚀 启动前端Vite开发服务器...")

    # 切换到前端目录
    os.chdir(frontend_dir)

    # 检查node_modules
    if not os.path.exists("node_modules"):
        print("📦 未找到node_modules，正在安装依赖...")
        install_proc = subprocess.run(
            ["npm", "install"],
            capture_output=True,
            text=True
        )
        if install_proc.returncode != 0:
            print("❌ npm install 失败")
            print(install_proc.stderr)
            return None

    # 启动Vite开发服务器
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    print(f"  前端服务器启动中 (PID: {frontend_proc.pid})")

    # 等待前端启动
    print("⏳ 等待前端服务器启动...")
    time.sleep(3)

    # 检查前端是否在运行
    if frontend_proc.poll() is not None:
        print("❌ 错误: 前端服务器启动失败")
        # 打印输出
        output, _ = frontend_proc.communicate()
        if output:
            print("前端输出:")
            print(output[:500])  # 只打印前500字符
        return None

    # 检查端口
    frontend_port = 5173
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("localhost", frontend_port))
        sock.close()
        # 端口可用，但Vite可能用了其他端口
        print(f"⚠️  端口 {frontend_port} 可用，但Vite可能使用了其他端口")
        print(f"   请检查Vite输出确认实际端口")
    except:
        print(f"✅ 前端服务器运行在端口: {frontend_port}")

    return frontend_proc

def main():
    """主函数"""
    print_header()

    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"

    print(f"📁 项目根目录: {project_root}")
    print(f"🔧 后端目录: {backend_dir}")
    print(f"🎨 前端目录: {frontend_dir}")

    # 检查目录是否存在
    if not backend_dir.exists():
        print(f"❌ 错误: 后端目录不存在: {backend_dir}")
        sys.exit(1)

    if not frontend_dir.exists():
        print(f"❌ 错误: 前端目录不存在: {frontend_dir}")
        sys.exit(1)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    backend_proc = None
    frontend_proc = None

    try:
        # 启动后端
        backend_proc = start_backend(backend_dir)
        if backend_proc is None:
            sys.exit(1)

        # 启动前端
        frontend_proc = start_frontend(frontend_dir)
        if frontend_proc is None:
            cleanup(backend_proc, None)
            sys.exit(1)

        # 注册清理函数
        def cleanup_handler():
            cleanup(backend_proc, frontend_proc)

        atexit.register(cleanup_handler)
        signal.signal(signal.SIGINT, lambda s, f: cleanup_handler())
        signal.signal(signal.SIGTERM, lambda s, f: cleanup_handler())

        # 显示成功信息
        print("\n" + "=" * 50)
        print("🎉 系统启动完成！")
        print()
        print("🌐 访问地址:")
        print("   前端界面: http://localhost:5173 (或查看Vite输出确认端口)")
        print("   后端API:  http://localhost:8080/api/")
        print()
        print("📊 API端点示例:")
        print("   - 站点列表: http://localhost:8080/api/stations/")
        print("   - 列车列表: http://localhost:8080/api/trains/")
        print("   - 客运记录: http://localhost:8080/api/passenger-flows/")
        print("   - 客流分析: http://localhost:8080/api/analytics/flow/ (POST)")
        print()
        print("🛑 按 Ctrl+C 关闭所有服务器")
        print("=" * 50)

        # 等待进程结束
        print("\n📋 服务器日志:")
        print("-" * 30)

        # 创建线程来读取输出（简化版本，只等待）
        try:
            # 简单等待，不处理输出
            while backend_proc.poll() is None and frontend_proc.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n接收到中断信号")
            cleanup_handler()

    except Exception as e:
        print(f"\n❌ 启动过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        cleanup(backend_proc, frontend_proc)
        sys.exit(1)
        
if __name__ == "__main__":
    main()