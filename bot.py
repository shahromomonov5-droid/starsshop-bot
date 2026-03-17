from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ChatMember
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8484695622:AAHrg3LDvCzUE_2rCEM3uOFmnRRMVhk-wkI"
ADMIN_IDS = [6316039013]
CHANNEL_IDS = ["@shaxrom_25", "@olimjon_rahimov"]
STAR_PRICE = 210
KARTA_RAQAM = "5614 6821 1298 8300"
KARTA_EGASI = "Omonqulov Shahrom"
ADMIN_USERNAME = "@Shakxrom"
REFERRAL_BONUS = 400

orders = {}
order_counter = [0]
user_state = {}
payment_history = []
users = {}

def get_user(user_id, username=None, first_name=None):
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "referrals": 0,
            "username": username or str(user_id),
            "first_name": first_name or "Foydalanuvchi"
        }
    return users[user_id]

async def check_subscription(bot, user_id):
    try:
        for channel in CHANNEL_IDS:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        return True
    except Exception as e:
        print(f"Subscription check error: {e}")
        return False

async def sub_required(update_or_query, context, is_callback=False):
    if is_callback:
        user_id = update_or_query.from_user.id
    else:
        user_id = update_or_query.effective_user.id

    is_sub = await check_subscription(context.bot, user_id)
    if not is_sub:
        keyboard = [
            [InlineKeyboardButton("📢 1-kanal: @shaxrom_25", url="https://t.me/shaxrom_25")],
            [InlineKeyboardButton("📢 2-kanal: @olimjon_rahimov", url="https://t.me/olimjon_rahimov")],
            [InlineKeyboardButton("✅ Obuna boldim, tekshirish", callback_data="check_subscription")],
        ]
        msg = "Botdan foydalanish uchun ikkala kanalga obuna boling!\n\n1 @shaxrom_25\n2 @olimjon_rahimov\n\nObunadan song tekshiring"
        if is_callback:
            try:
                await update_or_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await update_or_query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update_or_query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        return False
    return True

