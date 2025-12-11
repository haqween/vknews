import logging
import datetime
from telegram import Update, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, Dispatcher
from typing import Dict, Any, Callable, List
from flask import Flask, request

logger = logging.getLogger(__name__)

# Default keyword for searching news in Russian
DEFAULT_KEYWORD = "новости"

class TelegramBot:
    def __init__(self, bot_token: str, webhook_url: str, port: int = 8443):
        self.bot_token = bot_token
        self.user_chat_ids = set()  # 存储从用户消息中获取的聊天ID
        self.application = None
        self.fetch_callback = None
        self.updater = None
        self.bot = None  # 用于直接发送消息的Bot实例
        self.vk_api = None  # VK API实例
        self.webhook_url = webhook_url
        self.port = port
        self.flask_app = Flask(__name__)
        self.user_input_cache = {}  # 存储用户上一次的输入，格式：{chat_id: last_input}
        self.ai_processor = None  # AI处理器实例
        self.text_processor = None  # 文本处理器实例



    def start_handler(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        # 存储用户的chat_id
        chat_id = update.message.chat_id
        self.user_chat_ids.add(chat_id)
        logger.info(f"New user registered with chat_id: {chat_id}")
        
        # 创建Reply Keyboard
        keyboard = [[KeyboardButton("刷一下")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        update.message.reply_text(
            "欢迎使用VK信息摘要翻译机器人！点击下方按钮刷新最新消息。",
            reply_markup=reply_markup
        )


    

    def register_fetch_callback(self, callback: Callable):
        """Register content fetch callback function"""
        self.fetch_callback = callback
    
    def set_ai_processor(self, ai_processor):
        """Set AI processor instance for translation"""
        self.ai_processor = ai_processor
    
    def set_text_processor(self, text_processor):
        """Set text processor instance"""
        self.text_processor = text_processor
    


    def start(self):
        """Start Telegram bot"""
        try:
            self.updater = Updater(token=self.bot_token, use_context=True)
            
            # Register handlers
            dispatcher = self.updater.dispatcher
            
            # 注册基础命令处理函数
            self._register_base_handlers()
            
            logger.info("Telegram bot started")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {str(e)}")
            raise
    
    def keyboard_handler(self, update: Update, context: CallbackContext):
        """处理文本消息事件"""
        text = update.message.text
        chat_id = update.message.chat_id

        update.message.reply_text("正在获取最新消息...")
        if text == "刷一下":
            # 使用上一次的输入作为关键字，如果没有则使用默认的"новости"
            keyword = self.user_input_cache.get(chat_id, DEFAULT_KEYWORD)
            self._execute_refresh(update, chat_id, keyword)
        else:
            # 不是"刷一下"，需要翻译
            try:
                import asyncio
                keyword = asyncio.run(self.text_processor.translate_to_russian(text))
                if not keyword:
                    keyword = DEFAULT_KEYWORD
                
                else:
                    # 缓存用户输入
                    self.user_input_cache[chat_id] = keyword
                
                self._execute_refresh(update, chat_id, keyword)
            except Exception as e:
                logger.error(f"Translation error: {str(e)}")
                update.message.reply_text("发生错误，请稍后重试")
                return
                

        
    def _execute_refresh(self, update, chat_id, keyword):
        """执行刷新操作"""
        try:
            if self.fetch_callback:
                import asyncio
                # 调用回调函数，传递关键字
                result = asyncio.run(self.fetch_callback(chat_id=chat_id, keyword=keyword))
                if result and "success" in result and result["success"]:
                    if result.get("count", 0) > 0:
                        logger.info(f"Successfully fetched and sent {result['count']} newsfeed items with keyword: {keyword}")
                    else:
                        if update:
                            update.message.reply_text("没有获取到相关消息")
                        else:
                            self.send_message("没有获取到相关消息", chat_id=chat_id)
                else:
                    if update:
                        update.message.reply_text("获取消息失败，请稍后重试")
                    else:
                        self.send_message("获取消息失败，请稍后重试", chat_id=chat_id)
            else:
                if update:
                    update.message.reply_text("搜索功能尚未初始化")
                else:
                    self.send_message("搜索功能尚未初始化", chat_id=chat_id)
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            if update:
                update.message.reply_text("处理请求时出错，请稍后重试")
            else:
                self.send_message("处理请求时出错，请稍后重试", chat_id=chat_id)
    
    def _register_base_handlers(self):
        """注册基础命令处理函数"""
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start_handler))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.keyboard_handler))
    


    def send_message(self, text: str, parse_mode='HTML', chat_id=None):
        """Send message to specified chat using HTML format"""
        # 确定要使用的chat_id
        target_chat_id = chat_id
        
        if not target_chat_id:
            logger.error("No valid chat_id available")
            return False
        
        try:
            # 如果有updater，使用updater发送；否则创建一个临时Bot实例
            if self.updater:
                self.updater.bot.send_message(chat_id=target_chat_id, text=text, parse_mode=parse_mode)
            else:
                if not self.bot and self.bot_token:
                    from telegram import Bot
                    self.bot = Bot(token=self.bot_token)
                self.bot.send_message(chat_id=target_chat_id, text=text, parse_mode=parse_mode)
            
            logger.info(f"Successfully sent message to chat ID: {target_chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False


    def send_multiple_processed_content(self, contents: List[Dict[str, Any]], chat_id=None):
        """Send multiple processed contents as a single message"""
        if not contents:
            return False
        
        # Filter contents to ensure we only send messages with all required fields
        filtered_contents = [
            content for content in contents
            if content.get("zh_summary", "") and content.get("ru_summary", "") and content.get("url", "")
        ]
        
        if not filtered_contents:
            logger.info("No valid content to send (missing zh_summary, ru_summary, or url)")
            return False
        
        # Build combined message
        message = ""
        
        for i, content in enumerate(filtered_contents, 1):
            # Get content fields
            zh_summary = content.get("zh_summary", "")
            ru_summary = content.get("ru_summary", "")
            url = content.get("url", "")
            date_timestamp = content.get("date", 0)
            
            # Convert timestamp to readable time
            if date_timestamp:
                try:
                    publish_time = datetime.datetime.fromtimestamp(date_timestamp).strftime("%Y-%m-%d %H:%M")
                except Exception as e:
                    logger.error(f"Failed to convert timestamp {date_timestamp}: {e}")
                    publish_time = ""
            else:
                publish_time = ""
            
            # Format with publish time outside link
            message += f"🔗 <a href='{url}'><strong>{zh_summary}</strong></a>\n"
            message += f"<code>{ru_summary}（{publish_time}）</code>"
            
            # Consistent spacing at the end
            message += "\n"
        
        # Remove trailing newlines
        message = message.rstrip("\n")
        
        return self.send_message(message, chat_id=chat_id)

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

