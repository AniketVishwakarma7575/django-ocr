# ocr/serializers.py

from rest_framework import serializers
from django.conf import settings
from .models import OCRJob


class OCRJobUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading images and creating OCR jobs
    """
    image = serializers.ImageField(
        required=True,
        allow_empty_file=False,
        error_messages={
            'required': 'No image file provided',
            'empty': 'The submitted file is empty',
            'invalid': 'Invalid image file'
        }
    )
    
    class Meta:
        model = OCRJob
        fields = ['image']
    
    def validate_image(self, value):
        """
        Validate image file
        """
        # Check file size
        if value.size > settings.OCR_MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed size of "
                f"{settings.OCR_MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Check file extension
        ext = value.name.split('.')[-1].lower()
        if ext not in settings.OCR_ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"File extension '{ext}' is not allowed. "
                f"Allowed extensions: {', '.join(settings.OCR_ALLOWED_EXTENSIONS)}"
            )
        
        return value
    
    def create(self, validated_data):
        """
        Create OCR job with additional metadata
        """
        image = validated_data['image']
        
        ocr_job = OCRJob.objects.create(
            image=image,
            file_size=image.size,
            file_name=image.name,
            status='pending'
        )
        
        return ocr_job


class OCRJobStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for OCR job status response
    """
    class Meta:
        model = OCRJob
        fields = ['status', 'error_message']
    
    def to_representation(self, instance):
        """
        Custom representation based on status
        """
        data = {'status': instance.status}
        
        if instance.status == 'rejected' and instance.error_message:
            data['error'] = instance.error_message
        
        return data


class OCRJobResultSerializer(serializers.ModelSerializer):
    """
    Serializer for OCR job result response
    """
    jobId = serializers.UUIDField(source='id', read_only=True)
    text = serializers.CharField(source='extracted_text', read_only=True)
    
    class Meta:
        model = OCRJob
        fields = ['jobId', 'text']
    
    def to_representation(self, instance):
        """
        Custom representation based on completion status
        """
        if instance.status != 'done':
            return {'message': 'OCR not completed yet'}
        
        return super().to_representation(instance)


class OCRJobDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for OCR job (for admin/debugging)
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = OCRJob
        fields = [
            'id', 'status', 'extracted_text', 'error_message',
            'file_name', 'file_size', 'image_url',
            'created_at', 'updated_at', 'completed_at',
            'processing_time'
        ]
        read_only_fields = fields
    
    def get_image_url(self, obj):
        """Get absolute URL for image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None