import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    try:
        homework_name = homework['homework_name']
        current_homework_status = homework['status']
    except KeyError:
        logging.exception('Cant get homework status')
        return 'Возникла ошибка'
    homework_statuses = {
        'rejected': f'У вас проверили работу "{homework_name}"!\n\n'
                    f'К сожалению в работе нашлись ошибки.',
        'approved': f'У вас проверили работу "{homework_name}"!\n\n'
                    f'Ревьюеру всё понравилось, '
                    f'можно приступать к следующему уроку.',
        'reviewing': 'Работу взяли на проверку'
    }
    if current_homework_status in homework_statuses:
        return f'{homework_statuses[current_homework_status]}'
    else:
        logging.exception('Cant get homework status')


def get_homework_statuses(current_timestamp):
    homework_statuses = {}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    headers = {
        'Authorization': f'OAuth {PRAKTIKUM_TOKEN}',
    }
    params = {
        'from_date': current_timestamp
    }
    URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    try:
        homework_statuses = requests.get(URL, headers=headers, params=params)
    except requests.RequestException:
        return {}
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)  # проинициализировать бота здесь
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot)
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
