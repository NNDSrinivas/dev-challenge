# jobs/tests.py

from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from openai import OpenAIError

from .models import Job
from .serializers import JobSerializer
from .tasks import process_job


class JobModelTest(TestCase):
    def test_create_job_defaults(self):
        job = Job.objects.create(input_text="Test")
        self.assertEqual(job.status, Job.Status.PENDING)
        self.assertIsNone(job.summary)
        self.assertIsNone(job.checklist)


class JobSerializerTest(TestCase):
    def test_serializer_valid_data(self):
        data = {"input_text": "Test input"}
        serializer = JobSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        job = serializer.save()
        self.assertEqual(job.input_text, data["input_text"])

    def test_serializer_missing_input_text(self):
        serializer = JobSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("input_text", serializer.errors)


class JobAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("jobs.views.process_job.delay")
    def test_create_job_endpoint(self, mock_delay):
        data = {"input_text": "Test input"}
        resp = self.client.post(reverse("job-create"), data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("event_id", resp.data)

        job_id = resp.data["event_id"]
        mock_delay.assert_called_once_with(str(job_id))

        job = Job.objects.get(id=job_id)
        self.assertEqual(job.input_text, data["input_text"])
        self.assertEqual(job.status, Job.Status.PENDING)

    def test_get_job_endpoint(self):
        job = Job.objects.create(input_text="Another test")
        url = reverse("job-detail", kwargs={"id": job.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        serializer = JobSerializer(job)
        self.assertEqual(resp.data, serializer.data)


class ProcessJobTaskTest(TestCase):
    @patch("jobs.tasks.OpenAI")
    def test_successful_process_job(self, mock_openai_cls):
        # Arrange: create a pending job
        job = Job.objects.create(input_text="Some guideline text")

        # Fake OpenAI client and responses
        mock_client = mock_openai_cls.return_value
        summary_resp = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="a nice summary"))]
        )
        checklist_resp = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="- item1\n- item2"))]
        )
        # First call → summary_resp, second → checklist_resp
        mock_client.chat.completions.create.side_effect = [summary_resp, checklist_resp]

        # Act: run the task synchronously
        process_job.run(str(job.id))

        # Assert: job is marked succeeded with fields populated
        job.refresh_from_db()
        self.assertEqual(job.status, Job.Status.SUCCEEDED)
        self.assertEqual(job.summary, "a nice summary")
        self.assertEqual(job.checklist, "- item1\n- item2")

    @patch("jobs.tasks.OpenAI")
    def test_openai_error_marks_failed(self, mock_openai_cls):
        # Arrange: create a pending job
        job = Job.objects.create(input_text="Some guideline text")

        # Fake client that raises OpenAIError on first call
        mock_client = mock_openai_cls.return_value
        mock_client.chat.completions.create.side_effect = OpenAIError("API down")

        # Act: run the task synchronously
        process_job.run(str(job.id))

        # Assert: job is marked failed, no summary/checklist
        job.refresh_from_db()
        self.assertEqual(job.status, Job.Status.FAILED)
        self.assertIsNone(job.summary)
        self.assertIsNone(job.checklist)
