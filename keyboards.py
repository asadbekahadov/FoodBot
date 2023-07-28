from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import db

def generate_start_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    markup.row(
        KeyboardButton(text="📝 Asosiy menyu"),
    )
    markup.row(
        KeyboardButton(text="📜 Buyurtmalar tarixi"),
        KeyboardButton(text="🛒 Savatcha"),
    )
    
    return markup


def generate_categories_menu():
    categories = db.get_categories()
    # ( (1, "Lavash"), (2, "Burger"), ... )
    
    markup = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    start = 0
    end = 2
    in_row = 2
    
    rows = len(categories) // 2
    if len(categories) % 2 != 0:
        rows += 1
    
    
    for row in range(rows):
        buttons = []
        
        for category in categories[start:end]:
            buttons.append(
                InlineKeyboardButton(text=category[1], callback_data=f"category:{category[0]}")  # category:1
            )
        
        start = end
        end += in_row
        markup.row(*buttons)
    
    return markup


def generate_products_menu(category_id):
    categories = db.get_products(category_id=category_id)
    # ( (1, "Burger", ...), (2, "Lavash", ...), ... )
    
    markup = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    start = 0
    end = 2
    in_row = 2
    
    rows = len(categories) // 2
    if len(categories) % 2 != 0:
        rows += 1
    
    
    for row in range(rows):
        buttons = []
        
        for category in categories[start:end]:
            buttons.append(
                InlineKeyboardButton(text=category[1], callback_data=f"product:{category[0]}")  # category:1
            )
        
        start = end
        end += in_row
        markup.row(*buttons)
    
    return markup


def generate_product_order_menu(product_id, quantity=1):
    markup = InlineKeyboardMarkup()
    
    markup.row(
        InlineKeyboardButton(text="-", callback_data=f"order:{product_id}:{quantity}:minus"),
        InlineKeyboardButton(text=f"{quantity}", callback_data=f"order:{product_id}:{quantity}:show"),
        InlineKeyboardButton(text="+", callback_data=f"order:{product_id}:{quantity}:plus"),
    )
    
    markup.row(
        InlineKeyboardButton(text="🛒 Buyurtma berish", callback_data=f"order:{product_id}:{quantity}:order")
    )

    return markup


def generate_cart_buttons():
    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(text="Buyurtma berish", callback_data="cart-order")
    )
    markup.row(
        InlineKeyboardButton(text="Savatchani tozalash", 
                             callback_data="clear-cart")
    )

    return markup