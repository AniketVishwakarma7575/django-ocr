# ocr/tasks.py

from celery import shared_task
from .models import OCRJob
from .services.ocr_service import extract_text


@shared_task(bind=True)
def process_ocr_task(self, job_id):
    job = OCRJob.objects.get(id=job_id)

    try:
        job.status = "processing"
        job.save()

        text = extract_text(job.image.path)

        job.status = "completed"
        job.result_text = text
        job.save()

    except Exception as e:
        job.status = "rejected"
        job.error_message = str(e)
        job.save()
