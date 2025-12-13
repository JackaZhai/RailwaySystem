#!/usr/bin/env python3
"""
初始化铁路分析系统数据
1. 检查数据库迁移
2. 加载示例数据
3. 从CSV文件加载真实数据（如果存在）
"""

import os
import sys
import subprocess
import pandas as pd
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示输出"""
    print(f"\n🔧 {description}")
    print(f"   执行: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=BACKEND_DIR
        )
        if result.returncode == 0:
            print(f"   ✅ 成功")
            if result.stdout.strip():
                print(f"   输出: {result.stdout.strip()[:200]}")
        else:
            print(f"   ❌ 失败 (退出码: {result.returncode})")
            if result.stderr:
                print(f"   错误: {result.stderr.strip()[:200]}")
        return result.returncode == 0
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def check_migrations():
    """检查和应用数据库迁移"""
    print("\n📦 检查数据库迁移状态...")

    # 检查是否有待应用的迁移
    cmd = "python manage.py migrate --check"
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR
    )

    if result.returncode == 0:
        print("✅ 数据库迁移已是最新")
        return True
    else:
        print("⚠️  有待应用的数据库迁移")
        print("正在应用迁移...")
        return run_command("python manage.py migrate", "应用数据库迁移")

def load_sample_data():
    """加载内置示例数据"""
    print("\n📊 加载示例数据...")

    # 使用CLAUDE.md中的命令
    cmd = '''python manage.py shell -c "from backend.data_management.services import load_sample_data; result = load_sample_data(); print(f'已加载 {result.rows_ingested} 条记录')"'''

    if run_command(cmd, "加载示例数据"):
        print("✅ 示例数据加载完成")
        return True
    else:
        print("❌ 示例数据加载失败")
        return False

def generate_mock_data():
    """生成模拟的铁路客流数据"""
    print("\n🚆 生成模拟铁路客流数据...")

    # 创建更丰富的模拟数据
    import datetime
    import random

    # 模拟站点和线路
    stations = ["成都", "重庆", "内江", "永川", "资阳", "简阳", "荣昌", "隆昌"]
    lines = ["成渝线", "成内线", "内渝线", "成简线"]
    directions = ["N", "S", "E", "W"]

    # 生成7天的数据
    data = []
    base_date = datetime.datetime(2024, 1, 1, 8, 0, 0, tzinfo=datetime.timezone.utc)

    for day in range(7):
        for hour in range(8, 20):  # 8:00到20:00
            for minute in [0, 15, 30, 45]:  # 每15分钟
                for station in stations[:4]:  # 前4个站点
                    for line in lines[:2]:  # 前2条线路
                        timestamp = base_date + datetime.timedelta(
                            days=day,
                            hours=hour-8,
                            minutes=minute
                        )

                        # 生成合理的客流数据
                        base_traffic = random.randint(50, 200)
                        hour_factor = 1.0
                        if hour in [8, 9, 17, 18]:  # 高峰时段
                            hour_factor = 2.5
                        elif hour in [12, 13]:  # 午间
                            hour_factor = 1.5

                        passengers_in = int(base_traffic * hour_factor * random.uniform(0.8, 1.2))
                        passengers_out = int(base_traffic * hour_factor * random.uniform(0.8, 1.2))
                        direction = random.choice(directions)

                        data.append({
                            "timestamp": timestamp.isoformat(),
                            "station": station,
                            "line": line,
                            "direction": direction,
                            "passengers_in": passengers_in,
                            "passengers_out": passengers_out
                        })

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 保存到CSV文件
    csv_path = BACKEND_DIR / "sample_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ 生成 {len(df)} 条模拟数据，保存到: {csv_path}")

    # 加载到数据库
    print("正在导入模拟数据到数据库...")

    # 创建导入脚本
    import_script = BACKEND_DIR / "import_sample.py"
    import_script_content = """
import pandas as pd
from backend.data_management.services import DataIngestionService
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'railway_backend.settings')
django.setup()

