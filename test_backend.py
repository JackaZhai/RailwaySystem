#!/usr/bin/env python3
"""
测试后端API是否可用
"""

import requests
import sys
import time

def test_backend_api():
    """测试后端API端点"""
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/analytics/flow/",
        "/api/analytics/temporal/?freq=H",
        "/api/analytics/spatial/",
        "/api/lines/recommendations/",
        "/api/stations/metrics/"
    ]

    print("=" * 60)
    print("测试后端API连接...")
    print(f"后端地址: {base_url}")
    print("=" * 60)

    all_ok = True

    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: 成功 (返回 {len(data)} 条数据)")
                if len(data) == 0:
                    print(f"   警告: 端点返回空数据，可能需要加载测试数据")
            else:
                print(f"❌ {endpoint}: 失败 (状态码: {response.status_code})")
                all_ok = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: 连接失败 (后端服务器可能未运行)")
            all_ok = False
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint}: 请求超时")
            all_ok = False
        except Exception as e:
            print(f"❌ {endpoint}: 错误 ({e})")
            all_ok = False

    print("=" * 60)
    if all_ok:
        print("✅ 所有API端点测试通过!")
    else:
        print("⚠️  部分API端点存在问题")
        print("\n建议:")
        print("1. 确保后端服务器正在运行: python backend/manage.py runserver")
        print("2. 加载测试数据: python backend/manage.py shell -c \"from backend.data_management.services import load_sample_data; load_sample_data()\"")
        print("3. 检查数据库迁移: python backend/manage.py migrate")

    return all_ok

def check_django_server():
    """检查Django服务器是否运行"""
    print("\n" + "=" * 60)
    print("检查Django服务器状态...")
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        if response.status_code == 200:
            print("✅ Django服务器正在运行")
            return True
        else:
            print(f"⚠️  Django服务器响应异常 (状态码: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Django服务器未运行")
        return False
    except Exception as e:
        print(f"❌ 检查Django服务器时出错: {e}")
        return False

def main():
    """主函数"""
    print("铁路分析系统 - 后端API测试")
    print("=" * 60)

    # 首先检查服务器是否运行
    if not check_django_server():
        print("\n请先启动后端服务器:")
        print("方法1: 使用一键启动脚本")
        print("  python start_dev.py")
        print("\n方法2: 手动启动后端")
        print("  cd backend")
        print("  python manage.py runserver")
        sys.exit(1)

    # 测试API端点
    print("\n" + "=" * 60)
    print("开始API端点测试...")
    api_ok = test_backend_api()

    if not api_ok:
        print("\n" + "=" * 60)
        print("故障排除步骤:")
        print("1. 确保已应用数据库迁移:")
        print("   python backend/manage.py migrate")
        print("\n2. 加载测试数据:")
        print("   python backend/manage.py shell -c \"from backend.data_management.services import load_sample_data; load_sample_data()\"")
        print("\n3. 如果以上都失败，检查后端日志:")
        print("   查看 backend/ 目录下的控制台输出")

    print("\n" + "=" * 60)
    print("测试完成!")
    return 0 if api_ok else 1

if __name__ == "__main__":
    sys.exit(main())