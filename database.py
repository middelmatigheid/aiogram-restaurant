# Dotenv
import os
from dotenv import load_dotenv

# Datetime
import datetime

# PostgreSQL
import psycopg2


# Loading .env file
load_dotenv()

# Connecting to the database
HOST = os.getenv('HOST')
DBNAME = os.getenv('DBNAME')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
PORT = os.getenv('PORT')
connection = psycopg2.connect(host=HOST, dbname=DBNAME, user=USER, password=PASSWORD, port=PORT)


# Deleting tables
async def delete_tables():
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS users, staff, new_staff, menu_sections, menu_subsections, menu_positions, new_menu_position, stop_list, orders;")
        connection.commit()


# Creating tables
async def create_tables():
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users("  # Table stores info about users
                       "user_telegram_id INTEGER PRIMARY KEY, "  # User's telegram id 
                       "user_step TEXT, "  # User's current step 
                       "user_name TEXT, "  # User's name
                       "user_phone TEXT, "  # User's phone number for contact
                       "user_address TEXT, "  # User's address for delivery
                       "user_cart TEXT, "  # Menu positions, which user has chosen, separated by space
                       "user_balance INTEGER, "  # User's loyalty balance CURRENTLY NOT USED
                       "user_login TEXT,"  # Last login, which user has used for authorizing in admin panel
                       "user_needs_call BOOLEAN);")  # If user needs operator's call

        cursor.execute("CREATE TABLE IF NOT EXISTS staff("  # Table stores info about staff
                       "staff_login TEXT PRIMARY KEY, "  # Staff's login
                       "staff_password TEXT, "  # Staff's password
                       "staff_name TEXT, "  # Staff's name
                       "staff_position TEXT, "  # Staff's position
                       "staff_telegram_id INTEGER);")  # User's telegram id, who was authorized by this login

        cursor.execute("CREATE TABLE IF NOT EXISTS new_staff("  # Table stores info about new staff, who are currently appending
                       "admin_telegram_id INTEGER PRIMARY KEY, "  # Admin's telegram id, who are appending staff
                       "staff_login TEXT, "  # Staff's login
                       "staff_password TEXT, "  # Staff's password
                       "staff_name TEXT, "  # Staff's name
                       "staff_position TEXT);")  # Staff's position

        cursor.execute("CREATE TABLE IF NOT EXISTS menu_sections("  # Table stores info about menu sections
                       "menu_section_id SERIAL PRIMARY KEY, "  # Menu section's id
                       "menu_section_name TEXT);")  # Menu section's name

        cursor.execute("CREATE TABLE IF NOT EXISTS menu_subsections("  # Table stores info about menu subsections
                       "menu_subsection_id SERIAL PRIMARY KEY, "  # Menu subsection's id
                       "menu_section_id INTEGER, "  # Parent menu section's id, where subsection is stored
                       "menu_subsection_name TEXT);")  # Menu subsection's name

        cursor.execute("CREATE TABLE IF NOT EXISTS menu_positions("  # Table stores info about menu positions
                       "menu_position_id SERIAL PRIMARY KEY, "  # Menu position's id
                       "menu_section_id INTEGER, "  # Parent menu section's id, where position is stored
                       "menu_subsection_id INTEGER, "  # Parent menu subsection's id, where position is stored
                       "menu_position_name TEXT, "  # Menu position's name
                       "menu_position_description TEXT,"  # Menu position's description
                       "menu_position_weight TEXT, "  # Menu position's weight
                       "menu_position_price INTEGER);")  # Menu position's price

        cursor.execute("CREATE TABLE IF NOT EXISTS new_menu_position("  # Table stores info about new menu positions, which are currently appending
                       "admin_telegram_id INTEGER PRIMARY KEY, "  # Admin's telegram id, who are appending position
                       "menu_section_id INTEGER, "  # Parent menu section's id, where position is stored
                       "menu_subsection_id INTEGER, "  # Parent menu subsection's id, where position is stored
                       "menu_position_name TEXT, "  # Menu position's name
                       "menu_position_description TEXT,"  # Menu position's description
                       "menu_position_weight TEXT, "  # Menu position's weight
                       "menu_position_price INTEGER);")  # Menu position's price

        cursor.execute("CREATE TABLE IF NOT EXISTS stop_list("
                       "menu_position_id INTEGER PRIMARY KEY)")  # Menu position's id which is in stop list

        cursor.execute("CREATE TABLE IF NOT EXISTS orders("  # Table stores info about orders
                       "order_id SERIAL PRIMARY KEY, "  # Order's id
                       "user_telegram_id INTEGER, "  # User's telegram id, who has ordered
                       "order_positions TEXT, "  # Order's menu positions' ids
                       "order_phone TEXT, "  # User's phone for contact
                       "order_needs_call BOOLEAN, "  # If user needs operator's call
                       "order_address TEXT, "  # Order's address for delivery
                       "order_date TEXT, "  # Order's date in format %d.%m.%Y %H:%M
                       "order_price INTEGER, "  # Order's price
                       "order_payment_method TEXT, "  # Order's payment method
                       "order_operators TEXT, "  # Operators telegram ids and message ids to edit
                       "order_kitchen TEXT, "  # Kitchen telegram ids and message ids to edit
                       "order_note TEXT);")  # Order's additional note

        connection.commit()


