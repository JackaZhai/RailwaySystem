import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, time
from django.db import transaction
from .models import Station, Train, Route, RouteStation, PassengerFlow
import logging

logger = logging.getLogger(__name__)


class DataImportService:
    """数据导入服务"""

    def __init__(self, data_dir=None):
        self.data_dir = data_dir or Path(__file__).parent.parent / 'db'
        logger.info(f"数据目录: {self.data_dir}")

    def import_all_data(self):
        """导入所有数据"""
        try:
            with transaction.atomic():
                logger.info("开始导入所有数据...")

                # 按顺序导入：站点 -> 列车 -> 线路 -> 线路站点 -> 客运记录
                self.import_stations()
                self.import_trains()
                self.import_routes()
                self.import_route_stations()
                self.import_passenger_flow()

                logger.info("所有数据导入完成！")
                return True
        except Exception as e:
            logger.error(f"数据导入失败: {e}")
            raise

    def import_stations(self):
        """导入站点数据"""
        file_path = self.data_dir / 'stations.csv'
        logger.info(f"导入站点数据: {file_path}")

        # 读取CSV，跳过中文说明行（第二行）
        df = pd.read_csv(file_path, skiprows=[1])

        stations = []
        for _, row in df.iterrows():
            station = Station(
                id=int(row['zdid']),
                travel_area_id=int(row['lxid']) if pd.notna(row['lxid']) else None,
                name=str(row['zdmc']).strip(),
                code=int(row['station_code']) if pd.notna(row['station_code']) else None,
                telecode=str(row['station_telecode']).strip(),
                shortname=str(row['station_shortname']).strip() if pd.notna(row['station_shortname']) else None,
            )
            stations.append(station)

        Station.objects.bulk_create(stations, ignore_conflicts=True)
        logger.info(f"导入 {len(stations)} 个站点")

    def import_trains(self):
        """导入列车数据"""
        file_path = self.data_dir / 'trains.csv'
        logger.info(f"导入列车数据: {file_path}")

        # 读取CSV，跳过中文说明行（第二行）
        df = pd.read_csv(file_path, skiprows=[1])

        trains = []
        for _, row in df.iterrows():
            # 跳过空行
            if pd.isna(row['lcbm']):
                continue

            train = Train(
                id=int(row['lcbm']),
                code=str(row['lcdm']).strip(),
                capacity=int(row['lcyn']) if pd.notna(row['lcyn']) else 0,
            )
            trains.append(train)

        Train.objects.bulk_create(trains, ignore_conflicts=True)
        logger.info(f"导入 {len(trains)} 个列车")

    def import_routes(self):
        """导入线路数据（从route_stations中提取）"""
        file_path = self.data_dir / 'route_stations.csv'
        logger.info(f"从线路站点数据提取线路信息: {file_path}")

        # 读取CSV，跳过中文说明行（第二行）
        df = pd.read_csv(file_path, skiprows=[1])

        # 提取唯一的线路编码
        route_codes = df['yyxlbm'].unique()

        routes = []
        for route_code in route_codes:
            # 从数据中查找线路代码
            route_data = df[df['yyxlbm'] == route_code].iloc[0]
            route = Route(
                id=int(route_code),
                code=int(route_data['xldm']) if pd.notna(route_data['xldm']) else int(route_code),
                name=f"线路 {route_code}"
            )
            routes.append(route)

        Route.objects.bulk_create(routes, ignore_conflicts=True)
        logger.info(f"导入 {len(routes)} 条线路")

    def import_route_stations(self):
        """导入线路站点数据"""
        file_path = self.data_dir / 'route_stations.csv'
        logger.info(f"导入线路站点数据: {file_path}")

        # 读取CSV，跳过中文说明行（第二行）
        df = pd.read_csv(file_path, skiprows=[1])

        route_stations = []
        for _, row in df.iterrows():
            try:
                route = Route.objects.get(id=int(row['yyxlbm']))
                station = Station.objects.get(id=int(row['zdid']))

                # 处理外键引用
                previous_station = None
                if pd.notna(row['Q_zdid']):
                    try:
                        previous_station = Station.objects.get(id=int(row['Q_zdid']))
                    except Station.DoesNotExist:
                        pass

                next_station = None
                if pd.notna(row['H_zdid']):
                    try:
                        next_station = Station.objects.get(id=int(row['H_zdid']))
                    except Station.DoesNotExist:
                        pass

                route_station = RouteStation(
                    route=route,
                    station=station,
                    sequence=int(row['xlzdid']) if pd.notna(row['xlzdid']) else 0,
                    previous_station=previous_station,
                    next_station=next_station,
                    distance_to_previous=int(row['yqzdjjl']) if pd.notna(row['yqzdjjl']) else 0,
                    total_distance=int(row['ysjl']) if pd.notna(row['ysjl']) else 0,
                    is_start=bool(int(row['sfqszd'])) if pd.notna(row['sfqszd']) else False,
                    is_end=bool(int(row['sfzdzd'])) if pd.notna(row['sfzdzd']) else False,
                    must_stop=bool(int(row['sfytk'])) if pd.notna(row['sfytk']) else True,
                )
                route_stations.append(route_station)
            except (Route.DoesNotExist, Station.DoesNotExist) as e:
                logger.warning(f"跳过无效的线路站点记录: {row}, 错误: {e}")
                continue

        RouteStation.objects.bulk_create(route_stations, ignore_conflicts=True)
        logger.info(f"导入 {len(route_stations)} 个线路站点记录")

    def import_passenger_flow(self, batch_size=1000):
        """导入客运记录数据"""
        file_path = self.data_dir / 'passenger_flow.csv'
        logger.info(f"导入客运记录数据: {file_path}")

        # 读取CSV，跳过中文说明行（第二行）
        df = pd.read_csv(file_path, skiprows=[1])
        has_start_col = 'start_station_telecode' in df.columns
        has_end_col = 'end_station_telecode' in df.columns

        station_map = {
            item['id']: item['telecode']
            for item in Station.objects.values('id', 'telecode')
        }
        od_map = self._build_od_telecode_map(df, station_map)

        total_records = len(df)
        logger.info(f"总记录数: {total_records}")

        passenger_flows = []
        for i, row in df.iterrows():
            try:
                # 解析日期和时间
                operation_date = self._parse_date(str(row['yxrq']))

                arrival_time = None
                if pd.notna(row['ddsj']):
                    arrival_time = self._parse_time(str(int(row['ddsj'])))

                departure_time = None
                if pd.notna(row['cfsj']):
                    departure_time = self._parse_time(str(int(row['cfsj'])))

                # 获取相关对象
                route = Route.objects.get(id=int(row['yyxlbm']))
                train = Train.objects.get(id=int(row['lcbm']))
                station = Station.objects.get(id=int(row['zdid']))

                start_tc = None
                end_tc = None
                if has_start_col and pd.notna(row['start_station_telecode']):
                    start_tc = str(row['start_station_telecode']).strip()
                if has_end_col and pd.notna(row['end_station_telecode']):
                    end_tc = str(row['end_station_telecode']).strip()
                if not start_tc or not end_tc:
                    od_key = (int(row['yyxlbm']), int(row['lcbm']), str(row['yxrq']))
                    fallback = od_map.get(od_key)
                    if fallback:
                        start_tc = start_tc or fallback[0]
                        end_tc = end_tc or fallback[1]

                passenger_flow = PassengerFlow(
                    serial_number=int(row['xh']) if pd.notna(row['xh']) else None,
                    route=route,
                    train=train,
                    station=station,
                    route_station_sequence=int(row['xlzdid']) if pd.notna(row['xlzdid']) else None,
                    operation_date=operation_date,
                    arrival_time=arrival_time,
                    departure_time=departure_time,
                    passengers_in=int(row['skl']) if pd.notna(row['skl']) else 0,
                    passengers_out=int(row['xkl']) if pd.notna(row['xkl']) else 0,
                    ticket_price=float(row['ticket_price']) if pd.notna(row['ticket_price']) else None,
                    start_station_telecode=start_tc,
                    end_station_telecode=end_tc,
                    revenue=float(row['shouru']) if pd.notna(row['shouru']) else None,
                )
                passenger_flows.append(passenger_flow)

                # 批量插入
                if len(passenger_flows) >= batch_size:
                    PassengerFlow.objects.bulk_create(passenger_flows, ignore_conflicts=True)
                    logger.info(f"已导入 {i+1}/{total_records} 条记录")
                    passenger_flows = []

            except (Route.DoesNotExist, Train.DoesNotExist, Station.DoesNotExist) as e:
                logger.warning(f"跳过无效的客运记录: {row}, 错误: {e}")
                continue
            except Exception as e:
                logger.warning(f"解析客运记录时出错: {row}, 错误: {e}")
                continue

        # 插入剩余记录
        if passenger_flows:
            PassengerFlow.objects.bulk_create(passenger_flows, ignore_conflicts=True)

        logger.info(f"客运记录导入完成，共导入 {len(df)} 条记录")

    def _build_od_telecode_map(self, df, station_map):
        if 'xlzdid' not in df.columns or 'zdid' not in df.columns:
            return {}
        df_valid = df[pd.notna(df['xlzdid']) & pd.notna(df['zdid'])].copy()
        if df_valid.empty:
            return {}
        df_valid['xlzdid'] = df_valid['xlzdid'].astype(int)
        start_idx = df_valid.groupby(['yyxlbm', 'lcbm', 'yxrq'])['xlzdid'].idxmin()
        end_idx = df_valid.groupby(['yyxlbm', 'lcbm', 'yxrq'])['xlzdid'].idxmax()

        od_map = {}
        for idx in start_idx:
            row = df_valid.loc[idx]
            key = (int(row['yyxlbm']), int(row['lcbm']), str(row['yxrq']))
            start_tc = station_map.get(int(row['zdid']))
            if not start_tc:
                continue
            od_map[key] = [start_tc, None]

        for idx in end_idx:
            row = df_valid.loc[idx]
            key = (int(row['yyxlbm']), int(row['lcbm']), str(row['yxrq']))
            end_tc = station_map.get(int(row['zdid']))
            if not end_tc:
                continue
            if key not in od_map:
                od_map[key] = [None, end_tc]
            else:
                od_map[key][1] = end_tc

        return {key: (value[0], value[1]) for key, value in od_map.items() if value[0] and value[1]}

    def _parse_date(self, date_str):
        """解析日期字符串 (YYYYMMDD)"""
        try:
            return datetime.strptime(str(date_str), '%Y%m%d').date()
        except ValueError:
            # 尝试其他格式
            try:
                return datetime.strptime(str(date_str), '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"无法解析日期: {date_str}")
                return datetime.now().date()

    def _parse_time(self, time_str):
        """解析时间字符串 (HHMM)"""
        try:
            time_str = str(time_str).zfill(4)  # 确保4位
            return time(int(time_str[:2]), int(time_str[2:]))
        except ValueError:
            logger.warning(f"无法解析时间: {time_str}")
            return None

    def clear_all_data(self):
        """清除所有数据"""
        logger.info("清除所有数据...")
        PassengerFlow.objects.all().delete()
        RouteStation.objects.all().delete()
        Route.objects.all().delete()
        Train.objects.all().delete()
        Station.objects.all().delete()
        logger.info("所有数据已清除")


def import_sample_data():
    """导入示例数据（用于测试）"""
    service = DataImportService()
    try:
        service.import_all_data()
        return True
    except Exception as e:
        logger.error(f"导入示例数据失败: {e}")
        return False
