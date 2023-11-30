import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types.message import ContentType
import logging
import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

PRICE = types.LabeledPrice(label='подписка на 1 месяц', amount=150 * 100)


def send_notification_to_email(payment_info, user_name, user_email, telegram_link):
    subject = "Успешная оплата"
    body = f"Пользователь {user_name} ({user_email}, {telegram_link}) совершил успешную оплату. Сумма: {payment_info['total_amount'] / 100} рублей."

    from_email = "vinogradovdima557@gmail.com"
    password = "kjsv kdzo cxxw sviz"
    to_email = "vinogradovdima557@gmail.com"

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, password)

            server.sendmail(from_email, to_email, message.as_string())

        print("Уведомление успешно отправлено на почту.")
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")


@dp.message_handler()
async def start(message: types.Message):
    if config.PAY_TOKEN and ':' in config.PAY_TOKEN:
        if config.PAY_TOKEN.split(':')[1] == 'TEST':
            await bot.send_message(message.chat.id, 'Тестовый платёж')

        await bot.send_invoice(
            message.chat.id,
            title='Подписка на бота',
            description='активация подписки на бота',
            provider_token=config.PAY_TOKEN,
            currency='rub',
            prices=[PRICE],
            start_parameter='test-invoice',
            payload='test-invoice-payload',
            is_flexible=False
        )
    else:
        await bot.send_message(message.chat.id, 'Неверный формат PAY_TOKEN')


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("Succesful payment: ")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    user_name = message.from_user.full_name
    user_email = message.from_user.username
    telegram_link = f"https://t.me/{user_email}"

    send_notification_to_email(
        payment_info, user_name, user_email, telegram_link)

    await bot.send_message(message.chat.id, 'Спасибо за покупку!')


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
