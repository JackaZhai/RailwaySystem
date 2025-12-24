from django.core.management.base import BaseCommand
from data_management.services import DataImportService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '导入铁路客运数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据后再导入',
        )
        parser.add_argument(
            '--skip-stations',
            action='store_true',
            help='跳过站点导入',
        )
        parser.add_argument(
            '--skip-trains',
            action='store_true',
            help='跳过列车导入',
        )
        parser.add_argument(
            '--skip-routes',
            action='store_true',
            help='跳路线路导入',
        )
        parser.add_argument(
            '--skip-route-stations',
            action='store_true',
            help='跳路线路站点导入',
        )
        parser.add_argument(
            '--skip-passenger-flow',
            action='store_true',
            help='跳过客运记录导入',
        )

    def handle(self, *args, **options):
        service = DataImportService()

        if options['clear']:
            self.stdout.write(self.style.WARNING('清除现有数据...'))
            service.clear_all_data()
            self.stdout.write(self.style.SUCCESS('数据清除完成'))

        try:
            if not options['skip_stations']:
                self.stdout.write('导入站点数据...')
                service.import_stations()
                self.stdout.write(self.style.SUCCESS('站点数据导入完成'))

            if not options['skip_trains']:
                self.stdout.write('导入列车数据...')
                service.import_trains()
                self.stdout.write(self.style.SUCCESS('列车数据导入完成'))

            if not options['skip_routes']:
                self.stdout.write('导入线路数据...')
                service.import_routes()
                self.stdout.write(self.style.SUCCESS('线路数据导入完成'))

            if not options['skip_route_stations']:
                self.stdout.write('导入线路站点数据...')
                service.import_route_stations()
                self.stdout.write(self.style.SUCCESS('线路站点数据导入完成'))

            if not options['skip_passenger_flow']:
                self.stdout.write('导入客运记录数据（这可能需要一些时间）...')
                service.import_passenger_flow()
                self.stdout.write(self.style.SUCCESS('客运记录数据导入完成'))

            self.stdout.write(self.style.SUCCESS('所有数据导入完成！'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'数据导入失败: {e}'))
            logger.exception('数据导入失败')