from django.urls import path
from .views import (
    UploadImageView,
    GetStatusView,
    GetResultView,
    JobDetailView,
)

app_name = 'ocr'

urlpatterns = [
    path('ocr/upload/', UploadImageView.as_view(), name='upload'),
    path('ocr/status/<uuid:job_id>/', GetStatusView.as_view(), name='status'),
    path('ocr/result/<uuid:job_id>/', GetResultView.as_view(), name='result'),
    path('ocr/job/<uuid:job_id>/', JobDetailView.as_view(), name='job-detail'),
]
