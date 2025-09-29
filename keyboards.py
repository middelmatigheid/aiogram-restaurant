# Aiogram inline keyboard
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Python files
import database as db


# Profile keyboard
async def profile():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Номер телефона', callback_data='profile phone'))
    markup.row(InlineKeyboardButton(text='Адрес доставки', callback_data='profile address'))
    markup.row(InlineKeyboardButton(text='Мои заказы', callback_data='my orders'))
    return markup.as_markup()


# Cart keyboard
async def cart(user_cart):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    # Processing positions
    for position_id in set(user_cart.split()):
        position = await db.get_menu_position(position_id)
        markup.row(InlineKeyboardButton(text=f'{position["menu_position_name"]} {user_cart.split().count(position_id)}шт. {user_cart.split().count(position_id) * position["menu_position_price"]} руб', callback_data=f'position {position_id}'))
    markup.row(InlineKeyboardButton(text='Заказать', callback_data='order'))
    return markup.as_markup()


# Need call keyboard
async def need_call():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Да', callback_data=f'need call True'), InlineKeyboardButton(text='Нет', callback_data=f'need call False'))
    return markup.as_markup()


# Payment method keyboard
async def payment_method():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Картой онлайн', callback_data=f'pay online'))
    markup.row(InlineKeyboardButton(text='Картой курьеру', callback_data=f'pay by card'))
    markup.row(InlineKeyboardButton(text='Наличными курьеру', callback_data=f'pay by cash'))
    return markup.as_markup()


# Pay online keyboard
async def pay_online(price):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text=f'Оплатить {price // 100} руб', pay=True))
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Выбрать другой способ', callback_data=f'order'))
    return markup.as_markup()


# Operator's keyboard
async def operator(order_id, step):
    markup = InlineKeyboardBuilder()
    if step == 'processing':
        markup.row(InlineKeyboardButton(text='Подтвердить заказ', callback_data=f'order confirm {order_id}'))
        markup.row(InlineKeyboardButton(text='Отменить заказ', callback_data=f'order decline {order_id}'))
    elif step == 'done':
        markup.row(InlineKeyboardButton(text='Добавить примечание', callback_data=f'order note {order_id}'))
    else:
        markup.row(InlineKeyboardButton(text='Начать обрабатывать', callback_data=f'order processing {order_id}'))
    return markup.as_markup()


# Admin keyboard
async def admin():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Очистить стоп-лист', callback_data='clear stop-list'))
    markup.row(InlineKeyboardButton(text='Список администраторов', callback_data='staff list admin'))
    markup.row(InlineKeyboardButton(text='Список операторов', callback_data='staff list operator'))
    markup.row(InlineKeyboardButton(text='Список кухни', callback_data='staff list kitchen'))
    return markup.as_markup()


# Staff list keyboard
async def staff_list(staff_position):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    staff_arr = await db.get_staff_by_position(staff_position)
    if staff_arr:
        for x in staff_arr:
            markup.row(InlineKeyboardButton(text=x['staff_name'], callback_data=f'staff {x["staff_login"]}'))
    if staff_position == 'admin':
        markup.row(InlineKeyboardButton(text='Добавить нового администратора', callback_data='add staff admin'))
    elif staff_position == 'operator':
        markup.row(InlineKeyboardButton(text='Добавить нового оператора', callback_data='add staff operator'))
    elif staff_position == 'kitchen':
        markup.row(InlineKeyboardButton(text='Добавить нового члена кухни', callback_data='add staff kitchen'))
    else:
        markup.row(InlineKeyboardButton(text=f'Добавить нового {staff_position}', callback_data=f'add staff {staff_position}'))
    markup.row(InlineKeyboardButton(text='Вернуться в панель администрирования', callback_data=f'admin panel'))
    return markup.as_markup()


# Staff keyboard
async def staff(staff_login, staff_position):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Редактировать имя персонала', callback_data=f'edit staff name {staff_login}'))
    markup.row(InlineKeyboardButton(text='Удалить персонал', callback_data=f'delete staff {staff_login}'))
    markup.row(InlineKeyboardButton(text='Вернуться к списку', callback_data=f'staff list {staff_position}'))
    return markup.as_markup()


# Delete staff keyboard
async def delete_staff(staff_login, staff_position):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Да', callback_data=f'yes delete staff {staff_login}'), InlineKeyboardButton(text='Нет', callback_data=f'staff {staff_login}'))
    markup.row(InlineKeyboardButton(text='Вернуться к списку', callback_data=f'staff list {staff_position}'))
    return markup.as_markup()


# Main menu keyboard
async def main_menu():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    return markup.as_markup()


# Menu keyboard
async def menu(admin_boolean):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    menu_sections = await db.get_menu_sections()
    if menu_sections:
        for x in menu_sections:
            markup.row(InlineKeyboardButton(text=x['menu_section_name'], callback_data=f'section {x["menu_section_id"]}'))
    if admin_boolean:
        markup.row(InlineKeyboardButton(text='Панель администрирования', callback_data=f'admin panel'))
        markup.row(InlineKeyboardButton(text='Редактировать логотип', callback_data=f'edit logo'))
        markup.row(InlineKeyboardButton(text='Добавить новый раздел', callback_data=f'add section'))
        markup.row(InlineKeyboardButton(text='Редактировать название раздела', callback_data=f'edit section'))
        markup.row(InlineKeyboardButton(text='Удалить раздел', callback_data=f'delete section'))
    return markup.as_markup()


