from celery import shared_task
from openai import OpenAI, OpenAIError
from django.conf import settings
from .models import Job

@shared_task(bind=True, name="jobs.process_job")
def process_job(self, job_id):
    job = Job.objects.get(pk=job_id)
    job.status = Job.Status.RUNNING
    job.save(update_fields=["status"])

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        # 1) Summarize
        summary_resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Summarize the text."},
                {"role": "user", "content": job.input_text},
            ],
            max_tokens=150,
        )
        job.summary = summary_resp.choices[0].message.content
        job.save(update_fields=["summary"])

        # 2) Checklist
        checklist_resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Produce a bullet‐list checklist."},
                {"role": "user", "content": job.summary},
            ],
            max_tokens=300,
        )
        job.checklist = checklist_resp.choices[0].message.content
        job.save(update_fields=["checklist"])

    except OpenAIError as e:
        # Mark failed on API errors, no retries
        job.status = Job.Status.FAILED
        job.save(update_fields=["status"])
        return

    except Exception as e:
        # For unexpected errors, retry up to 3 times
        try:
            raise self.retry(exc=e, countdown=2, max_retries=3)
        except self.MaxRetriesExceededError:
            job.status = Job.Status.FAILED
            job.save(update_fields=["status"])
        return

    # Success
    job.status = Job.Status.SUCCEEDED
    job.save(update_fields=["status"])
