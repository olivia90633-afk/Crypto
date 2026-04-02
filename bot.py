import requests
import pandas as pd
import pandas_ta as ta
import asyncio
import time
from telegram import Bot
from config import BOT_TOKEN, CHAT_ID

bot = Bot(token=BOT_TOKEN)

# Coins to monitor
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# Send message
async def send_signal(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Get market data
def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
    data = requests.get(url).json()
    closes = [float(candle[4]) for candle in data]
    df = pd.DataFrame(closes, columns=["close"])
    return df

# Analyze market
def analyze(symbol):
    df = get_data(symbol)

    df["EMA10"] = ta.ema(df["close"], length=10)
    df["EMA50"] = ta.ema(df["close"], length=50)
    df["RSI"] = ta.rsi(df["close"], length=14)

    macd = ta.macd(df["close"])
    df = pd.concat([df, macd], axis=1)

    last = df.iloc[-1]

    signal = None

    # BUY condition
    if (
        last["RSI"] < 35 and
        last["EMA10"] > last["EMA50"] and
        last["MACD_12_26_9"] > last["MACDs_12_26_9"]
    ):
        signal = f"🔥 BUY SIGNAL\n{symbol}\nRSI: {round(last['RSI'],2)}"

    # SELL condition
    elif (
        last["RSI"] > 65 and
        last["EMA10"] < last["EMA50"] and
        last["MACD_12_26_9"] < last["MACDs_12_26_9"]
    ):
        signal = f"⚡ SELL SIGNAL\n{symbol}\nRSI: {round(last['RSI'],2)}"

    return signal

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

        await asyncio.sleep(300)  # wait 5 minutes

# Run bot
asyncio.run(main())
