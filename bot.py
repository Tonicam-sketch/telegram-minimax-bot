import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from quart import Quart, request

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "")

app = Quart(__name__)
bot_app = None

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
        
        if response.status_code != 200:
            await update.message.reply_text(f"API 错误 {response.status_code}")
            return
            
        result = response.json()
        
        if not result:
            await update.message.reply_text("API 返回空响应")
            return
        
        if "choices" in result and result["choices"]:
            ai_reply = result["choices"][0].get("message", {}).get("content", "")
            if not ai_reply:
                ai_reply = result["choices"][0].get("text", "")
        elif "reply" in result:
            ai_reply = result["reply"]
        else:
            ai_reply = "抱歉，无法理解 API 响应"
        
        if ai_reply:
            await update.message.reply_text(ai_reply)
        else:
            await update.message.reply_text("抱歉，没有收到回复")
    except Exception as e:
        print(f"错误: {e}")
        await update.message.reply_text(f"出错了: {str(e)[:100]}")

@app.route('/')
async def index():
    return 'Bot is running!'

@app.route('/webhook', methods=['POST'])
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return 'ok'

@app.before_serving
async def setup():
    global bot_app
    bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
    await bot_app.initialize()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    if WEBHOOK_URL:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        await bot_app.bot.set_webhook(url=webhook_url)
        print(f"Webhook 设置为: {webhook_url}")

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

