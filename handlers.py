# Dotenv
import os
from dotenv import load_dotenv

# Regular exp
import re

# Images
import datetime
import requests
import io
from PIL import Image

# Aiogram
from aiogram import F, Router
from aiogram.types import Message, InputMediaPhoto, FSInputFile, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command

# Python files
import database as db
import keyboards as kb


# Loading .env file
load_dotenv()


# Uri for downloading telegram's images
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')
TOKEN = os.getenv('BOT_TOKEN')
uri = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id='
uri_img = f'https://api.telegram.org/file/bot{TOKEN}/'
# Creating router to process messages
router = Router()


# Admin panel
@router.message(Command('admin'))
async def cmd_admin(message: Message):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(message.chat.id)
    if user is None:
        await db.add_user(message.chat.id)
    user = await db.get_user_by_telegram_id(message.chat.id)

    await db.update_user_step(message.chat.id, '')
    if 'admin' in user['staff_positions']:
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Выберите действие, чтобы продолжить', reply_markup=await kb.admin())
    else:
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот', reply_markup=await kb.menu('admin' in user['staff_positions']))


# Processing login
@router.message(Command('login'))
async def cmd_login(message: Message):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(message.chat.id)
    if user is None:
        await db.add_user(message.chat.id)
    user = await db.get_user_by_telegram_id(message.chat.id)

    await db.update_user_step(message.chat.id, 'login')
    await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Отправьте выданный логин', reply_markup=await kb.main_menu())


# Processing logout
@router.message(Command('logout'))
async def cmd_logout(message: Message):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(message.chat.id)
    if user is None:
        await db.add_user(message.chat.id)
    user = await db.get_user_by_telegram_id(message.chat.id)

    await db.update_user_step(message.chat.id, '')
    await db.staff_logout(message.chat.id)
    if len(user['staff_positions']) == 0:
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот', reply_markup=await kb.menu('admin' in user['staff_positions']))
    else:
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Вы успешно вышли со всех аккаунтов персонала', reply_markup=await kb.main_menu())


# Processing command start
@router.message(Command('start'))
async def cmd_start(message: Message):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(message.chat.id)
    if user is None:
        await db.add_user(message.chat.id)
    user = await db.get_user_by_telegram_id(message.chat.id)

    await db.update_user_step(message.chat.id, '')
    await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот', reply_markup=await kb.menu('admin' in user['staff_positions']))


