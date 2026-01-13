"""
URL configuration for candle project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Health check (for Railway / Vercel testing)
    path("health/", health),

    # API routes
    path("api/accounts/", include("accounts.urls")),
    path("api/market/", include("market.urls")),
]
