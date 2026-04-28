import os
from flask import Flask
from utils.premium import get_stats

app = Flask(__name__)

@app.route("/")
def home():
    s = get_stats()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MAX BOT DASHBOARD</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: sans-serif; text-align: center; padding-top: 50px;
                   background: #121212; color: white; }}
            .status {{ color: #00ff00; font-weight: bold; }}
            .container {{ border: 1px solid #333; display: inline-block; padding: 30px;
                         border-radius: 10px; background: #1e1e1e; min-width: 300px; }}
            .stat {{ margin: 10px 0; font-size: 18px; }}
            .stat b {{ color: #ffd700; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 MAX BOT DASHBOARD</h1>
            <p>Status: <span class="status">ONLINE</span></p>
            <p>Version: 2.1</p>
            <hr style="border-color:#333;">
            <div class="stat">👤 Foydalanuvchilar: <b>{s['users']}</b></div>
            <div class="stat">👑 Premium: <b>{s['premium']}</b></div>
            <div class="stat">⬇️ Yuklab olishlar: <b>{s['downloads']}</b></div>
        </div>
    </body>
    </html>
    """

@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
