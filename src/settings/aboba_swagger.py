# https://drf-spectacular.readthedocs.io/en/latest/drf_spectacular.html#drf_spectacular.utils.extend_schema
import hashlib
from functools import wraps
from typing import Any, Dict, List

from django.http import HttpResponse

# Отключил варнинги которые не смог поправить чтоб консоль не срали
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.decorators import api_view

from user.models import AccessGroup

spectacular_settings.apply_patches({"DISABLE_ERRORS_AND_WARNINGS": True})


TYPES_SERIALIZERS_DICT = {
    str: serializers.CharField,
    int: serializers.IntegerField,
    float: serializers.FloatField,
    list: serializers.ListField,
    dict: serializers.DictField,
    bool: serializers.BooleanField,
    bytes: serializers.FileField,
    # Добавляем поддержку дополнительных типов
    None: lambda: serializers.CharField(allow_null=True, required=False),
    type(None): lambda: serializers.CharField(allow_null=True, required=False),
    # Другие типы данных
    complex: lambda: serializers.CharField(help_text="Complex number as string"),
    set: lambda: serializers.ListField(child=serializers.CharField()),
    tuple: lambda: serializers.ListField(child=serializers.CharField()),
    # Типы из datetime
    "date": lambda: serializers.DateField(),
    "time": lambda: serializers.TimeField(),
    "datetime": lambda: serializers.DateTimeField(),
    # Добавление JSON поля
    "json": lambda: serializers.JSONField(),
}


