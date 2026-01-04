# ocr/management/commands/test_ocr.py

from django.core.management.base import BaseCommand
from ocr.services.ocr_service import OCRService, TextCleaner


class Command(BaseCommand):
    help = 'Test OCR service with an image file'

    def add_arguments(self, parser):
        parser.add_argument(
            'image_path',
            type=str,
            help='Path to the image file to process'
        )
        parser.add_argument(
            '--no-clean',
            action='store_true',
            help='Skip text cleaning'
        )

    def handle(self, *args, **options):
        image_path = options['image_path']
        no_clean = options['no_clean']
        
        self.stdout.write(
            self.style.SUCCESS(f'Processing image: {image_path}')
        )
        
        try:
            service = OCRService()
            
            # Validate image first
            service.validate_image(image_path)
            self.stdout.write(
                self.style.SUCCESS('✓ Image validation passed')
            )
            
            # Process OCR
            extracted_text = service.process_image(image_path)
            
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('EXTRACTED TEXT:'))
            self.stdout.write('='*50 + '\n')
            self.stdout.write(extracted_text)
            self.stdout.write('\n' + '='*50 + '\n')
            
            if not no_clean:
                cleaned_text = TextCleaner.clean(extracted_text)
                self.stdout.write('\n' + '='*50)
                self.stdout.write(self.style.SUCCESS('CLEANED TEXT:'))
                self.stdout.write('='*50 + '\n')
                self.stdout.write(cleaned_text)
                self.stdout.write('\n' + '='*50 + '\n')
            
            self.stdout.write(
                self.style.SUCCESS('✓ OCR processing completed successfully')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error: {str(e)}')
            )