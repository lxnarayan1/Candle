from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    Signup using EMAIL-based custom user model
    """
    email = request.data.get("email")
    password = request.data.get("password")
    full_name = request.data.get("full_name")

    if not email or not password or not full_name:
        return Response(
            {"detail": "Email, full name and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"email": ["User with this email already exists"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # IMPORTANT: use your custom UserManager
    user = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
    )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Login using EMAIL (USERNAME_FIELD)
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"detail": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 🔑 THIS IS THE KEY FIX
    user = authenticate(
        request=request,
        email=email,
        password=password,
    )

    if user is None:
        return Response(
            {"detail": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            },
        },
        status=status.HTTP_200_OK,
    )
