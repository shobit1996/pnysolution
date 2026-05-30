from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from .models import Job, JobApplication, ClientInquiry
from .serializers import JobSerializer, JobApplicationSerializer, ClientInquirySerializer


class JobListAPIView(generics.ListAPIView):
    """
    API endpoint that lists all active jobs.
    Accessed via: GET /api/jobs/
    """
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobSerializer
    permission_classes = []  # Public endpoint


class JobApplicationCreateAPIView(generics.CreateAPIView):
    """
    API endpoint that accepts candidates applying for a role.
    Supports file uploads (resumes).
    Dispatches an SMTP email alert to shobitsharma26@gmail.com on every new submission.
    Accessed via: POST /api/applications/
    """
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = []  # Public submission endpoint

    def perform_create(self, serializer):
        # Save the application into the database
        instance = serializer.save()

        # Gather all applicant details
        candidate_name = instance.full_name
        candidate_email = instance.email
        candidate_phone = instance.phone
        experience_years = instance.experience_years
        portfolio_link = instance.portfolio_link or "Not Provided"
        cover_note = instance.cover_note or "Not Provided"
        job_title = instance.job.title
        job_department = instance.job.department
        job_location = instance.job.location

        # Email subject line
        subject = f"[PNY Talent Application] New Applicant: {candidate_name} for {job_title}"

        # Plain text fallback body
        message_body = (
            f"Hello Shobhit,\n\n"
            f"A new candidate has applied for a role on the PNY Talent Solutions website.\n\n"
            f"Application Details:\n"
            f"-----------------------------------------\n"
            f"👤 Candidate Name:    {candidate_name}\n"
            f"✉️  Email Address:     {candidate_email}\n"
            f"📞 Contact Phone:     {candidate_phone}\n"
            f"🏢 Years Experience:  {experience_years} years\n"
            f"🔗 Portfolio / Link:  {portfolio_link}\n"
            f"-----------------------------------------\n"
            f"💼 Role Applied For:  {job_title}\n"
            f"📂 Department:        {job_department}\n"
            f"📍 Location:          {job_location}\n"
            f"-----------------------------------------\n\n"
            f"💬 Cover Note:\n"
            f"{cover_note}\n\n"
            f"Best regards,\n"
            f"PNY Talent Automated Email Dispatcher"
        )

        # Rich HTML email body
        html_message = (
            f"<div style='font-family: Arial, sans-serif; max-width: 620px; border: 1px solid #edf2f7; padding: 28px; border-radius: 10px; background-color: #f7fafc;'>"
            f"  <h2 style='color: #162646; margin-top: 0; border-bottom: 2px solid #00cccc; padding-bottom: 10px;'>📋 New Job Application Received</h2>"
            f"  <p style='color: #4a5568; font-size: 15px;'>Hello Shobhit,</p>"
            f"  <p style='color: #4a5568; font-size: 14px;'>A candidate has submitted an application for the <strong style='color: #162646;'>{job_title}</strong> role on the PNY Talent Solutions website. Their full details are below:</p>"
            f"  <div style='background: #eef6ff; border-left: 4px solid #162646; border-radius: 4px; padding: 10px 16px; margin: 16px 0; font-size: 13px; color: #162646;'>"
            f"    <strong>Role:</strong> {job_title} &nbsp;|&nbsp; <strong>Dept:</strong> {job_department} &nbsp;|&nbsp; <strong>Location:</strong> {job_location}"
            f"  </div>"
            f"  <div style='background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px 20px; margin: 20px 0;'>"
            f"    <table style='width: 100%; border-collapse: collapse; font-size: 14px; color: #4a5568;'>"
            f"      <tr style='border-bottom: 1px solid #edf2f7;'>"
            f"        <td style='padding: 9px 0; font-weight: bold; width: 38%; color: #2d3748;'>Candidate Name:</td>"
            f"        <td style='padding: 9px 0;'>{candidate_name}</td>"
            f"      </tr>"
            f"      <tr style='border-bottom: 1px solid #edf2f7;'>"
            f"        <td style='padding: 9px 0; font-weight: bold; color: #2d3748;'>Email Address:</td>"
            f"        <td style='padding: 9px 0;'><a href='mailto:{candidate_email}' style='color: #00cccc;'>{candidate_email}</a></td>"
            f"      </tr>"
            f"      <tr style='border-bottom: 1px solid #edf2f7;'>"
            f"        <td style='padding: 9px 0; font-weight: bold; color: #2d3748;'>Contact Number:</td>"
            f"        <td style='padding: 9px 0;'>{candidate_phone}</td>"
            f"      </tr>"
            f"      <tr style='border-bottom: 1px solid #edf2f7;'>"
            f"        <td style='padding: 9px 0; font-weight: bold; color: #2d3748;'>Total Experience:</td>"
            f"        <td style='padding: 9px 0;'><strong style='color: #162646;'>{experience_years} years</strong></td>"
            f"      </tr>"
            f"      <tr>"
            f"        <td style='padding: 9px 0; font-weight: bold; color: #2d3748;'>Portfolio / LinkedIn:</td>"
            f"        <td style='padding: 9px 0;'>"
            f"          {'<a href=\"' + portfolio_link + '\" target=\"_blank\" style=\"color: #00cccc;\">' + portfolio_link + '</a>' if portfolio_link != 'Not Provided' else '<em style=\"color: #a0aec0;\">Not Provided</em>'}"
            f"        </td>"
            f"      </tr>"
            f"    </table>"
            f"  </div>"
            f"  <h3 style='color: #2d3748; font-size: 14px; margin-bottom: 8px;'>💬 Cover Note / Additional Details:</h3>"
            f"  <div style='background: #edf2f7; padding: 15px; border-radius: 6px; font-size: 13.5px; line-height: 1.6; color: #2d3748; white-space: pre-wrap; font-style: italic;'>"
            f"    {cover_note}"
            f"  </div>"
            f"  <div style='background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-top: 20px; font-size: 13px; color: #856404;'>"
            f"    📎 <strong>Resume/CV:</strong> The uploaded resume file is stored in the Django admin panel. Log in to <a href='http://localhost:8000/admin/' style='color: #162646;'>http://localhost:8000/admin/</a> to download it directly."
            f"  </div>"
            f"  <hr style='border: 0; border-top: 1px solid #edf2f7; margin: 25px 0;' />"
            f"  <p style='font-size: 11px; color: #a0aec0; text-align: center; margin: 0;'>"
            f"    This is an automated dispatch from PNY Talent Solutions. Please do not reply directly to this email."
            f"  </p>"
            f"</div>"
        )

        recipient_list = settings.NOTIFICATION_RECIPIENTS

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list,
            )
            email.attach_alternative(html_message, "text/html")

            # Attach the resume file if it exists
            if instance.resume_file:
                try:
                    instance.resume_file.open('rb')
                    file_content = instance.resume_file.read()
                    file_name = instance.resume_file.name.split('/')[-1] or "resume.pdf"
                    email.attach(file_name, file_content, 'application/octet-stream')
                except Exception as attach_err:
                    print(f"[PNY] Failed to attach resume file: {str(attach_err)}")
                finally:
                    try:
                        instance.resume_file.close()
                    except:
                        pass

            email.send(fail_silently=False)
            print(f"[PNY] Application email dispatched successfully to shobhitdixit093@gmail.com for: {job_title}")
        except Exception as e:
            # Catch all SMTP errors so the API still returns 201 even on network failure
            print(f"[PNY] SMTP application email dispatch failed: {str(e)}")


