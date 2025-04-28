import json
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from validate_email import validate_email

from settings.aboba_swagger import aboba_swagger

from .middleware import create_token_obj, get_request_token, set_token_in_response
from .models import CustomUser


def validate_tg_hash(telegram_init_data):
    import hashlib
    import hmac
    from urllib.parse import parse_qs

    try:
        init_data = parse_qs(telegram_init_data)
        hash_value = init_data.get("hash", [None])[0]
        data_to_check = []

        sorted_items = sorted(
            (key, val[0]) for key, val in init_data.items() if key != "hash"
        )
        data_to_check = [f"{key}={value}" for key, value in sorted_items]

        secret = hmac.new(
            b"WebAppData", settings.TG_SECRET.encode(), hashlib.sha256
        ).digest()
        _hash = hmac.new(
            secret, "\n".join(data_to_check).encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(_hash, hash_value)
    except Exception:
        return False


@aboba_swagger(
    http_methods=["POST"],
    summary="Аутентификация через телеграмм",
    description="Логинит через тг, если нет аккаунта то создает его и авторизует",
    body_params={
        "initData": dict,
    },
    responses={
        "200": {"Успешный вход": {"success": True, "error": ""}},
        "400": {
            "Невалидный тг хэш": {"success": False, "error": "tg hash not valid"},
            "Уже вошли в аккаунт": {"success": False, "error": "already auth"},
        },
    },
    tags=["user"],
)
def tg_auth(request):
    response_template = {"success": False, "error": ""}
    if request.method == "POST" and request.user.is_anonymous:
        body = json.loads(request.body.decode("utf-8"))
        telegram_init_data = body.get("initData")

        if not validate_tg_hash(telegram_init_data):
            response_template["error"] = "tg hash not valid"
            return JsonResponse(response_template, status=400)

        parsed_tg_data = unquote(telegram_init_data)
        parsed_tg_data = dict(pair.split("=") for pair in parsed_tg_data.split("&"))
        tg_user = json.loads(parsed_tg_data["user"])

        tg_id = tg_user["id"]
        username = tg_user["username"]
        first_name = tg_user["first_name"]
        photo_url = tg_user["photo_url"]
        user = CustomUser.objects.filter(tg_id=tg_id).first()
        if not user:
            user = CustomUser.objects.create(
                tg_id=tg_id,
                username=f"aboba_no_username_{tg_id}" if not username else username,
                first_name=first_name,
                photo_url=photo_url,
            )
        else:
            if user.first_name != first_name:
                user.first_name = first_name
            if user.photo_url != photo_url:
                user.photo_url = photo_url
            if username and user.username != username:
                user.username = username
        user.save()
        token = create_token_obj(request, user)
        response_template["success"] = True
        response = set_token_in_response(
            JsonResponse(response_template, status=200), token
        )
        return response
    else:
        response_template["error"] = "already auth"
        return JsonResponse(response_template, status=400)


@aboba_swagger(
    http_methods=["POST"],
    summary="Аутентификация по почте и паролю",
    body_params={
        "email": str,
        "password": str,
    },
    responses={
        "200": {
            "Успешная аутентификация": {"success": True, "error": ""},
        },
        "400": {
            "Неверная почта или пароль": {
                "success": False,
                "error": "email or password is incorrect",
            },
            "Юзер неактивен": {"success": False, "error": "user is not active"},
            "Юзер уже залогинен": {"success": False, "error": "already logged in"},
        },
    },
    tags=["user"],
)
def login(request):
    response_template = {"success": False, "error": ""}
    if request.method == "POST" and request.user.is_anonymous:
        body = json.loads(request.body.decode("utf-8"))
        email = body.get("email")
        password = body.get("password")
        if (password and email) and (user := CustomUser.objects.filter(email=email)):
            user = user.first()
            if check_password(password, user.password):
                if user.is_active:
                    token = create_token_obj(request, user)
                    response_template["success"] = True
                    response = JsonResponse(response_template, status=200)
                    response = set_token_in_response(response, token)
                    return response
                else:
                    response_template["error"] = "user is not active"
                    return JsonResponse(response_template, status=400)
        else:
            response_template["error"] = "email or password is incorrect"
            return JsonResponse(response_template, status=400)
    else:
        response_template["error"] = "already logged in"
        return JsonResponse(response_template, status=400)


@aboba_swagger(
    http_methods=["POST"],
    summary="Регистрация по почте и паролю",
    body_params={
        "email": str,
        "password": str,
    },
    responses={
        "200": {
            "Успешная регистрация": {"success": True, "error": ""},
        },
        "400": {
            "Пользователь с такой почтой уже зарегистрирован": {
                "success": False,
                "error": "already exists",
            },
            "Чет сломалось при создании пользователя": {
                "success": False,
                "error": "server error",
            },
            "Пользователь уже зашел в аккаунт": {
                "success": False,
                "error": "already auth",
            },
            "В запросе не хватает пароля или почты": {
                "success": False,
                "error": "email or password is incorrect",
            },
        },
    },
    tags=["user"],
)
def registration(request):
    response_template = {
        "success": False,
        "error": "",
    }

    body = json.loads(request.body.decode("utf-8"))
    email = body["email"]
    password = body["password"]

    if request.user.is_anonymous:
        if email and password and validate_email(email):
            if CustomUser.objects.filter(email=email).exists():
                response_template["error"] = "already exists"
                return JsonResponse(response_template, status=400)
            try:
                CustomUser.objects.create(
                    username=email,
                    password=make_password(password),
                    email=email,
                    is_active=True,
                )
                response_template["success"] = True
                return JsonResponse(response_template, status=200)
            except Exception:
                response_template["error"] = "server error"
                return JsonResponse(response_template, status=400)
        response_template["error"] = "email or password is incorrect"
        return JsonResponse(response_template, status=400)
    response_template["error"] = "already auth"
    return JsonResponse(response_template, status=418)


@aboba_swagger(
    http_methods=["GET"],
    summary="Выход из аккаунта",
    responses={
        "200": {
            "Успешный выход из аккаунта": {"success": True, "error": ""},
        },
        "400": {
            "Пользователь не залогинен": {"success": False, "error": "not auth"},
        },
        "404": {
            "Пользователь с таким токеном не найден": {
                "success": False,
                "error": "user not found",
            },
        },
    },
    tags=["user"],
    need_auth=True,
)
def logout(request):
    response_template = {"success": False, "error": ""}
    token = get_request_token(request)
    if not request.user.is_anonymous and token:
        if user := CustomUser.objects.filter(token_hash=token).first():
            user.token_hash = None
            user.token_created_at = None
            user.save()
            response_template["success"] = True
            return JsonResponse(response_template, status=200)
        response_template["error"] = "user not found"
        return JsonResponse(response_template, status=404)
    response_template["error"] = "not auth"
    return JsonResponse(response_template, status=400)


@aboba_swagger(
    http_methods=["GET"],
    summary="Получить текущего пользователя",
    responses={
        "200": {
            "Успешно": {
                "user": {"tg_id": "str", "email": "str", "groups": ["str", "str"]}
            }
        },
    },
    tags=["user"],
    need_auth=True,
)
def current(request):
    return JsonResponse(
        {
            "user": {
                "email": request.user.email,
                "tg_id": request.user.tg_id,
                "groups": [group.name for group in request.user.groups.all()],
            }
        },
        status=200,
    )
