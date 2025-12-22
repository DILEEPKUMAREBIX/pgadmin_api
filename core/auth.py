from typing import Tuple, Optional

import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework.permissions import BasePermission
from django.utils import timezone
from datetime import timedelta

from properties.models import User


ALGORITHM = 'HS256'
TOKEN_TTL_HOURS = 24


def generate_jwt(user: User) -> str:
    now = timezone.now()
    payload = {
        'sub': user.id,
        'username': user.username,
        'property_id': user.property_id,
        'role': user.role,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(hours=TOKEN_TTL_HOURS)).timestamp()),
        'iss': 'pgadmin-api',
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_password(raw_password: str, password_hash: str) -> bool:
    return check_password(raw_password, password_hash)


class JWTAuthentication(BaseAuthentication):
    """Simple JWT auth reading Authorization: Bearer <token> and attaching app User."""

    def authenticate(self, request) -> Optional[Tuple[User, dict]]:
        auth_header = request.headers.get('Authorization') or ''
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        token = parts[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        user_id = payload.get('sub')
        if not user_id:
            raise exceptions.AuthenticationFailed('Invalid token payload')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        return (user, payload)


class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None
