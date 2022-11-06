import configparser, time, random
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import BoundFilter
import db
from string import ascii_letters, digits
import logging 

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["tgbot"]["token"]
class IsPrivate(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE
class Info(StatesGroup):
    upload_file = State()
    upload_file_password = State()
    delete_file = State()
    check_password = State()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(IsPrivate(), commands=['start'], state='*')
async def start_command(message: types.Message, state: FSMContext):
    args = message.get_args()
    aaa = message.get_args()
    bot_data = await bot.get_me()
    bot_name = bot_data['username']
    # type_file, fileID, views = db.get_file(args)
    type_file, fileID, views, password = db.get_file(args)
    if len(aaa) >= 30: 

        if type_file is None and fileID is None:
            await bot.send_message(chat_id=message.chat.id, text='<b>Я не нашел данный файл:(</b>', parse_mode="HTML")
        else:
            db.update_views(args)
            await bot.send_photo(chat_id=message.chat.id, photo=fileID[0])

@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def upload_file(message: types.Message, state: FSMContext):
    bot_data = await bot.get_me()
    bot_name = bot_data['username']
    if message.photo:
        fileID = message.photo[-1].file_id
        await message.delete()
        code = ''.join(random.sample(ascii_letters + digits, random.randint(33, 40)))
        db.add_new_file(message.from_user.id, 'photo', code, fileID)
        await bot.send_message(chat_id=message.chat.id, text=f'✓ Изображение загружено: \n https://t.me/{bot_name}?start={code}')

if __name__ == "__main__":
    db.check_db()
    executor.start_polling(dp, skip_updates=True)
