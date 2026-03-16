from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8484695622:AAHrg3LDvCzUE_2rCEM3uOFmnRRMVhk-wkI"
ADMIN_IDS = [8091289657]
STAR_PRICE = 210

KARTA_RAQAM = "5614 6821 1298 8300"
KARTA_EGASI = "Omonqulov Shahrom"

orders = {}
order_counter = [0]
user_state = {}
payment_history = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("⭐ Stars sotib olish", callback_data="stars")],
        [InlineKeyboardButton("💎 Premium sotib olish", callback_data="premium")],
        [InlineKeyboardButton("📦 Buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("✉️ Adminga xabar", callback_data="contact")],
        [InlineKeyboardButton("ℹ️ Bot haqida", callback_data="about")],
    ]
    await update.message.reply_text(
        f"✨ Xush kelibsiz, {user.first_name}!\n\n"
        f"⭐ 1 Star = {STAR_PRICE:,} so'm\n\n"
        "Telegram Stars tez va xavfsiz yetkazib beriladi!\n\n"
        "Quyidagi menyudan tanlang 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "stars":
        keyboard = [
            [InlineKeyboardButton(f"⭐ 50 Stars — {50*STAR_PRICE:,} so'm", callback_data="buy_50")],
            [InlineKeyboardButton(f"⭐ 100 Stars — {100*STAR_PRICE:,} so'm", callback_data="buy_100")],
            [InlineKeyboardButton(f"⭐ 250 Stars — {250*STAR_PRICE:,} so'm", callback_data="buy_250")],
            [InlineKeyboardButton(f"⭐ 500 Stars — {500*STAR_PRICE:,} so'm", callback_data="buy_500")],
            [InlineKeyboardButton(f"⭐ 1000 Stars — {1000*STAR_PRICE:,} so'm", callback_data="buy_1000")],
            [InlineKeyboardButton("✏️ O'zim miqdor kiritaman", callback_data="buy_custom")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back")],
        ]
        await query.edit_message_text(
            f"⭐ *Stars narxlari:*\n\n1 Star = {STAR_PRICE:,} so'm\n\nMiqdorni tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "premium":
        keyboard = [
            [InlineKeyboardButton("💎 1 oy — 45,000 so'm", callback_data="prem_1")],
            [InlineKeyboardButton("💎 3 oy — 120,000 so'm", callback_data="prem_3")],
            [InlineKeyboardButton("💎 6 oy — 220,000 so'm", callback_data="prem_6")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back")],
        ]
        await query.edit_message_text(
            "💎 *Telegram Premium narxlari:*\n\nMuddatni tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data.startswith("prem_"):
        months = int(query.data.split("_")[1])
        prices = {1: 45000, 3: 120000, 6: 220000}
        price = prices[months]
        context.user_data["pending"] = {"type": "Premium", "amount": months, "price": price, "label": f"{months} oy Premium"}
        # Premium uchun ham kimga so'rash
        keyboard = [
            [InlineKeyboardButton("👤 O'zim uchun", callback_data="receiver_self")],
            [InlineKeyboardButton("🎁 Boshqa birov uchun", callback_data="receiver_other")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="premium")],
        ]
        await query.edit_message_text(
            f"💎 *{months} oy Premium*\n💰 Narx: {price:,} so'm\n\n"
            f"❗ Premium kim uchun?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data.startswith("buy_") and query.data != "buy_custom":
        amount = int(query.data.split("_")[1])
        price = amount * STAR_PRICE
        context.user_data["pending"] = {"type": "Stars", "amount": amount, "price": price, "label": f"{amount} Stars"}
        keyboard = [
            [InlineKeyboardButton("👤 O'zim uchun", callback_data="receiver_self")],
            [InlineKeyboardButton("🎁 Boshqa birov uchun", callback_data="receiver_other")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="stars")],
        ]
        await query.edit_message_text(
            f"⭐ *{amount} Stars*\n💰 Narx: {price:,} so'm\n\n"
            f"❗ Stars kim uchun?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "buy_custom":
        user_state[user_id] = "waiting_custom_amount"
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="stars")]]
        await query.edit_message_text(
            "✏️ Nechta Stars olmoqchisiz?\n\nRaqam kiriting (masalan: 75):",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "receiver_self":
        pending = context.user_data.get("pending", {})
        username = query.from_user.username or query.from_user.first_name
        context.user_data["receiver"] = f"@{username} (o'zi uchun)"
        await proceed_to_payment(query, context, user_id)

    elif query.data == "receiver_other":
        user_state[user_id] = "waiting_receiver_username"
        pending = context.user_data.get("pending", {})
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="stars")]]
        await query.edit_message_text(
            f"⭐ *{pending.get('label', '')}*\n\n"
            f"❗ Qabul qiluvchining @username ni kiriting:\n\n"
            f"Masalan: @username",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "proceed_payment":
        await proceed_to_payment(query, context, user_id)

    elif query.data.startswith("user_cancel_"):
        order_id = int(query.data.split("_")[2])
        if order_id in orders:
            orders[order_id]["status"] = "cancelled"
            user_state.pop(user_id, None)
        keyboard = [[InlineKeyboardButton("🔙 Bosh menu", callback_data="back")]]
        await query.edit_message_text("❌ Buyurtma bekor qilindi.", reply_markup=InlineKeyboardMarkup(keyboard))

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
                     f"Chekingiz tasdiqlanmadi. Savollar uchun: @Shakxrom",
                parse_mode="Markdown"
            )
            await query.edit_message_text(f"❌ Buyurtma #{order_id} rad etildi.")

    elif query.data == "my_orders":
        user_orders = [(oid, o) for oid, o in orders.items() if o["user_id"] == user_id]
        if not user_orders:
            text = "📦 Sizda hali buyurtma yo'q."
        else:
            text = "📦 *Buyurtmalaringiz:*\n\n"
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
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "contact":
        user_state[user_id] = "waiting_message"
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]]
        await query.edit_message_text(
            "✉️ Adminga yuboriladigan xabarni yozing:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "about":
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]]
        await query.edit_message_text(
            "ℹ️ *Bot haqida*\n\n"
            f"⭐ 1 Star = {STAR_PRICE:,} so'm\n"
            "⚡ Yetkazib berish: 5-30 daqiqa\n"
            "👤 Admin: @Shakxrom",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "back":
        user = query.from_user
        keyboard = [
            [InlineKeyboardButton("⭐ Stars sotib olish", callback_data="stars")],
            [InlineKeyboardButton("💎 Premium sotib olish", callback_data="premium")],
            [InlineKeyboardButton("📦 Buyurtmalarim", callback_data="my_orders")],
            [InlineKeyboardButton("✉️ Adminga xabar", callback_data="contact")],
            [InlineKeyboardButton("ℹ️ Bot haqida", callback_data="about")],
        ]
        await query.edit_message_text(
            f"✨ Xush kelibsiz, {user.first_name}!\n\n"
            f"⭐ 1 Star = {STAR_PRICE:,} so'm\n\n"
            "Telegram Stars tez va xavfsiz yetkazib beriladi!\n\n"
            "Quyidagi menyudan tanlang 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def proceed_to_payment(query, context, user_id):
    pending = context.user_data.get("pending")
    receiver = context.user_data.get("receiver", "—")
    if not pending:
        await query.edit_message_text("❌ Xatolik! Qaytadan boshlang.")
        return
    order_counter[0] += 1
    order_id = order_counter[0]
    orders[order_id] = {
        "user_id": user_id,
        "username": query.from_user.username or query.from_user.first_name,
        "first_name": query.from_user.first_name,
        "receiver": receiver,
        **pending,
        "status": "waiting_payment"
    }
    user_state[user_id] = f"waiting_check_{order_id}"
    keyboard = [[InlineKeyboardButton("❌ Bekor qilish", callback_data=f"user_cancel_{order_id}")]]
    await query.edit_message_text(
        f"💳 *To'lov ma'lumotlari:*\n\n"
        f"🏦 Karta raqami:\n`{KARTA_RAQAM}`\n\n"
        f"👤 Karta egasi: *{KARTA_EGASI}*\n\n"
        f"💰 To'lov miqdori: *{pending['price']:,} so'm*\n\n"
        f"📌 Buyurtma #{order_id}: {pending['label']}\n"
        f"👤 Qabul qiluvchi: {receiver}\n\n"
        f"✅ To'lov qilgandan so'ng *chek (screenshot)* yuboring!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_state.get(user_id, "")

    if state == "waiting_custom_amount":
        text = update.message.text
        if text.isdigit() and int(text) > 0:
            amount = int(text)
            price = amount * STAR_PRICE
            user_state.pop(user_id, None)
            context.user_data["pending"] = {"type": "Stars", "amount": amount, "price": price, "label": f"{amount} Stars"}
            keyboard = [
                [InlineKeyboardButton("👤 O'zim uchun", callback_data="receiver_self")],
                [InlineKeyboardButton("🎁 Boshqa birov uchun", callback_data="receiver_other")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="stars")],
            ]
            await update.message.reply_text(
                f"⭐ *{amount} Stars*\n💰 Narx: {price:,} so'm\n\n❗ Stars kim uchun?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❗ To'g'ri raqam kiriting (masalan: 75)")

    elif state == "waiting_receiver_username":
        username_input = update.message.text.strip()
        if not username_input.startswith("@"):
            username_input = "@" + username_input
        context.user_data["receiver"] = username_input
        user_state.pop(user_id, None)
        pending = context.user_data.get("pending", {})
        keyboard = [
            [InlineKeyboardButton("✅ To'lovga o'tish", callback_data="proceed_payment")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="stars")],
        ]
        await update.message.reply_text(
            f"⭐ *{pending.get('label', '')}*\n"
            f"💰 Narx: {pending.get('price', 0):,} so'm\n"
            f"👤 Qabul qiluvchi: *{username_input}*\n\n"
            f"To'lovga o'tasizmi?",
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
                         f"💰 {o['price']:,} so'm\n\n"
                         f"Chek quyida 👇",
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

    elif state == "waiting_message":
        user_state.pop(user_id, None)
        username = update.effective_user.username or update.effective_user.first_name
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"✉️ *Foydalanuvchidan xabar:*\n\n"
                     f"👤 @{username} (ID: `{user_id}`)\n\n"
                     f"💬 {update.message.text}",
                parse_mode="Markdown"
            )
        await update.message.reply_text("✅ Xabaringiz adminga yuborildi!")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q!")
        return
    total = len(orders)
    pending = sum(1 for o in orders.values() if o["status"] == "waiting_confirm")
    confirmed = sum(1 for o in orders.values() if o["status"] == "confirmed")
    cancelled = sum(1 for o in orders.values() if o["status"] in ["cancelled", "rejected"])
    total_sum = sum(o["price"] for o in orders.values() if o["status"] == "confirmed")
    text = (
        f"🔧 *Admin Panel*\n\n"
        f"📦 Jami buyurtmalar: {total}\n"
        f"🔍 Tekshirilmoqda: {pending}\n"
        f"✅ Tasdiqlangan: {confirmed}\n"
        f"❌ Bekor/Rad: {cancelled}\n\n"
        f"💰 Jami tushum: {total_sum:,} so'm\n\n"
    )
    if pending > 0:
        text += "⏳ *Kutilayotgan to'lovlar:*\n"
        for oid, o in orders.items():
            if o["status"] == "waiting_confirm":
                text += f"#{oid} — @{o['username']} — {o['label']} — {o['price']:,} so'm\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q!")
        return
    if not payment_history:
        await update.message.reply_text("📋 To'lovlar tarixi bo'sh.")
        return
    text = "📋 *To'lovlar tarixi:*\n\n"
    for o in payment_history[-10:]:
        text += f"✅ @{o['username']} — {o['label']} — {o['price']:,} so'm — {o.get('receiver','—')}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
