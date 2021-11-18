from logging import error

MESSAGE_ERROR = 'Сообщение не отправлено: {error}'
HOMEWORK_LIST_ERROR = 'Данные не формате листа {error}'
HOMEWORK_KEY_ERROR = 'Ошибка запроса {error}'
PARSE_STATUS_ERROR = 'Не известный статус {error}'
SERVER_PROBLEMS = 'Сервер прилег, а ты вставай и разбирайся{error}'
RESPONSE_ERROR = 'Ошибка запроса{error}'

class Error(Exception):
    """базовый класс для всех исключений."""
    pass


class MessageError(Error):
    """сообщение не отправлено."""
    MESSAGE_ERROR = 'Сообщение не отправлено: {error}'
    print(MESSAGE_ERROR)


class ResponseError(Error):
    """Ошибка запроса."""
    RESPONSE_ERROR = 'Ошибка запроса{error}'
    print(RESPONSE_ERROR)
