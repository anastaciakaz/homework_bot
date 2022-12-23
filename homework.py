import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (EndPointIsNotReached, HTTPStatusCodeNotCorrect,
                        TelegramMessageError, UnknownStatus)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logger.debug(
            f'Отправка сообщения в чат {TELEGRAM_CHAT_ID}: {message}.'
        )
        bot.send_message(TELEGRAM_CHAT_ID, message)

    except telegram.error.TelegramError as error:
        mes_error = f'Ошибка при отправке сообщения {error}'
        logger.error(mes_error)
        raise TelegramMessageError(mes_error)
    else:
        logger.debug(f'Сообщение {message} отправлено')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timehomework = timestamp or int(time.time)
    payload = {'from_date': timehomework}
    params_dict = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': payload
    }
    try:
        logger.info('Начало запроса к эндпоинту API')
        homework = requests.get(**params_dict)
        logger.info('Отправлен запрос к эндпоинту API')
        if homework.status_code != HTTPStatus.OK:
            status_code_error = (
                f'Не удалось получить API, код ошибки: {homework.status_code}'
            )
            logger.error(status_code_error)
            raise HTTPStatusCodeNotCorrect(status_code_error)
        return homework.json()
    except requests.exceptions.RequestException as error:
        endpoint_error = f'Ошибка при запросе к эндпоинту {error}'
        logger.error(endpoint_error)
        raise EndPointIsNotReached(endpoint_error)


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logger.info('Проверка ответа API')
    if not isinstance(response, dict):
        API_not_dict = 'Ответ API не является словарём'
        logger.error(API_not_dict)
        raise TypeError(API_not_dict)
    if 'homeworks' and 'current_date' not in response:
        wrong_keys = 'В ответе API отсутствуют необходимые ключи'
        logger.error(wrong_keys)
        raise KeyError(wrong_keys)
    homeworks = response.get('homeworks')
    timestamp = response.get('current_date')
    if not isinstance(homeworks, list):
        API_not_list = 'Ответ API не является списком'
        logger.error(API_not_list)
        raise TypeError(API_not_list)
    if isinstance(timestamp, int) and isinstance(homeworks, list):
        return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы."""
    logger.info('Проверка наличия ключей в ответе и извлечение статуса')
    if 'homework_name' not in homework:
        raise KeyError('Отсутствует ключ "homework_name" в ответе API')
    if 'status' not in homework:
        raise KeyError('Отсутствует ключ "status" в ответе API')
    homework_status = homework.get('status')
    homework_name = homework.get('homework_name')
    if homework_status not in HOMEWORK_VERDICTS:
        raise UnknownStatus('Статус не определён')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        no_variable = 'Отсутствует необходимая переменная окружения'
        logger.critical(no_variable)
        sys.exit(no_variable)
    else:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        timestamp = int(time.time())
        last_hw_status = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response['current_date']
            homeworks = check_response(response)
            if homeworks:
                hw_status = parse_status(homeworks[0])
                if hw_status != last_hw_status:
                    send_message(bot, hw_status)
                    last_hw_status = hw_status
                    logger.info('Сообщение отправлено')
            else:
                logger.debug('Статус домашки не изменился')
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)  # Надеюсь, что поняла замечание:)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