def aboba_swagger(
    http_methods: List[str] = [],
    summary: str = "",
    description: str = "",
    query_params: Dict[str, Any] = {},
    body_params: Dict[str, Any] = {},
    responses: Dict[str, Any] = {},
    need_auth: bool = False,
    external_docs: Dict[str, List] = [],
    deprecated: bool = False,
    tags: List[str] = None,
    groups: List[str] = [],
    is_drf: bool = False,
    override_drf_autogen: bool = False,
):
    """
    Декоратор для автоматической генерации OpenAPI-документации и обработки запросов.

    Параметры:
        - http_methods (List[str]): Список HTTP-методов, которые поддерживает ручка (например, ["GET", "POST"]).
        - summary (str): Краткое описание ручки.
        - description (str): Подробное описание ручки.
        - query_params (Dict[str, Any]): Параметры запроса (query parameters).
            Пример: {"param_name": str, "other_param": int}
        - body_params (Dict[str, Any]): Параметры тела запроса (body parameters).
            Пример: {"field1": str, "field2": {"nested": int}}
        - responses (Dict[str, Any]): Возможные ответы ручки. Может быть задан в различных форматах:
            1. Простой формат: {"200": "Success message"}
            2. Словарь примеров: {"200": {"Example1": "Success", "Example2": {"key": "value"}}}
            3. С вложенными структурами: {"200": {"data": {"id": 1, "name": "Test"}}}
            4. С явным указанием типа: {"200": {"data": serializers.DateTimeField()}}
        - need_auth (bool): Требуется ли аутентификация для доступа к ручке.
        - external_docs (Dict[str, List]): Внешняя документация.
        - deprecated (bool): Устарела ли ручка.
        - tags (List[str]): Теги для группировки ручек в документации.
        - groups (List[str]): Группы пользователей, которым разрешен доступ к ручке.
        - is_drf (bool): Является ли метод на который ты хочешь повесить декоратор, методом ViewSet.
        - override_drf_autogen (bool): drf-spectacular генерит самостоятельно сваггер для ViewSet.
            False: Переопределятся только те поля которые ты указал
            True: Переопределятся все поля

    Примечания:
        - Ответы 401 и 403 добавляются автоматически, если указаны `need_auth` или `groups`.
        - Если указаны группы, доступ к ручке будет ограничен только для пользователей из этих групп.

    Пример использования декоратора со всеми аргументами:

    @aboba_swagger(
        http_methods=["POST"],
        summary="Это большая ручка для подношений большой тестовой абобе",
        description="Что бы ты в нее не передал, абоба будет довольна",
        query_params={
            "Теплые_слова": str,
            "Цифры_с_обратной_стороны_банковской_карты": int,
            "Обнять_абобу": bool,
            "Процент_дохода_жертвуемый_в_дар_абобе": float,
            "Объект": dict,
        },
        body_params={
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "bool": bool,
            "bytes": bytes,
            "custom_type": serializers.DateTimeField(),
            "nested_dict": {
                "field1": str,
                "field2": int,
                "deeper": {
                    "even_deeper": bool
                }
            },
            "array_of_objects": [{"id": int, "name": str}],
        },
        responses={
            "200": {
                "Спасибо": "Большое спасибо, абоба приняла ваши подношения",
                "Возьми это человек": {"key": "Абоба посылает вам реальное value"},
                "Сложный_ответ": {
                    "id": 123,
                    "data": {
                        "items": [1, 2, 3],
                        "metadata": {"created": "datetime"}
                    }
                }
            },
            "302": "Абоба отошла, оставьте свой пэйлоад здесь, она оценит когда вернется",
            "202": '{"message": "Абоба чихнула, ожидайте плодородный год"}',
            "500": {
                "Господи, о нет": "Абоба подавилась и умерла, вы обречены на гибель"
            }
        },
        need_auth=False,
        deprecated=False,
        external_docs={
            "url": "https://ru.wikipedia.org/wiki/Абоба_(интернет-мем)",
            "description": "Документация по абобе"
        },
        tags=["aboba"],
        groups=["Worker", "Manager"],
        is_drf=False,
        override_drf_autogen=False,
    )
    def my_view(request):
        # Ваша логика обработки запроса
        pass
    """

    def decorator(function):
        nonlocal description, need_auth  # https://stackoverflow.com/questions/1261875/what-does-nonlocal-do-in-python-3
        query_parameters = []
        body_parameters = {}
        formated_responses = {}
        formated_examples = []
        auth_group_names = set()
        response_403 = (
            f"К этой ручке имеют доступ только группы пользователей: {groups}."
        )

        if is_drf is False and len(http_methods) == 0:
            raise ValueError("http_methods is empty")

        # Тут обрабатываем query params
        for param_key in query_params.keys():
            query_parameters.append(
                OpenApiParameter(name=param_key, type=query_params[param_key])
            )

        # Тут обрабатываем ключи в body
        for param_key in body_params.keys():
            param_value = body_params[param_key]

            # Check if it's a basic type in our dictionary
            if isinstance(param_value, type) and param_value in TYPES_SERIALIZERS_DICT:
                body_parameters[param_key] = TYPES_SERIALIZERS_DICT[param_value]()
            # Handle nested dictionaries
            elif isinstance(param_value, dict):
                body_parameters[param_key] = parse_value_to_field(param_value)
            # Handle already instantiated serializer fields
            elif isinstance(param_value, serializers.Field):
                body_parameters[param_key] = param_value
            # Handle lists
            elif isinstance(param_value, list):
                body_parameters[param_key] = parse_value_to_field(param_value)
            # Handle strings that might be type references
            elif isinstance(param_value, str) and param_value in TYPES_SERIALIZERS_DICT:
                body_parameters[param_key] = TYPES_SERIALIZERS_DICT[param_value]()
            # Default case
            else:
                body_parameters[param_key] = param_value

        # Если группы есть, то делаем автоматически требование аутентификации
        if groups:
            need_auth = True
            description += "\n## Группы пользователей: "
            for group in groups:
                # Проверка наличия группы
                if AccessGroup.objects.filter(name=group).exists():
                    auth_group_names.add(group)
                else:
                    raise ValueError(f"Нет группы {group}")
            description += ", ".join([f"{group}" for group in auth_group_names])
            # Автоматическое добавление кода ответа 403
            response_403.format(", ".join(auth_group_names))
            if "403" in responses.keys():
                if type(responses["403"]) != dict:
                    saved_403_response = responses["403"]
                    responses["403"] = {"403": saved_403_response}
                responses["403"]["Разрешенные группы пользователей"] = response_403
            else:
                responses["403"] = response_403

        # Автоматическое добавление кода ответа 401
        if need_auth:
            description = f"Эта ручка требует авторизации \n\n {description}"
            responses["401"] = {"Unauthorized": "Unauthorized"}

        formated_responses = build_openapi_responses(
            responses_dict=responses, handler_name=function.__name__
        )

        if not is_drf:

            @wraps(function)
            @extend_schema(
                summary=summary,
                description=description,
                parameters=query_parameters,
                request={
                    "application/json": inline_serializer(
                        name=f"{function.__name__}_{hashlib.md5(str(body_parameters).encode()).hexdigest()[:8]}",
                        fields=body_parameters,
                    )
                },
                responses=formated_responses,
                examples=formated_examples,
                auth=[{"jwtAuth": []}] if need_auth else False,
                external_docs=external_docs,
                deprecated=deprecated,
                tags=tags,
            )
            @api_view(http_methods)
            def wrap(request, *args, **kwargs):
                if need_auth and not request.user.is_authenticated:
                    return HttpResponse("Unauthorized", status=401)
                if groups:
                    if (
                        not request.user.is_authenticated
                        or not request.user.groups.filter(
                            name__in=auth_group_names
                        ).exists()
                    ):
                        user_groups = request.user.groups.all()
                        groups_msg = f"""Вы находитесь в группах:
                            {''.join([group.name for group in user_groups]) if user_groups.exists() else 'Анонимный юзер'}
                        """
                        return HttpResponse(
                            f"У вас нет доступа {response_403} {groups_msg}", status=403
                        )
                return function(request, *args, **kwargs)

        else:
            # Сделано именно так, а не декоратором, потому что магическим образом именно так работает с drf.
            # Если делать то же самое декоратором то ручка в сваггере не дополняется.
            # Конечно можешь поэксперементировать, если сделаешь круче, с меня пиво.
            decorator_args = {
                "summary": summary,
                "description": description,
                "parameters": query_parameters,
                "request": {
                    "application/json": inline_serializer(
                        name=f"{function.__name__}_{hashlib.md5(str(body_parameters).encode()).hexdigest()[:8]}",
                        fields=body_parameters,
                    )
                },
                "responses": formated_responses,
                "examples": formated_examples,
                "auth": [{"jwtAuth": []}] if need_auth else False,
                "external_docs": external_docs,
                "deprecated": deprecated,
                "tags": tags,
            }
            if not override_drf_autogen:
                # Если не надо переопределять все поля то убираем не указанные, чтоб оставить сгенеренные
                if len(summary) == 0:
                    decorator_args.pop("summary", None)
                if len(description) == 0:
                    decorator_args.pop("description", None)
                if len(query_parameters) == 0:
                    decorator_args.pop("parameters", None)
                if len(body_params.keys()) == 0:
                    decorator_args.pop("request", None)
                if len(formated_responses.keys()) == 0:
                    decorator_args.pop("responses", None)

            function = extend_schema(**decorator_args)(function)

            @wraps(function)
            def wrap(self, request, *args, **kwargs):
                if need_auth and not request.user.is_authenticated:
                    return HttpResponse("Unauthorized", status=401)
                if groups:
                    if (
                        not request.user.is_authenticated
                        or not request.user.groups.filter(
                            name__in=auth_group_names
                        ).exists()
                    ):
                        user_groups = request.user.groups.all()
                        groups_msg = f"""Вы находитесь в группах:
                            {''.join([group.name for group in user_groups]) if user_groups.exists() else 'Анонимный юзер'}
                        """
                        return HttpResponse(
                            f"У вас нет доступа {response_403} {groups_msg}", status=403
                        )
                return function(self, request, *args, **kwargs)

        return wrap

    return decorator


