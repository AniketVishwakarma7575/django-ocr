# ocr/models.py

import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings


class OCRJob(models.Model):
    """
    Model to store OCR job information and status
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    image = models.ImageField(
        upload_to=settings.OCR_UPLOAD_PATH,
        validators=[
            FileExtensionValidator(
                allowed_extensions=settings.OCR_ALLOWED_EXTENSIONS
            )
        ],
        max_length=500
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    extracted_text = models.TextField(
        blank=True,
        null=True
    )
    
    error_message = models.TextField(
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    # Additional metadata
    file_size = models.PositiveIntegerField(
        help_text="File size in bytes",
        blank=True,
        null=True
    )
    
    file_name = models.CharField(
        max_length=255,
        blank=True
    )
    
    processing_time = models.FloatField(
        help_text="Processing time in seconds",
        blank=True,
        null=True
    )
    
    class Meta:
        db_table = 'ocr_jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
        verbose_name = 'OCR Job'
        verbose_name_plural = 'OCR Jobs'
    
    def __str__(self):
        return f"OCR Job {self.id} - {self.status}"
    
    def mark_as_processing(self):
        """Mark job as processing"""
        self.status = 'processing'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_done(self, extracted_text, processing_time=None):
        """Mark job as completed with extracted text"""
        self.status = 'done'
        self.extracted_text = extracted_text
        self.completed_at = timezone.now()
        if processing_time:
            self.processing_time = processing_time
        self.save(update_fields=[
            'status', 'extracted_text', 'completed_at', 
            'processing_time', 'updated_at'
        ])
    
    def mark_as_rejected(self, error_message):
        """Mark job as rejected with error message"""
        self.status = 'rejected'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=[
            'status', 'error_message', 'completed_at', 'updated_at'
        ])
    
    @property
    def is_completed(self):
        """Check if job is in a terminal state"""
        return self.status in ['done', 'rejected']
    
    @property
    def image_url(self):
        """Get full URL for the image"""
        if self.image:
            return self.image.url
        return None
    
    def clean_image_path(self):
        """Delete the associated image file"""
        if self.image:
            try:
                if self.image.storage.exists(self.image.name):
                    self.image.storage.delete(self.image.name)
            except Exception as e:
                # Log error but don't raise
                import logging
                logger = logging.getLogger('ocr')
                logger.error(f"Error deleting image for job {self.id}: {str(e)}")
    
    def delete(self, *args, **kwargs):
        """Override delete to clean up image file"""
        self.clean_image_path()
        super().delete(*args, **kwargs)