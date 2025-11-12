from django.contrib import admin

from .models import PassengerRecord


@admin.register(PassengerRecord)
class PassengerRecordAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "station", "line", "passengers_in", "passengers_out")
    search_fields = ("station", "line")
    list_filter = ("line", "station")
