class TelegramMessageError(Exception):
    """Ошибка отправки сообщения."""

    pass


class StatusCodeError(Exception):
    """Код запроса отличается."""

    pass


class EndPointIsNotReached(Exception):
    """Ошибка при обращении к эндпоинту."""

    pass


class HTTPStatusCodeNotCorrect(Exception):
    """Ошибка, если статус кода HTTP не равен 200."""

    pass


class APIResponseNotDict(Exception):
    """Ответ API не является словарём."""

    pass


class APIResponseNotCorrect(Exception):
    """Отсутствуют необходимые ключи."""

    pass


class APIResponseNotList(Exception):
    """Ответ API не является словарём."""

    pass


class VariableNotExists(Exception):
    """Необходимая переменная окружения отсутствует."""

    pass


class UnknownStatus(Exception):
    """Статус домашки не определён."""

    pass
