import telebot
import requests
import random
from datetime import datetime
import schedule
import time
import threading

# Configuration
BOT_TOKEN = "7989292150:AAH20ZGzPCapo-DLiqFOgX2HtzrRwJPXOBI"
CHANNEL_USERNAME = "@bestwinner224"
PROMO_CODE = "MDC24"
API_FOOTBALL_KEY = "681966372002f8f2d9cc615819019db5"
ADMIN_ID = 5426221156

# Liste des utilisateurs VIP
VIP_USERS = [5426221156]

bot = telebot.TeleBot(BOT_TOKEN)

TYPES_PARIS = [
    "Victoire de l'équipe 1",
    "Victoire de l'équipe 2",
    "Match nul ou équipe 1 gagne",
    "Les deux équipes marquent",
    "+2.5 buts dans le match",
    "-2.5 buts dans le match",
    "Score exact : 1-0",
    "Score exact : 2-1",
    "Score exact : 0-0",
    "Score exact : 3-2"
]

def generer_pronostic():
    pari = random.choice(TYPES_PARIS)
    cote = round(random.uniform(1.50, 2.80), 2)
    return pari, cote

def get_matchs_du_jour_avec_pronostics():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    params = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timezone": "Africa/Conakry"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        matchs = data.get("response", [])
        if not matchs:
            return "Désolé, aucun match n’est disponible aujourd’hui."
        message = "📊 *Pronostics du jour :*\n"
        for match in matchs[:2]:
            equipe1 = match["teams"]["home"]["name"]
            equipe2 = match["teams"]["away"]["name"]
            heure = match["fixture"]["date"][11:16]
            pari, cote = generer_pronostic()
            message += (
                f"\n• {equipe1} vs {equipe2} à {heure}\n"
                f"  ➤ Pronostic : {pari}\n"
                f"  ➤ Cote : {cote}\n"
            )
        message += (
            "\n\n**Pour des pronostics 100% VIP :**\n"
            f"👉 Rejoins notre VIP ici : https://t.me/{CHANNEL_USERNAME}"
        )
        return message
    else:
        return "Erreur lors de la récupération des matchs."

def envoyer_message_matin():
    texte = (
        "Bienvenue sur le canal où les pronostics riment avec résultats ! "
        "Ici, on ne plaisante pas avec les chiffres : analyses pointues, cotes sélectionnées "
        "et gains réguliers sont au rendez-vous. Rejoignez-nous pour transformer vos paris en profits !\n\n"
        "Bonjour ! Préparez-vous, les pronostics arrivent à 10h pile !"
    )
    bouton = telebot.types.InlineKeyboardMarkup()
    bouton.add(telebot.types.InlineKeyboardButton("Bonus", callback_data="bonus"))
    bot.send_message(chat_id=CHANNEL_USERNAME, text=texte, reply_markup=bouton)

def envoyer_message_soir():
    texte = (
        "Bienvenue sur le canal où les pronostics riment avec résultats ! "
        "Ici, on ne plaisante pas avec les chiffres : analyses pointues, cotes sélectionnées "
        "et gains réguliers sont au rendez-vous. Rejoignez-nous pour transformer vos paris en profits !\n\n"
        "Bonsoir à tous les parieurs !"
    )
    bouton = telebot.types.InlineKeyboardMarkup()
    bouton.add(telebot.types.InlineKeyboardButton("Bonus", callback_data="bonus"))
    bot.send_message(chat_id=CHANNEL_USERNAME, text=texte, reply_markup=bouton)

def envoyer_pronostics():
    message = get_matchs_du_jour_avec_pronostics()
    bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="Markdown")
    for user in VIP_USERS:
        bot.send_message(user, f"⭐ *PRONOSTIC VIP DU JOUR* ⭐\n{get_matchs_du_jour_avec_pronostics()}", parse_mode="Markdown")
        bot.send_message(ADMIN_ID, f"Le VIP {user} a reçu ses pronostics.")

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "bonus":
        bot.send_message(call.from_user.id,
            "Voici tes options BONUS :\n\n"
            "1. Partage le lien du canal pour gagner 1.000 GNF par partage.\n"
            "2. Partage le code promo *MDC24* : Si quelqu’un l’utilise pour recharger 20.000 GNF, tu gagnes 10.000 GNF !",
            parse_mode="Markdown"
        )

def start_schedule():
    schedule.every().day.at("07:00").do(envoyer_message_matin)
    schedule.every().day.at("19:00").do(envoyer_message_soir)
    schedule.every().day.at("10:00").do(envoyer_pronostics)

    while True:
        schedule.run_pending()
        time.sleep(30)

threading.Thread(target=start_schedule).start()

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Bienvenue sur le bot Best Winner !")

print("Bot lancé avec succès.")
bot.polling()
