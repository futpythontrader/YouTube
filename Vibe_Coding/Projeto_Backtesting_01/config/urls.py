from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from apps.accounts.views import profile
from apps.core.views import healthz

urlpatterns = [
    path("", TemplateView.as_view(template_name="landing.html"), name="landing"),
    path("healthz/", healthz, name="healthz"),
    path("painel-admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("dashboard/perfil/", profile, name="profile"),
    path("dashboard/", include("apps.backtest.urls")),
]
