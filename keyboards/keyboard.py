from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="🧑‍🏫 Преподаватели"),
        KeyboardButton(text="📅 Расписание"),
        KeyboardButton(text="➕ Уведомления")
    ],
    [
        KeyboardButton(text="✅ Отметиться"),
        KeyboardButton(text="📄 Посещаемость")
    ],
    [
        KeyboardButton(text="🔄 Обновление информации")
    ]
],
    one_time_keyboard=False,
    input_field_placeholder="Выберите нужную вам функцию!",
    resize_keyboard=True
)
attach = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="💢 Меня не будет"),
        KeyboardButton(text="✅ Я пришел")
    ],
    [
        KeyboardButton(text="💠 Свой вариант")
    ],
    [
        KeyboardButton(text="🔙 Обратно")
    ]
],
    one_time_keyboard=False,
    input_field_placeholder="Выберите нужный вам вариант!",
    resize_keyboard=True
)

attendance = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="🌑 Вчера"),
        KeyboardButton(text="☀️ Сегодня"),
        KeyboardButton(text="🌙 Завтра")
    ],
    [
        KeyboardButton(text="🔙 Обратно")
    ]
],
    one_time_keyboard=False,
    input_field_placeholder="Выберите нужный вам вариант!",
    resize_keyboard=True
)

teachers = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="БИОЛОГИЯ"),
        KeyboardButton(text="ХИМИЯ"),
        KeyboardButton(text="ВВЕДЕНИЕ В ПРОФЕССИЮ")
    ],
    [
        KeyboardButton(text="ГЕОГРАФИЯ"),
        KeyboardButton(text="ИНОСТРАННЫЙ ЯЗЫК"),
        KeyboardButton(text="ИНФОРМАТИКА")
    ],
    [
        KeyboardButton(text="ИСТОРИЯ"),
        KeyboardButton(text="ЛИТЕРАТУРА"),
        KeyboardButton(text="МАТЕМАТИКА")
    ],
    [
        KeyboardButton(text="ОБЩЕСТВОЗНАНИЕ"),
        KeyboardButton(text="РОДНАЯ ЛИТЕРАТУРА")
    ],
    [
        KeyboardButton(text="РУССКИЙ ЯЗЫК"),
        KeyboardButton(text="ФИЗИКА"),
        KeyboardButton(text="ФИЗИЧЕСКАЯ КУЛЬТУРА")
    ],
    [
        KeyboardButton(text="ВВЕДЕНИЕ В ПРОЕКТНУЮ ДЕЯТЕЛЬНОСТЬ"),
    ],
    [
        KeyboardButton(text="ОСНОВЫ БЕЗОПАСНОСТИ И ЗАЩИТЫ РОДИНЫ"),
    ],
    [
        KeyboardButton(text="🔙 Обратно"),
    ]
],
    one_time_keyboard=False,
    input_field_placeholder="Выберите нужный предмет!",
    resize_keyboard=True
)

schedule = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="🕛 Сегодня"),
        KeyboardButton(text="🕐 Завтра"),
        KeyboardButton(text="📄 Вся текущая неделя")
    ],
    [
        KeyboardButton(text="🔙 Обратно")
    ]
],
    one_time_keyboard=False,
    input_field_placeholder="Выберите нужную вам дату!",
    resize_keyboard=True
)

notification = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="🕛 За 30 минут"),
        KeyboardButton(text="🕐 За 1 час"),
        KeyboardButton(text="🕑 За 1.5 часа"),
        KeyboardButton(text="🕒 За 2 часа")
    ],
    [
        KeyboardButton(text="⛔ Выключить")
    ],
    [
        KeyboardButton(text="🔙 Обратно")
    ]
],
    one_time_keyboard=False,
    input_field_placeholder="Выберите нужное количество времени!",
    resize_keyboard=True
)

auth = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="✅ Авторизоваться")
    ],
    [
        KeyboardButton(text="🔙 Обратно")
    ]
],
    one_time_keyboard=False,
    input_field_placeholder="Выберете нужный вариант.",
    resize_keyboard=True
)

update = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄️ Обновить",callback_data="update yes")],[InlineKeyboardButton(text="⛔ Отказ",callback_data="update no")]])