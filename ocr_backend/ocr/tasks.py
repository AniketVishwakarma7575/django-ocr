# ocr/tasks.py

from celery import shared_task
from django.utils import timezone
import time
import logging
from .models import OCRJob
from .services.ocr_service import extract_text

logger = logging.getLogger('ocr')


@shared_task(bind=True)
def process_ocr(self, job_id):
    """
    Process OCR for the given job
    """
    try:
        job = OCRJob.objects.get(id=job_id)
        logger.info(f"Starting OCR processing for job: {job_id}")
        
        # Mark as processing
        job.status = "processing"
        job.save(update_fields=['status', 'updated_at'])
        
        # Track processing time
        start_time = time.time()
        
        # Extract text using OCR
        extracted_text = extract_text(job.image.path)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Mark as completed with results
        job.status = "done"
        job.extracted_text = extracted_text  # ✅ Correct field name
        job.completed_at = timezone.now()
        job.processing_time = processing_time
        job.save(update_fields=[
            'status', 
            'extracted_text', 
            'completed_at', 
            'processing_time',
            'updated_at'
        ])
        
        logger.info(f"OCR completed for job {job_id} in {processing_time:.2f}s")
        return {
            'job_id': str(job_id),
            'status': 'done',
            'text_length': len(extracted_text)
        }
        
    except OCRJob.DoesNotExist:
        logger.error(f"Job {job_id} not found")
        raise
        
    except Exception as e:
        logger.exception(f"OCR processing failed for job {job_id}")
        try:
            job = OCRJob.objects.get(id=job_id)
            job.status = "rejected"
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save(update_fields=[
                'status', 
                'error_message', 
                'completed_at',
                'updated_at'
            ])
        except Exception as save_error:
            logger.error(f"Failed to update job status: {save_error}")
        
        raise