import os
import requests
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return 'Bot is running!'

@flask_app.route('/health')
def health():
    return 'OK'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('你好！我是基于 MiniMax 的 AI 助手。')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "abab6.5s-chat",
        "messages": [{"role": "user", "content": user_message}],
        "tokens_to_generate": 1024
    }
    try:
        response = requests.post(MINIMAX_API_URL, json=payload, headers=headers, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        
        if response.status_code != 200:
            await update.message.reply_text(f"API 错误 {response.status_code}: {response.text[:100]}")
            return
            
        result = response.json()
        
        if not result:
            await update.message.reply_text("API 返回空响应")
            return
        
        if "choices" in result and result["choices"] and len(result["choices"]) > 0:
            ai_reply = result["choices"][0].get("message", {}).get("content", "")
            if not ai_reply:
                ai_reply = result["choices"][0].get("text", "抱歉，无法回答。")
        elif "reply" in result:
            ai_reply = result["reply"]
        else:
            ai_reply = f"未知格式: {str(result)[:200]}"
        
        await update.message.reply_text(ai_reply)
    except Exception as e:
        print(f"错误: {e}")
        await update.message.reply_text(f"出错了: {str(e)}")

def run_flask():
    port = int(os.getenv("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot 运行中...")
    app.run_polling()

if __name__ == '__main__':
    main()