# Processing photo message
@router.message(F.photo)
async def photo(message: Message):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(message.chat.id)
    if user is None:
        await db.add_user(message.chat.id)
    user = await db.get_user_by_telegram_id(message.chat.id)

    # Adding position's photo
    if user['user_step'] == 'add position photo' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, f'add position description')
        # Saving image
        img_path = requests.get(uri + message.photo[-1].file_id).json()['result']['file_path']
        with Image.open(io.BytesIO(requests.get(uri_img + img_path).content)) as img:
            img.save(f'images/positions/{message.chat.id}.jpg')
        # Getting position from the database
        position = await db.get_new_menu_position(message.chat.id)
        # Position is located in a section
        if position['menu_subsection_id'] == 0:
            section = await db.get_menu_section(position['menu_section_id'])
            # Checking if the section has a photo
            if os.path.exists(f'images/sections/{position["menu_section_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/sections/{position["menu_section_id"]}.jpg'), caption=f'Отправьте описание новой позиции меню', reply_markup=await kb.menu_section(section, user['user_step'].split()[-1]))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте описание новой позиции меню', reply_markup=await kb.menu_section(section, user['user_step'].split()[-1]))
        # Position is located in a subsection
        else:
            subsection = await db.get_menu_subsection(position['menu_subsection_id'])
            # Checking if the subsection has a photo
            if os.path.exists(f'images/subsections/{position["menu_subsection_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/subsections/{position["menu_subsection_id"]}.jpg'), caption=f'Отправьте описание новой позиции меню', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], user['user_step'].split()[-1]))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте описание новой позиции меню', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], user['user_step'].split()[-1]))

    # Editing logo
    elif user['user_step'] == 'edit logo' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        # Saving image
        img_path = requests.get(uri + message.photo[-1].file_id).json()['result']['file_path']
        with Image.open(io.BytesIO(requests.get(uri_img + img_path).content)) as img:
            img.save(f'images/logo.jpg')
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Логотип успешно изменен', reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Editing section's photo
    elif " ".join(user['user_step'].split()[:3]) == 'edit photo section' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        # Saving image
        img_path = requests.get(uri + message.photo[-1].file_id).json()['result']['file_path']
        with Image.open(io.BytesIO(requests.get(uri_img + img_path).content)) as img:
            img.save(f'images/sections/{user['user_step'].split()[-1]}.jpg')
        # Getting section from the database
        section_info = await db.get_menu_section_info(user['user_step'].split()[-1])
        await message.answer_photo(photo=FSInputFile(f'images/sections/{user['user_step'].split()[-1]}.jpg'), caption=f'Фотография раздела <b>{section_info["menu_section_name"]}</b> успешно изменена', reply_markup=await kb.menu_section(await db.get_menu_section(user['user_step'].split()[-1]), user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    # Editing subsection's photo
    elif " ".join(user['user_step'].split()[:3]) == 'edit photo subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        # Saving image
        img_path = requests.get(uri + message.photo[-1].file_id).json()['result']['file_path']
        with Image.open(io.BytesIO(requests.get(uri_img + img_path).content)) as img:
            img.save(f'images/subsections/{user['user_step'].split()[-1]}.jpg')
        # Getting subsection from the database
        subsection_info = await db.get_menu_subsection_info(user['user_step'].split()[-1])
        await message.answer_photo(photo=FSInputFile(f'images/subsections/{user['user_step'].split()[-1]}.jpg'), caption=f'Фотография подраздела <b>{subsection_info["menu_subsection_name"]}</b> успешно изменена', reply_markup=await kb.menu_subsection(await db.get_menu_subsection(user['user_step'].split()[-1]), user['user_step'].split()[-1], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))

    # Editing position's photo
    elif " ".join(user['user_step'].split()[:3]) == 'edit position photo' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, f'edit position desrciption {user["user_step"].split()[-1]}')
        # Saving image
        img_path = requests.get(uri + message.photo[-1].file_id).json()['result']['file_path']
        with Image.open(io.BytesIO(requests.get(uri_img + img_path).content)) as img:
            img.save(f'images/positions/{user['user_step'].split()[-1]}.jpg')
        # Getting position from the database
        position = await db.get_menu_position(user['user_step'].split()[-1])
        await message.answer_photo(photo=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новое описание позиции меню', reply_markup=await kb.edit_menu_position(user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    else:
        await db.update_user_step(message.chat.id, '')
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот', reply_markup=await kb.menu('admin' in user['staff_positions']))


# Processing file message
@router.message(F.document)
async def document(message: Message):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(message.chat.id)
    if user is None:
        await db.add_user(message.chat.id)
    user = await db.get_user_by_telegram_id(message.chat.id)

    # Adding position's photo
    if user['user_step'] == 'add position photo' and 'admin' in user['staff_positions']:
        position = await db.get_new_menu_position(message.chat.id)
        # Position is located in a section
        if position['menu_subsection_id'] == 0:
            section = await db.get_menu_section(position['menu_section_id'])
            # Checking if the section has a photo
            if os.path.exists(f'images/sections/{position["menu_section_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/sections/{position["menu_section_id"]}.jpg'), caption='Отправьте фотографию новой позиции меню, как изображение, не как файл', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Отправьте фотографию новой позиции меню, как изображение, не как файл', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
        # Position is located in a subsection
        else:
            subsection = await db.get_menu_subsection(position['menu_subsection_id'])
            # Checking if the subsection has a photo
            if os.path.exists(f'images/subsections/{position["menu_subsection_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/subsections/{position["menu_subsection_id"]}.jpg'), caption='Отправьте фотографию новой позиции меню, как изображение, не как файл', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Отправьте фотографию новой позиции меню, как изображение, не как файл', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))

    # Editing logo
    elif user['user_step'] == 'edit logo' and 'admin' in user['staff_positions']:
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Отправьте новый логотип, как изображение, не как файл', reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Editing section's photo
    elif " ".join(user['user_step'].split()[:3]) == 'edit photo section' and 'admin' in user['staff_positions']:
        section = await db.get_menu_section(user['user_step'].split()[-1])
        # Checking if the section has a photo
        if os.path.exists(f'images/subsections/{user['user_step'].split()[-1]}.jpg'):
            await message.answer_photo(photo=FSInputFile(f'images/subsections/{user['user_step'].split()[-1]}.jpg'), caption='Отправьте новую фотографию раздела меню, как изображение, не как файл', reply_markup=await kb.menu_section(section, user['user_step'].split()[-1], 'admin' in user['staff_positions']))
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Отправьте новую фотографию раздела меню, как изображение, не как файл', reply_markup=await kb.menu_section(section, user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    # Editing subsection's photo
    elif " ".join(user['user_step'].split()[:3]) == 'edit photo subsection' and 'admin' in user['staff_positions']:
        subsection = await db.get_menu_subsection(user['user_step'].split()[-1])
        subsection_info = await db.get_menu_subsection_info(user['user_step'].split()[-1])
        # Checking if the subsection has a photo
        if os.path.exists(f'images/subsections/{user['user_step'].split()[-1]}.jpg'):
            await message.answer_photo(photo=FSInputFile(f'images/subsections/{user['user_step'].split()[-1]}.jpg'), caption='Отправьте новую фотографию подраздела меню, как изображение, не как файл', reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Отправьте новую фотографию подраздела меню, как изображение, не как файл', reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))

    # Editing position's photo
    elif " ".join(user['user_step'].split()[:3]) == 'edit position photo' and 'admin' in user['staff_positions']:
        position = await db.get_menu_position(user['user_step'].split()[-1])
        # Checking if the position has a photo
        if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
            await message.answer_photo(photo=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую фотографию позиции меню, как изображение, не как файл', reply_markup=await kb.edit_menu_position(user['user_step'].split()[-1], 'admin' in user['staff_positions']))
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую фотографию позиции меню, как изображение, не как файл', reply_markup=await kb.edit_menu_position(user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    else:
        await db.update_user_step(message.chat.id, '')
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот', reply_markup=await kb.menu('admin' in user['staff_positions']))


# Processing error message
@router.message(F.audio, F.video)
async def error(message: Message):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(message.chat.id)
    if user is None:
        await db.add_user(message.chat.id)
    user = await db.get_user_by_telegram_id(message.chat.id)

    await db.update_user_step(message.chat.id, '')
    await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот', reply_markup=await kb.menu('admin' in user['staff_positions']))


# Processing text messages
@router.message(F.text)
async def text(message: Message):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(message.chat.id)
    if user is None:
        await db.add_user(message.chat.id)
    user = await db.get_user_by_telegram_id(message.chat.id)
    # Deleting forbidden symbol, that can cause database error
    message_text = message.text.replace("'", '')

    #Debugging
    print()
    print(message_text)
    print(user)

    # Staff login
    if user['user_step'] == 'login':
        await db.update_user_step(message.chat.id, 'password')
        await db.update_user_login(message.chat.id, message_text)
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Отправьте выданный пароль', reply_markup=await kb.main_menu())

    # Staff password
    elif user['user_step'] == 'password':
        staff = await db.get_staff_by_login(user['user_login'])
        # All correct
        if staff and staff['staff_password'] == message_text and staff['staff_telegram_id'] == 0:
            await db.update_user_step(message.chat.id, '')
            await db.update_staff_telegram_id(staff['staff_login'], message.chat.id)
            # Staff is an admin
            if staff['staff_position'] == 'admin':
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Вы успешно авторизовались как администратор', reply_markup=await kb.admin())
            # Staff is an operator
            elif staff['staff_position'] == 'operator':
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Вы успешно авторизовались как оператор', reply_markup=await kb.main_menu())
            # Staff is a kitchen
            elif staff['staff_position'] == 'kitchen':
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Вы успешно авторизовались как член кухни', reply_markup=await kb.main_menu())
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Вы успешно авторизовались как {staff["staff_position"]}', reply_markup=await kb.main_menu())
        # Staff is already authorized
        elif staff and staff['staff_password'] == message_text:
            await db.update_user_step(message.chat.id, '')
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Данный персонал уже авторизован', reply_markup=await kb.main_menu())
        # Incorrect login or password
        else:
            await db.update_user_step(message.chat.id, '')
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Неверный логин или пароль', reply_markup=await kb.main_menu())

    # Updating staff's name
    elif " ".join(user['user_step'].split()[:3]) == 'edit staff name' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        await db.update_staff_name(" ".join(user['user_step'].split()[3:]), message_text)
        staff = await db.get_staff_by_login(" ".join(user['user_step'].split()[3:]))
        # Staff is an admin
        if staff['staff_position'] == 'admin':
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'<b>{staff["staff_name"]}</b>\nЛогин {staff["staff_login"]}\nАдминистратор', reply_markup=await kb.staff(staff['staff_login'], staff['staff_position']))
        # Staff is an operator
        elif staff['staff_position'] == 'operator':
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'<b>{staff["staff_name"]}</b>\nЛогин {staff["staff_login"]}\nОператор', reply_markup=await kb.staff(staff['staff_login'], staff['staff_position']))
        # Staff is a kitchen
        elif staff['staff_position'] == 'kitchen':
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'<b>{staff["staff_name"]}</b>\nЛогин {staff["staff_login"]}\nЧлен кухни', reply_markup=await kb.staff(staff['staff_login'], staff['staff_position']))
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'<b>{staff["staff_name"]}</b>\nЛогин {staff["staff_login"]}\n{staff["staff_position"]}', reply_markup=await kb.staff(staff['staff_login'], staff['staff_position']))

    # Adding new staff login
    elif user['user_step'] == 'add staff login' and 'admin' in user['staff_positions']:
        # Login is already taken
        if await db.get_staff_by_login(message_text):
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Данный логин уже занят, попробуйте другой\nНе используйте одинарные кавычки', reply_markup=await kb.admin())
        # Login is free
        else:
            await db.update_user_step(message.chat.id, 'add staff password')
            await db.update_new_staff_login(message.chat.id, message_text)
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Отправьте пароль нового члена персонала\nНе используйте одинарные кавычки', reply_markup=await kb.admin())

    # Adding new staff password
    elif user['user_step'] == 'add staff password' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, 'add staff name')
        await db.update_new_staff_password(message.chat.id, message_text)
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Отправьте имя нового члена персонала\nНе используйте одинарные кавычки', reply_markup=await kb.admin())

    # Adding new staff name
    elif user['user_step'] == 'add staff name' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        new_staff = await db.get_new_staff(message.chat.id)
        await db.add_staff(new_staff['staff_login'], new_staff['staff_password'], message_text, new_staff['staff_position'])
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Новый член персонала <b>{message_text}</b> успешно добавлен\nСообщите ему логин и пароль для входа\nЛогин <b>{new_staff["staff_login"]}</b>\nПароль <b>{new_staff["staff_password"]}</b>', reply_markup=await kb.admin())

    # Adding section
    elif user['user_step'] == 'add section' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        await db.add_menu_section(message_text)
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Новый раздел меню <b>{message_text}</b> успешно добавлен', reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Editing section
    elif " ".join(user['user_step'].split()[:2]) == 'edit section' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        await db.update_menu_section(user['user_step'].split()[-1], message_text)
        # Checking if the section has a photo
        if os.path.exists(f'images/sections/{user['user_step'].split()[-1]}.jpg'):
            await message.answer_photo(photo=FSInputFile(f'images/sections/{user['user_step'].split()[-1]}.jpg'), caption=f'Название раздела успешно изменено на <b>{message_text}</b>', reply_markup=await kb.menu('admin' in user['staff_positions']))
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Название раздела успешно изменено на <b>{message_text}</b>', reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Adding subsection
    elif " ".join(user['user_step'].split()[:2]) == 'add subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        await db.add_menu_subsection(user['user_step'].split()[-1], message_text)
        # Checking if the section has a photo
        if os.path.exists(f'images/sections/{user['user_step'].split()[-1]}.jpg'):
            await message.answer_photo(photo=FSInputFile(f'images/sections/{user['user_step'].split()[-1]}.jpg'), caption=f'Новый подраздел меню <b>{message_text}</b> успешно добавлен', reply_markup=await kb.menu_section(await db.get_menu_section(user['user_step'].split()[-1]), user['user_step'].split()[-1], 'admin' in user['staff_positions']))
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Новый подраздел меню <b>{message_text}</b> успешно добавлен', reply_markup=await kb.menu_section(await db.get_menu_section(user['user_step'].split()[-1]), user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    # Editing subsection
    elif " ".join(user['user_step'].split()[:2]) == 'edit subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        await db.update_menu_subsection(user['user_step'].split()[-1], message_text)
        subsection_info = await db.get_menu_subsection_info(user['user_step'].split()[-1])
        # Checking if the subsection has a photo
        if os.path.exists(f'images/sections/{subsection_info["menu_section_id"]}.jpg'):
            await message.answer_photo(photo=FSInputFile(f'images/sections/{subsection_info["menu_section_id"]}.jpg'), caption=f'Название подраздела успешно изменено на <b>{message_text}</b>', reply_markup=await kb.menu_section( await db.get_menu_section(subsection_info['menu_section_id']), subsection_info['menu_section_id'], 'admin' in user['staff_positions']))
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Название подраздела успешно изменено на <b>{message_text}</b>', reply_markup=await kb.menu_section(await db.get_menu_section(subsection_info['menu_section_id']), subsection_info['menu_section_id'], 'admin' in user['staff_positions']))

    # Adding position's name
    elif user['user_step'] == 'add position name' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, 'add position photo')
        await db.update_new_menu_position_name(message.chat.id, message_text)
        position = await db.get_new_menu_position(message.chat.id)
        # Position is located in a section
        if position['menu_subsection_id'] == 0:
            section = await db.get_menu_section(position['menu_section_id'])
            # Checking if the section has a photo
            if os.path.exists(f'images/sections/{position["menu_section_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/sections/{position["menu_section_id"]}.jpg'), caption=f'Отправьте фотографию новой позиции меню', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте фотографию новой позиции меню', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
        # Position is located in a subsection
        else:
            subsection = await db.get_menu_subsection(position['menu_subsection_id'])
            # Checking if the subsection has a photo
            if os.path.exists(f'images/subsections/{position["menu_subsection_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/subsections/{position["menu_subsection_id"]}.jpg'), caption=f'Отправьте фотографию новой позиции меню', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте фотографию новой позиции меню', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))

    # Adding position's description
    elif user['user_step'] == 'add position description' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, 'add position weight')
        await db.update_new_menu_position_description(message.chat.id, message_text)
        position = await db.get_new_menu_position(message.chat.id)
        # Position is located in a section
        if position['menu_subsection_id'] == 0:
            section = await db.get_menu_section(position['menu_section_id'])
            # Checking if the section has a photo
            if os.path.exists(f'images/sections/{position["menu_section_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/sections/{position["menu_section_id"]}.jpg'), caption=f'Отправьте вес/объем новой позиции меню\nНе используйте одинарные кавычки', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте вес/объем новой позиции меню\nНе используйте одинарные кавычки', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
        # Position is located in a subsection
        else:
            subsection = await db.get_menu_subsection(position['menu_subsection_id'])
            # Checking if the subsection has a photo
            if os.path.exists(f'images/subsections/{position["menu_subsection_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/subsections/{position["menu_subsection_id"]}.jpg'), caption=f'Отправьте вес/объем новой позиции меню\nНе используйте одинарные кавычки', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте вес/объем новой позиции меню\nНе используйте одинарные кавычки', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))

    # Adding position's weight
    elif user['user_step'] == 'add position weight' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, 'add position price')
        await db.update_new_menu_position_weight(message.chat.id, message_text)
        position = await db.get_new_menu_position(message.chat.id)
        # Position is located in a section
        if position['menu_subsection_id'] == 0:
            section = await db.get_menu_section(position['menu_section_id'])
            # Checking if the section has a photo
            if os.path.exists(f'images/sections/{position["menu_section_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/sections/{position["menu_section_id"]}.jpg'), caption=f'Отправьте цену новой позиции меню\nЦена должна представлять из себя одно натуральное число', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте цену новой позиции меню\nЦена должна представлять из себя одно натуральное число', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
        # Position is located in a subsection
        else:
            subsection = await db.get_menu_subsection(position['menu_subsection_id'])
            # Checking if the subsection has a photo
            if os.path.exists(f'images/subsections/{position["menu_subsection_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/subsections/{position["menu_subsection_id"]}.jpg'), caption=f'Отправьте цену новой позиции меню\nЦена должна представлять из себя одно натуральное число', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте цену новой позиции меню\nЦена должна представлять из себя одно натуральное число', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))

    # Adding position's price
    elif user['user_step'] == 'add position price' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        # Price is correct
        if message_text.isdecimal() and int(message_text) > 0:
            await db.update_user_step(message.chat.id, '')
            position = await db.get_new_menu_position(message.chat.id)
            position_id = await db.add_menu_position(position['menu_section_id'], position['menu_subsection_id'], position['menu_position_name'], position['menu_position_description'], position['menu_position_weight'], message_text)
            # Saving position's image
            with Image.open(f'images/positions/{message.chat.id}.jpg') as img:
                img.save(f'images/positions/{position_id}.jpg')
                os.remove(f'images/positions/{message.chat.id}.jpg')
            # Position is located in a section
            if position['menu_subsection_id'] == 0:
                section = await db.get_menu_section(position['menu_section_id'])
                # Checking if the section has a photo
                if os.path.exists(f'images/sections/{position["menu_section_id"]}.jpg'):
                    await message.answer_photo(photo=FSInputFile(f'images/sections/{position["menu_section_id"]}.jpg'), caption=f'Новая позиция меню <b>{position["menu_position_name"]}</b> успешно добавлена', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
                else:
                    await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Новая позиция меню <b>{position["menu_position_name"]}</b> успешно добавлена',  reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
            # Position is located in a subsection
            else:
                subsection = await db.get_menu_subsection(position['menu_subsection_id'])
                # Checking if the subsection has a photo
                if os.path.exists(f'images/subsections/{position["menu_subsection_id"]}.jpg'):
                    await message.answer_photo(photo=FSInputFile(f'images/subsections/{position["menu_subsection_id"]}.jpg'), caption=f'Новая позиция меню <b>{position["menu_position_name"]}</b> успешно добавлена', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))
                else:
                    await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Новая позиция меню <b>{position["menu_position_name"]}</b> успешно добавлена', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))
        # Incorrect price
        else:
            position = await db.get_new_menu_position(message.chat.id)
            # Position is located in a section
            if position['menu_subsection_id'] == 0:
                section = await db.get_menu_section(position['menu_section_id'])
                # Checking if the section has a photo
                if os.path.exists(f'images/sections/{position["menu_section_id"]}.jpg'):
                    await message.answer_photo(photo=FSInputFile(f'images/sections/{position["menu_section_id"]}.jpg'), caption=f'Неверно указана цена, попробуйте отправить ее снова\nЦена должна представлять из себя одно натуральное число', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
                else:
                    await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Неверно указана цена, попробуйте отправить ее снова\nЦена должна представлять из себя одно натуральное число', reply_markup=await kb.menu_section(section, position['menu_section_id'], 'admin' in user['staff_positions']))
            # Position is located in a subsection
            else:
                subsection = await db.get_menu_subsection(position['menu_subsection_id'])
                # Checking if the subsection has a photo
                if os.path.exists(f'images/subsections/{position["menu_subsection_id"]}.jpg'):
                    await message.answer_photo(photo=FSInputFile(f'images/subsections/{position["menu_subsection_id"]}.jpg'), caption=f'Неверно указана цена, попробуйте отправить ее снова\nЦена должна представлять из себя одно натуральное число',reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))
                else:
                    await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Неверно указана цена, попробуйте отправить ее снова\nЦена должна представлять из себя одно натуральное число', reply_markup=await kb.menu_subsection(subsection, position['menu_section_id'], position['menu_subsection_id'], 'admin' in user['staff_positions']))

    # Edit position name
    elif " ".join(user['user_step'].split()[:3]) == 'edit position name' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, f'edit position photo {user["user_step"].split()[-1]}')
        await db.update_menu_position_name(user['user_step'].split()[-1], message_text)
        position = await db.get_menu_position(user['user_step'].split()[-1])
        # Checking if the position has a photo
        if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
            await message.answer_photo(photo=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую фотографию позиции меню', reply_markup=await kb.edit_menu_position(user['user_step'].split()[-1], 'admin' in user['staff_positions']))
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую фотографию позиции меню', reply_markup=await kb.edit_menu_position(user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    # Edit position description
    elif " ".join(user['user_step'].split()[:3]) == 'edit position description' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, f'edit position weight {user["user_step"].split()[-1]}')
        await db.update_menu_position_description(user['user_step'].split()[-1], message_text)
        position = await db.get_menu_position(user['user_step'].split()[-1])
        # Checking if the position has a photo
        if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
            await message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новый вес/объем позиции меню'), reply_markup=await kb.edit_menu_position(user['user_step'].split()[-1], 'admin' in user['staff_positions']))
        else:
            await message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новый вес/объем позиции меню'), reply_markup=await kb.edit_menu_position(user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    # Edit position weight
    elif " ".join(user['user_step'].split()[:3]) == 'edit position weight' and 'admin' in user['staff_positions']:
        await db.update_user_step(message.chat.id, f'edit position price {user["user_step"].split()[-1]}')
        await db.update_menu_position_weight(user['user_step'].split()[-1], message_text)
        position = await db.get_menu_position(user['user_step'].split()[-1])
        # Checking if the position has a photo
        if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
            await message.answer_photo(photo=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую цену позиции меню. Цена должна представлять из себя одно натуральное число', reply_markup=await kb.edit_menu_position(user['user_step'].split()[-1], 'admin' in user['staff_positions']))
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую цену позиции меню. Цена должна представлять из себя одно натуральное число', reply_markup=await kb.edit_menu_position(user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    # Edit position price
    elif " ".join(user['user_step'].split()[:3]) == 'edit position price' and 'admin' in user['staff_positions']:
        if message_text.isdecimal() and int(message_text) > 0:
            await db.update_user_step(message.chat.id, f'')
            await db.update_menu_position_price(user['user_step'].split()[-1], message_text)
            position = await db.get_menu_position(user['user_step'].split()[-1])
            # Position is located in a section
            if position['menu_subsection_id'] == 0:
                back_to = f'section {position["menu_section_id"]}'
            # Position is located in a subsection
            else:
                back_to = f'subsection {position["menu_subsection_id"]}'
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб', reply_markup=await kb.menu_position(user['user_step'].split()[-1], user['user_cart'].count(user['user_step'].split()[-1]), back_to, 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб', reply_markup=await kb.menu_position(user['user_step'].split()[-1], user['user_cart'].count(user['user_step'].split()[-1]), back_to, 'admin' in user['staff_positions']))
        else:
            position = await db.get_menu_position(user['user_step'].split()[-1])
            # Position is located in a section
            if position['menu_subsection_id'] == 0:
                back_to = f'section {position["menu_section_id"]}'
            # Position is located in a subsection
            else:
                back_to = f'subsection {position["menu_subsection_id"]}'
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await message.answer_photo(photo=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nНеверно указана цена, попробуйте отправить ее снова\nЦена должна представлять из себя одно натуральное число', reply_markup=await kb.menu_position(user['user_step'].split()[-1], user['user_cart'].count(user['user_step'].split()[-1]), back_to, 'admin' in user['staff_positions']))
            else:
                await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nНеверно указана цена, попробуйте отправить ее снова\nЦена должна представлять из себя одно натуральное число', reply_markup=await kb.menu_position(user['user_step'].split()[-1], user['user_cart'].count(user['user_step'].split()[-1]), back_to, 'admin' in user['staff_positions']))

    # Editing profile phone
    elif user['user_step'] == 'profile phone':
        # Phone number is correct
        if re.match(r'[78][0-9]{10}', message_text):
            await db.update_user_step(message.chat.id, '')
            await db.update_user_phone(message.chat.id, message_text)
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Ваш номер телефона успешно изменен на <b>{message_text}</b>', reply_markup=await kb.profile())
        # Incorrect phone number
        else:
            await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Неверно указан номер телефона, попробуйте отправить его без пробелов и прочих символов в формате 79876543210', reply_markup=await kb.profile())

    # Editing profile address
    elif user['user_step'] == 'profile address':
        await db.update_user_step(message.chat.id, '')
        await db.update_user_address(message.chat.id, message_text)
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Ваш адрес доставки успешно изменен на <b>{message_text}</b>', reply_markup=await kb.profile())

    # Adding order's decline note
    elif " ".join(user['user_step'].split()[:2]) == 'order decline' and 'operator' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        await db.update_order_note(user['user_step'].split()[-1], message_text)
        order = await db.get_order(user['user_step'].split()[-1])
        # Processing positions
        text = ''
        for position_id in set(order['order_positions']):
            position = await db.get_menu_position(position_id)
            if position:
                text += f'{position["menu_position_name"]} {order['order_positions'].split().count(position_id)}шт.\n'
            else:
                text += f'УДАЛЕННАЯ ПОЗИЦИЯ {order['order_positions'].split().count(position_id)}шт.\n'
        # Sending messages to the operators
        for operator in order['order_operators'].split():
            if order['order_payment_method'] == 'pay by card':
                await message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\nОплата картой\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nОТМЕНЕН', reply_markup=await kb.operator(order['order_id'], 'done')))
            elif order['order_payment_method'] == 'pay by cash':
                await message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\nОплата наличными\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nОТМЕНЕН', reply_markup=await kb.operator(order['order_id'], 'done')))
            else:
                await message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\nОплата онлайн\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nОТМЕНЕН', reply_markup=await kb.operator(order['order_id'], 'done')))
        # Sending message to the user
        await message.bot.send_photo(chat_id=order['user_telegram_id'], photo=FSInputFile(f'images/logo.jpg'), caption=f'Ваш заказ №<b>{order["order_id"]}</b> от {order["order_date"]} на сумму <b>{order["order_price"]}</b> руб был отменен по причине: {message_text}', reply_markup=await kb.main_menu())

    # Adding order's note
    elif " ".join(user['user_step'].split()[:2]) == 'order note' and 'operator' in user['staff_positions']:
        await db.update_user_step(message.chat.id, '')
        await db.update_order_note(user['user_step'].split()[-1], message_text)
        order = await db.get_order(user['user_step'].split()[-1])
        # Processing positions
        text = ''
        for position_id in set(order['order_positions'].split()):
            position = await db.get_menu_position(position_id)
            if position:
                text += f'{position["menu_position_name"]} {order['order_positions'].split().count(position_id)}шт.\n'
            else:
                text += f'УДАЛЕННАЯ ПОЗИЦИЯ {order['order_positions'].split().count(position_id)}шт.\n'
        # Sending messages to the operators
        for operator in order['order_operators'].split():
            if order['order_payment_method'] == 'pay by card':
                await message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\nОплата картой\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН', reply_markup=await kb.operator(order['order_id'], 'done')))
            elif order['order_payment_method'] == 'pay by cash':
                await message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\nОплата наличными\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН', reply_markup=await kb.operator(order['order_id'], 'done')))
            else:
                await message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\nОплата онлайн\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН', reply_markup=await kb.operator(order['order_id'], 'done')))
        # Sending messages to the kitchen
        for kitchen in order['order_kitchen'].split():
            if order['order_payment_method'] == 'pay by card':
                await message.bot.edit_message_media(chat_id=kitchen.split(':')[0], message_id=kitchen.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\nОплата картой\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН', reply_markup=await kb.operator(order['order_id'], 'done')))
            elif order['order_payment_method'] == 'pay by cash':
                await message.bot.edit_message_media(chat_id=kitchen.split(':')[0], message_id=kitchen.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\nОплата наличными\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН', reply_markup=await kb.operator(order['order_id'], 'done')))
            else:
                await message.bot.edit_message_media(chat_id=kitchen.split(':')[0], message_id=kitchen.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\nОплата онлайн\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН', reply_markup=await kb.operator(order['order_id'], 'done')))

    else:
        await db.update_user_step(message.chat.id, '')
        await message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот', reply_markup=await kb.menu('admin' in user['staff_positions']))


# Processing callbacks
@router.callback_query()
async def callbacks(callback: CallbackQuery):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(callback.message.chat.id)
    if user is None:
        await db.add_user(callback.message.chat.id)
    user = await db.get_user_by_telegram_id(callback.message.chat.id)

    # Debugging
    print()
    print(callback.message.invoice)
    print(callback.data)
    print(user)

    # Main menu button
    if callback.data == 'main menu':
        await db.update_user_step(callback.message.chat.id, '')
        if callback.message.invoice:
            await callback.message.answer_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот', reply_markup=await kb.menu('admin' in user['staff_positions']))
            await callback.message.delete()
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Edit logo button
    elif callback.data == 'edit logo':
        await db.update_user_step(callback.message.chat.id, 'edit logo')
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Отправьте новый логотип'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Admin panel button
    elif callback.data == 'admin panel' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Выберите действие, чтобы продолжить'), reply_markup=await kb.admin())

    # Clear stop-list button
    elif callback.data == 'clear stop list' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        await db.clear_stop_list()
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Стоп-лист успешно очищен'), reply_markup=await kb.admin())

    # Staff list button
    elif " ".join(callback.data.split()[:2]) == 'staff list' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        # List of admins
        if " ".join(callback.data.split()[2:]) == 'admin':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Список администраторов'), reply_markup=await kb.staff_list(" ".join(callback.data.split()[2:])))
        # List of operators
        elif " ".join(callback.data.split()[2:]) == 'operator':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Список операторов'), reply_markup=await kb.staff_list(" ".join(callback.data.split()[2:])))
        # List of kitchen
        elif " ".join(callback.data.split()[2:]) == 'kitchen':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Список кухни'), reply_markup=await kb.staff_list(" ".join(callback.data.split()[2:])))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Список {" ".join(callback.data.split()[2:])}'), reply_markup=await kb.staff_list(" ".join(callback.data.split()[2:])))

    # Staff button
    elif callback.data.split()[0] == 'staff' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        staff = await db.get_staff_by_login(" ".join(callback.data.split()[1:]))
        # Staff is admin
        if staff['staff_position'] == 'admin':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{staff["staff_name"]}</b>\nЛогин <b>{staff["staff_login"]}</b>\n<b>Администратор</b>'), reply_markup=await kb.staff(staff['staff_login'], staff['staff_position']))
        # Staff is operator
        elif staff['staff_position'] == 'operator':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{staff["staff_name"]}</b>\nЛогин <b>{staff["staff_login"]}</b>\n<b>Оператор</b>'), reply_markup=await kb.staff(staff['staff_login'], staff['staff_position']))
        # Staff is kitchen
        elif staff['staff_position'] == 'kitchen':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{staff["staff_name"]}</b>\nЛогин <b>{staff["staff_login"]}</b>\n<b>Кухня</b>'), reply_markup=await kb.staff(staff['staff_login'], staff['staff_position']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{staff["staff_name"]}</b>\nЛогин <b>{staff["staff_login"]}</b>\n<b>{staff["staff_position"]}</b>'), reply_markup=await kb.staff(staff['staff_login'], staff['staff_position']))

    # Edit staff name button
    elif " ".join(callback.data.split()[:3]) == 'edit staff name' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, callback.data)
        staff = await db.get_staff_by_login(" ".join(callback.data.split()[3:]))
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте новое имя для <b>{staff["staff_name"]}</b>'), reply_markup=await kb.staff(staff['staff_login'], staff['staff_position']))

    # Delete staff button
    elif " ".join(callback.data.split()[:2]) == 'delete staff' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        staff = await db.get_staff_by_login(" ".join(callback.data.split()[2:]))
        # Staff is admin
        if staff['staff_position'] == 'admin':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Вы уверены, что хотите удалить администратора <b>{staff["staff_name"]}</b>'), reply_markup=await kb.delete_staff(staff['staff_login'], staff['staff_position']))
        # Staff is operator
        elif staff['staff_position'] == 'operator':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Вы уверены, что хотите удалить оператора <b>{staff["staff_name"]}</b>'), reply_markup=await kb.delete_staff(staff['staff_login'], staff['staff_position']))
        # Staff is kitchen
        elif staff['staff_position'] == 'kitchen':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Вы уверены, что хотите удалить кухню <b>{staff["staff_name"]}</b>'), reply_markup=await kb.delete_staff(staff['staff_login'], staff['staff_position']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Вы уверены, что хотите удалить {staff["staff_position"]} <b>{staff["staff_name"]}</b>'), reply_markup=await kb.delete_staff(staff['staff_login'], staff['staff_position']))

    # Yes delete staff button
    elif " ".join(callback.data.split()[:3]) == 'yes delete staff' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        staff = await db.get_staff_by_login(" ".join(callback.data.split()[3:]))
        await db.delete_staff(" ".join(callback.data.split()[3:]))
        # Staff list of admin
        if staff['staff_position'] == 'admin':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Список администраторов'), reply_markup=await kb.staff_list(staff['staff_position']))
        # Staff list of operators
        elif staff['staff_position'] == 'operator':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Список операторов'), reply_markup=await kb.staff_list(staff['staff_position']))
        # Staff list of kitchen
        elif staff['staff_position'] == 'kitchen':
            await callback.message.edit_media( media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Список кухни'), reply_markup=await kb.staff_list(staff['staff_position']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Список {staff["staff_position"]}'), reply_markup=await kb.staff_list(staff['staff_position']))

    # Add staff button
    elif " ".join(callback.data.split()[:2]) == 'add staff' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, 'add staff login')
        # Creating empty field for adding new staff
        if await db.get_new_staff(callback.message.chat.id) is None:
            await db.add_new_staff(callback.message.chat.id)
        await db.update_new_staff_position(callback.message.chat.id, " ".join(callback.data.split()[2:]))
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте логин нового члена персонала\nНе используйте одинарные кавычки'), reply_markup=await kb.admin())

    # Add section button
    elif callback.data == 'add section' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, 'add section')
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте название нового раздела меню\nНе используйте одинарные кавычки'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Edit section button
    elif callback.data == 'edit section' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, 'edit section')
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Выбери раздел для редактирования'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Choosing section to edit
    elif callback.data.split()[0] == 'section' and user['user_step'] == 'edit section' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, f'edit {callback.data}')
        section_info = await db.get_menu_section_info(callback.data.split()[-1])
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте новое название для раздела <b>{section_info["menu_section_name"]}</b>\nНе используйте одинарные кавычки'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Edit section photo button
    elif " ".join(callback.data.split()[:3]) == 'edit photo section' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, callback.data)
        section_info = await db.get_menu_section_info(callback.data.split()[-1])
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте новую фотографию для раздела <b>{section_info["menu_section_name"]}</b>'), reply_markup=await kb.menu_section(await db.get_menu_section(callback.data.split()[-1]), callback.data.split()[-1],'admin' in user['staff_positions']))

    # Delete section button
    elif callback.data == 'delete section' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, 'delete section')
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Выбери раздел для удаления'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Choosing section to delete
    elif callback.data.split()[0] == 'section' and user['user_step'] == 'delete section' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        section_info = await db.get_menu_section_info(callback.data.split()[-1])
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Вы уверены, что хотите удалить раздел {section_info["menu_section_name"]}? Вместе с ним будет удалено все его содержимое'), reply_markup=await kb.delete_section(callback.data.split()[-1]))

    # Yes delete section button
    elif " ".join(callback.data.split()[:3]) == 'yes delete section' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        section = await db.get_menu_section(callback.data.split()[-1])
        section_info = await db.get_menu_section_info(callback.data.split()[-1])
        await db.delete_menu_section(callback.data.split()[-1])
        # Deleting section's photo
        if os.path.exists(f'images/sections/{callback.data.split()[-1]}.jpg'):
            os.remove(f'images/sections/{callback.data.split()[-1]}.jpg')
        # Deleting sections' subsections photos
        if section and section[0] == 'menu subsections':
            for subsection in section[1]:
                if os.path.exists(f'images/subsections/{subsection["menu_subsection_id"]}.jpg'):
                    os.remove(f'images/subsections/{subsection["menu_subsection_id"]}.jpg')
        # Deleting sections' positions photos
        elif section and section[0] == 'menu positions':
            for position in section[1]:
                if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                    os.remove(f'images/positions/{position["menu_position_id"]}.jpg')
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Раздел <b>{section_info["menu_section_name"]}</b> успешно удален'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Go to section
    elif callback.data.split()[0] == 'section':
        await db.update_user_step(callback.message.chat.id, '')
        section = await db.get_menu_section(callback.data.split()[-1])
        section_info = await db.get_menu_section_info(callback.data.split()[-1])
        # Section stores subsections
        if section_info and section and section[0] == 'menu subsections':
            # Checking is the section has a photo
            if os.path.exists(f'images/sections/{callback.data.split()[-1]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{callback.data.split()[-1]}.jpg'), caption='Выберите подраздел меню'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Выберите подраздел меню'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
        # Section stores positions
        elif section_info and section and section[0] == 'menu positions':
            # Checking is the section has a photo
            if os.path.exists(f'images/sections/{callback.data.split()[-1]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{callback.data.split()[-1]}.jpg'), caption='Выберите позиции меню'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Выберите позиции меню'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
        # Empty section
        elif section_info:
            # Checking is the section has a photo
            if os.path.exists(f'images/sections/{callback.data.split()[-1]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{callback.data.split()[-1]}.jpg'), caption=f'Раздел {section_info["menu_section_name"]} пока пуст'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Раздел {section_info["menu_section_name"]} пока пуст'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Add subsection button
    elif " ".join(callback.data.split()[:2]) == 'add subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, callback.data)
        section = await db.get_menu_section(callback.data.split()[-1])
        # Checking is the section has a photo
        if os.path.exists(f'images/sections/{callback.data.split()[-1]}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{callback.data.split()[-1]}.jpg'), caption=f'Отправьте название нового подраздела меню\nНе используйте одинарные кавычки'), reply_markup=await kb.menu_section(section, callback.data.split()[-1], 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте название нового подраздела меню\nНе используйте одинарные кавычки'), reply_markup=await kb.menu_section(section, callback.data.split()[-1], 'admin' in user['staff_positions']))

    # Edit subsection button
    elif " ".join(callback.data.split()[:2]) == 'edit subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, callback.data)
        section = await db.get_menu_section(callback.data.split()[-1])
        # Checking is the section has a photo
        if os.path.exists(f'images/sections/{callback.data.split()[-1]}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{callback.data.split()[-1]}.jpg'), caption=f'Выберите подраздел меню для редактирования'), reply_markup=await kb.menu_section(section, callback.data.split()[-1], 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Выберите подраздел меню для редактирования'), reply_markup=await kb.menu_section(section, callback.data.split()[-1], 'admin' in user['staff_positions']))

    # Choosing subsection to edit button
    elif callback.data.split()[0] == 'subsection' and " ".join(user['user_step'].split()[:2]) == 'edit subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, f'edit subsection {callback.data.split()[-1]}')
        section = await db.get_menu_section(user['user_step'].split()[-1])
        subsection_info = await db.get_menu_subsection_info(callback.data.split()[-1])
        # Checking is the section has a photo
        if os.path.exists(f'images/sections/{user['user_step'].split()[-1]}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{user['user_step'].split()[-1]}.jpg'), caption=f'Отправьте новое название для подраздела <b>{subsection_info["menu_subsection_name"]}</b>\nНе используйте одинарные кавычки'), reply_markup=await kb.menu_section(section, user['user_step'].split()[-1], 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте новое название для подраздела <b>{subsection_info["menu_subsection_name"]}</b>\nНе используйте одинарные кавычки'), reply_markup=await kb.menu_section(section, user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    # Edit subsection photo button
    elif " ".join(callback.data.split()[:3]) == 'edit photo subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, callback.data)
        subsection_info = await db.get_menu_subsection_info(callback.data.split()[-1])
        # Checking is the subsection has a photo
        if os.path.exists(f'images/subsections/{callback.data.split()[-1]}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/subsections/{callback.data.split()[-1]}.jpg'), caption=f'Отправьте новую фотографию для подраздела <b>{subsection_info["menu_subsection_name"]}</b>'), reply_markup=await kb.menu_subsection(await db.get_menu_subsection(callback.data.split()[-1]), subsection_info['menu_section_id'], callback.data.split()[-1], 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Отправьте новую фотографию для подраздела <b>{subsection_info["menu_subsection_name"]}</b>'), reply_markup=await kb.menu_subsection(await db.get_menu_subsection(callback.data.split()[-1]), subsection_info['menu_section_id'], callback.data.split()[-1], 'admin' in user['staff_positions']))

    # Delete subsection button
    elif " ".join(callback.data.split()[:2]) == 'delete subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, callback.data)
        section = await db.get_menu_section(callback.data.split()[-1])
        # Checking is the subsection has a photo
        if os.path.exists(f'images/sections/{callback.data.split()[-1]}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{callback.data.split()[-1]}.jpg'), caption=f'Выберите подраздел меню для удаления'), reply_markup=await kb.menu_section(section, callback.data.split()[-1], 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Выберите подраздел меню для удаления'), reply_markup=await kb.menu_section(section, callback.data.split()[-1], 'admin' in user['staff_positions']))

    # Choosing subsection to delete button
    elif callback.data.split()[0] == 'subsection' and " ".join(user['user_step'].split()[:2]) == 'delete subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, f'delete subsection {callback.data.split()[-1]}')
        subsection_info = await db.get_menu_subsection_info(callback.data.split()[-1])
        # Checking is the subsection has a photo
        if os.path.exists(f'images/sections/{user["user_step"].split()[-1]}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{user["user_step"].split()[-1]}.jpg'), caption=f'Вы уверены, что хотите удалить подраздел <b>{subsection_info["menu_subsection_name"]}</b>\nВместе с ним будет удалено все его содержимое'), reply_markup=await kb.delete_subsection(callback.data.split()[-1], user['user_step'].split()[-1]))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Вы уверены, что хотите удалить подраздел <b>{subsection_info["menu_subsection_name"]}</b>\nВместе с ним будет удалено все его содержимое'), reply_markup=await kb.delete_subsection(callback.data.split()[-1], user['user_step'].split()[-1]))

    # Yes delete subsection button
    elif " ".join(callback.data.split()[:3]) == 'yes delete subsection' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        subsection = await db.get_menu_subsection(callback.data.split()[-1])
        subsection_info = await db.get_menu_section_info(callback.data.split()[-1])
        section = await db.get_menu_section(subsection_info['menu_section_id'])
        await db.delete_menu_subsection(callback.data.split()[-1])
        # Deleting subsection photo
        if os.path.exists(f'images/subsections/{callback.data.split()[-1]}.jpg'):
            os.remove(f'images/subsections/{callback.data.split()[-1]}.jpg')
        # Deleting subsections' positions photos
        for position in subsection:
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                os.remove(f'images/positions/{position["menu_position_id"]}.jpg')
        # Checking is the section has a photo
        if os.path.exists(f'images/sections/{subsection_info['menu_section_id']}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{subsection_info['menu_section_id']}.jpg'), caption=f'Подраздел <b>{subsection_info["menu_subsection_name"]}</b> успешно удален'), reply_markup=await kb.menu_section(section, user['user_step'].split()[-1], 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Подраздел <b>{subsection_info["menu_subsection_name"]}</b> успешно удален'), reply_markup=await kb.menu_section(section, user['user_step'].split()[-1], 'admin' in user['staff_positions']))

    # Go to subsection
    elif callback.data.split()[0] == 'subsection':
        await db.update_user_step(callback.message.chat.id, '')
        subsection = await db.get_menu_subsection(callback.data.split()[-1])
        subsection_info = await db.get_menu_subsection_info(callback.data.split()[-1])
        # Subsection stores positions
        if subsection_info and subsection:
            # Checking if the subsection has a photo
            if os.path.exists(f'images/subsections/{callback.data.split()[-1]}.jpg'):
                await callback.message.edit_media( media=InputMediaPhoto(media=FSInputFile(f'images/subsections/{callback.data.split()[-1]}.jpg'), caption=f'Выберите позиции меню'), reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Выберите позиции меню'), reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))
        # Empty subsection
        elif subsection_info:
            # Checking if the subsection has a photo
            if os.path.exists(f'images/subsections/{callback.data.split()[-1]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/subsections/{callback.data.split()[-1]}.jpg'), caption=f'Подраздел <b>{subsection_info["menu_subsection_name"]}</b> пока пуст'), reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Подраздел <b>{subsection_info["menu_subsection_name"]}</b> пока пуст'), reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Add new position
    elif " ".join(callback.data.split()[:2]) == 'add position' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, 'add position name')
        # Creating empty field for adding new position
        if not await db.get_new_menu_position(callback.message.chat.id):
            await db.add_new_menu_position(callback.message.chat.id)
        # Position is located in a section
        if callback.data.split()[-2] == 'section':
            section = await db.get_menu_section(callback.data.split()[-1])
            await db.update_new_menu_position_section_id(callback.message.chat.id, callback.data.split()[-1])
            await db.update_new_menu_position_subsection_id(callback.message.chat.id, 0)
            # Checking if the section has a photo
            if os.path.exists(f'images/sections/{callback.data.split()[-1]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{callback.data.split()[-1]}.jpg'), caption=f'Введи название новой позиции меню\nНе используйте одинарные кавычки'), reply_markup=await kb.menu_section(section, callback.data.split()[-1], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Введи название новой позиции меню\nНе используйте одинарные кавычки'), reply_markup=await kb.menu_section(section, callback.data.split()[-1], 'admin' in user['staff_positions']))
        # Position is located in a subsection
        elif callback.data.split()[-2] == 'subsection':
            subsection_info = await db.get_menu_subsection_info(callback.data.split()[-1])
            await db.update_new_menu_position_section_id(callback.message.chat.id, subsection_info['menu_section_id'])
            await db.update_new_menu_position_subsection_id(callback.message.chat.id, callback.data.split()[-1])
            # Checking if the subsection has a photo
            if os.path.exists(f'images/subsections/{callback.data.split()[-1]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/subsections/{callback.data.split()[-1]}.jpg'), caption=f'Введи название новой позиции меню\nНе используйте одинарные кавычки'), reply_markup=await kb.menu_subsection(await db.get_menu_subsection(callback.data.split()[-1]), subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Введи название новой позиции меню\nНе используйте одинарные кавычки'), reply_markup=await kb.menu_subsection(await db.get_menu_subsection(callback.data.split()[-1]), subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))
        else:
            await db.update_user_step(callback.message.chat.id, '')
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Go to position button
    elif callback.data.split()[0] == 'position':
        if user['user_step'] != 'cart':
            await db.update_user_step(callback.message.chat.id, '')
        position = await db.get_menu_position(callback.data.split()[-1])
        if position:
            if user['user_step'] == 'cart':
                back_to = 'cart'
            elif position['menu_subsection_id'] == 0:
                back_to = f'section {position["menu_section_id"]}'
            else:
                back_to = f'subsection {position["menu_subsection_id"]}'
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб{"\nНаходится в стоп-листе" if position["menu_position_id"] in await db.get_stop_list() else ""}'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб{"\nНаходится в стоп-листе" if position["menu_position_id"] in await db.get_stop_list() else ""}'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Add position to stop-list button:
    elif " ".join(callback.data.split()[:3]) == 'add stop-list position' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        await db.add_to_stop_list(callback.data.split()[-1])
        position = await db.get_menu_position(callback.data.split()[-1])
        if position:
            if position['menu_subsection_id'] == 0:
                back_to = f'section {position["menu_section_id"]}'
            else:
                back_to = f'subsection {position["menu_subsection_id"]}'
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб{"\nНаходится в стоп-листе" if position["menu_position_id"] in await db.get_stop_list() else ""}'), reply_markup=await kb.menu_position(callback.data.split()[-1],user['user_cart'].count(callback.data.split()[-1]), back_to,'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб{"\nНаходится в стоп-листе" if position["menu_position_id"] in await db.get_stop_list() else ""}'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Remove position from stop-list button:
    elif " ".join(callback.data.split()[:3]) == 'remove stop-list position' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        await db.remove_from_stop_list(callback.data.split()[-1])
        position = await db.get_menu_position(callback.data.split()[-1])
        if position:
            if position['menu_subsection_id'] == 0:
                back_to = f'section {position["menu_section_id"]}'
            else:
                back_to = f'subsection {position["menu_subsection_id"]}'
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб{"\nНаходится в стоп-листе" if position["menu_position_id"] in await db.get_stop_list() else ""}'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб{"\nНаходится в стоп-листе" if position["menu_position_id"] in await db.get_stop_list() else ""}'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Edit position button
    elif " ".join(callback.data.split()[:2]) == 'edit position' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, f'edit position name {callback.data.split()[-1]}')
        position = await db.get_menu_position(callback.data.split()[-1])
        if position:
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новое название позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новое название позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Keep prev position button
    elif " ".join(callback.data.split()[:3]) == 'keep prev position' and 'admin' in user['staff_positions']:
        position = await db.get_menu_position(callback.data.split()[-1])
        # Keep prev position's name
        if position and " ".join(user['user_step'].split()[:3]) == 'edit position name':
            await db.update_user_step(callback.message.chat.id, f'edit position photo {callback.data.split()[-1]}')
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую фотографию позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую фотографию позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
        # Keep prev position's photo
        elif position and " ".join(user['user_step'].split()[:3]) == 'edit position photo':
            await db.update_user_step(callback.message.chat.id, f'edit position description {callback.data.split()[-1]}')
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новое описание позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новое описание позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
        # Keep prev position's description
        elif position and " ".join(user['user_step'].split()[:3]) == 'edit position description':
            await db.update_user_step(callback.message.chat.id, f'edit position weight {callback.data.split()[-1]}')
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новый вес/объем позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новый вес/объем позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
        # Keep prev position's weight
        elif position and " ".join(user['user_step'].split()[:3]) == 'edit position weight':
            await db.update_user_step(callback.message.chat.id, f'edit position price {callback.data.split()[-1]}')
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую цену позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nОтправьте новую цену позиции'), reply_markup=await kb.edit_menu_position(callback.data.split()[-1], 'admin' in user['staff_positions']))
        # Keep prev position's price
        elif position and " ".join(user['user_step'].split()[:3]) == 'edit position price':
            await db.update_user_step(callback.message.chat.id, f'')
            if position['menu_subsection_id'] == 0:
                back_to = f'section {position["menu_section_id"]}'
            else:
                back_to = f'subsection {position["menu_subsection_id"]}'
            # Checking if the position has a photo
            if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Delete position button
    elif " ".join(callback.data.split()[:2]) == 'delete position' and 'admin' in user['staff_positions']:
        position = await db.get_menu_position(callback.data.split()[-1])
        # Checking if the position has a photo
        if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nВы уверены, что хотите удалить эту позицию?'), reply_markup=await kb.delete_position(callback.data.split()[-1]))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб\nВы уверены, что хотите удалить эту позицию?'), reply_markup=await kb.delete_position(callback.data.split()[-1]))

    # Yes delete position button
    elif " ".join(callback.data.split()[:3]) == 'yes delete position' and 'admin' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        position = await db.get_menu_position(callback.data.split()[-1])
        await db.delete_menu_position(callback.data.split()[-1])
        # Deleting position's photo
        if os.path.exists(f'images/positions/{callback.data.split()[-1]}.jpg'):
            os.remove(f'images/positions/{callback.data.split()[-1]}.jpg')
        # Position is located in a section
        if position['menu_subsection_id'] == 0:
            section = await db.get_menu_section(position['menu_section_id'])
            section_info = await db.get_menu_section_info(position['menu_section_id'])
            # Section stores subsections
            if section_info and section and section[0] == 'menu subsections':
                # Checking if the section has a photo
                if os.path.exists(f'images/sections/{position['menu_section_id']}.jpg'):
                    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{position['menu_section_id']}.jpg'), caption='Выберите подраздел меню'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
                else:
                    await callback.message.edit_media( media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Выберите подраздел меню'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
            # Section stores positions
            elif section_info and section and section[0] == 'menu positions':
                # Checking if the section has a photo
                if os.path.exists(f'images/sections/{position['menu_section_id']}.jpg'):
                    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{position['menu_section_id']}.jpg'), caption='Выберите позиции меню'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
                else:
                    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Выберите позиции меню'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
            # Empty section
            elif section_info:
                # Checking if the section has a photo
                if os.path.exists(f'images/sections/{position['menu_section_id']}.jpg'):
                    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/sections/{position['menu_section_id']}.jpg'), caption=f'Раздел {section_info["menu_section_name"]} пока пуст'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
                else:
                    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Раздел {section_info["menu_section_name"]} пока пуст'), reply_markup=await kb.menu_section(section, section_info['menu_section_id'], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))
       # Position is located in a subsection
        else:
            subsection = await db.get_menu_subsection(position['menu_subsection_id'])
            subsection_info = await db.get_menu_subsection_info(position['menu_subsection_id'])
            # Subsection stores positions
            if subsection_info and subsection:
                # Checking if the subsection has a photo
                if os.path.exists(f'images/subsections/{position['menu_subsection_id']}.jpg'):
                    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/subsections/{position['menu_subsection_id']}.jpg'), caption=f'Выберите позиции меню'), reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))
                else:
                    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Выберите позиции меню'), reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_subsection_id'], 'admin' in user['staff_positions']))
            # Empty subsection
            elif subsection_info:
                # Checking if the subsection has a photo
                if os.path.exists(f'images/subsections/{position['menu_subsection_id']}.jpg'):
                    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/subsections/{position['menu_subsection_id']}.jpg'), caption=f'Подраздел <b>{subsection_info["menu_subsection_name"]}</b> пока пуст'), reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_section_id'], 'admin' in user['staff_positions']))
                else:
                    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Подраздел <b>{subsection_info["menu_subsection_name"]}</b> пока пуст'), reply_markup=await kb.menu_subsection(subsection, subsection_info['menu_section_id'], subsection_info['menu_section_id'], 'admin' in user['staff_positions']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

    # Increasing position's amount in user's cart
    elif " ".join(callback.data.split()[:3]) == 'increase amount position':
        if user['user_step'] != 'cart':
            await db.update_user_step(callback.message.chat.id, '')
        await db.add_to_user_cart(callback.message.chat.id, callback.data.split()[-1])
        user = await db.get_user_by_telegram_id(callback.message.chat.id)
        position = await db.get_menu_position(callback.data.split()[-1])
        if user['user_step'] == 'cart':
            back_to = 'cart'
        elif position['menu_subsection_id'] == 0:
            back_to = f'section {position["menu_section_id"]}'
        else:
            back_to = f'subsection {position["menu_subsection_id"]}'
        # Checking if the position has a photo
        if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))

    # Decreasing position's amount in user's cart
    elif " ".join(callback.data.split()[:3]) == 'decrease amount position':
        if user['user_step'] != 'cart':
            await db.update_user_step(callback.message.chat.id, '')
        await db.remove_from_user_cart(callback.message.chat.id, callback.data.split()[-1])
        user = await db.get_user_by_telegram_id(callback.message.chat.id)
        position = await db.get_menu_position(callback.data.split()[-1])
        if user['user_step'] == 'cart':
            back_to = 'cart'
        elif position['menu_subsection_id'] == 0:
            back_to = f'section {position["menu_section_id"]}'
        else:
            back_to = f'subsection {position["menu_subsection_id"]}'
        # Checking if the position has a photo
        if os.path.exists(f'images/positions/{position["menu_position_id"]}.jpg'):
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/positions/{position["menu_position_id"]}.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'<b>{position["menu_position_name"]}</b>\n{position["menu_position_description"]}\nВес/объем: {position["menu_position_weight"]}\nЦена: {position["menu_position_price"]} руб'), reply_markup=await kb.menu_position(callback.data.split()[-1], user['user_cart'].count(callback.data.split()[-1]), back_to, 'admin' in user['staff_positions']))

    # Profile button
    elif callback.data == 'profile':
        await db.update_user_step(callback.message.chat.id, '')
        if callback.message.invoice:
            await callback.message.edit_media(photo=FSInputFile(f'images/logo.jpg'), caption='Это ваш профиль, здесь вы можете указать свой адрес и номер телефона для использования доставки, а также посмотреть прошлые заказы', reply_markup=await kb.profile())
            await callback.message.delete()
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Это ваш профиль, здесь вы можете указать свой адрес и номер телефона для использования доставки, а также посмотреть прошлые заказы'), reply_markup=await kb.profile())

    # Profile phone button
    elif callback.data == 'profile phone':
        await db.update_user_step(callback.message.chat.id, 'profile phone')
        # User has phone number
        if user['user_phone'] != '':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Ваш номер телефона <b>{user["user_phone"]}</b>\nЧтобы его изменить отправьте новый номер без пробелов в формате 79876543210'), reply_markup=await kb.profile())
        # User hasn't phone number
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Ваш номер телефона пока пуст\nЧтобы его изменить отправьте новый номер без пробелов в формате 79876543210'), reply_markup=await kb.profile())

    # Profile address button
    elif callback.data == 'profile address':
        await db.update_user_step(callback.message.chat.id, 'profile address')
        # User has delivery address
        if user['user_address'] != '':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Ваш адрес доставки <b>{user["user_address"]}</b>\nЧтобы его изменить отправьте новый адрес доставки'), reply_markup=await kb.profile())
        # User hasn't delivery address
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Ваш адрес доставки пока пуст\nЧтобы его изменить отправьте новый адрес доставки'), reply_markup=await kb.profile())

    # Cart button
    elif callback.data == 'cart':
        await db.update_user_step(callback.message.chat.id, 'cart')
        if callback.message.invoice:
            # User's cart isn't empty
            if user['user_cart'] != '':
                for position_id in user['user_cart'].split():
                    if not await db.get_menu_position(position_id) or position_id in await db.get_stop_list():
                        await db.remove_from_user_cart(callback.message.chat.id, position_id)
                await callback.message.edit_send_photo(photo=FSInputFile(f'images/logo.jpg'), caption=f'Ваша корзина на сумму <b>{sum([user["user_cart"].split().count(x) * (await db.get_menu_position(x))["menu_position_price"] for x in set(user["user_cart"].split())])}</b> руб', reply_markup=await kb.cart(user['user_cart']))
            # Empty cart
            else:
                await callback.message.edit_send_photo(photo=FSInputFile(f'images/logo.jpg'), caption='Ваша корзина пока пуста', reply_markup=await kb.cart(user['user_cart']))
            await callback.message.delete()
        else:
            # User's cart isn't empty
            if user['user_cart'] != '':
                for position_id in user['user_cart'].split():
                    if not await db.get_menu_position(position_id) or position_id in await db.get_stop_list():
                        await db.remove_from_user_cart(callback.message.chat.id, position_id)
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=f'Ваша корзина на сумму <b>{sum([user["user_cart"].split().count(x) * (await db.get_menu_position(x))["menu_position_price"] for x in set(user["user_cart"].split())])}</b> руб'), reply_markup=await kb.cart(user['user_cart']))
            # Empty cart
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Ваша корзина пока пуста'), reply_markup=await kb.cart(user['user_cart']))

    # Order button
    elif callback.data == 'order' and user['user_cart']:
        # User has phone number and delivery address
        if user['user_address'] and user['user_phone']:
            for position_id in user['user_cart'].split():
                if not await db.get_menu_position(position_id) or position_id in await db.get_stop_list():
                    await db.remove_from_user_cart(callback.message.chat.id, position_id)
            user = await db.get_user_by_telegram_id(callback.message.chat.id)
            # Processing positions
            text = 'Ваш заказ\n\n'
            price = 0
            for position_id in set(user['user_cart'].split()):
                position = await db.get_menu_position(position_id)
                price += position["menu_position_price"] * user["user_cart"].split().count(position_id)
                text += f'<b>{position["menu_position_name"]}</b> {user["user_cart"].split().count(position_id)}шт. <b>{position["menu_position_price"] * user["user_cart"].split().count(position_id)}</b> руб\n'
            text += f'\nИтого: <b>{price}</b> руб\n'
            text += f'Адрес доставки: <b>{user["user_address"]}</b>\n'
            text += f'Телефон для связи: <b>{user["user_phone"]}</b>\n'
            text += 'Вам нужен звонок оператора?'
            if user['user_step'] == 'pay online':
                await callback.message.delete()
                await callback.message.answer_photo(media=FSInputFile(f'images/logo.jpg'), caption=text, reply_markup=await kb.need_call())
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=text), reply_markup=await kb.need_call())
            await db.update_user_step(callback.message.chat.id, '')
        # User hasn't phone number or delivery address
        else:
            if user['user_step'] == 'pay online':
                await callback.message.delete()
                await callback.message.answer_photo(media=FSInputFile(f'images/logo.jpg'), caption='Для заказа необходимо указать адрес доставки и контактный телефон в разделе Профиль', reply_markup=await kb.cart(user['user_cart']))
            else:
                await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Для заказа необходимо указать адрес доставки и контактный телефон в разделе Профиль'), reply_markup=await kb.cart(user['user_cart']))
            await db.update_user_step(callback.message.chat.id, '')

    # Need call button
    elif " ".join(callback.data.split()[:2]) == 'need call' and user['user_address'] and user['user_phone']:
        await db.update_user_step(callback.message.chat.id, '')
        await db.update_user_needs_call(callback.message.chat.id, callback.data.split()[-1])
        if user['user_cart']:
            for position_id in user['user_cart'].split():
                if not await db.get_menu_position(position_id) or position_id in await db.get_stop_list():
                    await db.remove_from_user_cart(callback.message.chat.id, position_id)
            user = await db.get_user_by_telegram_id(callback.message.chat.id)
            # Processing positions
            text = 'Ваш заказ\n\n'
            price = 0
            for position_id in set(user['user_cart'].split()):
                position = await db.get_menu_position(position_id)
                if position:
                    price += position["menu_position_price"] * user["user_cart"].split().count(position_id)
                    text += f'<b>{position["menu_position_name"]}</b> {user["user_cart"].split().count(position_id)}шт. <b>{position["menu_position_price"] * user["user_cart"].split().count(position_id)}</b> руб\n'
            text += f'\nИтого: <b>{price}</b> руб\n'
            text += f'Адрес доставки: <b>{user["user_address"]}</b>\n'
            text += f'Телефон для связи: <b>{user["user_phone"]}</b>\n'
            if callback.data.split()[-1] == 'True':
                text += f'Нужен звонок оператора\n'
            else:
                text += f'Звонок оператора не нужен\n'
            text += 'Выберите способ оплаты'
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=text), reply_markup=await kb.payment_method())
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Ваша корзина пока пуста'), reply_markup=await kb.cart(user['user_cart']))

    # Pay online button
    elif callback.data == 'pay online' and user['user_cart']:
        await db.update_user_step(callback.message.chat.id, 'pay online')
        price = 0
        text = ''
        # Checking if the position isn't in stop-list
        for position_id in user['user_cart'].split():
            if not await db.get_menu_position(position_id) or position_id in await db.get_stop_list():
                await db.remove_from_user_cart(callback.message.chat.id, position_id)
        user = await db.get_user_by_telegram_id(callback.message.chat.id)
        # Processing positions
        for position_id in set(user['user_cart'].split()):
            position = await db.get_menu_position(position_id)
            if position:
                price += position["menu_position_price"] * user["user_cart"].split().count(position_id)
                text += f'{position["menu_position_name"]} {user['user_cart'].split().count(position_id)}шт.\n'
        price = price * 100
        await callback.message.answer_invoice(title='Кафе',
                                              description=text,
                                              provider_token=PAYMENT_TOKEN,
                                              currency='rub',
                                              photo_url='https://i.ibb.co/qFJCjvpG/image.jpg',
                                              prices=[LabeledPrice(label="Оплатить", amount=price)],
                                              payload=f'{price}',
                                              reply_markup=await kb.pay_online(price))

    # Pay by card or pay by cash button
    elif callback.data in ['pay by card', 'pay by cash'] and user['user_cart']:
        await db.update_user_step(callback.message.chat.id, '')
        price = 0
        text = ''
        # Checking if the position isn't in stop-list
        for position_id in user['user_cart'].split():
            if not await db.get_menu_position(position_id) or position_id in await db.get_stop_list():
                await db.remove_from_user_cart(callback.message.chat.id, position_id)
        user = await db.get_user_by_telegram_id(callback.message.chat.id)
        # Processing positions
        for position_id in set(user['user_cart'].split()):
            position = await db.get_menu_position(position_id)
            price += position["menu_position_price"] * user["user_cart"].split().count(position_id)
            text += f'{position["menu_position_name"]} {user['user_cart'].split().count(position_id)}шт.\n'
        # Creating order
        order_id = await db.add_order(callback.message.chat.id, user['user_cart'], user['user_phone'], user['user_needs_call'], user['user_address'], datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=4))).strftime('%d.%m.%Y %H:%M'), price, callback.data)
        await db.clear_user_cart(callback.message.chat.id)
        operators = await db.get_staff_by_position('operator')
        order_operators = []
        # Sending messages to the operators
        for operator in operators:
            if operator['staff_telegram_id'] != 0:
                if callback.data == 'pay by card':
                    msg = await callback.message.bot.send_photo(chat_id=operator['staff_telegram_id'], photo=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order_id}</b> от {datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=4))).strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{price}</b> руб\nАдрес доставки: <b>{user["user_address"]}</b>\nТелефон для связи: <b>{user["user_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата картой', reply_markup=await kb.operator(order_id, 'None'))
                else:
                    msg = await callback.message.bot.send_photo(chat_id=operator['staff_telegram_id'], photo=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order_id}</b> от {datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=4))).strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{price}</b> руб\nАдрес доставки: <b>{user["user_address"]}</b>\nТелефон для связи: <b>{user["user_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата наличными', reply_markup=await kb.operator(order_id, 'None'))
                order_operators.append(f'{operator["staff_telegram_id"]}:{msg.message_id}')
        await db.update_order_operators(order_id, " ".join(order_operators))

        # Sending message to the user
        if callback.data == 'pay by card':
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Ваш заказ №<b>{order_id}</b> от {datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=4))).strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{price}</b> руб\nАдрес доставки: <b>{user["user_address"]}</b>\nТелефон для связи: <b>{user["user_phone"]}</b>\nОплата картой\nВаш заказ был успешно отправлен'), reply_markup=await kb.main_menu())
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Ваш заказ №<b>{order_id}</b> от {datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=4))).strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{price}</b> руб\nАдрес доставки: <b>{user["user_address"]}</b>\nТелефон для связи: <b>{user["user_phone"]}</b>\nОплата наличными\nВаш заказ был успешно отправлен'), reply_markup=await kb.main_menu())

    # Order add note button
    elif " ".join(callback.data.split()[:2]) == 'order note' and ('operator' in user['staff_positions'] or 'admin' in user['staff_positions']):
        await db.update_user_step(callback.message.chat.id, callback.data)
        order = await db.get_order(callback.data.split()[-1])
        await callback.message.bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"]}\n\nУкажите примечание к заказу')

    # Order processing button
    elif " ".join(callback.data.split()[:2]) == 'order processing' and 'operator' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        order = await db.get_order(callback.data.split()[-1])
        text = ''
        # Processing positions
        for position_id in set(user['user_cart'].split()):
            position = await db.get_menu_position(position_id)
            if position:
                text += f'{position["menu_position_name"]} {user['user_cart'].split().count(position_id)}шт.\n'
            else:
                text += f'УДАЛЕННАЯ ПОЗИЦИЯ {user['user_cart'].split().count(position_id)}шт.\n'
        # Sending messages to the operators
        for operator in order['order_operators'].split():
            if order['order_payment_method'] == 'pay by card':
                await callback.message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\n\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата картой\n\nОБРАБАТЫВАЕТСЯ'), reply_markup=await kb.operator(order['order_id'], 'processing'))
            elif order['order_payment_method'] == 'pay by cash':
                await callback.message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\n\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата наличными\n\nОБРАБАТЫВАЕТСЯ'), reply_markup=await kb.operator(order['order_id'], 'processing'))
            else:
                await callback.message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\n\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата онлайн\n\nОБРАБАТЫВАЕТСЯ'), reply_markup=await kb.operator(order['order_id'], 'processing'))

    # Order confirm button
    elif " ".join(callback.data.split()[:2]) == 'order confirm' and 'operator' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, '')
        order = await db.get_order(callback.data.split()[-1])
        text = ''
        # Processing positions
        for position_id in set(user['user_cart'].split()):
            position = await db.get_menu_position(position_id)
            if position:
                text += f'{position["menu_position_name"]} {user['user_cart'].split().count(position_id)}шт.\n'
            else:
                text += f'УДАЛЕННАЯ ПОЗИЦИЯ {user['user_cart'].split().count(position_id)}шт.\n'
        # Sending message to the operators
        for operator in order['order_operators'].split():
            if order['order_payment_method'] == 'pay by card':
                await callback.message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата картой\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН'), reply_markup=await kb.operator(order['order_id'], 'done'))
            elif order['order_payment_method'] == 'pay by cash':
                await callback.message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата наличными\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН'), reply_markup=await kb.operator(order['order_id'], 'done'))
            else:
                await callback.message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата онлайн\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН'), reply_markup=await kb.operator(order['order_id'], 'done'))
        # Sending messages to the kitchen
        kitchen = await db.get_staff_by_position('kitchen')
        order_kitchen = []
        for x in kitchen:
            if x['staff_telegram_id'] != 0:
                if order['order_payment_method'] == 'pay by card':
                    msg = await callback.message.bot.send_photo(chat_id=x['staff_telegram_id'], photo=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата картой\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН')
                elif order['order_payment_method'] == 'pay by cash':
                    msg = await callback.message.bot.send_photo(chat_id=x['staff_telegram_id'], photo=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата наличными\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН')
                else:
                    msg = await callback.message.bot.send_photo(chat_id=x['staff_telegram_id'], photo=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата онлайн\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nПОДТВЕРЖДЕН')
                order_kitchen.append(f'{x["staff_telegram_id"]}:{msg.message_id}')
        await db.update_order_kitchen(order['order_id'], " ".join(order_kitchen))

    # Order decline button
    elif " ".join(callback.data.split()[:2]) == 'order decline' and 'operator' in user['staff_positions']:
        await db.update_user_step(callback.message.chat.id, callback.data)
        order = await db.get_order(callback.data.split()[-1])
        text = ''
        # Processing positions
        for position_id in set(user['user_cart'].split()):
            position = await db.get_menu_position(position_id)
            if position:
                text += f'{position["menu_position_name"]} {user['user_cart'].split().count(position_id)}шт.\n'
            else:
                text += f'УДАЛЕННАЯ ПОЗИЦИЯ {user['user_cart'].split().count(position_id)}шт.\n'
        # Sending messages to the operators
        for operator in order['order_operators'].split():
            if order['order_payment_method'] == 'pay by card':
                await callback.message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата картой\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nОТМЕНЕН'), reply_markup=await kb.operator(order['order_id'], 'done'))
            elif order['order_payment_method'] == 'pay by cash':
                await callback.message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата наличными\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nОТМЕНЕН'), reply_markup=await kb.operator(order['order_id'], 'done'))
            else:
                await callback.message.bot.edit_message_media(chat_id=operator.split(':')[0], message_id=operator.split(':')[1], media=InputMediaPhoto(media=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{order["order_price"]}</b> руб\nАдрес доставки: <b>{order["order_address"]}</b>\nТелефон для связи: <b>{order["order_phone"]}</b>\n{"Нужен звонок оператора" if user["user_needs_call"] else "Звонок оператора не нужен"}\nОплата онлайн\n\nПРИМЕЧАНИЕ: {order["order_note"]}\n\nОТМЕНЕН'), reply_markup=await kb.operator(order['order_id'], 'done'))
        await callback.message.bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile('images/logo.jpg'), caption=f'Заказ {order["order_id"]} {order["order_date"]} ОТМЕНЕН\n\nУкажите причину отмены, которая будет видна пользователю')

    # My orders button
    elif callback.data == 'my orders':
        await db.update_user_step(callback.message.chat.id, '')
        orders = await db.get_user_orders(callback.message.chat.id)
        text = ''
        # Processing orders
        for order in orders:
            text += f'Ваш заказ №<b>{order["order_id"]}</b> от {order["order_date"].strftime('%d.%m.%Y %H:%M')}\n\n'
            for position_id in set(order['order_positions'].split()):
                position = await db.get_menu_position(position_id)
                if position:
                    text += f'<b>{position["menu_position_name"]}</b> {order['order_positions'].split().count(position_id)}шт.\n'
                else:
                    text += f'<b>УДАЛЕННАЯ ПОЗИЦИЯ</b> {order['order_positions'].split().count(position_id)}шт.\n'
            text += f'\nИтого: {order["order_price"]}руб'
            text += f'\nАдрес доставки: {order["order_address"]}'
            text += f'\nТелефон для связи: {order["order_phone"]}'
            if order['order_needs_call']:
                text += f'\nНужен звонок оператора\n\n'
            else:
                text += f'\nЗвонок оператора не нужен\n\n'
        if text == '':
            text = 'У Вас пока нет заказов'
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption=text), reply_markup=await kb.profile())


    else:
        await db.update_user_step(callback.message.chat.id, '')
        await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'images/logo.jpg'), caption='Привет! Добро пожаловать в бот'), reply_markup=await kb.menu('admin' in user['staff_positions']))