class ClientInquiryCreateAPIView(generics.CreateAPIView):
    """
    API endpoint that accepts client inquiries and dispatches them via SMTP email.
    Accessed via: POST /api/inquiries/
    """
    queryset = ClientInquiry.objects.all()
    serializer_class = ClientInquirySerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = []  # Public endpoint

    def perform_create(self, serializer):
        # Save structural details into database
        instance = serializer.save()

        # Gather details to compose the email
        client_name = instance.client_name
        client_email = instance.client_email
        client_phone = instance.client_phone
        client_company = instance.client_company or "Not Provided"
        inquiry_subject = instance.inquiry_subject
        inquiry_message = instance.inquiry_message

        # Email Subject
        subject = f"[PNY Talent Inquiry] {inquiry_subject} from {client_name}"

        # Composing the rich text plain body
        message_body = (
            f"Hello Shobhit,\n\n"
            f"You have received a new Client Partnership Inquiry from the PNY Talent Solutions website.\n\n"
            f"Here are the candidate inquiry details:\n"
            f"-----------------------------------------\n"
            f"👤 Client Name: {client_name}\n"
            f"✉️ Email Address: {client_email}\n"
            f"📞 Contact Phone: {client_phone}\n"
            f"🏢 Company Name: {client_company}\n"
            f"📌 Inquiry Topic: {inquiry_subject}\n"
            f"-----------------------------------------\n\n"
            f"💬 Message Details:\n"
            f"{inquiry_message}\n\n"
            f"Best regards,\n"
            f"PNY Talent Automated Email Dispatcher"
        )

        # Composing a premium, structured HTML email body
        html_message = (
            f"<div style='font-family: Arial, sans-serif; max-width: 600px; border: 1px solid #edf2f7; padding: 25px; border-radius: 8px; background-color: #f7fafc;'>"
            f"  <h2 style='color: #162646; margin-top: 0; font-family: sans-serif; border-bottom: 2px solid #00cccc; padding-bottom: 10px;'>New Business Inquiry</h2>"
            f"  <p style='color: #4a5568; font-size: 15px;'>Hello Shobhit Kumar,</p>"
            f"  <p style='color: #4a5568; font-size: 14px;'>A user has submitted a business partnership inquiry on the PNY Talent Solutions website. Details are outlined below:</p>"
            f"  <div style='background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px 20px; margin: 20px 0;'>"
            f"    <table style='width: 100%; border-collapse: collapse; font-size: 14px; color: #4a5568;'>"
            f"      <tr style='border-bottom: 1px solid #edf2f7;'>"
            f"        <td style='padding: 8px 0; font-weight: bold; width: 35%; color: #2d3748;'>Client Name:</td>"
            f"        <td style='padding: 8px 0;'>{client_name}</td>"
            f"      </tr>"
            f"      <tr style='border-bottom: 1px solid #edf2f7;'>"
            f"        <td style='padding: 8px 0; font-weight: bold; color: #2d3748;'>Email Address:</td>"
            f"        <td style='padding: 8px 0;'><a href='mailto:{client_email}' style='color: #00cccc;'>{client_email}</a></td>"
            f"      </tr>"
            f"      <tr style='border-bottom: 1px solid #edf2f7;'>"
            f"        <td style='padding: 8px 0; font-weight: bold; color: #2d3748;'>Contact Number:</td>"
            f"        <td style='padding: 8px 0;'>{client_phone}</td>"
            f"      </tr>"
            f"      <tr style='border-bottom: 1px solid #edf2f7;'>"
            f"        <td style='padding: 8px 0; font-weight: bold; color: #2d3748;'>Company Name:</td>"
            f"        <td style='padding: 8px 0;'>{client_company}</td>"
            f"      </tr>"
            f"      <tr>"
            f"        <td style='padding: 8px 0; font-weight: bold; color: #2d3748;'>Inquiry Topic:</td>"
            f"        <td style='padding: 8px 0; font-weight: bold; color: #162646;'>{inquiry_subject}</td>"
            f"      </tr>"
            f"    </table>"
            f"  </div>"
            f"  <h3 style='color: #2d3748; font-size: 14px; margin-bottom: 8px;'>💬 Message/Requirement Brief:</h3>"
            f"  <div style='background: #edf2f7; padding: 15px; border-radius: 6px; font-size: 13.5px; line-height: 1.5; color: #2d3748; white-space: pre-wrap; font-style: italic;'>"
            f"    {inquiry_message}"
            f"  </div>"
            f"  <hr style='border: 0; border-top: 1px solid #edf2f7; margin: 25px 0;' />"
            f"  <p style='font-size: 11px; color: #a0aec0; text-align: center; margin: 0;'>"
            f"    This is an automated dispatch from PNY Talent Solutions. Please do not reply directly to this mail."
            f"  </p>"
            f"</div>"
        )

        recipient_list = settings.NOTIFICATION_RECIPIENTS

        try:
            send_mail(
                subject=subject,
                message=message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False
            )
            print(f"[PNY] Inquiry email dispatched successfully to shobhitdixit093@gmail.com")
        except Exception as e:
            # We catch exceptions so that even if SMTP experiences network errors, 
            # the API request successfully responds, ensuring perfect front-end stability.
            print(f"SMTP Email dispatch failed: {str(e)}")

