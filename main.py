import telebot
import yt_dlp
import os
import re
from flask import Flask, request

# تنظیمات ربات تلگرام
BOT_TOKEN = os.getenv('BOT_TOKEN')  # توکن از متغیر محیطی خوانده می‌شود
bot = telebot.TeleBot(BOT_TOKEN)

# تنظیمات Flask برای Webhook
app = Flask(__name__)

# تنظیمات yt-dlp برای دانلود ویدیو با کیفیت 360p
ydl_opts = {
    'format': 'best[height<=360]',  # انتخاب کیفیت 360p یا نزدیک‌ترین کیفیت
    'outtmpl': 'video.%(ext)s',     # نام فایل خروجی
}

# الگوی regex برای شناسایی لینک‌ها
URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

# هندل کردن پیام‌های متنی حاوی لینک در گروه‌ها
@bot.message_handler(content_types=['text'], chat_types=['group', 'supergroup'])
def handle_video_link(message):
    # بررسی اینکه پیام حاوی لینک است یا خیر
    if URL_PATTERN.match(message.text):
        url = message.text
        try:
            # دانلود ویدیو با yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_file = 'video.mp4'  # نام فایل خروجی

            # ارسال ویدیو به گروه
            with open(video_file, 'rb') as video:
                bot.send_video(message.chat.id, video, timeout=60)

            # حذف فایل موقت
            os.remove(video_file)
            bot.reply_to(message, "ویدیو با موفقیت ارسال شد!")
        except Exception as e:
            bot.reply_to(message, f"خطا در دانلود یا ارسال ویدیو: {str(e)}")
    # پیام‌های بدون لینک نادیده گرفته می‌شوند

# تنظیم Webhook برای دریافت آپدیت‌ها
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return '', 200

# تنظیم Flask برای Webhook
@app.route('/')
def index():
    return 'Hello, this is a Telegram bot!'

if __name__ == '__main__':
    # حذف Webhook قبلی (در صورت وجود)
    bot.remove_webhook()
    # تنظیم Webhook با آدرس Render
    bot.set_webhook(url=f'https://{os.getenv("RENDER_APP_NAME")}.onrender.com/{BOT_TOKEN}')
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8443)))
