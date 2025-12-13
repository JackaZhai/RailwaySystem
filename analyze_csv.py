#!/usr/bin/env python3
"""
深入分析 db/migrations 下的CSV文件
"""

import pandas as pd
import os
import sys
from pathlib import Path

def analyze_csv_file(file_path, sample_rows=10):
    """深入分析CSV文件"""
    print(f"\n{'='*80}")
    print(f"分析文件: {os.path.basename(file_path)}")
    print(f"{'='*80}")

    if not os.path.exists(file_path):
        print("文件不存在!")
        return None

    # 尝试不同编码
    encodings = ['gbk', 'gb2312', 'utf-8', 'utf-8-sig', 'latin1']
    df = None
    used_encoding = None

    for encoding in encodings:
        try:
            # 读取前几行检查
            df = pd.read_csv(file_path, encoding=encoding, nrows=100)
            print(f"[成功] 使用编码: {encoding}")
            used_encoding = encoding
            break
        except Exception as e:
            continue

    if df is None:
        print("[失败] 无法读取文件，尝试过的编码:", encodings)
        return None

    # 基本信息
    print(f"文件大小: {os.path.getsize(file_path)} 字节")
    print(f"行数: {len(df)}")
    print(f"列数: {len(df.columns)}")

    # 列信息
    print("\n[列信息]:")
    for i, col in enumerate(df.columns):
        # 检查列类型和示例值
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()
        sample_value = df[col].iloc[0] if non_null > 0 else "N/A"

        print(f"  {i+1:2d}. {col:30s} | 非空: {non_null:4d} | 空值: {null_count:4d} | 示例: {str(sample_value)[:50]}")

    # 数据预览
    print(f"\n[预览] 数据预览 (前{sample_rows}行):")
    print(df.head(sample_rows).to_string())

    # 数据类型统计
    print(f"\n[类型统计] 数据类型统计:")
    print(df.dtypes.to_string())

    # 检查是否有中文表头行
    first_row_values = df.iloc[0].astype(str).values
    has_chinese_header = any(any('\u4e00' <= c <= '\u9fff' for c in str(val)) for val in first_row_values)

    if has_chinese_header:
        print("\n[警告] 第一行数据可能包含中文表头（需要跳过第一行）")
        print("第一行内容:")
        print(df.iloc[0].to_dict())

    return df, used_encoding, has_chinese_header

def compare_with_passenger_record(df, filename):
    """比较CSV结构与现有PassengerRecord模型"""
    print(f"\n[模型比较] 与PassengerRecord模型比较:")

    # PassengerRecord模型字段
    passenger_record_fields = {
        'timestamp': 'DateTime',
        'station': 'str',
        'line': 'str',
        'direction': 'str',
        'passengers_in': 'int',
        'passengers_out': 'int',
        'metadata': 'JSON'
    }

    csv_columns = set(df.columns.str.lower().str.strip())
    model_fields = set(passenger_record_fields.keys())

    print(f"PassengerRecord字段: {model_fields}")
    print(f"CSV列名: {csv_columns}")

    # 寻找可能的映射
    potential_mappings = {}

    # 常见字段映射
    field_mappings = {
        'timestamp': ['timestamp', '时间', '日期', 'datetime', 'time', 'date', 'yxrq', 'yxsj', 'ddsj', 'cfsj'],
        'station': ['station', '站点', '车站', 'zdmc', 'station_name'],
        'line': ['line', '线路', 'line_code', 'xldm', 'yyxlbm'],
        'passengers_in': ['passengers_in', '进站', '上客', 'skl', 'in', '上车'],
        'passengers_out': ['passengers_out', '出站', '下客', 'xkl', 'out', '下车']
    }

    for model_field, possible_names in field_mappings.items():
        found = None
        for possible in possible_names:
            if possible in csv_columns:
                found = possible
                break
            # 检查部分匹配
            for col in csv_columns:
                if possible.lower() in col.lower() or col.lower() in possible.lower():
                    found = col
                    break
            if found:
                break
        if found:
            potential_mappings[model_field] = found
            print(f"  ✅ {model_field} -> {found}")
        else:
            print(f"  ❌ {model_field}: 未找到匹配列")

    return potential_mappings

def main():
    """主函数"""
    print("铁路客运数据CSV文件分析")
    print("="*80)

    csv_files = [
        "db/migrations/客运站点（站点名称、站点编号、备注）.csv",
        "db/migrations/列车表（列车编码、列车代码、列车运量）(2).csv",
        "db/migrations/运营线路客运站（运营线路编码、站点id、线路站点id、上一站id、运营线路站间距离 、下一站id、运输距离、线路代码）.csv",
        "db/migrations/高铁客运量（成都--重庆）（运营线路编码、列车编码、站点id、日期、到达时间、出发时间、上客量、下客量等，起点站、终点站、票价、收入等）.csv"
    ]

    all_analysis = {}

    for file_path in csv_files:
        if os.path.exists(file_path):
            result = analyze_csv_file(file_path)
            if result:
                df, encoding, has_chinese_header = result
                all_analysis[file_path] = {
                    'df': df,
                    'encoding': encoding,
                    'has_chinese_header': has_chinese_header,
                    'filename': os.path.basename(file_path)
                }

                # 特别分析高铁客流数据
                if "高铁客运量" in file_path:
                    print("\n[详细分析] 高铁客流数据详细分析:")
                    mappings = compare_with_passenger_record(df, os.path.basename(file_path))

                    # 检查时间相关字段
                    time_cols = [col for col in df.columns if any(word in col.lower() for word in ['时间', 'date', 'time', 'sj', 'rq'])]
                    print(f"时间相关列: {time_cols}")

                    # 检查客流相关字段
                    passenger_cols = [col for col in df.columns if any(word in col.lower() for word in ['客', 'passenger', 'skl', 'xkl'])]
                    print(f"客流相关列: {passenger_cols}")
        else:
            print(f"\n❌ 文件不存在: {file_path}")

    # 总结分析
    print("\n" + "="*80)
    print("[分析总结] 分析总结")
    print("="*80)

    for file_path, info in all_analysis.items():
        print(f"\n[文件] {info['filename']}:")
        print(f"  编码: {info['encoding']}")
        print(f"  是否有中文表头: {info['has_chinese_header']}")
        print(f"  数据形状: {info['df'].shape}")
        print(f"  列名: {list(info['df'].columns)}")

    # 生成数据导入建议
    print("\n" + "="*80)
    print("🚀 数据导入建议")
    print("="*80)

    # 找到主要的客流数据文件
    passenger_file = None
    for file_path, info in all_analysis.items():
        if "高铁客运量" in info['filename']:
            passenger_file = info
            break

    if passenger_file:
        print("\n主要客流数据文件: 高铁客运量.csv")
        df = passenger_file['df']

        # 建议的字段映射
        print("\n建议的字段映射:")
        print("  1. 时间字段: 需要确定哪个字段作为timestamp")
        print("  2. 站点字段: 需要从站点ID映射到站点名称")
        print("  3. 线路字段: 需要从运营线路编码映射到线路名称")
        print("  4. 客流字段: skl(上客量) -> passengers_in, xkl(下客量) -> passengers_out")

        # 检查必要的数据关联
        print("\n需要的数据关联:")
        print("  ✓ 站点ID到站点名称的映射 (从客运站点.csv)")
        print("  ✓ 运营线路编码到线路名称的映射 (从运营线路客运站.csv)")
        print("  ✓ 列车编码到列车信息的映射 (从列车表.csv)")

    return 0

if __name__ == "__main__":
    sys.exit(main())