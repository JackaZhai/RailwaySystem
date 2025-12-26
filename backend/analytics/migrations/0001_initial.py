from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='OptimizationPlan',
            fields=[
                ('plan_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('draft', '草案'), ('running', '测算中'), ('ready', '可用'), ('failed', '异常')], default='ready', max_length=16)),
                ('expected_impact', models.CharField(blank=True, max_length=200)),
                ('filters', models.JSONField(default=dict)),
                ('goal', models.CharField(blank=True, max_length=200)),
                ('constraints', models.JSONField(default=list)),
                ('notes', models.TextField(blank=True)),
                ('recommendations', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '优化方案',
                'verbose_name_plural': '优化方案',
                'db_table': 'optimization_plan',
            },
        ),
        migrations.CreateModel(
            name='OptimizationScenario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('draft', '草案'), ('running', '测算中'), ('ready', '可用'), ('failed', '异常')], default='ready', max_length=16)),
                ('owner', models.CharField(blank=True, max_length=100)),
                ('tags', models.JSONField(default=list)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': '优化场景',
                'verbose_name_plural': '优化场景',
                'db_table': 'optimization_scenario',
            },
        ),
        migrations.CreateModel(
            name='OptimizationInsight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('detail', models.CharField(max_length=255)),
                ('tag', models.CharField(max_length=40)),
                ('impact', models.CharField(max_length=80)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': '优化洞察',
                'verbose_name_plural': '优化洞察',
                'db_table': 'optimization_insight',
            },
        ),
    ]
