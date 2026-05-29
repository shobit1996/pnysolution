from django.urls import path
from .views import JobListAPIView, JobApplicationCreateAPIView, ClientInquiryCreateAPIView

urlpatterns = [
    path('jobs/', JobListAPIView.as_view(), name='job-list'),
    path('applications/', JobApplicationCreateAPIView.as_view(), name='apply-job'),
    path('inquiries/', ClientInquiryCreateAPIView.as_view(), name='submit-inquiry'),
]

