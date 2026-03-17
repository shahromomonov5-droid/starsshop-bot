from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8484695622:AAHrg3LDvCzUE_2rCEM3uOFmnRRMVhk-wkI"
ADMIN_IDS = [6316039013]
STAR_PRICE = 210
KARTA_RAQAM = "5614 6821 1298 8300"
KARTA_EGASI = "Omonqulov Shahrom"
ADMIN_USERNAME = "@Shakxrom"
REFERRAL_BONUS = 5000  # har bir taklif uchun bonus (so'm)

orders = {}
order_counter = [0]
user_state = {}
payment_history = []
users = {}  # {user_id: {balance, referrals, ref_by}}

def get_user(user_id, username=None, first_name=None):
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "referrals": 0,
            "username": username or str(user_id),
            "first_name": first_name or "Foydalanuvchi"
        }
    return users[user_id]

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
        if ref_id != user.id and ref_id in users:
            if "ref_by" not in user_data:
                user_data["ref_by"] = ref_id
                users[ref_id]["balance"] += REFERRAL_BONUS
                users[ref_id]["referrals"] += 1
                try:
                    await context.bot.send_message(
                        chat_id=ref_id,
                        text=f"🎉 Yangi referal! @{user.username or user.first_name} botga qo'shildi!\n"
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

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    state = user_state.get(user_id, "")
    user_data = get_user(user_id, update.effective_user.username, update.effective_user.first_name)

    # PASTKI PANEL TUGMALARI
    if text == "⭐ Stars xarid qilish":
        await show_stars(update, context)
        return
    elif text == "👑 Premium xarid qilish":
        await show_premium(update, context)
        return
    elif text == "🛒 Buyurtmalarim":
        await show_my_orders(update, context)
        return
    elif text == "👥 Referal":
        await show_referral(update, context)
        return
    elif text == "💵 Balans":
        await show_balance(update, context)
        return
    elif text == "ℹ️ Bot haqida":
        await update.message.reply_text(
            "ℹ️ *Bot haqida*\n\n"
            f"⭐ 1 Star = {STAR_PRICE:,} so'm\n"
            "⚡ Yetkazib berish: 5-30 daqiqa\n"
            f"👤 Admin: {ADMIN_USERNAME}",
            parse_mode="Markdown"
        )
        return
    elif text == "📞 Bog'lanish":
        keyboard = [[InlineKeyboardButton(f"💬 {ADMIN_USERNAME} ga yozish", url=f"https://t.me/Shakxrom")]]
        await update.message.reply_text(
            "📞 *Bog'lanish*\n\n"
            "Yordam kerakmi? Savollaringiz bo'lsa admin bilan bog'laning:\n\n"
            f"👤 Admin: {ADMIN_USERNAME}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # HOLATLAR
    if state == "waiting_custom_amount":
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
            await update.message.reply_text("❗ To'g'ri raqam kiriting (masalan: 75)")

    elif state == "waiting_receiver_username":
        username_input = text.strip()
        if not username_input.startswith("@"):
            username_input = "@" + username_input
        context.user_data["receiver"] = username_input
        user_state.pop(user_id, None)
        pending = context.user_data.get("pending", {})
        keyboard = [
            [InlineKeyboardButton("💵 Balansdan to'lash", callback_data="pay_balance")],
            [InlineKeyboardButton("💳 Karta orqali to'lash", callback_data="pay_card")],
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
                         f"👤 Qabul qiluvchi: {o.get('receiver', '—')}\n"
                         f"💰 {o['price']:,} so'm\n\nChek quyida 👇",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                if update.message.photo:
                    await context.bot.send_photo(chat_id=admin_id, photo=update.message.photo[-1].file_id)
                elif update.message.document:
                    await context.bot.send_document(chat_id=admin_id, document=update.message.document.file_id)
            await update.message.reply_text(
                "✅ *Chekingiz qabul qilindi!*\n\n"
                "🔍 Admin tekshirib, tez orada tasdiqlaydi.\n"
                "O'rtacha 5-15 daqiqa.",
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
                    [InlineKeyboardButton(f"✅ Tasdiqlash (+{amount:,} so'm)", callback_data=f"dep_confirm_{user_id}_{amount}"),
                     InlineKeyboardButton("❌ Rad etish", callback_data=f"dep_reject_{user_id}")]
                ]
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"💰 *Balans to'ldirish so'rovi*\n\n"
                         f"👤 @{username} (ID: `{user_id}`)\n"
                         f"💵 Miqdor: {amount:,} so'm\n\nChek quyida 👇",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                if update.message.photo:
                    await context.bot.send_photo(chat_id=admin_id, photo=update.message.photo[-1].file_id)
                elif update.message.document:
                    await context.bot.send_document(chat_id=admin_id, document=update.message.document.file_id)
            await update.message.reply_text(
                "✅ *Chekingiz yuborildi!*\n\n"
                "🔍 Admin tasdiqlashini kuting.\n"
                "Tasdiqlangach balansingizga qo'shiladi.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("📸 Iltimos, to'lov cheki (screenshot) yuboring!")

    elif state == "waiting_deposit_amount":
        if text.isdigit() and int(text) >= 10000:
            amount = int(text)
            user_state[user_id] = f"waiting_deposit_check_{amount}"
            await update.message.reply_text(
                f"💳 *Balans to'ldirish*\n\n"
                f"💵 Miqdor: {amount:,} so'm\n\n"
                f"Quyidagi kartaga o'tkazma qiling:\n\n"
                f"🏦 Karta: `{KARTA_RAQAM}`\n"
                f"👤 Egasi: *{KARTA_EGASI}*\n\n"
                f"✅ To'lovdan so'ng chek yuboring!",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❗ Minimum 10,000 so'm kiriting!")

    elif state == "waiting_admin_message":
        user_state.pop(user_id, None)
        username = update.effective_user.username or update.effective_user.first_name
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"✉️ *Foydalanuvchidan xabar:*\n\n"
                     f"👤 @{username} (ID: `{user_id}`)\n\n"
                     f"💬 {text}",
                parse_mode="Markdown"
            )
        await update.message.reply_text("✅ Xabaringiz adminga yuborildi!")

async def show_stars(update, context):
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

async def show_premium(update, context):
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

async def show_my_orders(update, context):
    user_id = update.effective_user.id
    user_orders = [(oid, o) for oid, o in orders.items() if o["user_id"] == user_id]
    if not user_orders:
        text = "🛒 Sizda hali buyurtma yo'q."
    else:
        text = "🛒 *Buyurtmalaringiz:*\n\n"
        status_map = {
            "waiting_payment": "⏳ To'lov kutilmoqda",
            "waiting_confirm": "🔍 Tekshirilmoqda",
            "confirmed": "✅ Tasdiqlandi",
            "cancelled": "❌ Bekor",
            "rejected": "❌ Rad etildi"
        }
        for oid, o in user_orders[-5:]:
            st = status_map.get(o["status"], o["status"])
            text += f"#{oid} — {o['label']} — {st}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def show_referral(update, context):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    bot_info = await context.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    keyboard = [[InlineKeyboardButton("📤 Ulashish", url=f"https://t.me/share/url?url={ref_link}")]]
    await update.message.reply_text(
        f"👥 *Referal tizimi*\n\n"
        f"Do'stingizni taklif qiling va bonus oling!\n\n"
        f"🎁 Har bir referal uchun: *{REFERRAL_BONUS:,} so'm*\n"
        f"👥 Sizning referallaringiz: *{user_data['referrals']} ta*\n\n"
        f"⚠️ Eslatma: Bonus faqat taklif qilingan foydalanuvchi majburiy kanal obunasini bajargandan keyin hisoblanadi.\n\n"
        f"🔗 Sizning referal linkingiz:\n`{ref_link}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def show_balance(update, context):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    keyboard = [
        [InlineKeyboardButton("💳 Balansni to'ldirish", callback_data="deposit")],
    ]
    await update.message.reply_text(
        f"💵 *Balansingiz*\n\n"
        f"🆔 {user_id}\n\n"
        f"💵 Balans: *{user_data['balance']:,} so'm*\n\n"
        f"💡 Balansingizni to'ldirish uchun /deposit buyrug'idan foydalaning yoki kerakli to'lov tizimini tanlang!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = get_user(user_id, query.from_user.username, query.from_user.first_name)

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
            f"Qancha so'm to'ldirmoqchisiz?\n"
            f"(Minimum: 10,000 so'm)\n\n"
            f"Raqam kiriting:",
            parse_mode="Markdown"
        )

    elif query.data == "dep_admin":
        keyboard = [[InlineKeyboardButton(f"💬 {ADMIN_USERNAME}", url="https://t.me/Shakxrom")]]
        await query.edit_message_text(
            f"👤 *Admin orqali to'ldirish*\n\n"
            f"Admin bilan bog'laning:\n{ADMIN_USERNAME}",
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
        await query.edit_message_text(f"✅ {uid} foydalanuvchi balansi +{amount:,} so'm.")

    elif query.data.startswith("dep_reject_"):
        uid = int(query.data.split("_")[2])
        await context.bot.send_message(
            chat_id=uid,
            text="❌ Balans to'ldirish rad etildi. Savollar uchun: @Shakxrom"
        )
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
            f"⭐ *{pending.get('label', '')}*\n\n"
            f"❗ Qabul qiluvchining @username ni kiriting:",
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
                f"💰 Kerakli summa: {price:,} so'm\n\n"
                f"Balansingizni to'ldiring:",
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
                     f"Chekingiz tasdiqlanmadi. Savollar uchun: {ADMIN_USERNAME}",
                parse_mode="Markdown"
            )
            await query.edit_message_text(f"❌ Buyurtma #{order_id} rad etildi.")

async def show_payment_method(query, context, user_id):
    pending = context.user_data.get("pending", {})
    user_data = get_user(user_id)
    keyboard = [
        [InlineKeyboardButton(f"💵 Balansdan to'lash ({user_data['balance']:,} so'm)", callback_data="pay_balance")],
        [InlineKeyboardButton("💳 Karta orqali to'lash", callback_data="pay_card")],
    ]
    await query.edit_message_text(
        f"⭐ *{pending.get('label', '')}*\n"
        f"💰 Narx: {pending.get('price', 0):,} so'm\n"
        f"👤 Qabul qiluvchi: {context.user_data.get('receiver', '—')}\n\n"
        f"💳 To'lov usulini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

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
        f"👥 Jami foydalanuvchilar: {len(users)}\n"
        f"📦 Jami buyurtmalar: {total}\n"
        f"🔍 Tekshirilmoqda: {pending}\n"
        f"✅ Tasdiqlangan: {confirmed}\n"
        f"💰 Jami tushum: {total_sum:,} so'm\n\n"
    )
    if pending > 0:
        text += "⏳ *Kutilayotgan to'lovlar:*\n"
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
        await update.message.reply_text("📋 To'lovlar tarixi bo'sh.")
        return
    text = "📋 *To'lovlar tarixi:*\n\n"
    for o in payment_history[-10:]:
        text += f"✅ @{o['username']} — {o['label']} — {o['price']:,} so'm\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def deposit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 Humo/UzCard", callback_data="dep_card")],
        [InlineKeyboardButton("👤 Admin orqali", callback_data="dep_admin")],
    ]
    await update.message.reply_text(
        "💵 *Balans to'ldirish*\n\nTo'lov usulini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("history", history_cmd))
    app.add_handler(CommandHandler("deposit", deposit_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
