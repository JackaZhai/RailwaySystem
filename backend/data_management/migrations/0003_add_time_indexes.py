from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0002_add_passengerflow_indexes'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='passengerflow',
            index=models.Index(fields=['operation_date', 'arrival_time'], name='pf_op_arrival_idx'),
        ),
        migrations.AddIndex(
            model_name='passengerflow',
            index=models.Index(fields=['operation_date', 'departure_time'], name='pf_op_departure_idx'),
        ),
    ]