# Adding new user
async def add_user(user_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO users (user_telegram_id, user_step, user_name, user_phone, user_address, user_cart, user_balance, user_login, user_needs_call)"
                       f"VALUES ({user_telegram_id}, '', '', '', '', '', 0, '', True);")
        connection.commit()


# Updating user's step
async def update_user_step(user_telegram_id, user_step):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE users SET user_step = '{user_step}' WHERE user_telegram_id = {user_telegram_id};")
        connection.commit()


# Updating user's name
async def update_user_name(user_telegram_id, user_name):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE users SET user_name = '{user_name}' WHERE user_telegram_id = {user_telegram_id};")
        connection.commit()


# Updating user's phone
async def update_user_phone(user_telegram_id, user_phone):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE users SET user_phone = '{user_phone}' WHERE user_telegram_id = {user_telegram_id};")
        connection.commit()


# Updating user's address
async def update_user_address(user_telegram_id, user_address):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE users SET user_address = '{user_address}' WHERE user_telegram_id = {user_telegram_id};")
        connection.commit()


# Adding menu position to user's cart
async def add_to_user_cart(user_telegram_id, menu_position):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT user_cart FROM users WHERE user_telegram_id = {user_telegram_id};")
        user_cart = cursor.fetchone()[0]
        if not user_cart:
            cursor.execute(f"UPDATE users SET user_cart = '{menu_position}' WHERE user_telegram_id = {user_telegram_id};")
        else:
            cursor.execute(f"UPDATE users SET user_cart = '{user_cart} {menu_position}' WHERE user_telegram_id = {user_telegram_id};")
        connection.commit()


# Removing menu position from user's cart
async def remove_from_user_cart(user_telegram_id, menu_position):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT user_cart FROM users WHERE user_telegram_id = {user_telegram_id};")
        user_cart = cursor.fetchone()[0]
        if user_cart and menu_position in user_cart[0]:
            user_cart = user_cart.split()
            user_cart.remove(menu_position)
            user_cart = " ".join(user_cart)
            cursor.execute(f"UPDATE users SET user_cart = '{user_cart}' WHERE user_telegram_id = {user_telegram_id};")
        connection.commit()


