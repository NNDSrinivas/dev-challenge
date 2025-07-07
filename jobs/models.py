import uuid
from django.db import models

class Job(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    input_text = models.TextField(help_text="Original guideline text")
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current processing status",
    )
    summary = models.TextField(null=True, blank=True, help_text="GPT-generated summary")
    checklist = models.TextField(null=True, blank=True, help_text="GPT-generated checklist")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} – {self.status}"
