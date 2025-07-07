from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        # fields exposed in API
        fields = [
            "id",
            "input_text",
            "status",
            "summary",
            "checklist",
            "created_at",
            "updated_at",
        ]
        # only input_text is writable by clients
        read_only_fields = [
            "id",
            "status",
            "summary",
            "checklist",
            "created_at",
            "updated_at",
        ]
