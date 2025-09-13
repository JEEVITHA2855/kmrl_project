from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ...existing code...
] + static("/", document_root="e:/kmrl_project")