# Telegram MiniMax Bot

基于 MiniMax API 的 Telegram 机器人

## 部署到 Render.com（免费）

1. 访问 https://render.com 注册账号
2. 点击 "New +" -> "Web Service"
3. 连接你的 GitHub 账号
4. 选择这个仓库
5. 配置：
   - Name: telegram-minimax-bot
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
6. 添加环境变量：
   - TELEGRAM_TOKEN: 8673537660:AAGK9eeFE1RcctG_gKPWOHBUU1LSRtBRWfQ
   - MINIMAX_API_KEY: sk-cp-baAhBw_oyITPeuCPxqZrmJPug0AadUsAZp6PIVoZ5836ElSTx-JqXOC1S1q0M-LZIP3mtvFnMWCzWSy8XwfnFuWkdL466Uw8plbW_FIHlRY8CK1HArZMqxc
7. 点击 "Create Web Service"

部署完成后，在 Telegram 中搜索你的 bot 并开始聊天！
