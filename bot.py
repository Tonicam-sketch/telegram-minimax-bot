import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

API_KEY = os.getenv("API_KEY", "sk-656a3b5a97034e5496fcee067e547cc8")
API_URL = "https://right.codes/claude-aws/v1/chat/completions"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "")

bot_app = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('你好！我是 AI 助手，有什么可以帮你的吗？')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-sonnet-4-5",
        "messages": [{"role": "user", "content": user_message}]
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            await update.message.reply_text(f"API 错误 {response.status_code}")
            return
            
        result = response.json()
        
        if "choices" in result and result["choices"]:
            ai_reply = result["choices"][0]["message"]["content"]
            await update.message.reply_text(ai_reply)
        else:
            await update.message.reply_text("抱歉，无法获取回复")
    except Exception as e:
        print(f"错误: {e}")
        await update.message.reply_text(f"出错了: {str(e)[:100]}")

async def index(request):
    return web.Response(text='Bot is running!')

async def webhook(request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return web.Response(text='ok')

async def on_startup(app):
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
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_post('/webhook', webhook)
    app.on_startup.append(on_startup)
    
    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host='0.0.0.0', port=port)
