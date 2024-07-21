import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from telegram.ext import ApplicationBuilder

# Вставьте сюда ваш Telegram токен
TELEGRAM_TOKEN = ''

# Вставьте сюда ваш API ключ для сервиса погоды, например, OpenWeatherMap
WEATHER_API_KEY = ''
CITY_NAME = ''

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_weather():
    url = f'http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={WEATHER_API_KEY}&units=metric&lang=ru'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        return f'Погода в {CITY_NAME}:\n\nОписание: {weather_description}\nТемпература: {temp}°C\nВлажность: {humidity}%\nСкорость ветра: {wind_speed} м/с'
    else:
        return 'Не удалось получить данные о погоде.'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я буду присылать тебе ежедневные обновления о погоде.')

async def send_daily_weather(application: Application) -> None:
    weather_info = get_weather()
    for chat_id in application.job_queue.get_jobs_by_name('daily_weather'):
        await application.bot.send_message(chat_id=chat_id.data, text=weather_info)

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Команда /start
    application.add_handler(CommandHandler("start", start))

    # Запуск планировщика
    scheduler = BackgroundScheduler()
    scheduler.start()

    # Добавление ежедневного задания на 9 утра по вашему местному времени
    scheduler.add_job(send_daily_weather, 'cron', hour=9, minute=0, args=[application], name='daily_weather')

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
