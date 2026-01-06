from django.core.management.base import BaseCommand
from django.db.models import Case, When, IntegerField

from data_management.models import PassengerFlow, RouteStation


class Command(BaseCommand):
    help = 'Backfill PassengerFlow.route_station_sequence using RouteStation.sequence.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=2000,
            help='Rows per update batch.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only count rows to update, do not modify data.'
        )

    def handle(self, *args, **options):
        batch_size = max(100, options['batch_size'])
        dry_run = options['dry_run']

        self.stdout.write('Building route-station sequence map...')
        route_station_map = {
            (rs['route_id'], rs['station_id']): rs['sequence']
            for rs in RouteStation.objects.values('route_id', 'station_id', 'sequence')
        }
        self.stdout.write(f'RouteStation entries: {len(route_station_map)}')

        qs = PassengerFlow.objects.filter(route_station_sequence__isnull=True).values(
            'id', 'route_id', 'station_id'
        )
        total = qs.count()
        self.stdout.write(f'PassengerFlow missing route_station_sequence: {total}')
        if total == 0:
            return
        if dry_run:
            self.stdout.write('Dry run enabled. Exiting without updates.')
            return

        updated = 0
        skipped = 0
        batch = []

        def flush_batch(items):
            nonlocal updated, skipped
            if not items:
                return
            whens = []
            ids = []
            for row_id, seq in items:
                if seq is None:
                    skipped += 1
                    continue
                whens.append(When(id=row_id, then=seq))
                ids.append(row_id)
            if not whens:
                return
            PassengerFlow.objects.filter(id__in=ids).update(
                route_station_sequence=Case(*whens, output_field=IntegerField())
            )
            updated += len(ids)

        for row in qs.iterator(chunk_size=5000):
            seq = route_station_map.get((row['route_id'], row['station_id']))
            batch.append((row['id'], seq))
            if len(batch) >= batch_size:
                flush_batch(batch)
                batch = []

        flush_batch(batch)

        self.stdout.write(f'Updated: {updated}, skipped (no sequence): {skipped}')
