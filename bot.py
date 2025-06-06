import os
import json
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext,
)

TOKEN = "8078548699:AAEEkJo2vp1S4chVl25j0SuRv9xojSy_rj4"
ADMIN_ID = 6881537234
DB_FILE = "users.json"
FREE_SIGNALS = 2
BONUS_SIGNALS = 3
VALID_GAMES = ["Crash", "Aviator", "Lucky Jet"]

# --- Fonctions pour la base de données ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

def get_user(user_id):
    data = load_data()
    return data.get(str(user_id), {"signals_used": 0, "has_bonus": False})

def update_user(user_id, user_data):
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)

def get_all_users():
    return load_data()

# --- Fonction pour générer un signal aléatoire ---
def generate_signal():
    return f"🚀 MULTI PRÉVU : x{random.choice([1.5, 2, 3, 5, 7, 10])}"

# --- Commandes Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [KeyboardButton("📲 Demander un signal")],
        [KeyboardButton("🎮 Choisir le jeu")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"Bienvenue {user.first_name} 👋\n\nTu peux recevoir des signaux gratuits pour les jeux Crash, Aviator ou Lucky Jet.\n\nTape sur un bouton ci-dessous pour commencer 👇", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_data = get_user(user.id)

    if text == "📲 Demander un signal":
        if user_data["signals_used"] < FREE_SIGNALS:
            signal = generate_signal()
            user_data["signals_used"] += 1
            update_user(user.id, user_data)
            await update.message.reply_text(signal)
        elif not user_data["has_bonus"]:
            await update.message.reply_text(
                "⚠️ Tu as utilisé tes 2 signaux gratuits.\n\n✅ Crée un compte 1win avec le code promo *AK0127* et envoie une capture d’écran ici pour recevoir 3 signaux supplémentaires.",
                parse_mode="Markdown",
            )
        else:
            if user_data["signals_used"] < FREE_SIGNALS + BONUS_SIGNALS:
                signal = generate_signal()
                user_data["signals_used"] += 1
                update_user(user.id, user_data)
                await update.message.reply_text(signal)
            else:
                await update.message.reply_text("🚫 Tu as utilisé tous tes signaux. Reviens plus tard.")

    elif text == "🎮 Choisir le jeu":
        keyboard = [[KeyboardButton(game)] for game in VALID_GAMES]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Choisis un jeu :", reply_markup=reply_markup)

    elif text in VALID_GAMES:
        await update.message.reply_text(f"🎮 Tu as sélectionné *{text}*.\n\nClique sur 📲 Demander un signal pour recevoir un signal pour ce jeu.", parse_mode="Markdown")

    elif update.message.photo:
        if user_data["has_bonus"]:
            await update.message.reply_text("✅ Capture déjà vérifiée. Tu as déjà reçu tes bonus.")
        else:
            user_data["has_bonus"] = True
            update_user(user.id, user_data)
            await update.message.reply_text("✅ Capture reçue et vérifiée. Tu as maintenant accès à 3 signaux supplémentaires !")

    else:
        await update.message.reply_text("❓ Je n’ai pas compris. Utilise les boutons du menu.")

# --- Commande admin pour envoyer un signal manuellement ---
async def send_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Utilisation : /signal user_id message")
        return
    target_id = int(context.args[0])
    message = " ".join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=target_id, text=message)
        await update.message.reply_text("✅ Signal envoyé.")
    except Exception as e:
        await update.message.reply_text(f"Erreur : {e}")

# --- Commande admin pour voir la liste des utilisateurs ---
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    data = get_all_users()
    message = "📋 Utilisateurs :\n"
    for uid, info in data.items():
        message += f"- {uid}: {info['signals_used']} signaux utilisés, bonus = {info['has_bonus']}\n"
    await update.message.reply_text(message)

# --- Lancer le bot ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", send_signal))
    app.add_handler(CommandHandler("users", list_users))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
