from rest_framework import generics, status
from rest_framework.response import Response
from .models import Job
from .serializers import JobSerializer
from .tasks import process_job

class JobCreateView(generics.CreateAPIView):
    """
    POST /jobs/
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save()
        try:
            process_job.delay(str(job.id))
        except Exception:
            job.status = Job.Status.FAILED
            job.save(update_fields=["status"])
            raise
        return Response({"event_id": job.id}, status=status.HTTP_201_CREATED)

class JobDetailView(generics.RetrieveAPIView):
    """
    GET /jobs/{id}/
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = "id"
    lookup_url_kwarg = "id"
