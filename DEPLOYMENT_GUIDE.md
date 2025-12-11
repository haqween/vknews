# VK到Telegram新闻摘要与翻译机器人部署指南

本指南将帮助您在服务器上部署VK到Telegram的新闻摘要与翻译机器人。

## 1. 环境准备

### 1.1 Python环境
确保服务器上安装了Python 3.7或更高版本：

```bash
python3 --version
```

### 1.2 安装依赖
克隆项目代码后，安装所需依赖：

```bash
cd /path/to/vknews
pip3 install -r requirements.txt
```

## 2. 配置文件设置

### 2.1 复制配置文件模板
```bash
cp src/config/config.yaml.example src/config/config.yaml
```

### 2.2 编辑配置文件
使用文本编辑器打开`src/config/config.yaml`文件，根据您的需求配置以下部分：

#### VK配置
```yaml
vk:
  access_token: "your_vk_access_token"  # VK API访问令牌
  api_version: "5.131"  # API版本
  communities:
    - name: "news"  # 内部名称
      display_name: "新闻社群"  # 显示名称
      source:
        type: "wall"
        id: "-123456789"  # 社群ID（公共页面以负号开头）
```

#### Telegram配置
```yaml
telegram:
  bot_token: "your_telegram_bot_token"  # Telegram机器人令牌
  webhook_url: "https://your-domain.com"  # Webhook URL（必须是HTTPS）
  webhook_port: 8443  # Webhook服务器监听端口
```

#### AI配置
```yaml
ai:
  providers:
    - name: "siliconflow"  # AI提供商名称
      api_key: "your_siliconflow_api_key"  # AI服务API密钥
      model: "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"  # AI模型名称
    - name: "openrouter"  # 第二个AI提供商（可选）
      api_key: "your_openrouter_api_key"
      model: "openrouter/deepseek/deepseek-chat"
  summary:
    max_length: 30  # 摘要最大长度
    language: "zh"  # 摘要语言
  translation:
    target_language: "zh"  # 翻译目标语言
```

支持的提供商包括：deepseek、openai、gemini、dashscope、openrouter、siliconflow等。您可以配置多个提供商，系统会从有效配置中随机选择一个使用。

#### 系统配置
```yaml
system:
  fetch_interval: 60  # 内容获取间隔（分钟）
  max_content_per_fetch: 20  # 每次获取的最大内容数
```

## 3. 启动服务

### 3.1 直接启动

```bash
cd /path/to/vknews
PYTHONPATH=. python3 src/main.py
```

### 3.2 后台运行

使用nohup命令在后台运行服务：

```bash
cd /path/to/vknews
nohup PYTHONPATH=. python3 src/main.py > bot.log 2>&1 &
```

### 3.3 查看日志

```bash
tail -f bot.log
```

## 4. 系统服务配置（可选）

为了使服务能够在系统启动时自动运行，并便于管理，建议将其配置为系统服务。

### 4.1 创建systemd服务文件

```bash
sudo nano /etc/systemd/system/vktelegrambot.service
```

### 4.2 编辑服务文件

```ini
[Unit]
Description=VK to Telegram News Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/vknews
ExecStart=/usr/bin/python3 -m src.main
Environment=PYTHONPATH=/path/to/vknews
Restart=on-failure
User=your_username

[Install]
WantedBy=multi-user.target
```

### 4.3 启用并启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable vktelegrambot
sudo systemctl start vktelegrambot
```

### 4.4 管理服务

```bash
# 查看服务状态
sudo systemctl status vktelegrambot

# 停止服务
sudo systemctl stop vktelegrambot

# 查看日志
sudo journalctl -u vktelegrambot -f
```

## 5. 常见问题与解决方案

### 5.1 权限问题
确保配置文件和日志文件具有正确的读写权限。

### 5.2 API访问限制
- VK API：如果遇到访问限制，检查您的API令牌权限
- Telegram Bot API：如果机器人不响应，检查令牌和聊天ID是否正确
- AI API：如果遇到API错误，检查API密钥和模型配置

### 5.3 服务无法启动
- 检查配置文件格式是否正确（YAML格式）
- 检查依赖是否完全安装
- 查看日志文件获取详细错误信息

## 6. 更新服务

1. 停止服务
2. 拉取最新代码
3. 更新依赖（如果需要）
4. 重启服务

```bash
sudo systemctl stop vktelegrambot
git pull
pip3 install -r requirements.txt
sudo systemctl start vktelegrambot
```

## 7. 监控与维护

- 定期检查日志文件
- 监控API使用情况，避免超出限制
- 根据需求调整配置参数

---

部署完成后，机器人将按照配置的时间间隔自动从VK获取内容，经过AI处理后发送到您的Telegram聊天中。您也可以通过Telegram机器人的命令菜单手动触发内容获取。