# Processing pre checkout
@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


# Processing successful payment
@router.message(F.successful_payment)
async def on_successful_payment(message: Message):
    # Getting user info, adding him to the database if he isn`t there yet
    user = await db.get_user_by_telegram_id(message.chat.id)
    if user is None:
        await db.add_user(message.chat.id)
    user = await db.get_user_by_telegram_id(message.chat.id)

    await db.update_user_step(message.chat.id, '')
    price = 0
    text = ''
    # Processing positions
    for position_id in set(user['user_cart'].split()):
        position = await db.get_menu_position(position_id)
        price += position["menu_position_price"] * user["user_cart"].split().count(position_id)
        text += f'{position["menu_position_name"]} {user['user_cart'].split().count(position_id)}шт.\n\n'
    # Creating order
    order_id = await db.add_order(message.chat.id, user['user_cart'], user['user_phone'], user['user_needs_call'], user['user_address'], datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=4))).strftime('%d.%m.%Y %H:%M'), price, 'pay online')
    await db.clear_user_cart(message.chat.id)
    # Sending messages to the operators
    operators = await db.get_staff_by_position('operator')
    order_operators = []
    for operator in operators:
        if operator['staff_telegram_id'] != 0:
            msg = await message.bot.send_photo(chat_id=operator['staff_telegram_id'], photo=FSInputFile('images/logo.jpg'), caption=f'Заказ №<b>{order_id}</b> от {datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=4))).strftime('%d.%m.%Y %H:%M')}\n\n{text}\n\nИтого: <b>{price}</b> руб\nАдрес доставки: <b>{user["user_address"]}</b>\nТелефон для связи: <b>{user["user_phone"]}</b>\nОплата онлайн', reply_markup=await kb.operator(order_id, 'processing'))
            order_operators.append(f'{operator["staff_telegram_id"]}:{msg.message_id}')
    await db.update_order_operators(order_id, " ".join(order_operators))

    # Sending message to the user
    await message.bot.send_photo(chat_id=message.chat.id, photo=FSInputFile('images/logo.jpg'), caption=f'Ваш заказ №<b>{order_id}</b> от {datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=4))).strftime('%d.%m.%Y %H:%M')}\n\n{text}\nИтого: <b>{price}</b> руб\nАдрес доставки: <b>{user["user_address"]}</b>\nТелефон для связи: <b>{user["user_phone"]}</b>\nОплата онлайн\nВаш заказ был успешно отправлен', reply_markup=await kb.main_menu())