def parse_value_to_field(value):
    """
    Преобразует Python-значение или строку типа в DRF поле.
    Поддерживает вложенные структуры и различные типы данных.
    """
    # Handle None values
    if value is None:
        return serializers.CharField(allow_null=True, required=False)

    # Handle type references (str, int, etc.)
    if isinstance(value, type):
        if value in TYPES_SERIALIZERS_DICT:
            return TYPES_SERIALIZERS_DICT[value]()
        return serializers.CharField()

    # Handle string type references as strings
    if isinstance(value, str):
        # Try to interpret as a type reference
        type_mapping = {
            "str": serializers.CharField(),
            "int": serializers.IntegerField(),
            "float": serializers.FloatField(),
            "bool": serializers.BooleanField(),
            "list": serializers.ListField(),
            "dict": serializers.DictField(),
            "bytes": serializers.FileField(),
        }
        if value in type_mapping:
            return type_mapping[value]
        # Otherwise treat as a string value
        return serializers.CharField(default=value)

    # Handle dictionaries - create a nested serializer
    if isinstance(value, dict):
        fields = {}
        for k, v in value.items():
            fields[k] = parse_value_to_field(v)

        # Generate a unique name for the serializer based on content hash
        dict_str = str(sorted(value.items()))
        name = f"Nested_{hashlib.md5(dict_str.encode()).hexdigest()[:8]}"

        return inline_serializer(name=name, fields=fields)

    # Handle lists - create a list field with appropriate child
    if isinstance(value, list):
        if not value:  # Empty list
            return serializers.ListField(
                child=serializers.CharField(allow_null=True, required=False)
            )

        # If all items are of the same type, use that type for the child
        if all(isinstance(item, type(value[0])) for item in value):
            child = parse_value_to_field(value[0])
            return serializers.ListField(child=child)

        # Mixed types - use a generic serializer that can handle any type
        return serializers.ListField(child=serializers.JSONField())

    # Handle basic types
    if isinstance(value, bool):
        return serializers.BooleanField(default=value)

    if isinstance(value, int):
        return serializers.IntegerField(default=value)

    if isinstance(value, float):
        return serializers.FloatField(default=value)

    # Default to CharField for everything else
    return serializers.CharField(default=str(value))


def build_openapi_responses(responses_dict: dict, handler_name) -> dict:
    """
    Создает OpenAPI-совместимое описание ответов на основе словаря ответов.

    Args:
        responses_dict: Словарь с кодами ответов и их примерами.
        handler_name: Имя обработчика, используется для генерации уникальных имен.

    Returns:
        Словарь OpenAPI-совместимых объектов для описания ответов.
    """
    openapi_responses = {}

    for status_code, response_data in responses_dict.items():
        # Нормализуем данные ответа в словарь, если это еще не словарь
        if not isinstance(response_data, dict):
            # Handle JSON string
            if (
                isinstance(response_data, str)
                and response_data.strip().startswith("{")
                and response_data.strip().endswith("}")
            ):
                import json

                try:
                    response_data = {
                        f"Response {status_code}": json.loads(response_data)
                    }
                except json.JSONDecodeError:
                    response_data = {f"Response {status_code}": response_data}
            else:
                response_data = {f"Response {status_code}": response_data}

        # Clean examples by converting serializer fields to their string representation or default values
        cleaned_examples = {}
        for example_name, example_value in response_data.items():
            if isinstance(example_value, serializers.Field):
                # Convert serializer fields to a suitable default value
                cleaned_examples[example_name] = _get_serializer_default_value(
                    example_value
                )
            elif isinstance(example_value, dict):
                # Process nested dictionaries
                cleaned_dict = {}
                for k, v in example_value.items():
                    if isinstance(v, serializers.Field):
                        cleaned_dict[k] = _get_serializer_default_value(v)
                    else:
                        cleaned_dict[k] = v
                cleaned_examples[example_name] = cleaned_dict
            else:
                cleaned_examples[example_name] = example_value

        # Создаем список примеров для каждого варианта ответа
        examples_list = []
        for example_name, example_value in cleaned_examples.items():
            examples_list.append(
                OpenApiExample(
                    name=example_name,
                    value=example_value,
                    response_only=True,
                    status_codes=[str(status_code)],
                )
            )

        # Определяем схему ответа
        # Сначала пробуем создать унифицированную схему для всех примеров
        all_examples_values = list(cleaned_examples.values())

        # Если все значения одного типа и это не словари, используем простой тип
        if (
            all_examples_values
            and all(not isinstance(val, dict) for val in all_examples_values)
            and all(
                isinstance(val, type(all_examples_values[0]))
                for val in all_examples_values
            )
        ):
            response_schema = type(all_examples_values[0])
        # Если хотя бы один пример - словарь, создаем объединенную схему
        elif any(isinstance(val, dict) for val in all_examples_values):
            # Объединяем все поля из всех словарных примеров
            merged_fields = {}
            for example_value in all_examples_values:
                if isinstance(example_value, dict):
                    for key, val in example_value.items():
                        # Если поле уже есть и типы разные, используем более гибкий тип
                        if key in merged_fields:
                            # Если типы разные, используем JSONField
                            if type(val) != type(merged_fields[key]):
                                merged_fields[key] = parse_value_to_field(
                                    None
                                )  # Используем общий тип
                        else:
                            merged_fields[key] = parse_value_to_field(val)

            # Создаем инлайн-сериализатор с объединенными полями
            response_schema = inline_serializer(
                name=f"Response{status_code}_{handler_name}_{hashlib.md5(str(merged_fields).encode()).hexdigest()[:8]}",
                fields=merged_fields,
            )
        # Для строк и других простых типов
        else:
            # Если есть хотя бы одно значение, используем его тип
            if all_examples_values:
                first_value = all_examples_values[0]
                response_schema = parse_value_to_field(first_value)
            else:
                # Если примеры отсутствуют, используем строку
                response_schema = serializers.CharField()

        # Создаем объект ответа OpenAPI
        openapi_responses[status_code] = OpenApiResponse(
            response=response_schema,
            examples=examples_list,
            description=f"Response for status code {status_code}",
        )

    return openapi_responses


def _get_serializer_default_value(field):
    """Получает подходящее значение по умолчанию для поля сериализатора."""
    if isinstance(field, serializers.DateTimeField):
        return "2023-01-01T12:00:00Z"
    elif isinstance(field, serializers.DateField):
        return "2023-01-01"
    elif isinstance(field, serializers.TimeField):
        return "12:00:00"
    elif isinstance(field, serializers.IntegerField):
        return 0
    elif isinstance(field, serializers.FloatField):
        return 0.0
    elif isinstance(field, serializers.DecimalField):
        return "0.00"
    elif isinstance(field, serializers.BooleanField):
        return False
    elif isinstance(field, serializers.ListField):
        return []
    elif isinstance(field, serializers.DictField):
        return {}
    else:
        return "example"
