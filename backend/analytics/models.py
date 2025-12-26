from django.db import models
from django.utils import timezone


class OptimizationPlan(models.Model):
    STATUS_CHOICES = [
        ('draft', '草案'),
        ('running', '测算中'),
        ('ready', '可用'),
        ('failed', '异常'),
    ]

    plan_id = models.CharField(max_length=64, primary_key=True)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='ready')
    expected_impact = models.CharField(max_length=200, blank=True)
    filters = models.JSONField(default=dict)
    goal = models.CharField(max_length=200, blank=True)
    constraints = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'optimization_plan'
        verbose_name = '优化方案'
        verbose_name_plural = '优化方案'

    def __str__(self):
        return f'{self.plan_id} {self.title}'


class OptimizationScenario(models.Model):
    STATUS_CHOICES = OptimizationPlan.STATUS_CHOICES

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='ready')
    owner = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'optimization_scenario'
        verbose_name = '优化场景'
        verbose_name_plural = '优化场景'

    def __str__(self):
        return self.name


class OptimizationInsight(models.Model):
    title = models.CharField(max_length=120)
    detail = models.CharField(max_length=255)
    tag = models.CharField(max_length=40)
    impact = models.CharField(max_length=80)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'optimization_insight'
        verbose_name = '优化洞察'
        verbose_name_plural = '优化洞察'

    def __str__(self):
        return self.title
