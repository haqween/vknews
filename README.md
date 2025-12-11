# VK到Telegram信息摘要翻译机器人

一个自动化工具，用于从VK获取内容、生成摘要并翻译为指定语言，然后发送到Telegram频道或聊天中。

## 功能特性

- **VK内容获取**：支持从指定的VK公共主页和用户页面获取内容
- **内容搜索**：支持按关键词搜索VK内容
- **AI摘要生成**：使用AI模型生成内容摘要，支持自定义摘要长度
- **多语言翻译**：支持将内容翻译为多种语言（默认英语）
- **定时获取**：可配置自动获取内容的时间间隔
- **手动触发**：支持通过Telegram命令手动触发内容获取
- **内容去重**：自动过滤已处理过的内容
- **错误处理**：完善的错误处理和日志记录

## 支持的命令

- `/start` - 启动机器人并显示帮助信息

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd vknews
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置文件

复制配置文件模板并根据需要修改：

```bash
cp src/config/config.yaml.example src/config/config.yaml
```

## 配置说明

配置文件位于 `src/config/config.yaml`，包含以下部分：

### VK配置

```yaml
vk:
  access_token: "your_vk_access_token"
  api_version: "5.131"
  sources:
    - type: "public"
      id: "public123456"
      max_count: 10
    - type: "user"
      id: "7654321"
      max_count: 5
  keywords: ["关键词1", "关键词2"]
```

- `access_token`: VK API访问令牌
- `api_version`: VK API版本（默认5.131）
- `sources`: 内容来源列表
  - `type`: 来源类型（public 或 user）
  - `id`: 公共主页或用户ID
  - `max_count`: 每次获取的最大内容数
- `keywords`: 用于搜索内容的关键词列表

### Telegram配置

```yaml
telegram:
  bot_token: "your_telegram_bot_token"
  webhook_url: "https://your-domain.com"
  webhook_port: 8443
```

- `bot_token`: Telegram机器人令牌
- `webhook_url`: Webhook URL（必须是HTTPS）
- `webhook_port`: Webhook服务器监听端口

### AI配置

```yaml
ai:
  provider: "openai"
  api_key: "your_openai_api_key"
  model: "gpt-3.5-turbo"
  summary_length: "medium"
  target_language: "English"
```

- `provider`: AI提供商（目前仅支持openai）
- `api_key`: OpenAI API密钥
- `model`: AI模型名称
- `summary_length`: 摘要长度（short, medium, long）
- `target_language`: 翻译目标语言

### 系统配置

```yaml
system:
  fetch_interval: 60
  max_content_per_fetch: 20
  cache_enabled: true
  cache_size: 1000
  log_level: "INFO"
```

- `fetch_interval`: 自动获取内容的时间间隔（分钟）
- `max_content_per_fetch`: 每次获取的最大内容数
- `cache_enabled`: 是否启用内容缓存
- `cache_size`: 缓存大小（最多存储多少个已处理的内容ID）
- `log_level`: 日志级别

## 获取必要的API密钥

### VK Access Token

1. 访问 [VK开发者平台](https://vk.com/dev)
2. 创建一个应用程序（类型选择"Standalone"
3. 获取应用程序ID
4. 使用以下URL获取访问令牌：
   ```
   https://oauth.vk.com/authorize?client_id=YOUR_APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,friends,groups,offline&response_type=token&v=5.131
   ```
   - 确保包含 `offline` 权限以获得长期有效的令牌

### OpenAI API Key

1. 访问 [OpenAI平台](https://platform.openai.com/)
2. 登录并创建API密钥

### Telegram Bot Token

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按照提示创建机器人并获取令牌
4. 获取聊天ID：
   - 向机器人发送一条消息
   - 访问 `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
   - 在响应中找到 `chat.id`

## 使用方法

### 启动机器人

```bash
python src/main.py
```

## 目录结构

```
vknews/
├── src/
│   ├── __init__.py
│   ├── vk_api.py          # VK API交互模块
│   ├── ai_processor.py    # AI摘要生成和翻译模块
│   ├── telegram_bot.py    # Telegram机器人模块
│   ├── main.py            # 主程序和调度逻辑
│   └── config/
│       ├── config.yaml       # 配置文件
│       └── config.yaml.example # 配置文件模板
├── requirements.txt       # 依赖列表
├── README.md              # 项目说明
└── bot.log                # 日志文件
```

## 注意事项

1. 确保所有API密钥的安全性，不要将配置文件提交到版本控制系统
2. VK Access Token需要包含 `offline` 权限以获得长期有效令牌
3. 首次运行时，机器人会自动创建日志文件 `bot.log`
4. 如遇到问题，请检查日志文件获取详细信息
5. 确保网络连接正常，特别是可以访问VK和OpenAI API

## 故障排除

### 常见问题

1. **无法获取VK内容**
   - 检查VK Access Token是否有效
   - 确保来源ID正确
   - 检查网络连接

2. **AI处理失败**
   - 检查OpenAI API Key是否有效
   - 确保有足够的API调用额度
   - 检查网络连接

3. **Telegram消息发送失败**
   - 检查Bot Token是否有效
   - 确保Chat ID正确
   - 确保机器人已添加到频道（如果使用频道）

4. **机器人无响应**
   - 检查程序是否正在运行
   - 检查日志文件中的错误信息
   - 确保网络连接正常

## 日志

日志文件位于 `bot.log`，记录了程序运行状态、错误信息和操作记录。可以通过修改配置文件中的 `log_level` 调整日志级别。

## 版本更新

### v1.0.0
- 初始版本发布
- 支持VK内容获取和搜索
- 支持AI摘要生成和翻译
- 支持Telegram消息发送
- 支持定时和手动获取内容

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue到项目仓库
- 发送邮件到：[your-email@example.com]