def main_keyboard():
    keyboard = [
        [KeyboardButton("⭐ Stars xarid qilish"), KeyboardButton("👑 Premium xarid qilish")],
        [KeyboardButton("🛒 Buyurtmalarim"), KeyboardButton("👥 Referal"), KeyboardButton("💵 Balans")],
        [KeyboardButton("ℹ️ Bot haqida"), KeyboardButton("📞 Boglanish")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user(user.id, user.username, user.first_name)

    args = context.args
    if args and args[0].startswith("ref_"):
        try:
            ref_id = int(args[0].split("_")[1])
            if ref_id != user.id and ref_id in users and "ref_by" not in user_data:
                user_data["ref_by"] = ref_id
        except:
            pass

    if not await sub_required(update, context):
        return

    if "ref_by" in user_data and not user_data.get("ref_bonus_given"):
        ref_id = user_data["ref_by"]
        if ref_id in users:
            users[ref_id]["balance"] += REFERRAL_BONUS
            users[ref_id]["referrals"] += 1
            user_data["ref_bonus_given"] = True
            try:
                await context.bot.send_message(
                    chat_id=ref_id,
                    text=f"Yangi referal!\n{user.first_name} botga qoshildi!\nBalansingizga {REFERRAL_BONUS} som qoshildi!"
                )
            except:
                pass

    await update.message.reply_text(
        f"Xush kelibsiz, {user.first_name}!\n\n"
        f"1 Star = {STAR_PRICE} som\n\n"
        "Telegram Stars tez va xavfsiz yetkazib beriladi!\n\n"
        "Quyidagi menyudan tanlang",
        reply_markup=main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = get_user(user_id, query.from_user.username, query.from_user.first_name)

    if query.data == "check_subscription":
        is_sub = await check_subscription(context.bot, user_id)
        if is_sub:
            if "ref_by" in user_data and not user_data.get("ref_bonus_given"):
                ref_id = user_data["ref_by"]
                if ref_id in users:
                    users[ref_id]["balance"] += REFERRAL_BONUS
                    users[ref_id]["referrals"] += 1
                    user_data["ref_bonus_given"] = True
                    try:
                        await context.bot.send_message(
                            chat_id=ref_id,
                            text=f"Yangi referal tasdiqlandi! Balansingizga {REFERRAL_BONUS} som qoshildi!"
                        )
                    except:
                        pass
            await query.edit_message_text("Obuna tasdiqlandi! Botdan foydalanishingiz mumkin.")
            await context.bot.send_message(
                chat_id=user_id,
                text=f"Xush kelibsiz, {query.from_user.first_name}!\n\n1 Star = {STAR_PRICE} som\n\nMenyudan tanlang",
                reply_markup=main_keyboard()
            )
        else:
            keyboard = [
                [InlineKeyboardButton("📢 1-kanal: @shaxrom_25", url="https://t.me/shaxrom_25")],
                [InlineKeyboardButton("📢 2-kanal: @olimjon_rahimov", url="https://t.me/olimjon_rahimov")],
                [InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription")],
            ]
            await query.edit_message_text(
                "Siz hali obuna bolmadingiz!\n\n1 @shaxrom_25\n2 @olimjon_rahimov\n\nAvval obuna boling",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return

    if not await sub_required(query, context, is_callback=True):
        return

    if query.data == "deposit":
        keyboard = [
            [InlineKeyboardButton("💳 Humo/UzCard", callback_data="dep_card")],
            [InlineKeyboardButton("👤 Admin orqali", callback_data="dep_admin")],
        ]
        await query.edit_message_text("Balans toldirish\n\nTolov usulini tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "dep_card":
        user_state[user_id] = "waiting_deposit_amount"
        await query.edit_message_text("Karta orqali toldirish\n\nQancha som toldirmoqchisiz?\nMinimum: 10,000 som\n\nRaqam kiriting:")

    elif query.data == "dep_admin":
        keyboard = [[InlineKeyboardButton(f"Admin: {ADMIN_USERNAME}", url="https://t.me/Shakxrom")]]
        await query.edit_message_text(f"Admin orqali toldirish\n\nAdmin: {ADMIN_USERNAME}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("dep_confirm_"):
        parts = query.data.split("_")
        uid = int(parts[2])
        amount = int(parts[3])
        if uid in users:
            users[uid]["balance"] += amount
        await context.bot.send_message(
            chat_id=uid,
            text=f"Balansingiz toldirildi!\n+{amount} som\nJoriy balans: {users.get(uid, {}).get('balance', 0)} som"
        )
        await query.edit_message_text(f"Tasdiqlandi. +{amount} som")

    elif query.data.startswith("dep_reject_"):
        uid = int(query.data.split("_")[2])
        await context.bot.send_message(chat_id=uid, text="Balans toldirish rad etildi.")
        await query.edit_message_text("Rad etildi.")

    elif query.data.startswith("buy_") and query.data != "buy_custom":
        amount = int(query.data.split("_")[1])
        price = amount * STAR_PRICE
        context.user_data["pending"] = {"type": "Stars", "amount": amount, "price": price, "label": f"{amount} Stars"}
        keyboard = [
            [InlineKeyboardButton("Ozim uchun", callback_data="receiver_self")],
            [InlineKeyboardButton("Boshqa birov uchun", callback_data="receiver_other")],
        ]
        await query.edit_message_text(
            f"{amount} Stars\nNarx: {price} som\n\nStars kim uchun?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "buy_custom":
        user_state[user_id] = "waiting_custom_amount"
        await query.edit_message_text("Nechta Stars olmoqchisiz?\n\nRaqam kiriting (masalan: 75):")

    elif query.data.startswith("prem_"):
        months = int(query.data.split("_")[1])
        prices = {1: 45000, 3: 120000, 6: 220000}
        price = prices[months]
        context.user_data["pending"] = {"type": "Premium", "amount": months, "price": price, "label": f"{months} oy Premium"}
        keyboard = [
            [InlineKeyboardButton("Ozim uchun", callback_data="receiver_self")],
            [InlineKeyboardButton("Boshqa birov uchun", callback_data="receiver_other")],
        ]
        await query.edit_message_text(
            f"{months} oy Premium\nNarx: {price} som\n\nKim uchun?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "receiver_self":
        username = query.from_user.username or query.from_user.first_name
        context.user_data["receiver"] = f"@{username} (ozi uchun)"
        await show_payment_method(query, context, user_id)

    elif query.data == "receiver_other":
        user_state[user_id] = "waiting_receiver_username"
        pending = context.user_data.get("pending", {})
        await query.edit_message_text(f"{pending.get('label', '')}\n\nQabul qiluvchining @username ni kiriting:")

    elif query.data == "pay_balance":
        pending = context.user_data.get("pending", {})
        price = pending.get("price", 0)
        if user_data["balance"] >= price:
            user_data["balance"] -= price
            order_counter[0] += 1
            order_id = order_counter[0]
            receiver = context.user_data.get("receiver", "---")
            orders[order_id] = {
                "user_id": user_id,
                "username": query.from_user.username or query.from_user.first_name,
                "receiver": receiver,
                **pending,
                "status": "waiting_confirm"
            }
            payment_history.append(orders[order_id])
            for admin_id in ADMIN_IDS:
                keyboard = [
                    [InlineKeyboardButton("Tasdiqlash", callback_data=f"confirm_pay_{order_id}"),
                     InlineKeyboardButton("Rad etish", callback_data=f"reject_pay_{order_id}")]
                ]
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"Balansdan tolov #{order_id}\n\n@{orders[order_id]['username']} (ID: {user_id})\n{pending['label']}\nQabul qiluvchi: {receiver}\n{price} som (balansdan)",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            await query.edit_message_text(
                f"Buyurtma #{order_id} qabul qilindi!\n\nBalansdan yechildi: {price} som\nQolgan balans: {user_data['balance']} som\n\nTez orada yetkazib beriladi!"
            )
        else:
            keyboard = [[InlineKeyboardButton("Balansni toldirish", callback_data="deposit")]]
            await query.edit_message_text(
                f"Balans yetarli emas!\n\nJoriy balans: {user_data['balance']} som\nKerakli summa: {price} som",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif query.data == "pay_card":
        pending = context.user_data.get("pending", {})
        receiver = context.user_data.get("receiver", "---")
        order_counter[0] += 1
        order_id = order_counter[0]
        orders[order_id] = {
            "user_id": user_id,
            "username": query.from_user.username or query.from_user.first_name,
            "receiver": receiver,
            **pending,
            "status": "waiting_payment"
        }
        user_state[user_id] = f"waiting_check_{order_id}"
        await query.edit_message_text(
            f"Tolov malumotlari:\n\nKarta: {KARTA_RAQAM}\nEgasi: {KARTA_EGASI}\n\nTolov miqdori: {pending['price']} som\n\nBuyurtma #{order_id}: {pending['label']}\nQabul qiluvchi: {receiver}\n\nTolov qilgandan song chek (screenshot) yuboring!"
        )

    elif query.data.startswith("confirm_pay_"):
        order_id = int(query.data.split("_")[2])
        if order_id in orders:
            orders[order_id]["status"] = "confirmed"
            uid = orders[order_id]["user_id"]
            label = orders[order_id]["label"]
            receiver = orders[order_id].get("receiver", "---")
            payment_history.append(orders[order_id])
            await context.bot.send_message(
                chat_id=uid,
                text=f"Tolovingiz tasdiqlandi!\n\n{label} tez orada yuboriladi!\nQabul qiluvchi: {receiver}\nXarid uchun rahmat!"
            )
            await query.edit_message_text(f"Buyurtma #{order_id} tasdiqlandi.")

    elif query.data.startswith("reject_pay_"):
        order_id = int(query.data.split("_")[2])
        if order_id in orders:
            orders[order_id]["status"] = "rejected"
            uid = orders[order_id]["user_id"]
            await context.bot.send_message(
                chat_id=uid,
                text=f"Buyurtma #{order_id} rad etildi.\nSavollar uchun: {ADMIN_USERNAME}"
            )
            await query.edit_message_text(f"Buyurtma #{order_id} rad etildi.")

async def show_payment_method(query, context, user_id):
    pending = context.user_data.get("pending", {})
    user_data = get_user(user_id)
    keyboard = [
        [InlineKeyboardButton(f"Balansdan ({user_data['balance']} som)", callback_data="pay_balance")],
        [InlineKeyboardButton("Karta orqali", callback_data="pay_card")],
    ]
    await query.edit_message_text(
        f"{pending.get('label', '')}\nNarx: {pending.get('price', 0)} som\nQabul qiluvchi: {context.user_data.get('receiver', '---')}\n\nTolov usulini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    state = user_state.get(user_id, "")
    user_data = get_user(user_id, update.effective_user.username, update.effective_user.first_name)

    if not state:
        if not await sub_required(update, context):
            return

    if text == "⭐ Stars xarid qilish":
        keyboard = [
            [InlineKeyboardButton(f"50 Stars - {50*STAR_PRICE} som", callback_data="buy_50")],
            [InlineKeyboardButton(f"100 Stars - {100*STAR_PRICE} som", callback_data="buy_100")],
            [InlineKeyboardButton(f"250 Stars - {250*STAR_PRICE} som", callback_data="buy_250")],
            [InlineKeyboardButton(f"500 Stars - {500*STAR_PRICE} som", callback_data="buy_500")],
            [InlineKeyboardButton(f"1000 Stars - {1000*STAR_PRICE} som", callback_data="buy_1000")],
            [InlineKeyboardButton("Ozim miqdor kiritaman", callback_data="buy_custom")],
        ]
        await update.message.reply_text(
            f"Stars narxlari:\n\n1 Star = {STAR_PRICE} som\n\nMiqdorni tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif text == "👑 Premium xarid qilish":
        keyboard = [
            [InlineKeyboardButton("1 oy - 45,000 som", callback_data="prem_1")],
            [InlineKeyboardButton("3 oy - 120,000 som", callback_data="prem_3")],
            [InlineKeyboardButton("6 oy - 220,000 som", callback_data="prem_6")],
        ]
        await update.message.reply_text("Telegram Premium narxlari:\n\nMuddatni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "🛒 Buyurtmalarim":
        user_orders = [(oid, o) for oid, o in orders.items() if o["user_id"] == user_id]
        if not user_orders:
            t = "Sizda hali buyurtma yoq."
        else:
            t = "Buyurtmalaringiz:\n\n"
            sm = {"waiting_payment": "Kutilmoqda", "waiting_confirm": "Tekshirilmoqda",
                  "confirmed": "Tasdiqlandi", "cancelled": "Bekor", "rejected": "Rad"}
            for oid, o in user_orders[-5:]:
                t += f"#{oid} - {o['label']} - {sm.get(o['status'], o['status'])}\n"
        await update.message.reply_text(t)

    elif text == "👥 Referal":
        bot_info = await context.bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
        keyboard = [[InlineKeyboardButton("Ulashish", url=f"https://t.me/share/url?url={ref_link}")]]
        await update.message.reply_text(
            f"Referal tizimi\n\nHar bir referal uchun: {REFERRAL_BONUS} som\nSizning referallaringiz: {user_data['referrals']} ta\nJami bonus: {user_data['referrals'] * REFERRAL_BONUS} som\n\nBonus faqat kanal obunasidan song beriladi.\n\nReferal linkingiz:\n{ref_link}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif text == "💵 Balans":
        keyboard = [[InlineKeyboardButton("Balansni toldirish", callback_data="deposit")]]
        await update.message.reply_text(
            f"Balansingiz\n\nID: {user_id}\nBalans: {user_data['balance']} som\n\nBalansni toldirish uchun pastdagi tugmani bosing!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif text == "ℹ️ Bot haqida":
        await update.message.reply_text(
            f"Bot haqida\n\n1 Star = {STAR_PRICE} som\nYetkazib berish: 5-30 daqiqa\nAdmin: {ADMIN_USERNAME}"
        )

    elif text == "📞 Boglanish":
        keyboard = [[InlineKeyboardButton(f"Admin: {ADMIN_USERNAME}", url="https://t.me/Shakxrom")]]
        await update.message.reply_text(
            f"Boglanish\n\nYordam kerakmi? Admin: {ADMIN_USERNAME}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif state == "waiting_custom_amount":
        if text.isdigit() and int(text) > 0:
            amount = int(text)
            price = amount * STAR_PRICE
            user_state.pop(user_id, None)
            context.user_data["pending"] = {"type": "Stars", "amount": amount, "price": price, "label": f"{amount} Stars"}
            keyboard = [
                [InlineKeyboardButton("Ozim uchun", callback_data="receiver_self")],
                [InlineKeyboardButton("Boshqa birov uchun", callback_data="receiver_other")],
            ]
            await update.message.reply_text(
                f"{amount} Stars\nNarx: {price} som\n\nStars kim uchun?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text("Togri raqam kiriting!")

    elif state == "waiting_receiver_username":
        username_input = text.strip()
        if not username_input.startswith("@"):
            username_input = "@" + username_input
        context.user_data["receiver"] = username_input
        user_state.pop(user_id, None)
        pending = context.user_data.get("pending", {})
        keyboard = [
            [InlineKeyboardButton(f"Balansdan ({user_data['balance']} som)", callback_data="pay_balance")],
            [InlineKeyboardButton("Karta orqali", callback_data="pay_card")],
        ]
        await update.message.reply_text(
            f"{pending.get('label', '')}\nNarx: {pending.get('price', 0)} som\nQabul qiluvchi: {username_input}\n\nTolov usulini tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif state.startswith("waiting_check_"):
        order_id = int(state.split("_")[2])
        if update.message.photo or update.message.document:
            orders[order_id]["status"] = "waiting_confirm"
            user_state.pop(user_id, None)
            username = update.effective_user.username or update.effective_user.first_name
            o = orders[order_id]
            for admin_id in ADMIN_IDS:
                keyboard = [
                    [InlineKeyboardButton("Tasdiqlash", callback_data=f"confirm_pay_{order_id}"),
                     InlineKeyboardButton("Rad etish", callback_data=f"reject_pay_{order_id}")]
                ]
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"Yangi tolov #{order_id}\n\n@{username} (ID: {user_id})\n{o['label']}\nQabul qiluvchi: {o.get('receiver','---')}\n{o['price']} som\n\nChek quyida",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if update.message.photo:
                    await context.bot.send_photo(chat_id=admin_id, photo=update.message.photo[-1].file_id)
                elif update.message.document:
                    await context.bot.send_document(chat_id=admin_id, document=update.message.document.file_id)
            await update.message.reply_text("Chekingiz qabul qilindi!\n\nAdmin tekshirib tasdiqlaydi.\n5-15 daqiqa.")
        else:
            await update.message.reply_text("Iltimos, tolov cheki (screenshot) yuboring!")

    elif state.startswith("waiting_deposit_check_"):
        amount = int(state.split("_")[3])
        if update.message.photo or update.message.document:
            user_state.pop(user_id, None)
            username = update.effective_user.username or update.effective_user.first_name
            for admin_id in ADMIN_IDS:
                keyboard = [
                    [InlineKeyboardButton(f"+{amount} som tasdiqlash", callback_data=f"dep_confirm_{user_id}_{amount}"),
                     InlineKeyboardButton("Rad etish", callback_data=f"dep_reject_{user_id}")]
                ]
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"Balans toldirish\n\n@{username} (ID: {user_id})\n{amount} som\n\nChek quyida",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                if update.message.photo:
                    await context.bot.send_photo(chat_id=admin_id, photo=update.message.photo[-1].file_id)
                elif update.message.document:
                    await context.bot.send_document(chat_id=admin_id, document=update.message.document.file_id)
            await update.message.reply_text("Chekingiz yuborildi! Admin tasdiqlashini kuting.")
        else:
            await update.message.reply_text("Chek (screenshot) yuboring!")

    elif state == "waiting_deposit_amount":
        if text.isdigit() and int(text) >= 10000:
            amount = int(text)
            user_state[user_id] = f"waiting_deposit_check_{amount}"
            await update.message.reply_text(
                f"Balans toldirish\n\nMiqdor: {amount} som\n\nKarta: {KARTA_RAQAM}\nEgasi: {KARTA_EGASI}\n\nTolovdan song chek yuboring!"
            )
        else:
            await update.message.reply_text("Minimum 10,000 som kiriting!")

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Sizda admin huquqi yoq!")
        return
    total = len(orders)
    pending = sum(1 for o in orders.values() if o["status"] == "waiting_confirm")
    confirmed = sum(1 for o in orders.values() if o["status"] == "confirmed")
    total_sum = sum(o["price"] for o in orders.values() if o["status"] == "confirmed")
    text = (
        f"Admin Panel\n\n"
        f"Foydalanuvchilar: {len(users)}\n"
        f"Jami buyurtmalar: {total}\n"
        f"Tekshirilmoqda: {pending}\n"
        f"Tasdiqlangan: {confirmed}\n"
        f"Jami tushum: {total_sum} som\n\n"
    )
    if pending > 0:
        text += "Kutilayotgan:\n"
        for oid, o in orders.items():
            if o["status"] == "waiting_confirm":
                text += f"#{oid} - @{o['username']} - {o['label']} - {o['price']} som\n"
    await update.message.reply_text(text)

async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Sizda admin huquqi yoq!")
        return
    if not payment_history:
        await update.message.reply_text("Tarix bosh.")
        return
    text = "Tolovlar tarixi:\n\n"
    for o in payment_history[-10:]:
        text += f"@{o['username']} - {o['label']} - {o['price']} som\n"
    await update.message.reply_text(text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("history", history_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
