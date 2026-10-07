from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        "service": "PNY Talent Solutions API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "jobs": "/api/jobs/",
            "applications": "/api/applications/",
            "inquiries": "/api/inquiries/",
            "admin": "/admin/",
        }
    })


urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/', include('careers.urls')),
]

# Serve media files (like candidate resumes) during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
