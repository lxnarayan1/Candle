from django.urls import path
from .views import market_overview , company_search, company_detail

urlpatterns = [
    path("overview/", market_overview, name="market-overview"),
    path("search/", company_search),
    path("company/", company_detail),
]
