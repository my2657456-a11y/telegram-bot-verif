import random
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, ChatMemberHandler

# Ambil token dari Railway Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan!")

pending_users = {}

# Saat ada member baru
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    user = result.new_chat_member.user

    if result.old_chat_member.status in ["left", "kicked"] and result.new_chat_member.status == "member":
        if user.is_bot:
            return

        chat_id = update.effective_chat.id
        user_id = user.id

        a = random.randint(1, 10)
        b = random.randint(1, 10)
        answer = a + b

        pending_users[user_id] = {"answer": answer, "chat_id": chat_id}

        await context.bot.send_message(
            chat_id,
            f"Halo {user.first_name}! Verifikasi dulu ya!\n\nBerapa {a} + {b}? (60 detik)"
        )

        asyncio.create_task(timeout_kick(context, chat_id, user_id, user.first_name))


# Timeout kick
async def timeout_kick(context, chat_id, user_id, name):
    await asyncio.sleep(60)

    if user_id in pending_users:
        try:
            await context.bot.ban_chat_member(chat_id, user_id)
        except:
            pass

        del pending_users[user_id]

        await context.bot.send_message(chat_id, f"{name} tidak verifikasi. Auto kick!")


# Cek jawaban user
async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in pending_users:
        correct = pending_users[user_id]["answer"]

        try:
            if int(update.message.text) == correct:
                del pending_users[user_id]
                await update.message.reply_text("Verifikasi berhasil!")
            else:
                await update.message.reply_text("Jawaban salah!")
        except:
            await update.message.reply_text("Masukkan angka yang valid!")


# Main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))

    print("Bot berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
