import requests
import asyncio
from telegram import Bot
from config import BOT_TOKEN, CHAT_ID

bot = Bot(8242593757:AAHoIOP1pcXwPPGto5KAHg3A_gVctmrGhAU)

SYMBOLS = ["BTCUSDT", "ETHUSDT"]

# Get price data
def get_prices(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=50"
    data = requests.get(url).json()
    closes = [float(candle[4]) for candle in data]
    return closes

# Simple EMA
def calculate_ema(prices, period):
    ema = prices[0]
    k = 2 / (period + 1)
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

# Simple RSI
def calculate_rsi(prices, period=14):
    gains = []
    losses = []

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Analyze signal
def analyze(symbol):
    prices = get_prices(symbol)

    ema10 = calculate_ema(prices, 10)
    ema50 = calculate_ema(prices, 50)
    rsi = calculate_rsi(prices)

    last_price = prices[-1]

    # BUY
    if rsi < 35 and ema10 > ema50:
        return f"🔥 BUY SIGNAL\n{symbol}\nRSI: {round(rsi,2)}"

    # SELL
    elif rsi > 65 and ema10 < ema50:
        return f"⚡ SELL SIGNAL\n{symbol}\nRSI: {round(rsi,2)}"

    return None

# Send message
async def send_signal(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg)

# Main loop
async def main():
    while True:
        for symbol in SYMBOLS:
            try:
                signal = analyze(symbol)
                if signal:
                    await send_signal(signal)
                    print("Sent:", signal)
            except Exception as e:
                print("Error:", e)

        await asyncio.sleep(300)  # 5 minutes

asyncio.run(main())
