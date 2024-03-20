import os
import requests
import time
import logging
import random
from telegram.ext import Updater, CommandHandler

API_URL = 'https://api.telegram.org/'
API_CATS_URL = 'https://api.thecatapi.com/v1/images/search'
API_DOGS_URL = 'https://random.dog/woof.json'
ERROR_MESSAGE = 'Sorry, I could not send the image.'

log_filename = '/home/MrEwrin/mybot.log'
logging.basicConfig(filename=log_filename, level=logging.INFO)


def get_random_image(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data[0].get('url')
        elif isinstance(data, dict):
            return data.get('url')
        else:
            logging.warning("Unexpected response format. Unable to extract image URL.")
            return None
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while fetching the image: {http_err}")
        return None
    except requests.exceptions.JSONDecodeError as json_err:
        logging.error(f"JSON decoding error occurred while parsing the response: {json_err}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching the image: {e}")
        return None


def send_image(chat_id, image_url, bot_token):
    try:
        url = f"{API_URL}bot{bot_token}/sendPhoto"
        if image_url.endswith('.gif'):
            url = f"{API_URL}bot{bot_token}/sendAnimation"
        payload = {'chat_id': chat_id, 'animation' if image_url.endswith('.gif') else 'photo': image_url}
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 429:
            logging.warning("Too many requests. Waiting before retrying...")
            time.sleep(random.uniform(5, 10))
            send_image(chat_id, image_url, bot_token)
        else:
            logging.error(f"HTTP error occurred while sending the image: {http_err}")
    except Exception as e:
        logging.error(f"An error occurred while sending the image: {e}")


def pic(update, context):
    print("Received /pic command")  # Добавим отладочный вывод
    if random.choice([True, False]):  # случайный выбор между True (кошки) и False (собаки)
        api_url = API_CATS_URL
    else:
        api_url = API_DOGS_URL
    random_pic = get_random_image(api_url)
    if random_pic is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=ERROR_MESSAGE)
    else:
        print(f"Sending image: {random_pic}")  # Добавим отладочный вывод
        send_image(update.effective_chat.id, random_pic, os.environ.get('BOT_TOKEN'))


def def_main():
    updater = Updater(os.environ.get('BOT_TOKEN'))
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("pic", pic))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    print("Starting bot...")  # Добавим отладочный вывод
    def_main()