# Clearing user's cart
async def clear_user_cart(user_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE users SET user_cart = '' WHERE user_telegram_id = {user_telegram_id};")
        connection.commit()


# Updating user's login
async def update_user_login(user_telegram_id, user_login):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE users SET user_login = '{user_login}' WHERE user_telegram_id = {user_telegram_id};")
        connection.commit()


# Updating user's needs call
async def update_user_needs_call(user_telegram_id, user_needs_call):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE users SET user_needs_call = {user_needs_call} WHERE user_telegram_id = {user_telegram_id};")
        connection.commit()


# Getting user's info
async def get_user_by_telegram_id(user_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM users WHERE user_telegram_id = {user_telegram_id};")
        user = cursor.fetchone()
        if user:
            # Transforming data to a dictionary
            user_dict = {}
            user_keys = ['user_telegram_id', 'user_step', 'user_name', 'user_phone', 'user_address', 'user_cart', 'user_balance', 'user_login', 'user_needs_call']
            for i in range(len(user_keys)):
                user_dict[user_keys[i]] = user[i]
            cursor.execute(f"SELECT staff_position FROM staff WHERE staff_telegram_id = {user_telegram_id};")
            positions = cursor.fetchall()
            if positions:
                user_dict['staff_positions'] = [x[0] for x in positions]
            else:
                user_dict['staff_positions'] = []
            user = user_dict
        return user


# Adding new staff
async def add_staff(staff_login, staff_password, staff_name, staff_position):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO staff (staff_login, staff_password, staff_name, staff_position, staff_telegram_id) "
                       f"VALUES ('{staff_login}', '{staff_password}', '{staff_name}', '{staff_position}', 0);")
        connection.commit()


# Updating staff's telegram id
async def update_staff_telegram_id(staff_login, staff_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE staff SET staff_telegram_id = {staff_telegram_id} WHERE staff_login = '{staff_login}';")
        connection.commit()


# Updating staff's name
async def update_staff_name(staff_login, staff_name):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE staff SET staff_name = '{staff_name}' WHERE staff_login = '{staff_login}';")
        connection.commit()


# Logout staff from all positions
async def staff_logout(staff_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE staff set staff_telegram_id = 0 WHERE staff_telegram_id = {staff_telegram_id};")
        connection.commit()


# Getting staff's info
async def get_staff_by_login(staff_login):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM staff WHERE staff_login = '{staff_login}';")
        staff = cursor.fetchone()
        if staff:
            # Transforming data to a dictionary
            staff_dict = {}
            staff_keys = ['staff_login', 'staff_password', 'staff_name', 'staff_position', 'staff_telegram_id']
            for i in range(len(staff_keys)):
                staff_dict[staff_keys[i]] = staff[i]
            staff = staff_dict
        return staff


# Getting staff's info in certain position
async def get_staff_by_position(staff_position):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM staff WHERE staff_position = '{staff_position}';")
        staff = cursor.fetchall()
        if staff:
            # Transforming data to a dictionary
            staff_arr = []
            for x in staff:
                x_dict = {}
                x_keys = ['staff_login', 'staff_password', 'staff_name', 'staff_position', 'staff_telegram_id']
                for i in range(len(x_keys)):
                    x_dict[x_keys[i]] = x[i]
                staff_arr.append(x_dict)
            staff = staff_arr
        return staff


# Deleting staff
async def delete_staff(staff_login):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM staff WHERE staff_login = '{staff_login}';")
        connection.commit()


# Initializing adding new staff
async def add_new_staff(admin_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO new_staff (admin_telegram_id, staff_login, staff_password, staff_name, staff_position)"
                       f"VALUES ({admin_telegram_id}, '', '', '', '');")
        connection.commit()


# Updating new staff's login
async def update_new_staff_login(admin_telegram_id, staff_login):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_staff SET staff_login = '{staff_login}' WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Updating new staff's password
async def update_new_staff_password(admin_telegram_id, staff_password):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_staff SET staff_password = '{staff_password}' WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Updating new staff's name
async def update_new_staff_name(admin_telegram_id, staff_name):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_staff SET staff_name = '{staff_name}' WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Updating new staff's login
async def update_new_staff_position(admin_telegram_id, staff_position):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_staff SET staff_position = '{staff_position}' WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Getting new staff's info
async def get_new_staff(admin_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM new_staff WHERE admin_telegram_id = {admin_telegram_id};")
        new_staff = cursor.fetchone()
        if new_staff:
            # Transforming data to a dictionary
            new_staff_dict = {}
            new_staff_keys = ['admin_telegram_id', 'staff_login', 'staff_password', 'staff_name', 'staff_position']
            for i in range(len(new_staff_keys)):
                new_staff_dict[new_staff_keys[i]] = new_staff[i]
            new_staff = new_staff_dict
        return new_staff


# Adding menu section
async def add_menu_section(menu_section_name):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO menu_sections (menu_section_name) VALUES ('{menu_section_name}');")
        connection.commit()


# Updating menu section's name
async def update_menu_section(menu_section_id, menu_section_name):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE menu_sections SET menu_section_name = '{menu_section_name}' WHERE menu_section_id = {menu_section_id};")
        connection.commit()


# Getting menu section info
async def get_menu_section_info(menu_section_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM menu_sections WHERE menu_section_id = {menu_section_id};")
        menu_section = cursor.fetchone()
        if menu_section:
            menu_section_dict = {}
            menu_section_keys = ['menu_section_id', 'menu_section_name']
            for i in range(len(menu_section_keys)):
                menu_section_dict[menu_section_keys[i]] = menu_section[i]
            menu_section = menu_section_dict
        return menu_section


# Getting menu section
async def get_menu_section(menu_section_id):
    with connection.cursor() as cursor:
        # Checking if menu section stores menu subsections
        cursor.execute(f"SELECT menu_subsection_id, menu_subsection_name FROM menu_subsections WHERE menu_section_id = {menu_section_id};")
        menu_subsections = cursor.fetchall()
        if menu_subsections:
            # Transforming data to a dictionary
            menu_subsections_arr = []
            for x in menu_subsections:
                x_dict = {}
                x_keys = ['menu_subsection_id', 'menu_subsection_name']
                for i in range(len(x_keys)):
                    x_dict[x_keys[i]] = x[i]
                menu_subsections_arr.append(x_dict)
            menu_subsections = sorted(menu_subsections_arr, key=lambda x: x['menu_subsection_id'])
            return ['menu subsections', menu_subsections]

        # Checking if menu section stores menu positions
        cursor.execute(f"SELECT menu_position_id, menu_position_name FROM menu_positions WHERE menu_section_id = {menu_section_id};")
        menu_positions = cursor.fetchall()
        if menu_positions:
            # Transforming data to a dictionary
            menu_positions_arr = []
            for x in menu_positions:
                x_dict = {}
                x_keys = ['menu_position_id', 'menu_position_name']
                for i in range(len(x_keys)):
                    x_dict[x_keys[i]] = x[i]
                menu_positions_arr.append(x_dict)
            menu_positions = sorted(menu_positions_arr, key=lambda x: x['menu_position_id'])
            return ['menu positions', menu_positions]

        # Empty menu section
        return None


# Getting all menu sections
async def get_menu_sections():
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT menu_section_id, menu_section_name FROM menu_sections;")
        menu_sections = cursor.fetchall()
        if menu_sections:
            # Transforming data to a dictionary
            menu_sections_arr = []
            for x in menu_sections:
                x_dict = {}
                x_keys = ['menu_section_id', 'menu_section_name']
                for i in range(len(x_keys)):
                    x_dict[x_keys[i]] = x[i]
                menu_sections_arr.append(x_dict)
            menu_sections = sorted(menu_sections_arr, key=lambda x: x['menu_section_id'])
        return menu_sections


# Deleting menu section
async def delete_menu_section(menu_section_id):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM menu_sections WHERE menu_section_id = {menu_section_id};")
        cursor.execute(f"DELETE FROM menu_subsections WHERE menu_section_id = {menu_section_id};")
        positions = cursor.fetchall()
        cursor.execute(f"DELETE FROM menu_positions WHERE menu_section_id = {menu_section_id};")
        for menu_position_id in positions:
            if os.path.exists(f'images/positions/{menu_position_id}.jpg'):
                os.remove(f'images/positions/{menu_position_id}.jpg')
        connection.commit()


# Adding menu subsection
async def add_menu_subsection(menu_section_id, menu_subsection_name):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO menu_subsections (menu_section_id, menu_subsection_name) VALUES ({menu_section_id}, '{menu_subsection_name}');")
        connection.commit()
        cursor.execute(f"SELECT MAX(menu_subsection_id) FROM menu_subsections WHERE menu_section_id = {menu_section_id} AND menu_subsection_name = '{menu_subsection_name}';")
        return cursor.fetchone()[0]


# Updating menu subsection's name
async def update_menu_subsection(menu_subsection_id, menu_subsection_name):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE menu_subsections SET menu_subsection_name = '{menu_subsection_name}' WHERE menu_subsection_id = {menu_subsection_id};")
        connection.commit()


# Getting menu subsection info
async def get_menu_subsection_info(menu_subsection_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM menu_subsections WHERE menu_subsection_id = {menu_subsection_id};")
        menu_subsection = cursor.fetchone()
        if menu_subsection:
            menu_subsection_dict = {}
            menu_subsection_keys = ['menu_subsection_id', 'menu_section_id', 'menu_subsection_name']
            for i in range(len(menu_subsection_keys)):
                menu_subsection_dict[menu_subsection_keys[i]] = menu_subsection[i]
            menu_subsection = menu_subsection_dict
        return menu_subsection


# Getting menu subsection
async def get_menu_subsection(menu_subsection_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT menu_position_id, menu_position_name FROM menu_positions WHERE menu_subsection_id = {menu_subsection_id};")
        menu_positions = cursor.fetchall()
        if menu_positions:
            # Transforming data to a dictionary
            menu_positions_arr = []
            for x in menu_positions:
                x_dict = {}
                x_keys = ['menu_position_id', 'menu_position_name']
                for i in range(len(x_keys)):
                    x_dict[x_keys[i]] = x[i]
                menu_positions_arr.append(x_dict)
            menu_positions = sorted(menu_positions_arr, key=lambda x: x['menu_position_id'])
        return menu_positions


# Deleting menu subsection
async def delete_menu_subsection(menu_subsection_id):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM menu_subsections WHERE menu_subsection_id = {menu_subsection_id};")
        cursor.execute(f"SELECT menu_position_id FROM menu_positions WHERE WHERE menu_subsection_id = {menu_subsection_id};")
        positions = cursor.fetchall()
        cursor.execute(f"DELETE FROM menu_positions WHERE menu_subsection_id = {menu_subsection_id};")
        for menu_position_id in positions:
            if os.path.exists(f'images/positions/{menu_position_id}.jpg'):
                os.remove(f'images/positions/{menu_position_id}.jpg')
        connection.commit()


# Adding menu position
async def add_menu_position(menu_section_id, menu_subsection_id, menu_position_name, menu_position_description, menu_position_weight, menu_position_price):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO menu_positions (menu_section_id, menu_subsection_id, menu_position_name, menu_position_description, menu_position_weight, menu_position_price)"
                       f"VALUES ({menu_section_id}, {menu_subsection_id}, '{menu_position_name}', '{menu_position_description}', '{menu_position_weight}', {menu_position_price});")
        connection.commit()
        cursor.execute(f"SELECT MAX(menu_position_id) FROM menu_positions WHERE menu_section_id = {menu_section_id} AND menu_subsection_id = {menu_subsection_id} AND "
                       f"menu_position_name = '{menu_position_name}' AND menu_position_description = '{menu_position_description}' AND "
                       f"menu_position_weight = '{menu_position_weight}' AND menu_position_price = {menu_position_price};")
        return cursor.fetchone()[0]


# Updating menu position name
async def update_menu_position_name(menu_position_id, menu_position_name):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE menu_positions SET menu_position_name = '{menu_position_name}' WHERE menu_position_id = {menu_position_id};")
        connection.commit()


# Updating menu position description
async def update_menu_position_description(menu_position_id, menu_position_description):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE menu_positions SET menu_position_description = '{menu_position_description}' WHERE menu_position_id = {menu_position_id};")
        connection.commit()


# Updating menu position weight
async def update_menu_position_weight(menu_position_id, menu_position_weight):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE menu_positions SET menu_position_weight = '{menu_position_weight}' WHERE menu_position_id = {menu_position_id};")
        connection.commit()


# Updating menu position price
async def update_menu_position_price(menu_position_id, menu_position_price):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE menu_positions SET menu_position_price = {menu_position_price} WHERE menu_position_id = {menu_position_id};")
        connection.commit()


# Getting menu position
async def get_menu_position(menu_position_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM menu_positions WHERE menu_position_id = {menu_position_id};")
        menu_position = cursor.fetchone()
        if menu_position:
            # Transforming data to a dictionary
            menu_position_dict = {}
            menu_position_keys = ['menu_position_id', 'menu_section_id', 'menu_subsection_id', 'menu_position_name', 'menu_position_description', 'menu_position_weight', 'menu_position_price']
            for i in range(len(menu_position_keys)):
                menu_position_dict[menu_position_keys[i]] = menu_position[i]
            menu_position = menu_position_dict
        return menu_position


# Deleting menu position
async def delete_menu_position(menu_position_id):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM menu_positions WHERE menu_position_id = {menu_position_id};")
        if os.path.exists(f'images/positions/{menu_position_id}.jpg'):
            os.remove(f'images/positions/{menu_position_id}.jpg')
        connection.commit()


# Adding new menu position
async def add_new_menu_position(admin_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO new_menu_position (admin_telegram_id, menu_section_id, menu_subsection_id, menu_position_name, menu_position_description, menu_position_weight, menu_position_price)"
                       f"VALUES ({admin_telegram_id}, 0, 0, '', '', '', 0);")
        connection.commit()


# Update new menu position's section id
async def update_new_menu_position_section_id(admin_telegram_id, menu_section_id):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_menu_position SET menu_section_id = {menu_section_id} WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Update new menu position's subsection id
async def update_new_menu_position_subsection_id(admin_telegram_id, menu_subsection_id):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_menu_position SET menu_subsection_id = {menu_subsection_id} WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Update new menu position's name
async def update_new_menu_position_name(admin_telegram_id, menu_position_name):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_menu_position SET menu_position_name = '{menu_position_name}' WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Update new menu position's description
async def update_new_menu_position_description(admin_telegram_id, menu_position_description):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_menu_position SET menu_position_description = '{menu_position_description}' WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Update new menu position's weight
async def update_new_menu_position_weight(admin_telegram_id, menu_position_weight):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_menu_position SET menu_position_weight = '{menu_position_weight}' WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Update new menu position's price
async def update_new_menu_position_price(admin_telegram_id, menu_position_price):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE new_menu_position SET menu_position_price = {menu_position_price} WHERE admin_telegram_id = {admin_telegram_id};")
        connection.commit()


# Getting new menu position
async def get_new_menu_position(admin_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM new_menu_position WHERE admin_telegram_id = {admin_telegram_id};")
        new_menu_position = cursor.fetchone()
        if new_menu_position:
            # Transforming data to a dictionary
            new_menu_position_dict = {}
            new_menu_position_keys = ['admin_telegram_id', 'menu_section_id', 'menu_subsection_id', 'menu_position_name', 'menu_position_description', 'menu_position_weight', 'menu_position_price']
            for i in range(len(new_menu_position_keys)):
                new_menu_position_dict[new_menu_position_keys[i]] = new_menu_position[i]
            new_menu_position = new_menu_position_dict
        return new_menu_position


# Adding new position to a stop list
async def add_to_stop_list(menu_position_id):
    with connection.cursor() as cursor:
        if menu_position_id not in await get_stop_list():
            cursor.execute(f"INSERT INTO stop_list (menu_position_id) VALUES ({menu_position_id});")
            connection.commit()


# Removing position from a stop list
async def remove_from_stop_list(menu_position_id):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM stop_list WHERE menu_position_id = {menu_position_id};")
        connection.commit()


# Clear stop list
async def clear_stop_list():
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM stop_list;")
        connection.commit()


# Getting stop list
async def get_stop_list():
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT menu_position_id FROM stop_list;")
        stop_list = cursor.fetchall()
        if stop_list:
            stop_list = [x[0] for x in stop_list]
        print(stop_list)
        return stop_list


# Adding new order
async def add_order(user_telegram_id, order_positions, order_phone, order_needs_call, order_address, order_date, order_price, order_payment_method):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO orders (user_telegram_id, order_positions, order_phone, order_needs_call, order_address, order_date, order_price, order_payment_method, order_operators, order_kitchen, order_note)"
                       f"VALUES ({user_telegram_id}, '{order_positions}', '{order_phone}', {order_needs_call}, '{order_address}', '{order_date}', {order_price}, '{order_payment_method}', '', '', '');")
        connection.commit()
        cursor.execute(f"SELECT MAX(order_id) FROM orders WHERE user_telegram_id = {user_telegram_id};")
        return cursor.fetchone()[0]


# Updating order's operators
async def update_order_operators(order_id, order_operators):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE orders SET order_operators = '{order_operators}' WHERE order_id = {order_id};")
        connection.commit()


# Updating order's kitchen
async def update_order_kitchen(order_id, order_kitchen):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE orders SET order_kitchen = '{order_kitchen}' WHERE order_id = {order_id};")
        connection.commit()


# Adding order's note
async def update_order_note(order_id, order_note):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE orders SET order_note = '{order_note}' WHERE order_id = {order_id};")
        connection.commit()


# Getting order
async def get_order(order_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM orders WHERE order_id = {order_id};")
        order = cursor.fetchone()
        if order:
            # Transforming data to a dictionary
            order_dict = {}
            order_keys = ['order_id', 'user_telegram_id', 'order_positions', 'order_phone', 'order_needs_call', 'order_address', 'order_date', 'order_price', 'order_payment_method', 'order_operators', 'order_kitchen', 'order_note']
            for i in range(len(order_keys)):
                order_dict[order_keys[i]] = order[i]
            order_dict['order_date'] = datetime.datetime.strptime(order_dict['order_date'], '%d.%m.%Y %H:%M')
            order = order_dict
        return order


# Getting user's orders
async def get_user_orders(user_telegram_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM orders WHERE user_telegram_id = {user_telegram_id};")
        orders = cursor.fetchall()
        if orders:
            # Transforming data to a dictionary
            orders_arr = []
            for x in orders:
                x_dict = {}
                x_keys = ['order_id', 'user_telegram_id', 'order_positions', 'order_phone', 'order_needs_call', 'order_address', 'order_date', 'order_price', 'order_payment_method', 'order_operators', 'order_kitchen', 'order_note']
                for i in range(len(x_keys)):
                    x_dict[x_keys[i]] = x[i]
                x_dict['order_date'] = datetime.datetime.strptime(x_dict['order_date'], '%d.%m.%Y %H:%M')
                orders_arr.append(x_dict)
            orders = sorted(orders_arr, key=lambda x: x['order_date'], reverse=True)[:5]
        return orders
