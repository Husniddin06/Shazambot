from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MAX BOT DASHBOARD</title>
        <style>
            body { font-family: sans-serif; text-align: center; padding-top: 50px; background: #121212; color: white; }
            .status { color: #00ff00; font-weight: bold; }
            .container { border: 1px solid #333; display: inline-block; padding: 20px; border-radius: 10px; background: #1e1e1e; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 MAX BOT DASHBOARD</h1>
            <p>Status: <span class="status">ONLINE</span></p>
            <p>Version: 2.0 (Pro Level)</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
