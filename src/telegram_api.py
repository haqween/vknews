import logging
import datetime
from telegram import Update, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, Dispatcher
from typing import Dict, Any, Callable, List
from flask import Flask, request

logger = logging.getLogger(__name__)

class TelegramAPI:
    def __init__(self, bot_token: str, webhook_url: str, port: int = 8443):
        self.bot_token = bot_token
        self.updater = None
        self.webhook_url = webhook_url
        self.port = port
        self.flask_app = Flask(__name__)

    def start(self, bot):
        """Start Telegram bot"""
        try:
            self.updater = Updater(token=self.bot_token, use_context=True)
            
            # Register handlers to Telegram API
            dispatcher = self.updater.dispatcher
            dispatcher.add_handler(CommandHandler("start", bot.start_handler))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, bot.keyboard_handler))

            # 使用webhook模式
            logger.info("Starting bot in webhook mode...")
            self.run_webhook()

            logger.info("Telegram bot started")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {str(e)}")
            raise


    def _setup_flask_app(self):
        """设置Flask应用和webhook路由"""
        @self.flask_app.route(f'/{self.bot_token}', methods=['POST'])
        def webhook():
            """处理webhook请求"""
            update = Update.de_json(request.get_json(force=True), self.updater.bot)
            self.updater.dispatcher.process_update(update)
            return 'OK', 200

        @self.flask_app.route('/')
        def index():
            """健康检查端点"""
            return 'Telegram Bot Webhook is running', 200

    def set_webhook(self):
        """设置webhook"""
        if not self.updater or not self.webhook_url:
            logger.error("Updater or webhook_url not configured")
            return False
        
        try:
            # 设置webhook URL
            self.updater.bot.set_webhook(
                url=f"{self.webhook_url}/{self.bot_token}",
                drop_pending_updates=True
            )
            logger.info(f"Webhook set to: {self.webhook_url}/{self.bot_token}")
            return True
        except Exception as e:
            logger.error(f"Failed to set webhook: {str(e)}")
            return False

    def delete_webhook(self):
        """删除webhook"""
        if not self.updater:
            return
        
        try:
            self.updater.bot.delete_webhook()
            logger.info("Webhook deleted")
        except Exception as e:
            logger.error(f"Failed to delete webhook: {str(e)}")

    def run_webhook(self):
        """运行webhook服务器"""
        if not self.updater:
            self.start()
        
        if not self.webhook_url:
            logger.error("Webhook URL not configured")
            return
        
        try:
            # 设置webhook
            if self.set_webhook():
                # 设置Flask应用
                self._setup_flask_app()
                logger.info(f"Starting webhook server on port {self.port}")
                # 启动Flask应用
                self.flask_app.run(
                    host='0.0.0.0',
                    port=self.port,
                    ssl_context=None  # 如果需要HTTPS，这里可以配置ssl_context
                )
        except Exception as e:
            logger.error(f"Webhook server exception: {str(e)}")
            # 发生错误时删除webhook
            self.delete_webhook()
            raise

