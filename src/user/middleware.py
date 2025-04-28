import json
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from user.models import CustomUser

from .auth_utils import create_token, get_client_ip


def create_token_obj(request, user):
    request_ip = get_client_ip(request)
    timestamp = str(timezone.now())

    TOKEN_HASH = create_token(request_ip, f"timestamp{timestamp}user_id{user.id}")

    user.token_hash = TOKEN_HASH
    user.token_created_at = datetime.now()
    user.save()
    return TOKEN_HASH


def set_token_in_response(response, token):
    if settings.COOKIE_AUTH:
        response.set_cookie(
            key=settings.TOKEN_SETTINGS.get("NAME"),
            value=token,
            expires=datetime.now()
            + settings.TOKEN_SETTINGS.get("ACCESS_TOKEN_LIFETIME"),
            httponly=settings.TOKEN_SETTINGS.get("ACCESS_COOKIE_HTTP_ONLY"),
        )
    if settings.BEARER_AUTH:
        body = json.loads(response.content.decode("utf-8"))
        body[settings.TOKEN_SETTINGS.get("NAME")] = token
        response.content = json.dumps(body)
    return response


def get_request_token(request):
    if settings.BEARER_AUTH:
        if "HTTP_AUTHORIZATION" in request.META.keys():
            return request.META["HTTP_AUTHORIZATION"].replace("Bearer ", "")
        elif "Authorization" in request.headers.keys():
            return request.headers.get("Authorization").replace("Bearer ", "")

    if settings.COOKIE_AUTH:
        if settings.TOKEN_SETTINGS.get("NAME") in request.COOKIES.keys():
            return request.COOKIES.get(settings.TOKEN_SETTINGS.get("NAME"))
    return None


class CustomAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.split("/")[1] == "admin":
            return self.get_response(request)

        new_token = None
        current_user = AnonymousUser()
        bearer_token = None
        cookie_token = None

        if settings.BEARER_AUTH:
            if "HTTP_AUTHORIZATION" in request.META.keys():
                bearer_token = request.META["HTTP_AUTHORIZATION"].replace("Bearer ", "")
            elif "Authorization" in request.headers.keys():
                bearer_token = request.headers.get("Authorization").replace(
                    "Bearer ", ""
                )

        if settings.COOKIE_AUTH and bearer_token is None:
            if settings.TOKEN_SETTINGS.get("NAME") in request.COOKIES.keys():
                cookie_token = request.COOKIES.get(settings.TOKEN_SETTINGS.get("NAME"))

        if cookie_token or bearer_token:
            token = cookie_token if bearer_token is None else bearer_token
            if current_user := CustomUser.objects.filter(token_hash=token).first():
                if (
                    current_user.token_created_at
                    + settings.TOKEN_SETTINGS.get("TOTAL_ACCESS_TOKEN_LIFETIME")
                    < timezone.now()
                ):
                    current_user.token_hash = ""
                    current_user.save()
                    current_user = AnonymousUser()

                elif (
                    current_user.token_created_at
                    + settings.TOKEN_SETTINGS.get("ACCESS_TOKEN_LIFETIME")
                    < timezone.now()
                ):
                    new_token = create_token_obj(request, current_user)
            else:
                current_user = AnonymousUser()
        request.user = current_user
        request._user = current_user
        response = self.get_response(request)
        if token := new_token:
            response = set_token_in_response(response, token)
        return response
