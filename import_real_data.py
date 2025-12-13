#!/usr/bin/env python3
"""
铁路分析系统 - 真实数据导入脚本（最终版）
从 db/migrations 文件夹加载真实的铁路客运数据到数据库
使用正确的CSV结构：跳过前2行，使用拼音列名
"""
import os
import sys
import django
import pandas as pd
from pathlib import Path
import logging
import warnings
warnings.filterwarnings('ignore')

# 设置Django环境
sys.path.insert(0, str(Path(__file__).parent / "backend"))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'railway_backend.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django设置失败: {e}")
    print("\n请确保已安装所有依赖: pip install -r backend/requirements.txt")
    sys.exit(1)

from backend.data_management.models import PassengerRecord

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealDataImporter:
    """真实铁路数据导入器（最终版）"""

    def __init__(self, data_dir="db/migrations"):
        self.data_dir = Path(data_dir)
        self.station_map = {}  # 站点ID -> 站点名称
        self.column_names = []  # 客运数据列名

    def load_column_names(self):
        """加载客运数据的列名（拼音列名）"""
        logger.info("加载客运数据列名...")
        passenger_file = self.data_dir / "高铁客运量（成都--重庆）（运营线路编码、列车编码、站点id、日期、到达时间、出发时间、上客量、下客量等，起点站、终点站、票价、收入等）.csv"

        if not passenger_file.exists():
            logger.error(f"客运文件不存在: {passenger_file}")
            return False

        try:
            # 读取第一行获取拼音列名
            df_header = pd.read_csv(passenger_file, encoding='utf-8', nrows=1)
            self.column_names = df_header.columns.tolist()
            logger.info(f"加载了 {len(self.column_names)} 个列名")
            logger.info(f"前10个列名: {self.column_names[:10]}")
            return True
        except Exception as e:
            logger.error(f"加载列名失败: {e}")
            return False

    def load_station_mapping(self):
        """加载站点ID到名称的映射"""
        logger.info("加载站点映射数据...")
        station_file = self.data_dir / "客运站点（站点名称、站点编号、备注）.csv"

        if not station_file.exists():
            logger.error(f"站点文件不存在: {station_file}")
            return False

        # 尝试不同编码
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
            try:
                # 读取第一行获取列名
                df_header = pd.read_csv(station_file, encoding=encoding, nrows=1)
                station_col_names = df_header.columns.tolist()

                # 读取数据，跳过前2行，使用拼音列名
                df = pd.read_csv(
                    station_file,
                    encoding=encoding,
                    skiprows=2,
                    names=station_col_names,
                    nrows=None  # 读取所有行
                )

                # 创建映射
                for _, row in df.iterrows():
                    station_id = row.get('zdid')
                    station_name = row.get('zdmc')
                    if pd.notna(station_id) and pd.notna(station_name):
                        self.station_map[int(station_id)] = str(station_name).strip()

                logger.info(f"使用编码 {encoding} 建立了 {len(self.station_map)} 个站点的映射")
                return True

            except Exception as e:
                logger.warning(f"编码 {encoding} 失败: {e}")
                continue

        logger.error("所有编码尝试都失败")
        return False

    def convert_passenger_data(self, sample_only=False, sample_size=10000):
        """转换高铁客运数据为PassengerRecord格式"""
        logger.info("转换高铁客运数据...")
        passenger_file = self.data_dir / "高铁客运量（成都--重庆）（运营线路编码、列车编码、站点id、日期、到达时间、出发时间、上客量、下客量等，起点站、终点站、票价、收入等）.csv"

        if not passenger_file.exists():
            logger.error(f"客运文件不存在: {passenger_file}")
            return []

        try:
            # 确定读取行数
            nrows = sample_size if sample_only else None

            logger.info(f"读取客运数据 (样本模式: {sample_only}, 行数: {nrows})...")

            # 使用chunksize分批读取大文件
            chunksize = 50000
            records = []
            total_rows = 0
            chunk_num = 0

            # 创建读取器
            reader = pd.read_csv(
                passenger_file,
                encoding='utf-8',
                skiprows=2,
                names=self.column_names,
                chunksize=chunksize,
                nrows=nrows,
                low_memory=False
            )

            for chunk in reader:
                chunk_num += 1
                logger.info(f"处理第 {chunk_num} 块, 大小: {len(chunk)} 行")

                chunk_records = self._process_chunk(chunk)
                records.extend(chunk_records)
                total_rows += len(chunk)

                logger.info(f"已转换 {len(chunk_records)} 条记录, 累计 {len(records)} 条")

                # 如果是样本模式，达到目标后停止
                if sample_only and total_rows >= sample_size:
                    break

            logger.info(f"转换完成: 总共处理 {total_rows} 行, 转换出 {len(records)} 条记录")
            return records

        except Exception as e:
            logger.error(f"转换客运数据失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _process_chunk(self, chunk):
        """处理一个数据块"""
        records = []

        for _, row in chunk.iterrows():
            try:
                # 获取关键字段
                station_id = int(float(row['zdid'])) if pd.notna(row['zdid']) else 0
                line_code = int(float(row['yyxlbm'])) if pd.notna(row['yyxlbm']) else 0
                date_val = row['yxrq']
                time_val = row['yxsj']
                passengers_in = int(float(row['skl'])) if pd.notna(row['skl']) else 0
                passengers_out = int(float(row['xkl'])) if pd.notna(row['xkl']) else 0

                # 跳过没有客流的记录
                if passengers_in == 0 and passengers_out == 0:
                    continue

                # 获取车站名称
                station_name = self.station_map.get(station_id, f"车站{station_id}")

                # 解析日期时间
                if pd.isna(date_val) or pd.isna(time_val):
                    continue

                try:
                    date_str = str(int(float(date_val)))
                    time_str = str(int(float(time_val))).zfill(4)

                    if len(date_str) != 8 or len(time_str) != 4:
                        continue

                    datetime_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {time_str[:2]}:{time_str[2:4]}:00"
                    # 添加时区信息
                    timestamp = pd.to_datetime(datetime_str, errors='coerce')
                    if pd.isna(timestamp):
                        continue
                    # 转换为上海时区
                    timestamp = timestamp.tz_localize('Asia/Shanghai')
                except:
                    continue

                # 获取方向信息（如果有）
                direction = ""
                if 'sxxbm' in row and pd.notna(row['sxxbm']):
                    direction = str(row['sxxbm'])

                # 创建记录
                record = PassengerRecord(
                    timestamp=timestamp,
                    station=station_name,
                    line=f"线路{line_code}",
                    direction=direction,
                    passengers_in=passengers_in,
                    passengers_out=passengers_out,
                    metadata={
                        'source': 'real_data',
                        'station_id': station_id,
                        'line_code': line_code,
                        'original_date': date_str,
                        'original_time': time_str
                    }
                )
                records.append(record)

            except Exception as e:
                # 静默失败，继续处理下一行
                continue

        return records

    def import_to_database(self, records, batch_size=2000):
        """将记录导入数据库"""
        logger.info(f"准备导入 {len(records)} 条记录到数据库...")

        if not records:
            logger.warning("没有记录可导入")
            return False

        try:
            total_imported = 0
            num_batches = (len(records) + batch_size - 1) // batch_size

            # 分批导入
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                batch_num = i // batch_size + 1

                # 使用bulk_create，忽略重复记录
                PassengerRecord.objects.bulk_create(batch, ignore_conflicts=True)
                total_imported += len(batch)

                logger.info(f"批次 {batch_num}/{num_batches}: 已导入 {total_imported} / {len(records)} 条记录")

            logger.info(f"成功导入 {total_imported} 条记录到数据库")
            return True

        except Exception as e:
            logger.error(f"导入数据库失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self, sample_only=False, sample_size=10000):
        """运行完整的数据导入流程"""
        logger.info("=" * 60)
        logger.info("开始导入真实铁路客运数据")
        if sample_only:
            logger.info(f"样本模式: 只导入前 {sample_size} 行数据")
        logger.info("=" * 60)

        # 步骤1: 加载列名
        logger.info("\n1. 加载列名...")
        if not self.load_column_names():
            logger.error("加载列名失败，终止导入")
            return False

        # 步骤2: 加载站点映射
        logger.info("\n2. 加载站点映射...")
        if not self.load_station_mapping():
            logger.error("加载站点映射失败，终止导入")
            return False

        # 步骤3: 转换客运数据
        logger.info("\n3. 转换客运数据...")
        records = self.convert_passenger_data(sample_only=sample_only, sample_size=sample_size)

        if not records:
            logger.error("没有转换出任何乘客记录")
            return False

        # 步骤4: 导入数据库
        logger.info("\n4. 导入数据库...")
        success = self.import_to_database(records, batch_size=2000)

        if success:
            logger.info("=" * 60)
            logger.info("数据导入成功完成!")
            logger.info(f"总共导入 {len(records)} 条记录")
            logger.info("=" * 60)
        else:
            logger.error("数据导入失败!")

        return success

def main():
    """主函数"""
    print("=" * 60)
    print("铁路分析系统 - 真实数据导入工具（最终版）")
    print("=" * 60)

    # 检查数据目录
    data_dir = Path("db/migrations")
    if not data_dir.exists():
        print(f"错误: 数据目录不存在: {data_dir}")
        print("请确保 db/migrations 文件夹存在并包含CSV文件")
        return 1

    print(f"数据目录: {data_dir.absolute()}")

    # 询问用户
    print("\n选择导入模式:")
    print("  1. 样本模式 (导入前10000行数据用于测试)")
    print("  2. 完整模式 (导入所有数据，约50万行)")
    print("  3. 自定义样本大小")

    choice = input("\n请选择 (1-3, 默认 1): ").strip()

    sample_only = True
    sample_size = 10000

    if choice == "2":
        sample_only = False
        print("\n警告: 完整模式将导入约50万行数据")
        print("这可能需要几分钟时间和几百MB内存")
        confirm = input("确定要继续吗? (y/N): ").strip().lower()
        if confirm != 'y':
            print("用户取消")
            return 1
    elif choice == "3":
        try:
            sample_size = int(input("请输入样本大小 (例如 50000): ").strip())
            print(f"将导入前 {sample_size} 行数据")
        except:
            print("无效输入，使用默认10000行")
            sample_size = 10000
    else:  # 默认或选择1
        print(f"\n使用样本模式: 导入前 {sample_size} 行数据")

    # 运行导入器
    importer = RealDataImporter()

    try:
        if importer.run(sample_only=sample_only, sample_size=sample_size):
            total_records = PassengerRecord.objects.count()
            print("\n" + "=" * 60)
            print("成功! 数据已导入数据库")
            print(f"数据库现在包含 {total_records} 条记录")
            print("\n下一步:")
            print("  1. 启动后端服务器: python start_dev.py")
            print("  2. 或手动启动:")
            print("     cd backend && python manage.py runserver")
            print("     cd frontend && npm run dev")
            print("  3. 访问 http://localhost:5173 查看数据可视化")
            print("=" * 60)
            return 0
        else:
            print("\n" + "=" * 60)
            print("数据导入失败!")
            print("=" * 60)
            return 1

    except KeyboardInterrupt:
        print("\n\n用户中断导入过程")
        return 1
    except Exception as e:
        print(f"\n导入过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())