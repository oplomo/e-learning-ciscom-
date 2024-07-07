from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from courses.views import permission_denied_view

handler403 = permission_denied_view

urlpatterns = [
    path("", include("courses.urls")),  # Include your app's URLs here
    path("admin/", admin.site.urls),
]

# Serve static files during development
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
