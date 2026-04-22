import random
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Ambil token dari Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan!")

pending_users = {}

# 🔥 DETECT MEMBER BARU (FIX)
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    for user in update.message.new_chat_members:
        if user.is_bot:
            continue

        chat_id = update.effective_chat.id
        user_id = user.id

        # Soal random
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        answer = a + b

        pending_users[user_id] = {"answer": answer, "chat_id": chat_id}

        await update.message.reply_text(
            f"Halo {user.first_name}! Verifikasi dulu ya!\n\nBerapa {a} + {b}? (60 detik)"
        )

        # Timer kick
        asyncio.create_task(timeout_kick(context, chat_id, user_id, user.first_name))


# ⏱️ AUTO KICK JIKA TIDAK JAWAB
async def timeout_kick(context, chat_id, user_id, name):
    await asyncio.sleep(60)

    if user_id in pending_users:
        try:
            await context.bot.ban_chat_member(chat_id, user_id)
        except:
            pass

        del pending_users[user_id]

        await context.bot.send_message(chat_id, f"{name} tidak verifikasi. Auto kick!")


# ✅ CEK JAWABAN
async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in pending_users:
        correct = pending_users[user_id]["answer"]

        try:
            if int(update.message.text) == correct:
                del pending_users[user_id]
                await update.message.reply_text("Verifikasi berhasil! ✅")
            else:
                await update.message.reply_text("Jawaban salah ❌")
        except:
            await update.message.reply_text("Masukkan angka yang valid!")


# 🚀 MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 🔥 FIX handler join
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))

    # cek jawaban
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))

    print("Bot berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
