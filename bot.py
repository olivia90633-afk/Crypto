import requests
import asyncio
import os
from telegram import Bot

# Load from Railway environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=BOT_TOKEN)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# Get price data
def get_prices(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=50"
    data = requests.get(url).json()
    return [float(candle[4]) for candle in data]

# EMA calculation
def calculate_ema(prices, period):
    ema = prices[0]
    k = 2 / (period + 1)
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

# RSI calculation
def calculate_rsi(prices, period=14):
    gains, losses = [], []
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

# Signal logic
def analyze(symbol):
    prices = get_prices(symbol)

    ema10 = calculate_ema(prices, 10)
    ema50 = calculate_ema(prices, 50)
    rsi = calculate_rsi(prices)

    last_price = prices[-1]

    # BUY condition
    if rsi < 35 and ema10 > ema50:
        return f"""🔥 BUY SIGNAL
Pair: {symbol}
Price: {last_price}
RSI: {round(rsi,2)}
Trend: Uptrend confirmed"""

    # SELL condition
    elif rsi > 65 and ema10 < ema50:
        return f"""⚡ SELL SIGNAL
Pair: {symbol}
Price: {last_price}
RSI: {round(rsi,2)}
Trend: Downtrend confirmed"""

    return None

# Send message
async def send_signal(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Main loop
async def main():
    # First test message (IMPORTANT)
    await send_signal("✅ Bot started successfully!")

    while True:
        for symbol in SYMBOLS:
            try:
                signal = analyze(symbol)

                if signal:
                    await send_signal(signal)
                    print("Sent:", signal)
                else:
                    print(f"No signal for {symbol}")

            except Exception as e:
                print("Error:", e)

        await asyncio.sleep(300)  # 5 minutes

# Run bot
asyncio.run(main())
