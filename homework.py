import os
import time
import logging
import requests
from dotenv import load_dotenv
import telegram
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
    logger.info('Отправка {message} для {TELEGRAM_CHAT_ID}')
    try:
        new_massage = bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as sending_error:
        logging.error(exceptions.MESSAGE_ERROR.format(error=sending_error))
    return new_massage


def get_api_answer(current_timestamp):
    """делает запрос к серверу."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            params=params,
            headers=HEADERS,
        )
        if homework_statuses.status_code == 200:
            return homework_statuses.json()
        else:
            raise Exception(exceptions.SERVER_PROBLEMS)
    except Exception as e:
        logger.exception(f'Бот столкнулся с ошибкой: {e}')
        send_message(f'Бот столкнулся с ошибкой: {e}')


def check_response(response: list):
    """Валидация ответов API."""
    if 'error' in response:
        raise Exception()
    if type(response['homeworks']) != list:
        raise Exception(exceptions.HOMEWORK_LIST_ERROR)
    if 'error' in response.keys():
        raise Exception(exceptions.HOMEWORK_KEY_ERROR)
    if 'homeworks' not in response.keys():
        raise Exception(exceptions.HOMEWORK_KEY_ERROR)
    return response['homeworks']
    # Это должно работать, но ломает тесты
    # Продублировал суть в check_response_status
    """homework_list = response['homeworks']
    for homeworks in homework_list:
        if homeworks.get('status') in HOMEWORK_STATUSES.keys():
            return homework_list
        else:
            raise Exception(PARSE_STATUS_ERROR)
    return response['homeworks']"""


def check_response_status(homework: dict):
    """Дополнительная валидация ответов API."""
    if not isinstance(homework, dict):
        raise TypeError("Неожиданный ответ API, homework не dict")
    status = homework.get("status")
    homework_name = homework.get("homework_name")
    if not status or not homework_name:
        raise KeyError(exceptions.HOMEWORK_KEY_ERROR)
    if status not in HOMEWORK_STATUSES.keys():
        raise KeyError(exceptions.PARSE_STATUS_ERROR)
    return True


def parse_status(homework: dict):
    """статус конкретной ДЗ и проверка статусов."""
    check_response_status(homework)
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    # предыдущий код до применения check_response_status(homework)
    """if homework_status in HOMEWORK_STATUSES.keys():
        verdict = HOMEWORK_STATUSES.get(homework_status)
    else:
        raise ValueError(PARSE_STATUS_ERROR)"""
    """if homework_status not in HOMEWORK_STATUSES.keys():
        raise Exception(PARSE_STATUS_ERROR)"""
    if homework_status is None:
        raise Exception(exceptions.PARSE_STATUS_ERROR)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка сетевого окружения."""
    if PRACTICUM_TOKEN is None:
        return False
    elif TELEGRAM_TOKEN is None:
        return False
    elif TELEGRAM_CHAT_ID is None:
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""
    logger.debug('Запуск бота')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            api_answer = get_api_answer(current_timestamp)
            result = check_response(api_answer)
            if result:
                for homework in result:
                    parse_status_result = parse_status(homework)
                    send_message(bot, parse_status_result)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error('Bot down')
            bot.send_message(
                chat_id=TELEGRAM_CHAT_ID, text=message
            )
            time.sleep(RETRY_TIME)
            continue


if __name__ == '__main__':
    main()
