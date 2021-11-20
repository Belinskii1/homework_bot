import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(handlers=[logging.FileHandler(
    filename='program.log',
    encoding='utf-8',
    mode='a+'
)],
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='my_logger.log',
    encoding='utf-8',
    mode='w'
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(message, bot):
    """Отправка сообщения ботом в чат."""
    try:
        message = bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info('Отправка {message} для {TELEGRAM_CHAT_ID}')
    except telegram.error.TelegramError as sending_error:
        logging.error(exceptions.MessageError.format(error=sending_error))
    return message


def get_api_answer(current_timestamp):
    """делает запрос к серверу."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(
        ENDPOINT,
        params=params,
        headers=HEADERS,
    )
    if homework_statuses.status_code != 200:
        raise exceptions.ServerError(exceptions.SERVER_PROBLEMS)
    return homework_statuses.json()


def check_response(response: list):
    """Валидация ответов API."""
    if 'error' in response:
        raise exceptions.ResponseError(exceptions.RESPONSE_ERROR)
    if not isinstance(response['homeworks'], list):
        raise exceptions.HomeworkListError(exceptions.HOMEWORK_LIST_ERROR)
    """Сначала (в строке 80) проверяется тип в response['homeworks'],
    а потом проверяется, есть ли вообще ключ homeworks в ответе.
    Это как-то нелогично, нужно поменять местами"""
    # Если поменять местами, то падают тесты
    if 'homeworks' not in response:
        raise exceptions.HomeworkKeyError(exceptions.HOMEWORK_KEY_ERROR)
    return response['homeworks']


def check_response_status(homework: dict):
    """Дополнительная валидация ответов API."""
    if not isinstance(homework, dict):
        raise exceptions.HomeworkDictError(exceptions.HOMEWORK_DICT_ERROR)
    status = homework.get("status")
    homework_name = homework.get("homework_name")
    if not status or not homework_name:
        raise KeyError(exceptions.HOMEWORK_KEY_ERROR)
    if status not in HOMEWORK_STATUSES:
        raise KeyError(exceptions.PARSE_STATUS_ERROR)
    return True


def parse_status(homework: dict):
    """статус конкретной ДЗ и проверка статусов."""
    check_response_status(homework)
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка сетевого окружения."""
    PT = PRACTICUM_TOKEN is None
    TT = TELEGRAM_TOKEN is None
    TC = TELEGRAM_CHAT_ID is None
    if PT or TT or TC:
        return False
    return True


def main():
    """Основная логика работы бота."""
    logger.debug('Запуск бота')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    set_errors = ["test_error"]
    set_status = ["test_status"]
    while True:
        time.sleep(RETRY_TIME)
        try:
            current_timestamp = int(time.time())  # первая точка
            api_answer = get_api_answer(current_timestamp)
            current_timestamp = api_answer.get(
                'current_date')  # обновляем точку
            result = check_response(api_answer)  # list
            for homework in result:
                parse_status_result = parse_status(homework)
                if set_status[-1] != homework.get('status'):
                    send_message(bot, parse_status_result)
                    set_status.append(homework.get('status'))
                else:
                    logger.debug('статус не изменился')
        except Exception as error:
            logging.error('Bot down')
            if set_errors[-1] != error:
                set_errors.append(error)
                message = f'Бот столкнулся с ошибкой: {error}'
                logger.exception(message)
                bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID, text=message
                )


if __name__ == '__main__':
    main()
