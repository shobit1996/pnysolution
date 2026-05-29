from django.db import models


class Job(models.Model):
    DEPARTMENT_CHOICES = [
        ('Engineering', 'Engineering'),
        ('Product Management', 'Product Management'),
        ('Training Services', 'Training Services'),
    ]

    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ]

    title = models.CharField(max_length=200, help_text="e.g. Senior Frontend Engineer (React/Vue)")
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='Engineering')
    location = models.CharField(max_length=150, help_text="e.g. Remote / Noida, Noida Office, Hybrid")
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='Full-time')
    salary = models.CharField(max_length=100, help_text="e.g. $80,000 - $110,000 or $60 - $80 / hr")
    tags = models.CharField(
        max_length=255, 
        help_text="Comma-separated list of keywords, e.g. 'React, TypeScript, CSS, SEO'",
        blank=True
    )
    description = models.TextField(help_text="Detailed responsibilities, expectations, and benefits.", blank=True)
    is_active = models.BooleanField(default=True, help_text="Toggle this off to hide the job listing from the Careers page.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.department})"

    @property
    def tags_list(self):
        """Returns the tags as an array of stripped strings for the frontend API"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications', help_text="The role applied for")
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    experience_years = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        help_text="Total years of work experience, e.g., 3.5"
    )
    portfolio_link = models.URLField(blank=True, null=True, help_text="Link to candidate portfolio, GitHub, or LinkedIn")
    resume_file = models.FileField(upload_to='resumes/%Y/%m/', help_text="Uploaded CV/Resume file (PDF, DOC, DOCX)")
    cover_note = models.TextField(blank=True, null=True, help_text="Optional message or cover note from candidate")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Application by {self.full_name} for {self.job.title}"


class ClientInquiry(models.Model):
    client_name = models.CharField(max_length=150)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    client_company = models.CharField(max_length=150, blank=True, null=True)
    inquiry_subject = models.CharField(max_length=200)
    inquiry_message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Client Inquiry"
        verbose_name_plural = "Client Inquiries"

    def __str__(self):
        return f"Inquiry by {self.client_name} - {self.inquiry_subject}"

