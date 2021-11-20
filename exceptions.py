from logging import error

MESSAGE_ERROR = 'Сообщение не отправлено: {error}'
HOMEWORK_LIST_ERROR = 'Данные не в формате list {error}'
HOMEWORK_DICT_ERROR = 'Данные не в формате dict {error}'
HOMEWORK_KEY_ERROR = 'Ошибка запроса {error}'
PARSE_STATUS_ERROR = 'Не известный статус {error}'
SERVER_PROBLEMS = 'Сервер прилег, а ты вставай и разбирайся{error}'
RESPONSE_ERROR = 'Ошибка запроса{error}'


class BotErrors(Exception):
    """базовый класс для всех исключений."""
    pass


class MessageError(BotErrors):
    """сообщение не отправлено."""
   

class ResponseError(BotErrors):
    """Ошибка запроса."""


class ServerError(BotErrors):
    """Ошибка подключения к серверу."""


class HomeworkListError(BotErrors):
    """данные не в формате list."""


class HomeworkKeyError(BotErrors):
    """ошибка ключа запроса."""


class ParseStatusError(BotErrors):
    """не известный статус."""


class HomeworkDictError(BotErrors):
    """данные не в формате dict."""

