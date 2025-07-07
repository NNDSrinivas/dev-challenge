from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "id",
        "input_text",
        "summary",
        "checklist",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
