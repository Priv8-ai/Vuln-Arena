from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from core import views

urlpatterns = [
    path("", views.home), path("health", views.health),
    path("api/builds", views.builds), path("api/builds/<int:build_id>", views.build_detail),
    path("api/builds/<int:build_id>/credit", views.consume_credit),
    path("api/webhooks/test", views.webhook_test), path("api/render", views.render_name),
    path("api/export", views.export_file), path("api/task/import", views.import_task),
    path("api/queue", views.queue_task), path("api/run", views.run_ref), path("logs", views.logs),
]

# The benchmark image deliberately keeps the service self-contained. Django's
# development static handler is sufficient for these local-only fixtures.
urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
