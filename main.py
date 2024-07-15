import asyncio
from aiogram import Bot, Dispatcher, types
from discord.ext import commands
import discord
from aiogram.methods.get_user_profile_photos import UserProfilePhotos
from discord import Webhook
import aiohttp
from aiogram.methods import DeleteWebhook
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


telegram_token = "TOKEN"
telegram_bot = Bot(token=telegram_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
telegram_dp = Dispatcher()

discord_token = "TOKEN"
discord_client = commands.Bot(intents=discord.Intents.all(), command_prefix="/")

@discord_client.event
async def on_ready():
    print(f"Logged in as {discord_client.user.name}")

@discord_client.event
async def on_message(message):
    if message.author.bot: return
    formatted_message = f"*{message.author.name}*: {message.clean_content}"
    if message.reference:
        ref_message = await message.channel.fetch_message(message.reference.message_id)
        ref_author = ref_message.author.name
        ref_content = ref_message.clean_content
        formatted_message = f"*{message.author.name}*: {message.clean_content}\n> *{ref_author}*: {ref_content}"
    await telegram_bot.send_message(chat_id=-1002132860111, text=formatted_message)



@telegram_dp.message()
async def telegram_message(message: types.Message):
    if message.from_user.is_bot:
        return

    async with aiohttp.ClientSession() as session:
        webhook: Webhook = Webhook.from_url("WEBHOOK", session=session)
        result: UserProfilePhotos = await telegram_bot.get_user_profile_photos(message.from_user.id, limit=1)

        current_photo = result.photos[0][0] if result.photos else None
        file = await telegram_bot.get_file(current_photo.file_id) if current_photo else None
        avatar_url = f"https://api.telegram.org/file/bot{telegram_token}/{file.file_path}" if file else None

        async def send_file(file_id, filename):
            file = await telegram_bot.get_file(file_id)
            file_path = file.file_path
            file_obj = await telegram_bot.download_file(file_path)
            file_obj.seek(0)  
            discord_file = discord.File(fp=file_obj, filename=filename)
            await webhook.send( 
                            file=discord_file, 
                            username=message.from_user.username, 
                            avatar_url=avatar_url)

        if message.text:
            message_text = message.text
            if len(message_text) > 2000:
                parts = [message_text[i:i+2000] for i in range(0, len(message_text), 2000)]
                for part in parts:
                    await webhook.send(part, username=message.from_user.username, avatar_url=avatar_url)
            else:
                await webhook.send(message_text, username=message.from_user.username, avatar_url=avatar_url)

        elif message.document:
            await send_file(message.document.file_id, message.document.file_name)

        elif message.photo:
            photo = message.photo[-1]  
            await send_file(photo.file_id, f"photo_{photo.file_id}.jpg")

        elif message.sticker:
            if message.sticker.is_animated:
                await send_file(message.sticker.file_id, f"sticker_{message.sticker.file_id}.mp4")
            else:
                await send_file(message.sticker.file_id, f"sticker_{message.sticker.file_id}.mp4")

        elif message.voice:
            await send_file(message.voice.file_id, f"voice_{message.voice.file_id}.ogg")

        elif message.video:
            await send_file(message.video.file_id, f"video_{message.video.file_id}.mp4")

        elif message.animation:
            await send_file(message.animation.file_id, f"animation_{message.animation.file_id}.mp4")
        
        elif message.video_note:
            await send_file(message.video_note.file_id, f"videomsg_{message.video_note.file_id}.mp4")
            

        else:
            await webhook.send(f"{message.from_user.username} отправил неподдерживаемый файл.", 
                               username=message.from_user.username, 
                               avatar_url=avatar_url)



async def start_discord():
    await telegram_bot(DeleteWebhook(drop_pending_updates=True))
    await telegram_dp.start_polling(telegram_bot)

async def start_telegram():
    await discord_client.start(discord_token)

async def main():
    discord_task = asyncio.create_task(start_discord())
    telegram_task = asyncio.create_task(start_telegram())

    await asyncio.gather(discord_task, telegram_task)

if __name__ == "__main__":
    asyncio.run(main())