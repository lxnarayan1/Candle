from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .services import get_yahoo_market_data
from .services import search_companies
from rest_framework.permissions import IsAuthenticated
from .services import get_company_data


@api_view(["GET"])
@permission_classes([AllowAny])
def market_overview(request):
    symbol = request.query_params.get("symbol", "^NSEI")
    range_key = request.query_params.get("range", "1D")

    try:
        data = get_yahoo_market_data(symbol, range_key)
        return Response(data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(["GET"])
@permission_classes([AllowAny])  # 🔓 Public search suggestions
def company_search(request):
    query = request.query_params.get("q", "").strip()

    results = search_companies(query)

    return Response(results)

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # 🔒 LOGIN REQUIRED
def company_detail(request):
    symbol = request.query_params.get("symbol")
    range_key = request.query_params.get("range", "1D")

    try:
        data = get_company_data(symbol, range_key)
        return Response(data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        return Response(
            {"detail": "Failed to fetch company data"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )