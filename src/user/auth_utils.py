import sys

import _frozen_importlib as _bootstrap
from django.conf import settings


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def create_token(ip, brow):
    _str = ip + brow
    token = make_hash(_str)
    return token


def make_hash(password, salt=None, hasher="default"):
    hasher = get_hasher(hasher)
    salt = salt or hasher.salt()
    return hasher.encode(password, salt)


def get_hasher(algorithm="default"):
    if hasattr(algorithm, "algorithm"):
        return algorithm
    elif algorithm == "default":
        return get_hashers()[0]
    else:
        hashers = get_hashers_by_algorithm()
        try:
            return hashers[algorithm]
        except KeyError:
            raise ValueError(
                "Unknown password hashing algorithm '%s'. "
                "Did you specify it in the PASSWORD_HASHERS "
                "setting?" % algorithm
            )


def get_hashers():
    hashers = []
    for hasher_path in settings.PASSWORD_HASHERS:
        hasher_cls = import_string(hasher_path)
        hasher = hasher_cls()
        hashers.append(hasher)
    return hashers


def import_string(dotted_path):
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    try:
        return cached_import(module_path, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class'
            % (module_path, class_name)
        ) from err


def cached_import(module_path, class_name):
    if not (
        (module := sys.modules.get(module_path))
        and (spec := getattr(module, "__spec__", None))
        and getattr(spec, "_initializing", False) is False
    ):
        module = import_module(module_path)
    return getattr(module, class_name)


def import_module(name, package=None):
    level = 0
    if name.startswith("."):
        if not package:
            msg = (
                "the 'package' argument is required to perform a relative "
                "import for {!r}"
            )
            raise TypeError(msg.format(name))
        for character in name:
            if character != ".":
                break
            level += 1
    return _bootstrap._gcd_import(name[level:], package, level)


def get_hashers_by_algorithm():
    return {hasher.algorithm: hasher for hasher in get_hashers()}


def identify_hasher(encoded):
    if (len(encoded) == 32 and "$" not in encoded) or (
        len(encoded) == 37 and encoded.startswith("md5$$")
    ):
        algorithm = "unsalted_md5"
    elif len(encoded) == 46 and encoded.startswith("sha1$$"):
        algorithm = "unsalted_sha1"
    else:
        algorithm = encoded.split("$", 1)[0]
    return get_hasher(algorithm)
