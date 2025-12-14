#!/usr/bin/env python3
"""
一键启动前端开发服务器（简化版）

功能：
1. 检查Node.js环境
2. 自动安装前端依赖
3. 启动Vite开发服务器

使用方法：
python start_frontend_simple.py
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def run_command(cmd, cwd=None, description=""):
    """运行命令并显示输出"""
    if description:
        print(f"[INFO] {description}")

    try:
        process = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        if process.returncode == 0:
            if process.stdout.strip():
                print(f"[SUCCESS] 完成")
            return True
        else:
            print(f"[ERROR] 失败")
            if process.stderr:
                print(f"错误信息:\n{process.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] 执行命令时出错: {e}")
        return False

def check_nodejs():
    """检查Node.js是否安装"""
    print("=" * 60)
    print("检查Node.js环境...")

    # 检查node命令
    try:
        result = subprocess.run(['node', '--version'],
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"[SUCCESS] Node.js版本: {result.stdout.strip()}")
        else:
            print("[ERROR] Node.js未安装或未在PATH中")
            print("请从 https://nodejs.org/ 下载安装Node.js")
            return False
    except:
        print("[ERROR] 无法执行node命令")
        return False

    # 检查npm命令
    try:
        result = subprocess.run(['npm', '--version'],
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"[SUCCESS] npm版本: {result.stdout.strip()}")
            return True
        else:
            print("[ERROR] npm未安装或未在PATH中")
            return False
    except:
        print("[ERROR] 无法执行npm命令")
        return False

def install_dependencies():
    """安装前端依赖"""
    print("=" * 60)
    print("安装前端依赖...")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("[ERROR] frontend目录不存在")
        return False

    # 检查是否已安装依赖
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print("[INFO] 依赖似乎已安装，跳过安装步骤")
        return True

    # 安装依赖
    return run_command(
        "npm install",
        cwd="frontend",
        description="正在安装npm依赖..."
    )

def start_dev_server():
    """启动开发服务器"""
    print("=" * 60)
    print("启动开发服务器...")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        return False

    print("[INFO] 服务器将在 http://localhost:5173 启动")
    print("[INFO] 按 Ctrl+C 停止服务器")

    try:
        # 启动开发服务器
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )

        # 等待服务器启动
        print("[INFO] 等待服务器启动...")
        time.sleep(3)

        # 检查进程是否仍在运行
        if process.poll() is not None:
            print("[ERROR] 服务器启动失败")
            return False

        print("[SUCCESS] 开发服务器已启动!")

        # 尝试打开浏览器 - Vite已配置自动打开，此处不再重复打开
        # try:
        #     webbrowser.open("http://localhost:5173")
        #     print("[INFO] 已在浏览器中打开应用")
        # except:
        #     print("[INFO] 请手动访问: http://localhost:5173")

        print("\n" + "=" * 60)
        print("服务器日志:")
        print("=" * 60)

        # 输出服务器日志
        try:
            for line in process.stdout:
                if line:
                    print(line.rstrip())
        except KeyboardInterrupt:
            print("\n[INFO] 正在停止服务器...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()

        return True

    except Exception as e:
        print(f"[ERROR] 启动服务器时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("铁路客运分析系统 - 前端一键启动脚本")
    print("=" * 60)

    # 检查环境
    if not check_nodejs():
        input("\n按Enter键退出...")
        sys.exit(1)

    # 安装依赖
    if not install_dependencies():
        input("\n按Enter键退出...")
        sys.exit(1)

    # 启动服务器
    if not start_dev_server():
        input("\n按Enter键退出...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] 未处理的错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")
        sys.exit(1)