import json

from django.http import HttpResponse, JsonResponse

from settings.aboba_swagger import aboba_swagger
from user.models import ErrorLog


def healthcheck(request):
    return HttpResponse(status=200)


@aboba_swagger(
    http_methods=["POST"],
    summary="Ручка для логов ошибок с фронта и не только, можешь хоть с бэкендерами общаться через нее",
    description="Ограничение в 2048 симоволов",
    tags=["logs"],
    body_params={"description": str},
    responses={200: "Успех"},
)
def log_error(request):
    body = json.loads(request.body.decode("utf-8"))
    ErrorLog.objects.create(description=body["description"])
    return HttpResponse(status=200)


def handle_404(request, exception=None):
    return JsonResponse(
        {
            "error": "Not Found",
            "message": "The requested resource was not found on this server.",
        },
        status=404,
    )


def handle_500(request, *args, **argv):
    return JsonResponse(
        {
            "error": "Internal Server Error",
            "message": "The server encountered an internal error or misconfiguration and was unable to complete your request.",
        },
        status=500,
    )
