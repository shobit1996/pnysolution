from django.contrib import admin
from django.utils.html import format_html
from .models import Job, JobApplication, ClientInquiry


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'location', 'job_type', 'salary', 'is_active', 'created_at')
    list_filter = ('department', 'job_type', 'is_active')
    list_editable = ('is_active',)  # Allows rapid toggling of jobs directly from list view
    search_fields = ('title', 'tags', 'location')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'department', 'location', 'job_type', 'salary')
        }),
        ('Keywords & Details', {
            'fields': ('tags', 'description', 'is_active')
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'job', 'experience_years', 'submitted_at', 'resume_download_link')
    list_filter = ('job', 'submitted_at')
    search_fields = ('full_name', 'email', 'phone', 'cover_note')
    readonly_fields = ('job', 'full_name', 'email', 'phone', 'experience_years', 'portfolio_link', 'resume_file', 'cover_note', 'submitted_at')

    def resume_download_link(self, obj):
        if obj.resume_file:
            return format_html(
                '<a href="{url}" target="_blank" style="'
                'display: inline-block; padding: 5px 12px; background: #0284c7; '
                'color: #ffffff; text-decoration: none; border-radius: var(--radius-sm, 4px); '
                'font-weight: 600; font-size: 11px; transition: background 0.2s;">'
                '📄 Download CV</a>',
                url=obj.resume_file.url
            )
        return "No resume uploaded"
        
    resume_download_link.short_description = "Candidate Resume"
    resume_download_link.admin_order_field = 'resume_file'

    # Disable add/change/delete permissions in admin to preserve original records
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ClientInquiry)
class ClientInquiryAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_email', 'client_phone', 'client_company', 'inquiry_subject', 'submitted_at')
    list_filter = ('inquiry_subject', 'submitted_at')
    search_fields = ('client_name', 'client_email', 'client_phone', 'client_company', 'inquiry_message')
    readonly_fields = ('client_name', 'client_email', 'client_phone', 'client_company', 'inquiry_subject', 'inquiry_message', 'submitted_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

