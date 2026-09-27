# requests_box/admin.py
from django.contrib import admin
from .models import SiteRequest

@admin.register(SiteRequest)
class SiteRequestAdmin(admin.ModelAdmin):
    list_display = ("created_at", "kind", "email", "username", "status")
    list_filter = ("kind", "status")
    search_fields = ("email", "username", "message")
    readonly_fields = ("created_at",)