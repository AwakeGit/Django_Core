from typing import Dict, Optional

from django.http import HttpRequest


def current_url_name(request: HttpRequest) -> Dict[str, Optional[str]]:
    """
    Возвращает имя текущего маршрута URL.

    :param request: HttpRequest объект.
    :return: Словарь с именем текущего маршрута.
    """
    return {"current_url_name": request.resolver_match.url_name}
