import json
import time
import requests

TOKEN = "8538013322:AAHeZNanm4rWh2GDfnfk4w7--hl_Qf8-Zo8"  # Apna Token yahan rakhein
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def send_message_with_keyboard(chat_id, text, reply_markup=None):
  url = f"{BASE_URL}/sendMessage"
  payload = {
      "chat_id": chat_id,
      "text": text,
      "parse_mode": "Markdown",
  }
  if reply_markup:
    payload["reply_markup"] = json.dumps(reply_markup)

  try:
    requests.post(url, json=payload)
  except Exception as e:
    print("Send error:", e)


def get_pro_analysis(symbol):
  symbol_upper = symbol.upper()
  symbol_pair = symbol_upper + "USDT"
  url = f"https://api.binance.com/api/v3/klines?symbol={symbol_pair}&interval=1h&limit=25"

  try:
    res = requests.get(url, timeout=10).json()
    if not isinstance(res, list) or len(res) < 10:
      return None, "❌ Invalid symbol! Sahi naam dalein (e.g., btc, eth)."

    closes = [float(c[4]) for c in res]
    highs = [float(c[2]) for c in res]
    lows = [float(c[3]) for c in res]

    current_price = closes[-1]
    max_price = max(highs)
    min_price = min(lows)
    diff = max_price - min_price
    fib_618 = max_price - 0.618 * diff

    # RSI Calculation (14-period)
    gains, losses = [], []
    for i in range(1, len(closes)):
      chg = closes[i] - closes[i - 1]
      gains.append(chg if chg > 0 else 0)
      losses.append(abs(chg) if chg < 0 else 0)

    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    rsi = 100 if avg_loss == 0 else round(100 - (100 / (1 + (avg_gain / avg_loss))), 2)

    if rsi < 30:
      signal = (
          "🟢 **STRONG BUY SIGNAL (Oversold)**\nMarket support & golden zone ke"
          " paas hai!"
      )
    elif rsi > 70:
      signal = (
          "🔴 **STRONG SELL SIGNAL (Overbought)**\nMarket resistance par hai,"
          " profit book karein!"
      )
    else:
      signal = (
          "⏳ **NEUTRAL / HOLD**\nTrend clear hone ka wait karein."
      )

    sl = round(current_price * 0.98, 2)
    tp = round(current_price * 1.04, 2)

    report = (
        f"📊 **TRADINGVIEW PRO ANALYSIS ({symbol_pair})**\n\n"
        f"💵 **Current Price:** `${current_price:,.2f}`\n"
        f"📈 **RSI (1-Hour):** `{rsi}`\n\n"
        f"💡 **Signal:**\n{signal}\n\n"
        f"--- 🎯 **PRICE ACTION & LEVELS** ---\n"
        f"• **Resistance (High):** `${max_price:,.2f}`\n"
        f"• **Support (Low):** `${min_price:,.2f}`\n"
        f"• **Fib 0.618 (Golden Zone):** `${fib_618:,.2f}`\n\n"
        f"--- ⚖️ **RISK MANAGEMENT (1:2)** ---\n"
        f"• **Stop-Loss (-2%):** `${sl:,.2f}`\n"
        f"• **Take-Profit (+4%):** `${tp:,.2f}`"
    )

    # TradingView Direct Interactive URL Button
    tv_url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol_pair}"
    keyboard = {
        "inline_keyboard": [[
            {"text": f"📈 Open {symbol_pair} on TradingView", "url": tv_url}
        ]]
    }

    return report, keyboard
  except Exception as e:
    print("Error:", e)
    return "⚠️ Analysis fetch karne mein error aaya.", None


def main():
  print("🤖 TradingView Connected Bot Started...")
  offset = None

  while True:
    try:
      url = f"{BASE_URL}/getUpdates?timeout=20"
      if offset:
        url += f"&offset={offset}"

      response = requests.get(url, timeout=30).json()

      if "result" in response:
        for update in response["result"]:
          offset = update["update_id"] + 1

          if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"].strip()

            if text == "/start":
              msg = (
                  "👋 **Welcome to TradingView Bot!**\n\n"
                  "Send:\n🔹 `/chart btc` - Live Analysis + TradingView Button\n🔹"
                  " `/chart eth` - Ethereum Report"
              )
              send_message_with_keyboard(chat_id, msg)

            elif text.startswith("/chart") or text.startswith("/analysis"):
              parts = text.split()
              if len(parts) > 1:
                coin = parts[1]
                send_message_with_keyboard(
                    chat_id,
                    f"⚡ {coin.upper()} ka data fetch ho raha hai...",
                )
                report, keyboard = get_pro_analysis(coin)
                send_message_with_keyboard(
                    chat_id, report, reply_markup=keyboard
                )
              else:
                send_message_with_keyboard(
                    chat_id, "⚠️ Kripya coin ka naam dein. Example: `/chart btc`"
                )

    except Exception as e:
      print("Loop error:", e)

    time.sleep(1)


if __name__ == "__main__":
  main()
