# ocr/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import OCRJob


@admin.register(OCRJob)
class OCRJobAdmin(admin.ModelAdmin):
    """
    Admin interface for OCR Jobs
    """
    list_display = [
        'id',
        'status_badge',
        'file_name',
        'file_size_display',
        'created_at',
        'processing_time_display',
        'view_image_link'
    ]
    
    list_filter = [
        'status',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'id',
        'file_name',
        'extracted_text'
    ]
    
    readonly_fields = [
        'id',
        'status',
        'created_at',
        'updated_at',
        'completed_at',
        'file_size',
        'file_name',
        'processing_time',
        'image_preview'
    ]
    
    fieldsets = (
        ('Job Information', {
            'fields': (
                'id',
                'status',
                'file_name',
                'file_size'
            )
        }),
        ('Image', {
            'fields': (
                'image',
                'image_preview'
            )
        }),
        ('Results', {
            'fields': (
                'extracted_text',
                'error_message'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
                'processing_time'
            )
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'pending': '#808080',
            'processing': '#007bff',
            'done': '#28a745',
            'rejected': '#dc3545'
        }
        color = colors.get(obj.status, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        if not obj.file_size:
            return '-'
        
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    file_size_display.short_description = 'File Size'
    
    def processing_time_display(self, obj):
        """Display processing time in human-readable format"""
        if not obj.processing_time:
            return '-'
        return f"{obj.processing_time:.2f}s"
    processing_time_display.short_description = 'Processing Time'
    
    def view_image_link(self, obj):
        """Link to view the image"""
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank">View Image</a>',
                obj.image.url
            )
        return '-'
    view_image_link.short_description = 'Image'
    
    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" '
                f'style="max-width: 300px; max-height: 300px;" />'
            )
        return '-'
    image_preview.short_description = 'Preview'
    
    def has_add_permission(self, request):
        """Disable manual job creation"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make jobs read-only"""
        return False
    
    actions = ['delete_selected']
    
    def get_actions(self, request):
        """Keep only delete action"""
        actions = super().get_actions(request)
        return {'delete_selected': actions['delete_selected']}