# ocr/views.py

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .models import OCRJob
from .serializers import (
    OCRJobUploadSerializer,
    OCRJobStatusSerializer,
    OCRJobResultSerializer,
    OCRJobDetailSerializer
)
# from .tasks import process_ocr  # ✅ CORRECT IMPORT

from .tasks import process_ocr

logger = logging.getLogger('ocr')


@method_decorator(never_cache, name='dispatch')
class UploadImageView(APIView):
    """
    POST /api/ocr/upload/
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            serializer = OCRJobUploadSerializer(data=request.data)

            if not serializer.is_valid():
                error_msg = serializer.errors.get('image', serializer.errors)
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )

            job = serializer.save()
            logger.info(f"OCR job created: {job.id}")

            # ✅ Celery async call
            process_ocr.delay(str(job.id))

            return Response(
                {
                    'jobId': str(job.id),
                    'message': 'Image uploaded successfully'
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.exception("Upload failed")
            return Response(
                {'error': 'Upload failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(never_cache, name='dispatch')
class GetStatusView(APIView):
    """
    GET /api/ocr/status/<job_id>/
    """

    def get(self, request, job_id):
        try:
            job = OCRJob.objects.get(id=job_id)
            serializer = OCRJobStatusSerializer(job)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (ObjectDoesNotExist, ValueError):
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.exception("Status fetch failed")
            return Response(
                {'error': 'Failed to get status', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(never_cache, name='dispatch')
class GetResultView(APIView):
    """
    GET /api/ocr/result/<job_id>/
    """

    def get(self, request, job_id):
        try:
            job = OCRJob.objects.get(id=job_id)
            serializer = OCRJobResultSerializer(job)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (ObjectDoesNotExist, ValueError):
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.exception("Result fetch failed")
            return Response(
                {'error': 'Failed to get result', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JobDetailView(APIView):
    """
    GET /api/ocr/job/<job_id>/
    """

    def get(self, request, job_id):
        try:
            job = OCRJob.objects.get(id=job_id)
            serializer = OCRJobDetailSerializer(job, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (ObjectDoesNotExist, ValueError):
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.exception("Job detail fetch failed")
            return Response(
                {'error': 'Failed to get job details', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """
    GET /health
    """

    def get(self, request):
        return Response(
            {'status': 'OK', 'message': 'OCR Backend running'},
            status=status.HTTP_200_OK
        )
