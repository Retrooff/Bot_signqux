import telebot 
from telebot import types 
import json 
import os

=== CONFIGURATION ===

TOKEN = "8078548699:AAEEkJo2vp1S4chVl25j0SuRv9xojSy_rj4" ADMIN_ID = 8121512840  # Ton ID admin

=== FICHIER DE DONNÉES ===

DB_FILE = "users.json"

def load_data(): if not os.path.exists(DB_FILE): return {} with open(DB_FILE, 'r') as f: return json.load(f)

def save_data(data): with open(DB_FILE, 'w') as f: json.dump(data, f, indent=2)

data = load_data() bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

=== START ===

@bot.message_handler(commands=['start']) def start(msg): user_id = str(msg.from_user.id) if user_id not in data: data[user_id] = { "signals_used": 0, "verified": False } save_data(data)

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row("📊 Crash", "✈️ Aviator", "🚀 Lucky Jet")
keyboard.row("🎁 Mon ID Telegram", "💎 Premium")
bot.send_message(msg.chat.id, f"👋 Bienvenue sur le bot de prédiction !\n\n🎁 Tu as droit à 5 signaux gratuits.\n💡 Utilise le code promo <b>AK0127</b> pour t'inscrire sur 1win et débloquer les signaux.\n\nChoisis ton jeu ci-dessous ⬇️", reply_markup=keyboard)

=== IDENTIFIANT ===

@bot.message_handler(func=lambda m: m.text == "🎁 Mon ID Telegram") def send_id(msg): bot.reply_to(msg, f"🪪 Ton ID est : <code>{msg.from_user.id}</code>\nEnvoie-le à l'admin pour recevoir des signaux 🎯")

=== JEU ===

def handle_game_prediction(msg, game): user_id = str(msg.from_user.id) user = data.get(user_id)

if not user:
    return start(msg)

if user["signals_used"] < 2:
    user["signals_used"] += 1
    save_data(data)
    return bot.reply_to(msg, generate_prediction(game))

elif not user["verified"]:
    bot.send_message(msg.chat.id, "🔐 Tu as utilisé tes 2 signaux gratuits.\nPour débloquer les 3 autres, crée un compte 1win avec le code <b>AK0127</b> et envoie une capture d’écran ici.")
    bot.register_next_step_handler(msg, handle_verification)

elif user["signals_used"] < 5:
    user["signals_used"] += 1
    save_data(data)
    return bot.reply_to(msg, generate_prediction(game))

else:
    bot.send_message(msg.chat.id, "🚫 Tu as utilisé tous tes 5 signaux gratuits. Contacte l’admin pour en recevoir plus ✉️")

@bot.message_handler(func=lambda m: m.text in ["📊 Crash", "✈️ Aviator", "🚀 Lucky Jet"]) def game_selector(msg): if msg.text == "📊 Crash": handle_game_prediction(msg, "Crash") elif msg.text == "✈️ Aviator": handle_game_prediction(msg, "Aviator") elif msg.text == "🚀 Lucky Jet": handle_game_prediction(msg, "Lucky Jet")

=== GÉNÉRATION DE SIGNAL ===

import random

def generate_prediction(game): x = round(random.uniform(1.5, 100), 2) return f"📡 Signal pour <b>{game}</b> : x<b>{x}</b> 🔥\n\nCode promo : <b>AK0127</b>"

=== VÉRIFICATION DE CAPTURE ===

def handle_verification(msg): if msg.content_type == 'photo': bot.send_message(ADMIN_ID, f"📸 Nouvelle capture reçue de <code>{msg.from_user.id}</code>") bot.forward_message(ADMIN_ID, msg.chat.id, msg.message_id) bot.send_message(msg.chat.id, "✅ Capture envoyée à l'admin. Attends la validation !") else: bot.send_message(msg.chat.id, "❌ Merci d’envoyer une capture (image). Réessaie avec une photo.")

=== ADMIN PEUT AJOUTER DES SIGNAUX ===

@bot.message_handler(commands=['add']) def add_signal(msg): if msg.from_user.id != ADMIN_ID: return

args = msg.text.split()
if len(args) != 2:
    return bot.reply_to(msg, "❗ Utilisation : /add ID")

user_id = args[1]
if user_id in data:
    data[user_id]["signals_used"] = 0
    data[user_id]["verified"] = True
    save_data(data)
    bot.send_message(msg.chat.id, f"✅ Signaux réinitialisés pour l’utilisateur {user_id} !")
else:
    bot.reply_to(msg, "Utilisateur introuvable.")

=== PREMIUM ===

@bot.message_handler(func=lambda m: m.text == "💎 Premium") def premium(msg): bot.send_message(msg.chat.id, "🌟 Abonne-toi au Premium pour des signaux spéciaux à forte cote !\n\nContacte @Knak0127 pour en profiter. N’oublie pas le code promo : <b>AK0127</b>")

=== LIMITATION EN PRIVÉ ===

@bot.message_handler(func=lambda m: True) def all_private(msg): if msg.chat.type != "private": bot.reply_to(msg, "❌ Ce bot fonctionne uniquement en privé.")

bot.infinity_polling()

