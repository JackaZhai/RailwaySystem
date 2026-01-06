from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='passengerflow',
            index=models.Index(fields=['train', 'operation_date'], name='pf_train_date_idx'),
        ),
        migrations.AddIndex(
            model_name='passengerflow',
            index=models.Index(fields=['start_station_telecode', 'operation_date'], name='pf_start_tc_date_idx'),
        ),
        migrations.AddIndex(
            model_name='passengerflow',
            index=models.Index(fields=['end_station_telecode', 'operation_date'], name='pf_end_tc_date_idx'),
        ),
    ]
