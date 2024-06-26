import logging
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from io import BytesIO
import threading
import os

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a photo and I will watermark it for you.')

# Define the function to watermark the image
def watermark_image(main_image_url: str, mark_image_url: str = "https://i.ibb.co/n6tHyjw/20240627-001522.png", mark_ratio: float = 0.7, position: str = "center") -> BytesIO:
    url = f"https://quickchart.io/watermark?mainImageUrl={main_image_url}&markImageUrl={mark_image_url}&markRatio={mark_ratio}&position={position}"
    response = requests.get(url)
    watermarked_image = BytesIO(response.content)
    return watermarked_image

# Define the function to handle photo messages
def handle_photo(update: Update, context: CallbackContext) -> None:
    photo = update.message.photo[-1]
    file_id = photo.file_id
    caption = update.message.caption

    new_thread = threading.Thread(target=process_photo, args=(update, context, file_id, caption))
    new_thread.start()

def process_photo(update: Update, context: CallbackContext, file_id: str, caption: str) -> None:
    file = context.bot.getFile(file_id)
    main_image_url = file.file_path

    watermarked_image = watermark_image(main_image_url)
    watermarked_image.seek(0)

    update.message.reply_photo(photo=InputFile(watermarked_image), caption=caption)

def main() -> None:
    # Initialize the bot and dispatcher
    updater = Updater(os.getenv("TELEGRAM_BOT_TOKEN"))
    dispatcher = updater.dispatcher

    # Register the handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()