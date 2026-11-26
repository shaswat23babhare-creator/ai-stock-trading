from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
import threading

app = Flask(__name__)

STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS",
    "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "ITC.NS", "TATAMOTORS.NS",
    "TATASTEEL.NS", "BHARTIARTL.NS",
    "AXISBANK.NS", "LT.NS", "WIPRO.NS",
    "MARUTI.NS", "ADANIENT.NS"
]

def scan_stock(stock):
    try:
        df = yf.download(
            stock, period="6mo",
            interval="1d", progress=False
        )

        if df.empty or len(df) < 30:
            return None

        close = df["Close"].squeeze()

        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()

        rs = gain / loss.replace(0, float("nan"))
        rsi = 100 - (100 / (1 + rs))

        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()

        price = float(close.iloc[-1])
        current_rsi = float(rsi.iloc[-1])

        score = 0

        if price > float(ema20.iloc[-1]):
            score += 3

        if float(ema20.iloc[-1]) > float(ema50.iloc[-1]):
            score += 3

        if 45 <= current_rsi <= 65:
            score += 2

        signal = "WATCH"

        if score >= 6:
            signal = "BUY WATCH"

        return {
            "Stock": stock,
            "Price": round(price, 2),
            "RSI": round(current_rsi, 2),
            "Score": score,
            "Signal": signal
        }

    except Exception:
        return None


@app.route("/")
def home():
    results = []

    for stock in STOCKS:
        data = scan_stock(stock)
        if data:
            results.append(data)

    results.sort(
        key=lambda x: x["Score"],
        reverse=True
    )

    html = """
    <h1>AI STOCK SCANNER</h1>
    <h2>NSE Swing Scanner</h2>
    <p>Stocks scanned: {{total}}</p>
    <table border="1" cellpadding="10">
    <tr>
    <th>Stock</th><th>Price</th>
    <th>RSI</th><th>Score</th><th>Signal</th>
    </tr>
    {% for s in stocks %}
    <tr>
    <td>{{s.Stock}}</td>
    <td>{{s.Price}}</td>
    <td>{{s.RSI}}</td>
    <td>{{s.Score}}</td>
    <td>{{s.Signal}}</td>
    </tr>
    {% endfor %}
    </table>
    <br>
    <a href="/">REFRESH SCANNER</a>
    """

    return render_template_string(
        html, stocks=results, total=len(results)
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
