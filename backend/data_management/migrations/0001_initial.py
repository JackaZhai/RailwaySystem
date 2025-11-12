"""Initial schema for passenger records."""
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PassengerRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField()),
                ("station", models.CharField(max_length=255)),
                ("line", models.CharField(max_length=255)),
                ("direction", models.CharField(blank=True, max_length=50)),
                ("passengers_in", models.PositiveIntegerField(default=0)),
                ("passengers_out", models.PositiveIntegerField(default=0)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["timestamp", "station", "line"],
                "unique_together": {("timestamp", "station", "line", "direction")},
            },
        ),
    ]