# Section keyboard
async def menu_section(data, section_id, admin_boolean=False):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    # Section stores subsections
    if data and data[0] == 'menu subsections':
        subsections = data[1]
        for subsection in subsections:
            markup.row(InlineKeyboardButton(text=subsection['menu_subsection_name'], callback_data=f'subsection {subsection["menu_subsection_id"]}'))
        if admin_boolean:
            markup.row(InlineKeyboardButton(text='Редактировать фото раздела', callback_data=f'edit photo section {section_id}'))
            markup.row(InlineKeyboardButton(text='Добавить новый подраздел', callback_data=f'add subsection section {section_id}'))
            markup.row(InlineKeyboardButton(text='Редактировать подраздел', callback_data=f'edit subsection section {section_id}'))
            markup.row(InlineKeyboardButton(text='Удалить подраздел', callback_data=f'delete subsection section {section_id}'))
    # Section stores positions
    elif data and data[0] == 'menu positions':
        positions = data[1]
        for position in positions:
            markup.row(InlineKeyboardButton(text=position['menu_position_name'], callback_data=f'position {position["menu_position_id"]}'))
        if admin_boolean:
            markup.row(InlineKeyboardButton(text='Редактировать фото раздела', callback_data=f'edit photo section {section_id}'))
            markup.row(InlineKeyboardButton(text='Добавить новую позицию', callback_data=f'add position section {section_id}'))
    # Empty section
    elif admin_boolean:
        markup.row(InlineKeyboardButton(text='Редактировать фото раздела', callback_data=f'edit photo section {section_id}'))
        markup.row(InlineKeyboardButton(text='Добавить новый подраздел', callback_data=f'add subsection section {section_id}'))
        markup.row(InlineKeyboardButton(text='Добавить новую позицию', callback_data=f'add position section {section_id}'))
    markup.row(InlineKeyboardButton(text='Вернуться в меню', callback_data='main menu'))
    return markup.as_markup()


# Delete section keyboard
async def delete_section(menu_section_id):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Да', callback_data=f'yes delete section {menu_section_id}'), InlineKeyboardButton(text='Нет', callback_data=f'main menu'))
    return markup.as_markup()


# Subsection keyboard
async def menu_subsection(positions, section_id, subsection_id, admin_boolean=False):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    for position in positions:
        markup.row(InlineKeyboardButton(text=position['menu_position_name'], callback_data=f'position {position["menu_position_id"]}'))
    if admin_boolean:
        markup.row( InlineKeyboardButton(text='Редактировать фото подраздела', callback_data=f'edit photo subsection {subsection_id}'))
        markup.row(InlineKeyboardButton(text='Добавить новую позицию', callback_data=f'add position subsection {subsection_id}'))
    markup.row(InlineKeyboardButton(text='Вернуться в раздел', callback_data=f'section {section_id}'))
    return markup.as_markup()


# Delete subsection keyboard
async def delete_subsection(menu_subsection_id, menu_section_id):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Да', callback_data=f'yes delete subsection {menu_subsection_id}'), InlineKeyboardButton(text='Нет', callback_data=f'section {menu_section_id}'))
    return markup.as_markup()


# Position keyboard
async def menu_position(position_id, position_amount, back_to, admin_boolean=False):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'),  InlineKeyboardButton(text='Корзина', callback_data='cart'))
    if position_amount == 0 and int(position_id) not in await db.get_stop_list():
        markup.row(InlineKeyboardButton(text='Добавить в корзину', callback_data=f'increase amount position {position_id}'))
    elif int(position_id) not in await db.get_stop_list():
        markup.row(InlineKeyboardButton(text='-', callback_data=f'decrease amount position {position_id}'), InlineKeyboardButton(text=str(position_amount), callback_data='None'), InlineKeyboardButton(text='+', callback_data=f'increase amount position {position_id}'))
    if admin_boolean and back_to != 'cart':
        if int(position_id) not in await db.get_stop_list():
            markup.row(InlineKeyboardButton(text='Добавить в стоп-лист', callback_data=f'add stop-list position {position_id}'))
        else:
            markup.row(InlineKeyboardButton(text='Удалить из стоп-листа', callback_data=f'remove stop-list position {position_id}'))
        markup.row(InlineKeyboardButton(text='Редактировать позицию', callback_data=f'edit position {position_id}'))
        markup.row(InlineKeyboardButton(text='Удалить позицию', callback_data=f'delete position {position_id}'))
    if back_to.split()[0] == 'section':
        markup.row(InlineKeyboardButton(text='Вернуться в раздел', callback_data=back_to))
    elif back_to.split()[0] == 'subsection':
        markup.row(InlineKeyboardButton(text='Вернуться в подраздел', callback_data=back_to))
    else:
        markup.row(InlineKeyboardButton(text='Вернуться в корзину', callback_data=back_to))
    return markup.as_markup()


# Edit position keyboard
async def edit_menu_position(position_id, admin_boolean=False):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'),  InlineKeyboardButton(text='Корзина', callback_data='cart'))
    if admin_boolean:
        markup.row(InlineKeyboardButton(text='Сохранить прежнее', callback_data=f'keep prev position {position_id}'))
        markup.row(InlineKeyboardButton(text='Удалить позицию', callback_data=f'delete position price {position_id}'))
    markup.row(InlineKeyboardButton(text='Вернуться к позиции', callback_data=f'position {position_id}'))
    return markup.as_markup()


# Delete position keyboard
async def delete_position(menu_position_id):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Главное меню', callback_data='main menu'))
    markup.row(InlineKeyboardButton(text='Профиль', callback_data='profile'), InlineKeyboardButton(text='Корзина', callback_data='cart'))
    markup.row(InlineKeyboardButton(text='Да', callback_data=f'yes delete position {menu_position_id}'), InlineKeyboardButton(text='Нет', callback_data=f'position {menu_position_id}'))
    return markup.as_markup()