# 读取CSV文件
df = pd.read_csv('sample_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 导入数据
service = DataIngestionService(chunk_size=1000)
result = service._import_dataframe(df)

print(f"导入完成:")
print(f"  总行数: {result.total_rows}")
print(f"  成功导入: {result.rows_ingested}")
print(f"  失败: {result.rows_failed}")
if result.errors:
    print(f"  错误: {result.errors}")
"""

    import_script.write_text(import_script_content)

    # 运行导入
    cmd = f"python manage.py shell < {import_script}"
    success = run_command(cmd, "导入模拟数据")

    # 清理临时文件
    if csv_path.exists():
        csv_path.unlink()
    if import_script.exists():
        import_script.unlink()

    return success

def check_api_data():
    """检查API是否有数据"""
    print("\n📡 检查API数据...")

    try:
        import requests
        import time

        # 等待服务器启动（如果刚启动的话）
        time.sleep(2)

        endpoints = [
            ("客流分析", "/api/analytics/flow/"),
            ("时间趋势", "/api/analytics/temporal/?freq=H"),
            ("空间分布", "/api/analytics/spatial/"),
            ("线路优化", "/api/lines/recommendations/"),
            ("站点指标", "/api/stations/metrics/"),
        ]

        has_data = False
        for name, endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        print(f"✅ {name}: {len(data)} 条数据")
                        has_data = True
                    else:
                        print(f"⚠️  {name}: 无数据")
                else:
                    print(f"❌ {name}: HTTP {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"❌ {name}: 无法连接到服务器")
            except Exception as e:
                print(f"❌ {name}: 错误 - {e}")

        return has_data

    except ImportError:
        print("⚠️  无法导入requests模块，跳过API检查")
        return True
    except Exception as e:
        print(f"❌ API检查失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("铁路分析系统 - 数据初始化工具")
    print("=" * 60)

    # 检查当前目录
    current_dir = Path(__file__).parent
    if not (current_dir / "backend" / "manage.py").exists():
        print("❌ 错误: 请在项目根目录运行此脚本")
        print(f"   当前目录: {current_dir}")
        print(f"   未找到: backend/manage.py")
        return 1

    print(f"📁 项目目录: {current_dir}")

    # 设置全局变量
    global BACKEND_DIR
    BACKEND_DIR = current_dir / "backend"

    # 步骤1: 数据库迁移
    if not check_migrations():
        print("\n❌ 数据库迁移失败，请手动检查:")
        print("   cd backend")
        print("   python manage.py migrate")
        return 1

    # 步骤2: 询问用户要加载什么数据
    print("\n" + "=" * 60)
    print("选择要加载的数据类型:")
    print("  1. 仅加载最小示例数据 (2条记录)")
    print("  2. 生成模拟铁路客流数据 (推荐)")
    print("  3. 跳过数据加载")

    choice = input("\n请选择 (1-3, 默认 2): ").strip()

    if choice == "1":
        if not load_sample_data():
            print("\n❌ 示例数据加载失败")
            return 1
    elif choice == "2" or choice == "":
        if not generate_mock_data():
            print("\n❌ 模拟数据生成失败")
            return 1
    elif choice == "3":
        print("\n⏭️  跳过数据加载")
    else:
        print(f"\n❌ 无效选择: {choice}")
        return 1

    # 步骤3: 检查API数据
    print("\n" + "=" * 60)
    print("数据加载完成!")

    if choice in ["1", "2", ""]:
        print("\n🔍 建议进行API检查:")
        print("   1. 确保后端服务器正在运行")
        print("   2. 运行测试脚本: python test_backend.py")
        print("\n📋 启动命令:")
        print("   一键启动: python start_dev.py")
        print("   或手动启动:")
        print("     cd backend && python manage.py runserver")
        print("     cd frontend && npm run dev")

    print("\n" + "=" * 60)
    print("初始化完成!")
    return 0

if __name__ == "__main__":
    BACKEND_DIR = None
    sys.exit(main())