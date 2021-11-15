import os
import time
import logging
import requests
import telegram
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from exceptions import *

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



def send_message(message, bot_client):
    logger.info('Отправка {message} для {TELEGRAM_CHAT_ID}')
    try:
        new_massage = bot_client.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as sending_error:
        logging.error(MESSAGE_ERROR.format(error=sending_error))
    return new_massage


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            params=params,
            headers=headers,
        )
        if homework_statuses.status_code == 200:
            return homework_statuses.json()
        else:
            raise Exception(SERVER_PROBLEMS)
    except Exception as e:
        logger.exception(f'Бот столкнулся с ошибкой: {e}')
        send_message(f'Бот столкнулся с ошибкой: {e}')
    


def check_response(response):
    if error in response:
        raise Exception(
            f'{response:{error}}'
        )
    if type(response['homeworks']) != list:
        raise Exception(HOMEWORK_LIST_ERROR)  
    if error in response.keys():
        raise Exception(HOMEWORK_KEY_ERROR)
    if 'homeworks' not in response.keys():
        raise Exception(HOMEWORK_KEY_ERROR)
    if not isinstance(response['homeworks'], list):
        raise Exception(HOMEWORK_LIST_ERROR)
    return response['homeworks']


def parse_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if homework_name is None:
        raise Exception(HOMEWORK_KEY_ERROR)
    if homework_status not in HOMEWORK_STATUSES.keys():
        raise Exception(PARSE_STATUS_ERROR)
    if homework_status is None:
        raise Exception(PARSE_STATUS_ERROR)
    if homework_status == 'reviewing':
        return verdict
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    ...


def main():
    """Основная логика работы бота."""
    logger.debug('Запуск бота')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
