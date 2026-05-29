from rest_framework import serializers
from .models import Job, JobApplication, ClientInquiry


class JobSerializer(serializers.ModelSerializer):
    # Aliased fields to match the exact keys used in React frontend pages
    dept = serializers.CharField(source='department')
    loc = serializers.CharField(source='location')
    type = serializers.CharField(source='job_type')
    sal = serializers.CharField(source='salary')
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'dept', 'loc', 'type', 'sal', 'tags', 'description']

    def get_tags(self, obj):
        return obj.tags_list


class JobApplicationSerializer(serializers.ModelSerializer):
    # Aliased fields to map incoming React form data directly into Django db fields
    name = serializers.CharField(source='full_name')
    experience = serializers.DecimalField(source='experience_years', max_digits=4, decimal_places=1)
    portfolio = serializers.URLField(source='portfolio_link', required=False, allow_blank=True, allow_null=True)
    message = serializers.CharField(source='cover_note', required=False, allow_blank=True, allow_null=True)
    resume = serializers.FileField(source='resume_file')

    class Meta:
        model = JobApplication
        fields = ['job', 'name', 'email', 'phone', 'experience', 'portfolio', 'resume', 'message']


class ClientInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientInquiry
        fields = ['id', 'client_name', 'client_email', 'client_phone', 'client_company', 'inquiry_subject', 'inquiry_message', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']

