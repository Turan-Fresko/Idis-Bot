import asyncio
import json
import logging
import random
import sys
import time
import mongo
import datetime
import IdisApi

import dotenv
from aiogram import Bot, Dispatcher,F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from keyboards import keyboard
from aiogram.client.bot import DefaultBotProperties
from aiogram.utils.markdown import hbold
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

__api_token = dotenv.get_key(".env",key_to_get="TOKEN")

dp = Dispatcher()
bot = Bot(__api_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
cll = mongo.get_client()
notification = cll.Telegram.Notifications
users = cll.Telegram.Auths
attendance = cll.Telegram.Attendance

OWNER_ID = 5482163475
CHANNEL_ID = -1002302401336

def find_lesson(name:str, data:list) -> dict:
    for item in data:
        if item["name"] == name:
            return item
    return None

class AuthUser(StatesGroup):
    FullName = State()

class AttachReason(StatesGroup):
    reason = State()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте :)", reply_markup=keyboard.auth)
    await message.answer("Привет!\nВыбери нужную кнопочку!💫\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=keyboard.main)

@dp.message(F.text == 'Привет')
async def hello(message:Message):
    await message.reply("Привет дорогой! 🌺")

@dp.message(F.text == 'Доброе утро всем')
async def happyday(message:Message):
    await message.reply("Доброе! ☀️")

@dp.message(F.text == '✅ Авторизоваться')
async def auth_bot(message:Message, state:FSMContext):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 1:
        return await message.reply("✅ Вы уже авторизованы!")
    try:
        member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if not member.status in ['member', 'administrator', 'creator']: return await message.reply("💢 Ошибка, вы не находитесь в группе с одногруппниками.")
        await message.reply("💠 Введите свое ФИО, информация будет просматриваться куратором.\nПример: Фамилия Имя Отчество",reply_markup=ReplyKeyboardRemove())
        await state.set_state(AuthUser.FullName)
    except Exception as e:
        await message.reply("💢 Ошибка, обратитесь к владельцу бота.")

@dp.message(AuthUser.FullName)
async def auth_userName(message:Message,state:FSMContext):
    await state.update_data(FullName=message.text)
    data = await state.get_data()
    await state.clear()
    if users.count_documents({"user":message.from_user.id}) == 0:
        users.insert_one({"user":message.from_user.id,"tag": message.from_user.username, "fullname": data['FullName'],'lvl':1})
    await message.reply(f"✅ Успешная авторизация.\n☀️Доброго времени суток <b>{data['FullName']}</b>!",reply_markup=keyboard.main)

@dp.message(F.text == '🧑‍🏫 Преподаватели')
async def teachers(message:Message):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    await message.reply("💢 Выберете нужный предмет для вывода информации.",reply_markup=keyboard.teachers)

@dp.message(F.text.in_([
    "БИОЛОГИЯ", "ХИМИЯ", "ВВЕДЕНИЕ В ПРОФЕССИЮ", "ГЕОГРАФИЯ", 
    "ИНОСТРАННЫЙ ЯЗЫК", "ИНФОРМАТИКА", "ИСТОРИЯ", "ЛИТЕРАТУРА", 
    "МАТЕМАТИКА", "ОБЩЕСТВОЗНАНИЕ", "РОДНАЯ ЛИТЕРАТУРА", 
    "РУССКИЙ ЯЗЫК", "ФИЗИКА", "ФИЗИЧЕСКАЯ КУЛЬТУРА", 
    "ВВЕДЕНИЕ В ПРОЕКТНУЮ ДЕЯТЕЛЬНОСТЬ", "ОСНОВЫ БЕЗОПАСНОСТИ И ЗАЩИТЫ РОДИНЫ", 
    "🔙 Обратно"
]))
async def handle_teacher_selection(message: Message):
    if message.text == "🔙 Обратно":
        if message.from_user.id != message.chat.id:
            return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
        if users.count_documents({"user":message.from_user.id}) == 0:
            return await message.answer("💢 Тебе нужно сначала авторизоваться в боте!",reply_markup=keyboard.auth)
        await message.reply("Выбери нужную кнопочку!💫", reply_markup=keyboard.main)
    else:
        try:
            teachers_array = IdisApi.get_last_teachers()
            info = find_lesson(message.text,teachers_array['teachers'])
            text = f"📕 Информация по предмету {hbold(info['name'])}\n\n"
            for a in info["lessons"]:
                text += f"• {a['title']} <a href='{a['href']}'>{a['teacher']}</a>\n\n"
            current_time = datetime.datetime.now()
            last_update = datetime.datetime.strptime(teachers_array['last'], "%d/%m/%Y, %H:%M:%S")
            time_difference = current_time - last_update
            minutes_ago = time_difference.total_seconds() // 60
            if minutes_ago < 1: output = "Менее минуты назад."
            elif minutes_ago == 1: output = "1 минуту назад."
            else: output = f"{int(minutes_ago)} минут назад."
            text += f"⚠️ Последнее обновление информации в системе: {hbold(output)}"
            await message.reply(text) # 📄
        except Exception as err:
            await bot.send_message(OWNER_ID,f"💢 Ошибка!\n{err}")
            await message.reply("💢 Произошла ошибка при обработки данных. Уже передал администратору.")

@dp.message(F.text == '📅 Расписание')
async def teachers(message:Message):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    await message.reply("⌛ Выберете нужную дату для вывода информации.",reply_markup=keyboard.schedule)

async def get_schedule(last_message: Message,date1:str,date2:str):
    schedule_array = IdisApi.get_last_schedule(date1,date2)
    if not schedule_array[0]:
        await last_message.edit_text(f"⌛ Информация не найдена, обновляю список пар...\nЗаймет не более минуты..")
        response = IdisApi.update_all()
        await bot.send_message(OWNER_ID,f"💫 Принудительное обновление информации!\n\n❓Статус: {response[0]}\n⌛ Процессы:\n<pre><code class='language-json'>{json.dumps(response[1], indent=4, ensure_ascii=False)}</code></pre>")
        if not response[0]:
            await bot.send_message(OWNER_ID,f"💢 Ошибка!\n{response[1]}")
            await last_message.edit_text(f"⚠️ Произошла ошибка при обновлении информации.\nИнформация была отправлена администратору.")
            return None
        schedule_array = IdisApi.get_last_schedule(date1,date2)
    text = ""
    if date1 == date2: text = f"📊 Расписание пар на {hbold(date1)}\n\n"
    else: text = f"📊 Расписание пар с {hbold(date1)} по {hbold(date2)}\n\n"
    number = 0
    for lesson in schedule_array[1]:
        if lesson['name'] == "Нету пар":
            text += f"☀️ Солнышно, на {hbold(lesson['date']['date'])} нету пар! Радуйся)\n\n"
            break
        number+=1
        link_comment = ""
        if lesson['comment'][:8] in ["https://", "http://"]:
            link_comment = f"<a href='{lesson['comment']}'>Ссылка от преподавателя</a>"
        else:
            link_comment = lesson['comment']
        text += f"☀️ Дата: {hbold(lesson['date']['week'])} - {hbold(lesson['date']['date'])}\n🔗 {hbold(lesson['time'])} - {lesson['name']}\n🏙️ Адрес: {hbold(lesson['place']['address'])}\n🚪 Аудитория: {hbold(lesson['place']['audience'])}\n💬 Коментарий: {link_comment}\n🧑‍🏫 Группы/Преподаватель: {hbold(lesson['teacher'])}\n\n"
    last_update = datetime.datetime.strptime(schedule_array[2], "%d/%m/%Y, %H:%M:%S")
    today = datetime.datetime.now()
    time_difference = today - last_update
    minutes_ago = time_difference.total_seconds() // 60
    if minutes_ago < 1: output = "Менее минуты назад."
    elif minutes_ago == 1: output = "1 минуту назад."
    else: output = f"{int(minutes_ago)} минут назад."
    text += f"📄 Всего: <b>{number} пар(а/ы)</b>\n"
    text += f"⚠️ Последнее обновление информации в системе: <b>{output}</b>"
    return text

@dp.message(F.text.in_(["🕛 Сегодня","🕐 Завтра","📄 Вся текущая неделя"]))
async def handle_schedule_selection(message: Message):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    last_message = await message.reply("⌛ Обработка...")
    today = datetime.datetime.now()
    if message.text == "🕛 Сегодня":
        date1 = date2 = today.strftime("%d.%m.%Y")
    elif message.text == "🕐 Завтра":
        tomorrow = today + datetime.timedelta(days=1)
        date1 = date2 = tomorrow.strftime("%d.%m.%Y")
    elif message.text == "📄 Вся текущая неделя":
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
        date1 = start_of_week.strftime("%d.%m.%Y")
        date2 = end_of_week.strftime("%d.%m.%Y")
    response = await get_schedule(last_message,date1,date2)
    if response == None: return
    await last_message.edit_text(text=response)

@dp.message(F.text.in_(["➕ Уведомления"]))
async def handle_notification(message: Message):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    if notification.count_documents({"user":message.from_user.id}) == 0:
        notification.insert_one({"user":message.from_user.id, "isOn": False, "type": 0,"onSend": datetime.datetime.now().strftime("%d.%m.%Y")})
    mass = notification.find_one({"user":message.from_user.id})
    if mass['isOn']: status = "Включены"
    else: status = "Отключены"
    text = f"❔ Состояние уведомлений: <b>{status}</b>"
    if mass['type'] == 1: clock = "30 минут"
    elif mass['type'] == 2: clock = "1 час"
    elif mass['type'] == 3: clock = "1.5 часа"
    else: clock = "2 часа"
    if mass['isOn']:
        text += f"\n\n🕑 Вас уведомляет о паре за <b>{clock}</b>!"
    else:
        text += f"\n\n💢 Выберете количество времени за сколько до пары оповестить!"
    await message.reply(text,reply_markup=keyboard.notification)

@dp.message(F.text.in_(["🕛 За 30 минут", "🕐 За 1 час", "🕑 За 1.5 часа","🕒 За 2 часа", "⛔ Выключить"]))
async def handle_notification_selection(message: Message):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    if message.text == "⛔ Выключить":
        notification.update_one({"user":message.from_user.id},{"$set": {"isOn": False}})
        await message.reply("✅ Вы успешно выключили уведомления!")
        return
    elif message.text == "🕛 За 30 минут": datetype = 1; clock = "30 минут"
    elif message.text == "🕐 За 1 час": datetype = 2; clock = "1 час"
    elif message.text == "🕑 За 1.5 часа": datetype = 3; clock = "1.5 часа"
    elif message.text == "🕒 За 2 часа": datetype = 4; clock = "2 часа"
    notification.update_one({"user":message.from_user.id},{"$set": {"isOn": True, "type": datetype}})
    await message.reply(f"✅ Теперь вас будет оповещать за <b>{clock}</b> до пары!")

@dp.message(F.text == '🔄 Обновление информации')
async def handle_update_info(message:Message):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    if message.from_user.id == OWNER_ID:
        response = IdisApi.update_all()
        await message.reply(f"💫 Принудительное обновление информации!\n\n❓Статус: {response[0]}\n⌛ Процессы:\n<pre><code class='language-json'>{json.dumps(response[1], indent=4, ensure_ascii=False)}</code></pre>")
        return
    teachers_array = IdisApi.get_last_teachers()
    current_time = datetime.datetime.now()
    last_update = datetime.datetime.strptime(teachers_array['last'], "%d/%m/%Y, %H:%M:%S")
    time_difference = current_time - last_update
    minutes_ago = time_difference.total_seconds() // 60
    if minutes_ago < 60:
        return await message.reply(f"💢 Информация актуальная, она была обновлена <b>{minutes_ago} минут назад.</b>")
    await bot.send_message(OWNER_ID,f"❔ Запрос на обновление информации!\n⌛ Информация была обновлена <b>{minutes_ago} минут назад.</b>.", reply_markup=keyboard.update)
    await message.reply("✅ Запрос на обновление информации отправлен.\nЖдём когда Туран подтвердит обновление информации.")

@dp.callback_query(F.data == 'update yes')
async def __update_callback(callback:CallbackQuery):
    await callback.answer("🔄️ Обновление информации...")
    response = IdisApi.update_all()
    await bot.send_message(OWNER_ID,f"💫 Принудительное обновление информации!\n\n❓Статус: {response[0]}\n⌛ Процессы:\n<pre><code class='language-json'>{json.dumps(response[1], indent=4, ensure_ascii=False)}</code></pre>")

@dp.callback_query(F.data == 'update no')
async def __updateNo_callback(callback:CallbackQuery):
    await callback.answer("⛔ Отмена..")
    await callback.message.delete()

@dp.message(F.text == "✅ Отметиться")
async def handle_attach(message:Message):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    await message.answer("☀️ Ты отмечаешься за сегодня.\n🔴 Давайте не будем подставлять нашего любимого старосту, пишите правду.\n😈 Вас все равно вас найдет староста, если не староста то - куратор.",reply_markup=keyboard.attach)

def add_attach(userid:int, date:str, reason: str) -> bool:
    count = attendance.count_documents({"user":userid,"date":date})
    if count >= 1:
        attendance.update_one({"user":userid,"date":date},{"$set":{"reason":reason}})
        return True
    else:
        attendance.insert_one({"user":userid,"date":date,"reason":reason})
        return False

@dp.message(F.text.in_(["💢 Меня не будет", "✅ Я пришел", "💠 Свой вариант"]))
async def handle_attach_vote(message:Message, state:FSMContext):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    vote = ""
    if message.text == "💠 Свой вариант":
        await message.reply("💠 Напиши свой вариант, что случилось.\nПример: Я на первой паре не буду.\n\n💢 Учти, что куратор все видит, не пишите бред.",reply_markup=ReplyKeyboardRemove())
        await state.set_state(AttachReason.reason)
        return
    elif message.text == "💢 Меня не будет":
        vote = '-'
    elif message.text == "✅ Я пришел":
        vote = '+'
    status = add_attach(message.from_user.id,today,vote)
    if status:
        await message.reply(f"💫 Вы успешно поменяли свой вариант на <b>{message.text}</b>")
    else:
        await message.reply(f"💫 Вы успешно отметились за сегодня.")

@dp.message(AttachReason.reason)
async def AttachReason_handle(message:Message,state:FSMContext):
    await state.update_data(reason=message.text)
    data = await state.get_data()
    await state.clear()
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    status = add_attach(message.from_user.id,today,data['reason'])
    if status:
        await message.reply(f"💫 Вы успешно поменяли свой вариант на <b>{data['reason']}</b>",reply_markup=keyboard.main)
    else:
        await message.reply(f"💫 Вы успешно отметились за сегодня.",reply_markup=keyboard.main)

@dp.message(F.text == '📄 Посещаемость')
async def handle_attendance(message:Message):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    await message.answer("💫 Выбери нужный вариант!",reply_markup=keyboard.attendance)

@dp.message(F.text.in_(["🌑 Вчера", "☀️ Сегодня", "🌙 Завтра"]))
async def handle_attendance_days(message:Message):
    if message.from_user.id != message.chat.id:
        return await message.answer("Привет, используй меня в личных сообщениях!\n\n💠 Команды:\n/start - Вызвать меню взаимодействия.\n/ping - Проверить состояние бота.\n/checkin - Отметиться на паре.\n/today - Посмотреть расписание на сегодня.\n/tomorrow - Посмотреть расписание на завтра.",reply_markup=ReplyKeyboardRemove())
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    today = datetime.datetime.now()
    if message.text == "🌑 Вчера": day = today - datetime.timedelta(days=1)
    elif message.text == "☀️ Сегодня": day = today
    elif message.text == "🌙 Завтра": day = today + datetime.timedelta(days=1)
    text = f"📊 Посещаемость за <b>{day.strftime('%d-%m-%Y')}</b>\n\n═══════════════════════════════\n\n"
    index = 0
    bad = 0
    steep = 0
    for student in users.find({}).sort('fullname', 1):
        index += 1
        if attendance.count_documents({'user':student['user'], 'date': day.strftime("%d-%m-%Y")}) == 0:
            bad += 1
            text += f"<u>[{index}]</u> <code>{student['fullname']}</code> | <b>- (Не отметился)</b>\n\n"
            continue
        mass = attendance.find_one({'user':student['user'], 'date': day.strftime("%d-%m-%Y")})
        if mass['reason'] == '-': bad += 1
        else: steep +=1
        text += f"<u>[{index}]</u> <code>{student['fullname']}</code> | <b>{mass['reason']}</b>\n\n"
    text += f"═══════════════════════════════\n\n➖ Всего плохишей: <b>{bad}</b>\n➕ Всего крутышей: <b>{steep}</b>"
    await message.reply(text)

@dp.message(Command('ping'))
async def ping(message:Message) -> None:
    start = time.time()
    sent_message = await message.answer("⌛ Секундочку...")
    end = time.time()
    await sent_message.edit_text(f"💠 Пинг: {end - start} секунд")

@dp.message(Command('checkin'))
async def checkin(message: Message) -> None:
    if message.from_user.id != message.chat.id and users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("Привет, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    args = message.text.split()[1:]
    reason = ' '.join(args)
    if reason == '':
        return await message.reply(f"🔴 Введите /checkin [ <b>+</b> | <b>-</b> | <b>Свой вариант</b> ]")
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    status = add_attach(message.from_user.id,today,reason)
    if status:
        await message.reply(f"💫 Вы успешно поменяли свой вариант на <b>{reason}</b>")
    else:
        await message.reply(f"💫 Вы успешно отметились за сегодня.")

@dp.message(Command('today'))
async def today(message: Message) -> None:
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    last_message = await message.reply("⌛ Обработка...")
    today = datetime.datetime.now()
    date1 = date2 = today.strftime("%d.%m.%Y")
    response = await get_schedule(last_message,date1,date2)
    if response == None: return
    await last_message.edit_text(text=response)

@dp.message(Command('tomorrow'))
async def today(message: Message) -> None:
    if users.count_documents({"user":message.from_user.id}) == 0:
        return await message.answer("💢 Тебе нужно сначала авторизоваться в боте, перейдите по моему профилю и нажмите личные сообщения, далее нажмите <b>Начать</b> или /start")
    last_message = await message.reply("⌛ Обработка...")
    today = datetime.datetime.now()+datetime.timedelta(days=1)
    date1 = date2 = today.strftime("%d.%m.%Y")
    response = await get_schedule(last_message,date1,date2)
    if response == None: return
    await last_message.edit_text(text=response)

@dp.message(Command('stat'))
async def stat(message: Message) -> None:
    if not message.from_user.id == OWNER_ID: return
    db = "Не известно!"
    try:
        cll.server_info()
        db = "Стабильно."
    except: db = "Соединение потеряно."
    await message.answer(f"Информация!\n\nСостояние базы данных: {hbold(db)}")

@dp.message(Command('id'))
async def id_channel(message: Message) -> None:
    if not message.from_user.id == OWNER_ID: return
    await message.reply(f"📊 Chat ID: {message.chat.id}")

@dp.message(Command('all'))
async def all_mention(message: Message) -> None:
    author = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if not author.status in ['administrator', 'creator']: return await message.reply("💢 Ошибка, вы не можете использовать данную команду!")
    chat_members = []
    for member in users.find({}):
        chat_members.append(f"@{member['tag']}")
    
    await message.reply(f"💢 Упоминание всех пользователей.\n👥 Упомянул: @{author.user.username}\n\n" + " ".join(chat_members) + f"💠 Всего: <b>{len(chat_members)}</b>")

@dp.message(Command('qr'))
async def qr_send(message: Message) -> None:
    if not message.from_user.id == OWNER_ID: return
    qr = FSInputFile("/root/idisBot/image/QRCodeDisplay.png")
    if message.chat.id != OWNER_ID:
        await message.reply("💫 Отправил вам в личные сообщения.")
    await bot.send_photo(chat_id=OWNER_ID, photo=qr)

async def task_loop():
    while True:
        try:
            today = datetime.datetime.now()
            schedule_array = IdisApi.get_last_schedule(today.strftime("%d.%m.%Y"),today.strftime("%d.%m.%Y"))
            if not schedule_array[0]:
                response = IdisApi.update_all()
                await bot.send_message(OWNER_ID,f"💫 Принудительное обновление информации!\n\n❓Статус: {response[0]}\n⌛ Процессы:\n<pre><code class='language-json'>{json.dumps(response[1], indent=4, ensure_ascii=False)}</code></pre>")
                if not response[0]:
                    await bot.send_message(OWNER_ID,f"💢 Ошибка!\n{response[1]}")
            lesson = schedule_array[1][0]
            if not lesson['name'] == "Нету пар":
                time_onepar = (str(lesson['time']).split(" "))[0]
                lesson_time = datetime.datetime.strptime(f"{today.strftime('%d.%m.%Y')} {time_onepar}", "%d.%m.%Y %H:%M")
                before_lesson = lesson_time - datetime.timedelta(minutes=5)
                last_befor_lesson = users.find_one({'user':OWNER_ID})['last_notif']
                links = []
                if (today >= before_lesson) and (last_befor_lesson != today.strftime("%d.%m.%Y")):
                    for student in users.find({}).sort('fullname', 1):
                        if attendance.count_documents({'user':student['user'], 'date': today.strftime("%d-%m-%Y")}) == 0:
                            links.append(f"@{student['tag']}")
                    text = f"💢 Осталось 5 минут до пары.\n\n{' '.join(links)}\n\nВам нужно отметиться, что бы быстро отметиться:\n/checkin [ <b>+</b> | <b>-</b> | <b>Свой вариант</b> ]"
                    await bot.send_message(CHANNEL_ID,text=text)
                    users.update_one({'user':OWNER_ID},{"$set":{'last_notif':today.strftime("%d.%m.%Y")}})
                for user in notification.find({"isOn": True}):
                    if not user["onSend"] == today.strftime("%d.%m.%Y"):
                        notification_time = lesson_time - datetime.timedelta(minutes=30*user["type"])
                        if today >= notification_time:
                            try:
                                last_update = datetime.datetime.strptime(schedule_array[2], "%d/%m/%Y, %H:%M:%S")
                                time_difference = today - last_update
                                minutes_ago = time_difference.total_seconds() // 60
                                if minutes_ago < 1: output = "Менее минуты назад."
                                elif minutes_ago == 1: output = "1 минуту назад."
                                else: output = f"{int(minutes_ago)} минут назад."
                                await bot.send_message(user['user'],f"☀️ Солнышко пора на пару!\n\n💫 Дата: {hbold(lesson['date']['week'])} - {hbold(lesson['date']['date'])}\n🔗 {hbold(lesson['time'])} - {lesson['name']}\n🏙️ Адресс: {hbold(lesson['place']['address'])}\n🚪 Аудитория: {hbold(lesson['place']['audience'])}\n🧑‍🏫 Группы/Преподаватель: {hbold(lesson['teacher'])}\n\n⚠️ Последнее обновление информации в системе: {hbold(output)}")
                                notification.update_one({"user": user['user']},{"$set": {"onSend": today.strftime("%d.%m.%Y")}})
                            except: continue
        except Exception as err:
            print(err)
        await asyncio.sleep(10)

async def main() -> None:
    asyncio.create_task(task_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())