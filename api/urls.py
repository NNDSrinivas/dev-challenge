from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from jobs.views import JobCreateView, JobDetailView

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny]), name="swagger-ui"),

    path("jobs/", JobCreateView.as_view(), name="job-create"),
    path("jobs/<uuid:id>/", JobDetailView.as_view(), name="job-detail"),
]
