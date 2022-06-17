from django.contrib import admin
from app import models


# Register your models here.
admin.site.register(models.Division)
admin.site.register(models.Material)
admin.site.register(models.HolidaysCalendar)
admin.site.register(models.Product)
admin.site.register(models.WorkData)
admin.site.register(models.CalendarConfigurationTreatement)
admin.site.register(models.CalendarConfigurationCpordo)
admin.site.register(models.Coois)
admin.site.register(models.Zpp)
admin.site.register(models.Shopfloor)