import time
import talib
import numpy as np
import requests
from binance.client import Client
from binance.enums import *
import os
from dotenv import load_dotenv  # Import dotenv for environment variables

# Load environment variables from .env
load_dotenv()

# Setup your Binance API client securely
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key, api_secret)

# Function to send a message to your Telegram
def send_telegram_message(message):
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(telegram_url)

# Function to check market and generate trade signal
def check_signal():
    symbol = "BTCUSDT"
    candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=100)
    
    closes = [float(candle[4]) for candle in candles]  # Extract closing prices
    
    rsi = talib.RSI(np.array(closes), timeperiod=14)
    macd, macdsignal, macdhist = talib.MACD(np.array(closes), fastperiod=12, slowperiod=26, signalperiod=9)
    
    current_price = closes[-1]

    print(f"Latest RSI: {rsi[-1]:.2f}, Latest MACD: {macd[-1]:.2f}, MACD Signal: {macdsignal[-1]:.2f}")
    
    if rsi[-1] < 30 and macd[-1] > macdsignal[-1]:  # Buy Signal
        entry_price = current_price
        stop_loss = current_price * 0.99  # 1% below entry
        take_profit = current_price * 1.05  # 5% above entry
        leverage = 10  

        signal = f"📈 Buy Long Signal\nEntry: {entry_price:.2f}, Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}, Leverage: {leverage}x"
        return signal
    
    elif rsi[-1] > 70 and macd[-1] < macdsignal[-1]:  # Sell Signal
        entry_price = current_price
        stop_loss = current_price * 1.01  # 1% above entry
        take_profit = current_price * 0.95  # 5% below entry
        leverage = 10  

        signal = f"📉 Sell Short Signal\nEntry: {entry_price:.2f}, Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}, Leverage: {leverage}x"
        return signal
    
    return None  

# Run only when a strong signal is found
def run_bot():
    while True:
        print("Checking for trade signal...")

        signal = check_signal()

        if signal:  
            print(f"✅ Strong Signal Found: {signal}")
            send_telegram_message(signal)  # Send message to Telegram
        
        time.sleep(60)  # Check every 1 minute instead of waiting 5 mins if no signal

# Start the bot
run_bot()
