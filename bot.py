import os
import sys
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

# 添加 Hermes 到 Python 路径
sys.path.insert(0, '/opt/render/project/src/hermes-agent')

from run_agent import AIAgent

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "")

bot_app = None
hermes_sessions = {}  # 存储每个用户的 Hermes 会话

def get_hermes_agent(user_id):
    """为每个用户创建独立的 Hermes Agent"""
    if user_id not in hermes_sessions:
        hermes_sessions[user_id] = AIAgent(
            model="anthropic/claude-sonnet-4",
            max_iterations=50,
            enabled_toolsets=["core", "file", "web"],
            quiet_mode=True,
            platform="telegram"
        )
    return hermes_sessions[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '你好！我是 Hermes Agent，可以帮你执行各种任务：\n'
        '- 搜索信息\n'
        '- 编写代码\n'
        '- 文件操作\n'
        '- 执行命令\n\n'
        '直接发消息给我就可以了！'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    try:
        # 获取用户的 Hermes Agent
        agent = get_hermes_agent(user_id)
        
        # 在后台线程运行 Hermes（因为它是同步的）
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            agent.chat,
            user_message
        )
        
        await update.message.reply_text(response)
    except Exception as e:
        print(f"错误: {e}")
        await update.message.reply_text(f"出错了: {str(e)[:200]}")

async def index(request):
    return web.Response(text='Hermes Telegram Bot is running!')

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
