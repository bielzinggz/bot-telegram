import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# Tokens (Telegram + WeatherAPI)
TELEGRAM_TOKEN = "8585551971:AAEEAAv00XSoplZk_Un_oGS0mNRJ9bmNunk"
WEATHER_API_KEY = "3ac274427c914feb9f1232710252711"


# Consulta clima e dados astronômicos
def get_weather_and_astronomy(city):
    weather_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    astro_url = f"https://api.weatherapi.com/v1/astronomy.json?key={WEATHER_API_KEY}&q={city}&dt=today"

    weather_data = requests.get(weather_url).json()
    if "error" in weather_data:
        return None

    astro_data = requests.get(astro_url).json()

    location = weather_data["location"]
    current = weather_data["current"]
    astro = astro_data["astronomy"]["astro"]

    # Texto final enviado ao usuário
    texto = (
        f"Cidade: {location['name']} - {location['region']} / {location['country']}\n"
        f"Hora local: {location['localtime']}\n"
        f"Coordenadas: {location['lat']}, {location['lon']}\n\n"
        f"Clima agora: {current['condition']['text']}\n"
        f"Temperatura: {current['temp_c']}°C\n"
        f"Umidade: {current['humidity']}%\n"
        f"Vento: {current['wind_kph']} km/h\n\n"
        f"Nascer do sol: {astro['sunrise']}\n"
        f"Pôr do sol: {astro['sunset']}\n"
        f"Fase da Lua: {astro['moon_phase']}\n"
        f"Iluminação: {astro['moon_illumination']}%\n"
    )

    return texto


# Responde saudações; caso contrário trata como cidade
async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    saudacoes = ["oi", "olá", "ola", "hello", "hi", "bom dia", "boa tarde", "boa noite"]

    # Mensagem inicial
    if any(texto.startswith(m) for m in saudacoes):
        await update.message.reply_text(
            "👋 Olá! Me envie o nome de uma cidade, ex:\n"
            "Lisboa, Paris, São Paulo.\n\n"
            "Ou use /cidade Nome da Cidade",
            parse_mode="Markdown"
        )
        return

    # Consulta cidade
    city = update.message.text.strip()
    await update.message.reply_text("⏳ Buscando dados...")

    result = get_weather_and_astronomy(city)
    if result is None:
        await update.message.reply_text("❌ Cidade não encontrada.")
        return

    await update.message.reply_text(result, parse_mode="Markdown")


# Comando /cidade
async def cidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Exemplo: /cidade Lisboa")
        return

    city = " ".join(context.args)
    await update.message.reply_text("⏳ Buscando dados...")

    result = get_weather_and_astronomy(city)
    if result is None:
        await update.message.reply_text("❌ Cidade não encontrada.")
        return

    await update.message.reply_text(result, parse_mode="Markdown")


# Inicialização do bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("cidade", cidade))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, boas_vindas))

    print("Bot rodando...")
    app.run_polling()