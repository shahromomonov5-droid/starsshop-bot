from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8329450751:AAHTSn2cDfoA91ZbyKbx8Y46jcFDbujQZHk"
ADMIN_IDS = [8091289657]
STAR_PRICE = 210  # 1 star narxi so'mda

# Buyurtmalar ro'yxati
orders = {}
order_counter = [0]

# Foydalanuvchi holati
user_state = {}

# ==================== START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("⭐ Stars sotib olish", callback_data="stars")],
        [InlineKeyboardButton("📦 Buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("✉️ Adminga xabar", callback_data="contact")],
        [InlineKeyboardButton("ℹ️ Bot haqida", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"✨ Xush kelibsiz, {user.first_name}!\n\n"
        f"⭐ 1 Star = {STAR_PRICE:,} so'm\n\n"
        "Telegram Stars tez va xavfsiz yetkazib beriladi!\n\n"
        "Quyidagi menyudan tanlang 👇",
        reply_markup=reply_markup
    )

# ==================== BUTTON HANDLER ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "stars":
        keyboard = [
            [InlineKeyboardButton(f"⭐ 50 Stars — {50 * STAR_PRICE:,} so'm", callback_data="buy_50")],
            [InlineKeyboardButton(f"⭐ 100 Stars — {100 * STAR_PRICE:,} so'm", callback_data="buy_100")],
            [InlineKeyboardButton(f"⭐ 250 Stars — {250 * STAR_PRICE:,} so'm", callback_data="buy_250")],
            [InlineKeyboardButton(f"⭐ 500 Stars — {500 * STAR_PRICE:,} so'm", callback_data="buy_500")],
            [InlineKeyboardButton(f"⭐ 1000 Stars — {1000 * STAR_PRICE:,} so'm", callback_data="buy_1000")],
            [InlineKeyboardButton("✏️ O'zim miqdor kiritaman", callback_data="buy_custom")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back")],
        ]
        await query.edit_message_text(
            f"⭐ *Stars narxlari:*\n\n"
            f"1 Star = {STAR_PRICE:,} so'm\n\n"
            "Miqdorni tanlang yoki o'zingiz kiriting:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data.startswith("buy_") and query.data != "buy_custom":
        amount = int(query.data.split("_")[1])
        total = amount * STAR_PRICE
        keyboard = [
            [InlineKeyboardButton("✅ Buyurtma berish", callback_data=f"confirm_{amount}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="stars")],
        ]
        await query.edit_message_text(
            f"⭐ *{amount} Stars*\n\n"
            f"💰 Narx: {total:,} so'm\n\n"
            "Buyurtma berishni tasdiqlaysizmi?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "buy_custom":
        user_state[user_id] = "waiting_custom_amount"
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="stars")]]
        await query.edit_message_text(
            "✏️ Nechta Stars olmoqchisiz?\n\n"
            "Raqam kiriting (masalan: 75):",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("confirm_"):
        amount = int(query.data.split("_")[1])
        total = amount * STAR_PRICE
        order_counter[0] += 1
        order_id = order_counter[0]

        orders[order_id] = {
            "user_id": user_id,
            "username": query.from_user.username or query.from_user.first_name,
            "amount": amount,
            "total": total,
            "status": "pending"
        }

        # Adminga xabar
        for admin_id in ADMIN_IDS:
            keyboard = [
                [InlineKeyboardButton("✅ Bajarildi", callback_data=f"done_{order_id}"),
                 InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel_{order_id}")]
            ]
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🔔 *Yangi buyurtma #{order_id}*\n\n"
                     f"👤 Foydalanuvchi: @{orders[order_id]['username']}\n"
                     f"🆔 ID: `{user_id}`\n"
                     f"⭐ Miqdor: {amount} Stars\n"
                     f"💰 Narx: {total:,} so'm",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

        keyboard = [[InlineKeyboardButton("🔙 Bosh menu", callback_data="back")]]
        await query.edit_message_text(
            f"✅ *Buyurtma #{order_id} qabul qilindi!*\n\n"
            f"⭐ {amount} Stars\n"
            f"💰 {total:,} so'm\n\n"
            f"📞 To'lov uchun: @Shakxrom ga murojaat qiling\n"
            "To'lovdan so'ng Stars yetkazib beriladi! ⚡",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data.startswith("done_"):
        order_id = int(query.data.split("_")[1])
        if order_id in orders:
            orders[order_id]["status"] = "done"
            user_id_to_notify = orders[order_id]["user_id"]
            amount = orders[order_id]["amount"]
            await context.bot.send_message(
                chat_id=user_id_to_notify,
                text=f"🎉 *Buyurtma #{order_id} bajarildi!*\n\n"
                     f"⭐ {amount} Stars hisobingizga yuborildi!\n"
                     "Xarid uchun rahmat! 🙏",
                parse_mode="Markdown"
            )
            await query.edit_message_text(
                f"✅ Buyurtma #{order_id} bajarildi va foydalanuvchiga xabar yuborildi."
            )

    elif query.data.startswith("cancel_"):
        order_id = int(query.data.split("_")[1])
        if order_id in orders:
            orders[order_id]["status"] = "cancelled"
            user_id_to_notify = orders[order_id]["user_id"]
            await context.bot.send_message(
                chat_id=user_id_to_notify,
                text=f"❌ *Buyurtma #{order_id} bekor qilindi.*\n\n"
                     "Savollar uchun: @Shakxrom ga murojaat qiling.",
                parse_mode="Markdown"
            )
            await query.edit_message_text(
                f"❌ Buyurtma #{order_id} bekor qilindi."
            )

    elif query.data == "my_orders":
        user_orders = [(oid, o) for oid, o in orders.items() if o["user_id"] == user_id]
        if not user_orders:
            text = "📦 Sizda hali buyurtma yo'q."
        else:
            text = "📦 *Buyurtmalaringiz:*\n\n"
            for oid, o in user_orders[-5:]:
                status = "✅ Bajarildi" if o["status"] == "done" else "❌ Bekor" if o["status"] == "cancelled" else "⏳ Kutilmoqda"
                text += f"#{oid} — {o['amount']} Stars — {status}\n"
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
            "Bu bot orqali Telegram Stars xavfsiz va tez sotib olishingiz mumkin.\n\n"
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

# ==================== MATN HANDLER ====================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_state.get(user_id) == "waiting_custom_amount":
        if text.isdigit() and int(text) > 0:
            amount = int(text)
            total = amount * STAR_PRICE
            user_state.pop(user_id, None)
            keyboard = [
                [InlineKeyboardButton("✅ Buyurtma berish", callback_data=f"confirm_{amount}")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="stars")],
            ]
            await update.message.reply_text(
                f"⭐ *{amount} Stars*\n\n"
                f"💰 Narx: {total:,} so'm\n\n"
                "Buyurtma berishni tasdiqlaysizmi?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❗ Iltimos, to'g'ri raqam kiriting (masalan: 75)")

    elif user_state.get(user_id) == "waiting_message":
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

# ==================== ADMIN ====================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q!")
        return

    pending = [(oid, o) for oid, o in orders.items() if o["status"] == "pending"]
    done = [(oid, o) for oid, o in orders.items() if o["status"] == "done"]

    await update.message.reply_text(
        f"🔧 *Admin panel*\n\n"
        f"📦 Jami buyurtmalar: {len(orders)}\n"
        f"⏳ Kutilmoqda: {len(pending)}\n"
        f"✅ Bajarildi: {len(done)}\n",
        parse_mode="Markdown"
    )

# ==================== MAIN ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
