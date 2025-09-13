import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========= CONFIG =========
BOT_TOKEN = "8051121625:AAHzLJuDSMtEbpyVnM_vgYGJBvpZqPAkJVo"
API_BASE = "https://osint.stormx.pw/index.cpp?key=dark"
ADMIN_IDS = [7549280896]  # admin chat_id list
ACCESS_LIST = []  # user_ids with access
# ==========================

# --- Formatter ---
def format_result(raw_text, data_type):
    """
    Clean, concise, emoji-enhanced formatting for OSINT results
    """
    lines = raw_text.splitlines()
    formatted_lines = []
    person_counter = 1

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Person separator
        if any(k in line.lower() for k in ["name", "person"]):
            formatted_lines.append(f"\n🔎 {data_type.capitalize()} Person {person_counter}:")
            person_counter += 1
        # Map fields to emoji
        if "name" in line.lower():
            val = line.split(":",1)[-1].strip()
            formatted_lines.append(f"👤 Name: {val}")
        elif "father" in line.lower():
            val = line.split(":",1)[-1].strip()
            formatted_lines.append(f"👨‍👦 Father's Name: {val}")
        elif "address" in line.lower():
            val = line.split(":",1)[-1].strip()
            formatted_lines.append(f"🏠 Address: {val}")
        elif "circle" in line.lower():
            val = line.split(":",1)[-1].strip()
            formatted_lines.append(f"🌎 Circle: {val}")
        elif "mobile" in line.lower():
            val = line.split(":",1)[-1].strip()
            formatted_lines.append(f"📱 Mobile: {val}")
        elif "alt" in line.lower():
            val = line.split(":",1)[-1].strip()
            formatted_lines.append(f"📞 Alt Mobile: {val}")
        elif "id" in line.lower():
            val = line.split(":",1)[-1].strip()
            formatted_lines.append(f"🆔 ID: {val}")
        elif "email" in line.lower():
            val = line.split(":",1)[-1].strip()
            formatted_lines.append(f"📧 Email: {val}")
    return "\n".join(formatted_lines) if formatted_lines else "❌ No data found."

# --- Access check ---
async def is_admin(update: Update):
    return update.effective_user.id in ADMIN_IDS

async def check_access(user_id):
    return user_id in ACCESS_LIST or user_id in ADMIN_IDS

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_access(user_id):
        await update.message.reply_text("❌ You do not have access. Ask admin for /access")
        return
    await update.message.reply_text(
        "✅ Welcome to GHOST OSINT Bot\n\nCommands:\n"
        "/numinfo <number>\n"
        "/vehicle <number>\n"
        "/aadhaar <number>\n"
        "/upi <upi_id>\n"
        "/access <chat_id> (Admin only)"
    )

async def give_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /access <chat_id>")
        return
    try:
        user_id = int(context.args[0])
        if user_id not in ACCESS_LIST:
            ACCESS_LIST.append(user_id)
            await update.message.reply_text(f"✅ Access granted to user {user_id}")
        else:
            await update.message.reply_text("User already has access.")
    except:
        await update.message.reply_text("❌ Invalid chat_id")

async def fetch_osint(update: Update, context: ContextTypes.DEFAULT_TYPE, field):
    user_id = update.effective_user.id
    if not await check_access(user_id):
        await update.message.reply_text("❌ You do not have access. Ask admin for /access")
        return
    if not context.args:
        await update.message.reply_text(f"Usage: /{field} <value>")
        return
    value = context.args[0]
    url = f"{API_BASE}&{field}={value}"
    try:
        raw = requests.get(url).text
        formatted = format_result(raw, field)
        # Telegram message splitting for 4096 char limit
        for i in range(0, len(formatted), 4000):
            await update.message.reply_text(formatted[i:i+4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def numinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_osint(update, context, "number")

async def vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_osint(update, context, "vehicle")

async def aadhaar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_osint(update, context, "aadhaar")

async def upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_osint(update, context, "upi")

# --- Main ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("access", give_access))
    app.add_handler(CommandHandler("numinfo", numinfo))
    app.add_handler(CommandHandler("vehicle", vehicle))
    app.add_handler(CommandHandler("aadhaar", aadhaar))
    app.add_handler(CommandHandler("upi", upi))

    print("GHOST OSINT Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
