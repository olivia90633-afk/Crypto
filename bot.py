# bot.py
import requests
import pandas as pd
import pandas_ta as ta
from telegram import Bot
from config import BOT_TOKEN, CHAT_ID

# Step 1: Fetch BTC/USDT data from Binance (last 100 1-hour candles)
url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100"
data = requests.get(url).json()

# Step 2: Extract closing prices
close_prices = [float(candle[4]) for candle in data]
df = pd.DataFrame(close_prices, columns=["close"])

# Step 3: Calculate indicators
df["EMA10"] = ta.ema(df["close"], length=10)
df["RSI"] = ta.rsi(df["close"], length=14)
macd = ta.macd(df["close"])
df = pd.concat([df, macd], axis=1)

# Step 4: Simple rule for signal
last_rsi = df["RSI"].iloc[-1]
last_ema10 = df["EMA10"].iloc[-1]
last_close = df["close"].iloc[-1]

signal = ""
if last_rsi < 35 and last_close > last_ema10:
    signal = "🔥 Buy Signal for BTC!"
elif last_rsi > 65 and last_close < last_ema10:
    signal = "⚡ Sell Signal for BTC!"
else:
    signal = "No signal right now."

# Step 5: Send message to Telegram
bot = Bot(token=8242593757:AAHoIOP1pcXwPPGto5KAHg3A_gVctmrGhAU)
bot.send_message(chat_id=CHAT_ID, text=signal)
print("Signal sent:", signal)
