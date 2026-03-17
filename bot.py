from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ChatMember
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8484695622:AAHrg3LDvCzUE_2rCEM3uOFmnRRMVhk-wkI"
ADMIN_IDS = [6316039013]
CHANNEL_ID = "@shaxrom_25"
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
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Subscription check error: {e}")
        return False

async def sub_required(update_or_query, context, is_callback=False):
    """Obuna tekshirib, kerak bo'lsa xabar yuboradi. True = obuna bor"""
    if is_callback:
        user_id = update_or_query.from_user.id
    else:
        user_id = update_or_query.effective_user.id
    
    is_sub = await check_subscription(context.bot, user_id)
    if not is_sub:
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/shaxrom_25")],
            [InlineKeyboardButton("✅ Obuna bo'ldim, tekshirish", callback_data="check_subscription")],
        ]
        msg = "⚠️ Botdan foydalanish uchun kanalga obuna bo'ling!\n\n📢 @shaxrom_25\n\nObuna bo'lgach tekshiring 👇"
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
        [KeyboardButton("ℹ️ Bot haqida"), KeyboardButton("📞 Bog'lanish")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user(user.id, user.username, user.first_name)

    # Referral tekshirish
    args = context.args
    if args and args[0].startswith("ref_"):
        ref_id = int(args[0].split("_")[1])
        if ref_id != user.id and ref_id in users and "ref_by" not in user_data:
            user_data["ref_by"] = ref_id

    # Kanal obunasini tekshirish
    if not await sub_required(update, context):
        return

    # Referral bonus berish (obuna bo'lgandan keyin)
    if "ref_by" in user_data and not user_data.get("ref_bonus_given"):
        ref_id = user_data["ref_by"]
        if ref_id in users:
            users[ref_id]["balance"] += REFERRAL_BONUS
            users[ref_id]["referrals"] += 1
            user_data["ref_bonus_given"] = True
            try:
                await context.bot.send_message(
                    chat_id=ref_id,
                    text=f"🎉 Yangi referal!\n"
                         f"👤 @{user.username or user.first_name} botga qo'shildi!\n"
                         f"💰 Balansingizga {REFERRAL_BONUS:,} so'm qo'shildi!"
                )
            except:
                pass

    await update.message.reply_text(
        f"✨ Xush kelibsiz, {user.first_name}!\n\n"
        f"⭐ 1 Star = {STAR_PRICE:,} so'm\n\n"
        "Telegram Stars tez va xavfsiz yetkazib beriladi!\n\n"
        "Quyidagi menyudan tanlang 👇",
        reply_markup=main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = get_user(user_id, query.from_user.username, query.from_user.first_name)

    if query.data == "check_subscription":
        is_subscribed = await check_subscription(context.bot, user_id)
        if is_subscribed:
            # Referral bonus berish
            if "ref_by" in user_data and not user_data.get("ref_bonus_given"):
                ref_id = user_data["ref_by"]
                if ref_id in users:
                    users[ref_id]["balance"] += REFERRAL_BONUS
                    users[ref_id]["referrals"] += 1
                    user_data["ref_bonus_given"] = True
                    try:
                        await context.bot.send_message(
                            chat_id=ref_id,
                            text=f"🎉 Yangi referal tasdiqlandi!\n"
                                 f"💰 Balansingizga {REFERRAL_BONUS:,} so'm qo'shildi!"
                        )
                    except:
                        pass
            await query.edit_message_text(
                f"✅ Rahmat! Obuna tasdiqlandi!\n\n"
                f"Endi botdan to'liq foydalanishingiz mumkin.",
            )
            await context.bot.send_message(
                chat_id=user_id,
                text=f"✨ Xush kelibsiz, {query.from_user.first_name}!\n\n"
                     f"⭐ 1 Star = {STAR_PRICE:,} so'm\n\n"
                     "Quyidagi menyudan tanlang 👇",
                reply_markup=main_keyboard()
            )
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/shaxrom_25")],
                [InlineKeyboardButton("✅ Obuna bo'ldim, tekshirish", callback_data="check_subscription")],
            ]
            await query.edit_message_text(
                "❌ Siz hali obuna bo'lmadingiz!\n\n"
                f"📢 Kanal: @shaxrom_25\n\n"
                "Avval obuna bo'ling, keyin tekshiring 👇",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        return

    # Kanal obunasini tekshirish
    if query.data != "check_subscription":
        if not await sub_required(query, context, is_callback=True):
            return

    if query.data == "deposit":
        keyboard = [
            [InlineKeyboardButton("💳 Humo/UzCard", callback_data="dep_card")],
            [InlineKeyboardButton("👤 Admin orqali", callback_data="dep_admin")],
        ]
        await query.edit_message_text(
            "💵 *Balans to'ldirish*\n\nTo'lov usulini tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "dep_card":
        user_state[user_id] = "waiting_deposit_amount"
        await query.edit_message_text(
            f"💳 *Karta orqali to'ldirish*\n\n"
            f"Qancha so'm to'ldirmoqchisiz?\n(Minimum: 10,000 so'm)\n\nRaqam kiriting:",
            parse_mode="Markdown"
        )

    elif query.data == "dep_admin":
        keyboard = [[InlineKeyboardButton(f"💬 {ADMIN_USERNAME}", url="https://t.me/Shakxrom")]]
        await query.edit_message_text(
            f"👤 *Admin orqali to'ldirish*\n\nAdmin: {ADMIN_USERNAME}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data.startswith("dep_confirm_"):
        parts = query.data.split("_")
        uid = int(parts[2])
        amount = int(parts[3])
        if uid in users:
            users[uid]["balance"] += amount
        await context.bot.send_message(
            chat_id=uid,
            text=f"✅ *Balansingiz to'ldirildi!*\n\n"
                 f"💵 +{amount:,} so'm\n"
                 f"💰 Joriy balans: {users.get(uid, {}).get('balance', 0):,} so'm",
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"✅ {uid} balansi +{amount:,} so'm.")

    elif query.data.startswith("dep_reject_"):
        uid = int(query.data.split("_")[2])
        await context.bot.send_message(chat_id=uid, text="❌ Balans to'ldirish rad etildi.")
        await query.edit_message_text("❌ Rad etildi.")

    elif query.data.startswith("buy_") and query.data != "buy_custom":
        amount = int(query.data.split("_")[1])
        price = amount * STAR_PRICE
        context.user_data["pending"] = {"type": "Stars", "amount": amount, "price": price, "label": f"{amount} Stars"}
        keyboard = [
            [InlineKeyboardButton("👤 O'zim uchun", callback_data="receiver_self")],
            [InlineKeyboardButton("🎁 Boshqa birov uchun", callback_data="receiver_other")],
        ]
        await query.edit_message_text(
            f"⭐ *{amount} Stars*\n💰 Narx: {price:,} so'm\n\n❗ Stars kim uchun?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "buy_custom":
        user_state[user_id] = "waiting_custom_amount"
        await query.edit_message_text("✏️ Nechta Stars olmoqchisiz?\n\nRaqam kiriting (masalan: 75):")

    elif query.data.startswith("prem_"):
        months = int(query.data.split("_")[1])
        prices = {1: 45000, 3: 120000, 6: 220000}
        price = prices[months]
        context.user_data["pending"] = {"type": "Premium", "amount": months, "price": price, "label": f"{months} oy Premium"}
        keyboard = [
            [InlineKeyboardButton("👤 O'zim uchun", callback_data="receiver_self")],
            [InlineKeyboardButton("🎁 Boshqa birov uchun", callback_data="receiver_other")],
        ]
        await query.edit_message_text(
            f"💎 *{months} oy Premium*\n💰 Narx: {price:,} so'm\n\n❗ Kim uchun?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "receiver_self":
        username = query.from_user.username or query.from_user.first_name
        context.user_data["receiver"] = f"@{username} (o'zi uchun)"
        await show_payment_method(query, context, user_id)

    elif query.data == "receiver_other":
        user_state[user_id] = "waiting_receiver_username"
        pending = context.user_data.get("pending", {})
        await query.edit_message_text(
            f"⭐ *{pending.get('label', '')}*\n\n❗ Qabul qiluvchining @username ni kiriting:",
            parse_mode="Markdown"
        )

    elif query.data == "pay_balance":
        pending = context.user_data.get("pending", {})
        price = pending.get("price", 0)
        if user_data["balance"] >= price:
            user_data["balance"] -= price
            order_counter[0] += 1
            order_id = order_counter[0]
            receiver = context.user_data.get("receiver", "—")
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
                    [InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_pay_{order_id}"),
                     InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_pay_{order_id}")]
                ]
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"💵 *Balansdan to'lov #{order_id}*\n\n"
                         f"👤 @{orders[order_id]['username']} (ID: `{user_id}`)\n"
                         f"📦 {pending['label']}\n"
                         f"👤 Qabul qiluvchi: {receiver}\n"
                         f"💰 {price:,} so'm (balansdan)",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
            await query.edit_message_text(
                f"✅ *Buyurtma #{order_id} qabul qilindi!*\n\n"
                f"💵 Balansdan yechildi: {price:,} so'm\n"
                f"💰 Qolgan balans: {user_data['balance']:,} so'm\n\n"
                f"⚡ Tez orada yetkazib beriladi!",
                parse_mode="Markdown"
            )
        else:
            keyboard = [[InlineKeyboardButton("💳 Balansni to'ldirish", callback_data="deposit")]]
            await query.edit_message_text(
                f"❌ *Balans yetarli emas!*\n\n"
                f"💵 Joriy balans: {user_data['balance']:,} so'm\n"
                f"💰 Kerakli summa: {price:,} so'm",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

    elif query.data == "pay_card":
        pending = context.user_data.get("pending", {})
        receiver = context.user_data.get("receiver", "—")
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
            f"💳 *To'lov ma'lumotlari:*\n\n"
            f"🏦 Karta raqami:\n`{KARTA_RAQAM}`\n\n"
            f"👤 Karta egasi: *{KARTA_EGASI}*\n\n"
            f"💰 To'lov miqdori: *{pending['price']:,} so'm*\n\n"
            f"📌 Buyurtma #{order_id}: {pending['label']}\n"
            f"👤 Qabul qiluvchi: {receiver}\n\n"
            f"✅ To'lov qilgandan so'ng *chek (screenshot)* yuboring!",
            parse_mode="Markdown"
        )

    elif query.data.startswith("confirm_pay_"):
        order_id = int(query.data.split("_")[2])
        if order_id in orders:
            orders[order_id]["status"] = "confirmed"
            uid = orders[order_id]["user_id"]
            label = orders[order_id]["label"]
            receiver = orders[order_id].get("receiver", "—")
            payment_history.append(orders[order_id])
            await context.bot.send_message(
                chat_id=uid,
                text=f"✅ *To'lovingiz tasdiqlandi!*\n\n"
                     f"⭐ {label} tez orada yuboriladi!\n"
                     f"👤 Qabul qiluvchi: {receiver}\n"
                     f"Xarid uchun rahmat! 🙏",
                parse_mode="Markdown"
            )
            await query.edit_message_text(f"✅ Buyurtma #{order_id} tasdiqlandi.")

    elif query.data.startswith("reject_pay_"):
        order_id = int(query.data.split("_")[2])
        if order_id in orders:
            orders[order_id]["status"] = "rejected"
            uid = orders[order_id]["user_id"]
            await context.bot.send_message(
                chat_id=uid,
                text=f"❌ *Buyurtma #{order_id} rad etildi.*\n\n"
                     f"Savollar uchun: {ADMIN_USERNAME}",
                parse_mode="Markdown"
            )
            await query.edit_message_text(f"❌ Buyurtma #{order_id} rad etildi.")

async def show_payment_method(query, context, user_id):
    pending = context.user_data.get("pending", {})
    user_data = get_user(user_id)
    keyboard = [
        [InlineKeyboardButton(f"💵 Balansdan ({user_data['balance']:,} so'm)", callback_data="pay_balance")],
        [InlineKeyboardButton("💳 Karta orqali", callback_data="pay_card")],
    ]
    await query.edit_message_text(
        f"⭐ *{pending.get('label', '')}*\n"
        f"💰 Narx: {pending.get('price', 0):,} so'm\n"
        f"👤 Qabul qiluvchi: {context.user_data.get('receiver', '—')}\n\n"
        f"💳 To'lov usulini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    state = user_state.get(user_id, "")
    user_data = get_user(user_id, update.effective_user.username, update.effective_user.first_name)

    # Kanal obunasini tekshirish - barcha xabarlarda
    if not state:
        if not await sub_required(update, context):
            return

    if text == "⭐ Stars xarid qilish":
        keyboard = [
            [InlineKeyboardButton(f"⭐ 50 Stars — {50*STAR_PRICE:,} so'm", callback_data="buy_50")],
            [InlineKeyboardButton(f"⭐ 100 Stars — {100*STAR_PRICE:,} so'm", callback_data="buy_100")],
            [InlineKeyboardButton(f"⭐ 250 Stars — {250*STAR_PRICE:,} so'm", callback_data="buy_250")],
            [InlineKeyboardButton(f"⭐ 500 Stars — {500*STAR_PRICE:,} so'm", callback_data="buy_500")],
            [InlineKeyboardButton(f"⭐ 1000 Stars — {1000*STAR_PRICE:,} so'm", callback_data="buy_1000")],
            [InlineKeyboardButton("✏️ O'zim miqdor kiritaman", callback_data="buy_custom")],
        ]
        await update.message.reply_text(
            f"⭐ *Stars narxlari:*\n\n1 Star = {STAR_PRICE:,} so'm\n\nMiqdorni tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif text == "👑 Premium xarid qilish":
        keyboard = [
            [InlineKeyboardButton("💎 1 oy — 45,000 so'm", callback_data="prem_1")],
            [InlineKeyboardButton("💎 3 oy — 120,000 so'm", callback_data="prem_3")],
            [InlineKeyboardButton("💎 6 oy — 220,000 so'm", callback_data="prem_6")],
        ]
        await update.message.reply_text(
            "💎 *Telegram Premium narxlari:*\n\nMuddatni tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif text == "🛒 Buyurtmalarim":
        user_orders = [(oid, o) for oid, o in orders.items() if o["user_id"] == user_id]
        if not user_orders:
            t = "🛒 Sizda hali buyurtma yo'q."
        else:
            t = "🛒 *Buyurtmalaringiz:*\n\n"
            sm = {"waiting_payment": "⏳ Kutilmoqda", "waiting_confirm": "🔍 Tekshirilmoqda",
                  "confirmed": "✅ Tasdiqlandi", "cancelled": "❌ Bekor", "rejected": "❌ Rad"}
            for oid, o in user_orders[-5:]:
                t += f"#{oid} — {o['label']} — {sm.get(o['status'], o['status'])}\n"
        await update.message.reply_text(t, parse_mode="Markdown")
    elif text == "👥 Referal":
        bot_info = await context.bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
        keyboard = [[InlineKeyboardButton("📤 Ulashish", url=f"https://t.me/share/url?url={ref_link}")]]
        await update.message.reply_text(
            f"👥 *Referal tizimi*\n\n"
            f"🎁 Har bir referal uchun: *{REFERRAL_BONUS:,} so'm*\n"
            f"👥 Sizning referallaringiz: *{user_data['referrals']} ta*\n"
            f"💰 Jami bonus: *{user_data['referrals'] * REFERRAL_BONUS:,} so'm*\n\n"
            f"⚠️ Bonus faqat kanal obunasidan so'ng beriladi.\n\n"
            f"🔗 Referal linkingiz:\n`{ref_link}`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif text == "💵 Balans":
        keyboard = [[InlineKeyboardButton("💳 Balansni to'ldirish", callback_data="deposit")]]
        await update.message.reply_text(
            f"💵 *Balansingiz*\n\n"
            f"🆔 {user_id}\n\n"
            f"💵 Balans: *{user_data['balance']:,} so'm*\n\n"
            f"💡 Balansingizni to'ldirish uchun pastdagi tugmani bosing!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif text == "ℹ️ Bot haqida":
        await update.message.reply_text(
            "ℹ️ *Bot haqida*\n\n"
            f"⭐ 1 Star = {STAR_PRICE:,} so'm\n"
            "⚡ Yetkazib berish: 5-30 daqiqa\n"
            f"👤 Admin: {ADMIN_USERNAME}",
            parse_mode="Markdown"
        )
    elif text == "📞 Bog'lanish":
        keyboard = [[InlineKeyboardButton(f"💬 {ADMIN_USERNAME} ga yozish", url="https://t.me/Shakxrom")]]
        await update.message.reply_text(
            f"📞 *Bog'lanish*\n\n"
            f"Yordam kerakmi? Admin bilan bog'laning:\n\n"
            f"👤 Admin: {ADMIN_USERNAME}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif state == "waiting_custom_amount":
        if text.isdigit() and int(text) > 0:
            amount = int(text)
            price = amount * STAR_PRICE
            user_state.pop(user_id, None)
            context.user_data["pending"] = {"type": "Stars", "amount": amount, "price": price, "label": f"{amount} Stars"}
            keyboard = [
                [InlineKeyboardButton("👤 O'zim uchun", callback_data="receiver_self")],
                [InlineKeyboardButton("🎁 Boshqa birov uchun", callback_data="receiver_other")],
            ]
            await update.message.reply_text(
                f"⭐ *{amount} Stars*\n💰 Narx: {price:,} so'm\n\n❗ Stars kim uchun?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❗ To'g'ri raqam kiriting!")
    elif state == "waiting_receiver_username":
        username_input = text.strip()
        if not username_input.startswith("@"):
            username_input = "@" + username_input
        context.user_data["receiver"] = username_input
        user_state.pop(user_id, None)
        pending = context.user_data.get("pending", {})
        keyboard = [
            [InlineKeyboardButton(f"💵 Balansdan ({user_data['balance']:,} so'm)", callback_data="pay_balance")],
            [InlineKeyboardButton("💳 Karta orqali", callback_data="pay_card")],
        ]
        await update.message.reply_text(
            f"⭐ *{pending.get('label', '')}*\n"
            f"💰 Narx: {pending.get('price', 0):,} so'm\n"
            f"👤 Qabul qiluvchi: *{username_input}*\n\n"
            f"💳 To'lov usulini tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
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
                    [InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_pay_{order_id}"),
                     InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_pay_{order_id}")]
                ]
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"💳 *Yangi to'lov #{order_id}*\n\n"
                         f"👤 @{username} (ID: `{user_id}`)\n"
                         f"📦 {o['label']}\n"
                         f"👤 Qabul qiluvchi: {o.get('receiver','—')}\n"
                         f"💰 {o['price']:,} so'm\n\nChek quyida 👇",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                if update.message.photo:
                    await context.bot.send_photo(chat_id=admin_id, photo=update.message.photo[-1].file_id)
                elif update.message.document:
                    await context.bot.send_document(chat_id=admin_id, document=update.message.document.file_id)
            await update.message.reply_text(
                "✅ *Chekingiz qabul qilindi!*\n\n🔍 Admin tekshirib tasdiqlaydi.\nO'rtacha 5-15 daqiqa.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("📸 Iltimos, to'lov cheki (screenshot) yuboring!")
    elif state.startswith("waiting_deposit_check_"):
        amount = int(state.split("_")[3])
        if update.message.photo or update.message.document:
            user_state.pop(user_id, None)
            username = update.effective_user.username or update.effective_user.first_name
            for admin_id in ADMIN_IDS:
                keyboard = [
                    [InlineKeyboardButton(f"✅ +{amount:,} so'm", callback_data=f"dep_confirm_{user_id}_{amount}"),
                     InlineKeyboardButton("❌ Rad etish", callback_data=f"dep_reject_{user_id}")]
                ]
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"💰 *Balans to'ldirish #{user_id}*\n\n"
                         f"👤 @{username}\n💵 {amount:,} so'm\n\nChek quyida 👇",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                if update.message.photo:
                    await context.bot.send_photo(chat_id=admin_id, photo=update.message.photo[-1].file_id)
                elif update.message.document:
                    await context.bot.send_document(chat_id=admin_id, document=update.message.document.file_id)
            await update.message.reply_text(
                "✅ Chekingiz yuborildi! Admin tasdiqlashini kuting.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("📸 Chek (screenshot) yuboring!")
    elif state == "waiting_deposit_amount":
        if text.isdigit() and int(text) >= 10000:
            amount = int(text)
            user_state[user_id] = f"waiting_deposit_check_{amount}"
            await update.message.reply_text(
                f"💳 *Balans to'ldirish*\n\n"
                f"💵 Miqdor: {amount:,} so'm\n\n"
                f"Karta: `{KARTA_RAQAM}`\n"
                f"Egasi: *{KARTA_EGASI}*\n\n"
                f"✅ To'lovdan so'ng chek yuboring!",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❗ Minimum 10,000 so'm kiriting!")

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q!")
        return
    total = len(orders)
    pending = sum(1 for o in orders.values() if o["status"] == "waiting_confirm")
    confirmed = sum(1 for o in orders.values() if o["status"] == "confirmed")
    total_sum = sum(o["price"] for o in orders.values() if o["status"] == "confirmed")
    text = (
        f"🔧 *Admin Panel*\n\n"
        f"👥 Foydalanuvchilar: {len(users)}\n"
        f"📦 Jami buyurtmalar: {total}\n"
        f"🔍 Tekshirilmoqda: {pending}\n"
        f"✅ Tasdiqlangan: {confirmed}\n"
        f"💰 Jami tushum: {total_sum:,} so'm\n\n"
    )
    if pending > 0:
        text += "⏳ *Kutilayotgan:*\n"
        for oid, o in orders.items():
            if o["status"] == "waiting_confirm":
                text += f"#{oid} — @{o['username']} — {o['label']} — {o['price']:,} so'm\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q!")
        return
    if not payment_history:
        await update.message.reply_text("📋 Tarix bo'sh.")
        return
    text = "📋 *To'lovlar tarixi:*\n\n"
    for o in payment_history[-10:]:
        text += f"✅ @{o['username']} — {o['label']} — {o['price']:,} so'm\n"
    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("history", history_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
