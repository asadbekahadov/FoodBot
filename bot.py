from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.types import LabeledPrice

from database import db
from keyboards import (generate_start_menu, 
                       generate_categories_menu,
                        generate_products_menu,
                        generate_product_order_menu,
                        generate_cart_buttons,
                        generate_clear_users_orders_menu)


TOKEN = "5966178767:AAFHJyEUx4M9El6dQdRH5NGw72lr0LJrX-8"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)



@dp.message_handler(commands="start")
async def start(message: Message):
    fullname = message.from_user.full_name
    telegram_id = message.from_user.id
    
    try:
        db.register_user(telegram_id=telegram_id,
                        fullname=fullname)
        await message.answer(
            text=f"Assalomu alaykum, {fullname} ! Muvaffaqiyatli ro'yxatga olindingiz !",
            reply_markup=generate_start_menu())
    except:
        await message.answer(
            text=f"Assalomu alaykum, {fullname} ! Sizni qayta ko'rib turganimizdan xursandmiz !",
            reply_markup=generate_start_menu())
    
    

@dp.message_handler(Text(equals="📝 Asosiy menyu"))
async def show_categories_menu(message: Message):
    await message.answer(text="Biznin menyuda hozirda quyidagi kategoriyadagi maxsulotlar mavjud",
                         reply_markup=generate_categories_menu())
    

@dp.message_handler(Text(equals="🛒 Savatcha"))
async def show_user_cart(message: Message):
    telegram_id = message.from_user.id  # 71212121
    user_id = db.get_user(telegram_id=telegram_id)[0]  # (1, "Ulug'bek", ...)
    products = db.get_users_cart(user_id=user_id)
    
    if len(products) > 0:
        text = "=== Savatchangiz ===\n\n"
        
        counter = 0
        for product in products:
            counter += 1
            
            text += f"{counter}) {product[2]}\nNarxi: {product[-3]} so'm\nMiqdori: {product[-2]} ta\nUmumiy narxi: {product[-1]} so'm\n\n"
        
        await message.answer(text=text, reply_markup=generate_cart_buttons())
    else:
        await message.answer(text="Savatchangiz bosh🙄")


@dp.message_handler(Text(equals="📜 Buyurtmalar tarixi"))
async def show_orders_history(message: Message):
    telegram_id = message.from_user.id
    user_id = db.get_user(telegram_id=telegram_id)[0]
    
    orders = db.get_users_orders_history(user_id=user_id)
    
    text = "=== Buyurtmalar tarixi ===\n\n"
    
    if len(orders) > 0:
        counter = 0
        for order in orders:
            counter += 1
            text += f"{counter}. {'=' * 10}\n"
            text += f"Maxsulot nomi: {order[2]}\n"
            text += f"Miqdori: {order[-2]} ta\n"
            text += f"Narxi: {order[-1]} so'm\n\n"

        await message.answer(text=text, reply_markup=generate_clear_users_orders_menu())
    else:
        await message.answer(text="Buyurtmalar tarixingiz shundoq ham bo'sh 😕")


@dp.callback_query_handler(lambda call: 'clear-users-order' in call.data)
async def clear_users_orders(call: CallbackQuery):
    telegram_id = call.from_user.id
    user_id = db.get_user(telegram_id=telegram_id)[0]
    
    db.clear_users_orders(user_id=user_id)
    
    await call.message.delete()
    await call.answer(text="Buyurtmalar tarixingiz muvaffaqiyatli tozalandi", show_alert=True)


@dp.callback_query_handler(lambda call: "cart-order" in call.data)
async def cart_order(call: CallbackQuery):
    chat_id = call.from_user.id
    user_id = db.get_user()[0]

    cart = db.get_users_cart(user_id=user_id)

    check_title = "==Umumiy hisob=="
    total_price = 0
    for product in cart:
        total_price += product[-1]

    total_price = int(total_price * 100)
    await bot.send_invoice(
        chat_id=chat_id,
        title=check_title,
        description="Savatchangizdagi barcha mahsulotlar narxi",
        payload="...",
        currency="UZS",
        provider_token="398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065",
        prices=[
            LabeledPrice(label="Umumiy narx", amount=total_price),
            LabeledPrice(label="Yetkazib berish", amount=1000000)
        ]

    )

    for product in cart:
        db.register_order_history(user_id=user_id,
                                product_name=product[2],
                                quantity=product[-2],
                                total_price=product[-1])
    db.clear_users_cart(user_id=user_id)

    await call.message.delete()
    await call.message.answer(text="Savatchangizdagi maxsulotlar yeykazib berish uchun navbatga qoyildi va savatchangiz tozalandi")                                
        


@dp.callback_query_handler(lambda call: "clear-cart" in call.data)
async def clear_users_cart(call: CallbackQuery):
    telegram_id = call.from_user.id
    user_id = db.get_user(telegram_id=telegram_id)[0]

    db.clear_users_cart(user_id=user_id)
    await call.message.delete()
    await call.answer(text="Savatchangiz muvaffaqiyatli tozaklandi !", show_alert=True)




@dp.callback_query_handler(lambda call: "category" in call.data)
async def show_category_products(call: CallbackQuery):
    category_id = int(call.data.split(":")[-1])  
    # "category:1" -> ["category". "1"] -> "1"
    
    await call.message.delete()
    await call.message.answer(
        text="Siz tanlagan kategoriyaga mos barcha maxsulotlar",
        reply_markup=generate_products_menu(category_id=category_id)
    )


@dp.callback_query_handler(lambda call: "product" in call.data)
async def show_product_details(call: CallbackQuery):
    product_id = call.data.split(":")[-1]
    product = db.get_product(product_id=product_id)
    
    await call.message.delete()
    
    with open(file=product[-1], mode="r", encoding="UTF-8") as file:
        description = file.read()
        description += f"\n\nNarxi: {product[2]} so'm"
    
    title = f"{product[1]}\n\n"
    
    with open(file=product[-2], mode="rb") as photo:
        await call.message.answer_photo(
            photo=photo,
            caption=title + description,
            reply_markup=generate_product_order_menu(
                product_id=product_id,
            )
        )
    
    

@dp.callback_query_handler(lambda call: "order" in call.data)
async def product_order(call: CallbackQuery):
    telegram_id = call.from_user.id
    user_id = db.get_user(telegram_id=telegram_id)[0]
    # "order:1:1:minus".split(":") => ["order", "1", "1", "minus"]
    info = call.data.split(":")
    product_id = info[1]
    quantity = int(info[-2])
    action = info[-1]
    edited = False
    
    if action == "minus":
        if quantity > 1:
            quantity = quantity - 1
            edited = True
    
    elif action == "plus":
        quantity = quantity + 1
        edited = True
    
    elif action == "order":
        await call.message.answer(text=f"Maxsulot ID: {product_id}\nMiqdori: {quantity} ta")

        product_info = db.get_product(product_id = product_id)
        product_name = product_info[1]
        product_price = product_info[2]

    else:
        product = db.get_product(product_id=product_id)  # (1, "Lavash", 16000, ..., ...)
        product_name = product[1]
        product_price = product[2]
        
        await call.answer(text=f"Maxsulot: {product_name}\nNarxi: {product_price} so'm", show_alert=True)
    
    if edited:
        await call.message.edit_reply_markup(
            reply_markup=generate_product_order_menu(
                product_id=product_id,
                quantity=quantity,
            )
        )


executor.start_polling(dispatcher=dp, skip_updates=True)
