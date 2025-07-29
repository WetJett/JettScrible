# -*- coding: utf-8 -*-
import os
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

from aiogram.types import FSInputFile 
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from storage import get_user_language, set_user_language, load_user_data, save_user_data, LANGUAGE_MAP

# Завантажуємо змінні середовища з файлу .env
load_dotenv()

# Отримуємо токен бота зі змінних середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
REPORT_CHANNEL_ID = os.getenv("REPORT_CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found. Make sure that .env file has been added.")
if not REPORT_CHANNEL_ID: 
    raise ValueError("REPORT_CHANNEL_ID not found. Pls check .env file.")
if not OPENAI_API_KEY: 
    raise ValueError("OPENAI_API_KEY not found. Pls check .env file.")

bot = Bot(token=BOT_TOKEN)
# check Telegram updates
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)


TELEGRAM_MESSAGE_MAX_LENGTH = 4096
FILE_SEND_THRESHOLD = 2000 #Symbols to sent

class UserState(StatesGroup):
    choosing_language = State() 
    writing_report = State()
    


def get_welcome_message(lang_code: str) -> str:
    """
    function for receiving greeting text 
    """
    if lang_code == "ua":
        return "Чудово! Встановлена українська мова. \n\n" \
                        " Тепер ви можете надіслати мені голосове повідомлення, і я перетворю його в текст. " \
                        "Також я можу зробити коротку вижимку, якщо ви попросите."
    elif lang_code == "en":
        return  "Great! Language set to English. \n\n" \
                        "Now you can send me a voice message, and I will convert it to text. " \
                        "I can also provide a brief summary if you ask."
    elif lang_code == "pl":
        return u"Świetnie! Ustawiłeś język polski. \n\n" \
                        u"Teraz możesz wysłać mi wiadomość głosową, a ja zamienię ją na tekst. " \
                        u"Mogę również podać krótkie podsumowanie, jeśli poprosisz"
    elif lang_code == "ru":
        return "Отлично! Установлен русский язык. \n\n" \
                         "Теперь вы можете отправить мне голосовое сообщение, и я преобразую его в текст. " \
                         "Я также могу предоставить краткое изложение, если вы попросите."    
    else:
        return "Oops.. Error: Unknown language."



@dp.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext):
    """
    Processes the /start command.
    Prompts the user to select a language.
    """
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано команду /start від користувача {message.from_user.full_name} ({message.from_user.id})")
    
    await state.clear()
    
    if message.from_user.username == "WetJett" or message.from_user.username == "From_Grove_Street":
        await message.answer("Здарова Атєц!")
    if message.from_user.username == "CATAHA_23":
        await message.answer("Жэка, дароу!! :)")
        
    user_id = message.from_user.id
    current_user_lang = get_user_language(user_id)
    
    if current_user_lang:
       response_text = get_welcome_message(current_user_lang)
       await message.answer(response_text)
       
        
    else:
        
     #Buttons
      keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
         [types.InlineKeyboardButton(text="Українська", callback_data="lang_ua")],
         [types.InlineKeyboardButton(text="English", callback_data="lang_en")],
         [types.InlineKeyboardButton(text=u"Polski", callback_data="lang_pl")],
         [types.InlineKeyboardButton(text="Русский", callback_data="lang_ru")]
      ])

      await message.answer(
          "Your language:",
          reply_markup=keyboard
       )
      # change user state
      await state.set_state(UserState.choosing_language)
    

@dp.message(Command("language")) #Command to process the /language command
async def handle_language(message: types.Message, state: FSMContext):
    
    
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано команду /lannguage від користувача {message.from_user.full_name} ({message.from_user.id})")

    await state.clear()
    
    #Buttons
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Українська", callback_data="lang_ua")],
        [types.InlineKeyboardButton(text="English", callback_data="lang_en")],
        [types.InlineKeyboardButton(text=u"Polski", callback_data="lang_pl")],
        [types.InlineKeyboardButton(text="Русский", callback_data="lang_ru")]
    ])

    await message.answer(
        "Please, choose language:",
        reply_markup=keyboard
    )
    
    await state.set_state(UserState.choosing_language)

    """
@dp.message(Command("restart"))
async def handle_restart(message: types.Message, state: FSMContext):
    
   
    
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано команду /restart від користувача {message.from_user.full_name} ({message.from_user.id})")

   
    await state.clear()

   
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Українська", callback_data="lang_ua")],
        [types.InlineKeyboardButton(text="English", callback_data="lang_en")],
        [types.InlineKeyboardButton(text=u"Polski", callback_data="lang_pl")],
        [types.InlineKeyboardButton(text="Русский", callback_data="lang_ru")]
    ])

    await message.answer(
        "Dialogue restarted! Please, choose your language:",
        reply_markup=keyboard
    )
  
    await state.set_state(UserState.choosing_language)

    """
@dp.message(UserState.writing_report, Command("cancel"))
async def cancel_report(message: types.Message, state: FSMContext):
    """
    Cancels the report writing process. Or/and clean all user states
    """
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Користувач {message.from_user.full_name} ({message.from_user.id}) скасував репорт.")
    await state.clear() 
    await message.answer("The report writing has been canceled. You can continue using the bot.",
                         reply_markup=types.ReplyKeyboardRemove()) # hiding the keyboard (optional)
    
@dp.message(Command("cancel"))
async def handle_cancel_command(message: types.Message, state: FSMContext):
    """
    Processes the /cancel command.
    Cleans users state
    """
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано команду /cancel від користувача {message.from_user.full_name} ({message.from_user.id})")

    current_state = await state.get_state()
    if current_state is None:
        await message.answer("There are no operations to cancel.",
                             reply_markup=types.ReplyKeyboardRemove())
        return

    await state.clear() 
    await message.answer("Operation canceled.",
                         reply_markup=types.ReplyKeyboardRemove())
    

@dp.message(Command("report"))
async def handle_report_command(message: types.Message, state: FSMContext):
    """
    Обробляє команду /report.
    Просить користувача ввести текст скарги.
    """
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано команду /report від користувача {message.from_user.full_name} ({message.from_user.id})")

    # saving ID and name of user
    await state.update_data(reporter_id=message.from_user.id, reporter_name=message.from_user.full_name)
    
    
    await message.answer(
        "Please describe your problem or bag. If you change your mind, send /cancel.",
        reply_markup=types.ReplyKeyboardRemove() 
    )
    # Up 'writing_report' statre
    await state.set_state(UserState.writing_report)
    
@dp.message(UserState.writing_report, F.text) # check state and type of message
async def process_report_text(message: types.Message, state: FSMContext):
    """
    Receives the complaint text from the user and sends it to the reports tg channel.
    """
    report_text = message.text
    user_data = await state.get_data()
    reporter_id = user_data.get("reporter_id")
    reporter_name = user_data.get("reporter_name")

    report_message = (
        f"**Від користувача:** [{reporter_name}](tg://user?id={reporter_id}) \(ID: `{reporter_id}`\)\n"
        f"**Час:** `{message.date.strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
        f"**Повідомлення:**\n"
        f"```\n{report_text}\n```"
    )

    try:
        # sends report to channal
        await bot.send_message(
            chat_id=REPORT_CHANNEL_ID,
            text=report_message,
            parse_mode="MarkdownV2"
        )
        await message.answer("Your report has been accepted! Thank you for helping us improve the bot.")
        print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Репорт від користувача {reporter_name} ({reporter_id}) успішно відправлено.")
    except Exception as e:
        await message.answer("Sorry, your report could not be sent. Please try again later or contact the administrator.")
        print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Помилка при відправці репорту від {reporter_name} ({reporter_id}): {e}")

    await state.clear()

@dp.message(Command("help")) # Process /info
async def handle_info(message: types.Message):
    """
    Processes the /info command.
    shows the user information about the bot and manuals
    """
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано команду /info від користувача {message.from_user.full_name} ({message.from_user.id})")
    
    user_id = message.from_user.id
    chosen_language = get_user_language(user_id)
    
    if chosen_language == "ua":
        info_text = (
            u"🤖 *Привіт\! Я ваш голосовий помічник\!* \n\n" 
            "Я перетворюю ваші голосові повідомлення на текст, а також можу "
            "зробити коротку вижимку з них, щоб ви швидко зрозуміли головну суть\.\n\n"
            "**Як я працюю:**\n"
            "1\. Просто надішліть мені голосове повідомлення\.\n"
            "2\. Я автоматично розпізнаю його і надішлю вам текст\.\n"
            "3\. Якщо ви хочете вижимку, виберіть summarize після транскрипції\.\n\n"
            "**Корисні команди:**\n"
            "/start \- Почати діалог або перезапустити\n"
            "/help \- Детальна довідка\n"
            "/language \- Вибір мови\n"
            "/report \- Повідомити про проблему\n"
            "Сподіваюся, я буду вам корисною\!"
        )
    elif chosen_language == "en" or chosen_language == None: 
        info_text = (
            "🤖*Hi\! I'm your voice assistant\!* \n\n" 
            "I convert your voice messages into text, and I can also "
            "provide a short summary of them to help you quickly grasp the main idea\.\n\n"
            "**How to use:**\n"
            "1\. Just send me a voice message\.\n"
            "2\. I'll automatically transcribe it and send you the text\.\n"
            "3\. If you want a summary, click SUMMARIZE after transcription\.\n\n"
            "**Useful Commands:**\n"
            "/start \- Start a dialogue\n"
            "/help \- Detailed help\n"
            "/language \- change bot's language\n"
            "/report \- Report a problem\n"
            "Hope I'll be useful to you\!"
        )
    elif chosen_language == "ru":
        info_text = ("🤖*Привет\! Я ваш голосовой помощник\!* \n\n" 
                     "Я преобразую ваши голосовые сообщения в текст, а также могу "
                     "предоставить их краткое изложение, чтобы помочь вам быстро уловить основную идею\.\n\n"
                     "**Как использовать:**\n"
                     "1\. Просто отправьте мне голосовое сообщение\.\n"
                     "2\. Я автоматически расшифрую его и отправлю вам текст\.\n"
                     "3\. Если вам нужно изложение, нажмите summarize после транскрипции\.\n\n"
                     "**Полезные команды:**\n"
                     "/start \- Начать диалог или перезапустить\n"
                     "/help \- Подробная справка\n"
                     "/language \- Выбрать другой язык\n"
                     "/report \- Сообщить о проблеме\n"
                     "Надеюсь, я буду вам полезна\!")
    elif chosen_language == "pl":
        info_text = ("🤖*Cześć\! Jestem twoim asystentem głosowym\!* \n\n" 
                     "Konwertuję twoje wiadomości głosowe na tekst, a także mogę "
                     "podać ich krótkie podsumowanie, aby pomóc ci szybko zrozumieć główną myśl\.\n\n"
                     "**Jak działam:**\n"
                     "1\. Po prostu wyślij mi wiadomość głosową\.\n"
                     "2\. Automatycznie ją przepiszę i wyślę ci tekst\.\n"
                     "3\. Jeśli chcesz podsumowanie, użyj SUMMARIZE po transkrypcji\.\n\n"
                     "**Useful Commands:**\n"
                     "/start \- Rozpocznij dialog\n"
                     "/help \- Szczegółowa pomoc\n"
                     "/lnaguage \- Ustawienia języka\n"
                     "/report \- Zgłoś problem\n"
                     "Mam nadzieję, że będę dla ciebie przydatna\!")
        
    await message.answer(info_text, parse_mode="MarkdownV2")

 
  
@dp.message(Command("policy")) # process /policy
async def handle_info(message: types.Message):
    """
    Processes the /policy command.
    shows the user the privacy policy of this bot
    """
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано команду /policy від користувача {message.from_user.full_name} ({message.from_user.id})")

    await message.answer("Are you scared about your personal data? Just don't share it!")

@dp.callback_query(UserState.choosing_language, F.data.startswith("lang_"))
async def handle_language_choice(callback: types.CallbackQuery, state: FSMContext):
    """
    Handles the user's language selection.
    """
    lang_code = callback.data.split('_')[1] # Taking lang code
    user_id = callback.from_user.id
    
    set_user_language(user_id, lang_code)
    response_text = get_welcome_message(lang_code)
  
    response_text = get_welcome_message(lang_code)

    
    await callback.message.edit_text(response_text) # Edits existing message with buttons
    # OR await callback.answer("Мова вибрана!") # a pop-up notification
    # OR await callback.message.answer(response_text) # a new message.
   
    await state.clear()

    print(f"[{callback.message.date.strftime('%Y-%m-%d %H:%M:%S')}] Користувач {callback.from_user.full_name} ({callback.from_user.id}) вибрав мову: {lang_code}")
    
@dp.callback_query(F.data == "summarize_text")
async def handle_summarize_callback(callback: types.CallbackQuery, state: FSMContext):
    """
    Handles summarize callback.
    """
    print(f"[{callback.message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано запит на підсумовування від {callback.from_user.full_name} ({callback.from_user.id}).")

    
    user_data = await state.get_data()
    text_to_summarize = user_data.get("last_transcribed_text")
    user_id = callback.from_user.id
    chosen_language = get_user_language(user_id)
    openai_lang_code = LANGUAGE_MAP.get(chosen_language, "en") # Takes user's lang for prompt to GPT

    if not text_to_summarize:
        if openai_lang_code == "uk":
            await callback.answer("Не можу зараз підсумувати. Спробуйте надіслати голосове повідомлення ще раз.", show_alert=True)
        elif openai_lang_code == "pl":
            await callback.answer(u"Nie mogę tego teraz podsumować. Spróbuj wysłać wiadomość głosową ponownie.", show_alert=True)
        elif openai_lang_code == "ru":
            await callback.answer("Не могу сейчас это обобщить. Попробуйте отправить голосовое сообщение еще раз", show_alert=True)
        else: # Default in English
            await callback.answer("Can't summarize it now. Try sending a voice message again.", show_alert=True)
        
        return

    
    summarizing_message = await callback.message.answer("Summarizing... ⏳")
    await callback.answer() #Disable the button loading indicator

    try:
        # Prompt in dif langs (acording user's lang)
        prompt_text = ""
        if openai_lang_code == "uk":
            prompt_text = "Скороти наступний текст до головної думки. Якщо потрібно, використай додаткові тезиси, щоб передати основний зміст повідомлення. Відповідь має бути українською мовою."
        elif openai_lang_code == "pl":
            prompt_text = "Skróć poniższy tekst do głównej myśli. W razie potrzeby użyj dodatkowych tez, aby przekazać główną treść wiadomości. Odpowiedź powinna być w języku polskim."
        elif openai_lang_code == "ru":
            prompt_text = "Сократи следующий текст до главной мысли. Если нужно, используй дополнительные тезисы, чтобы передать основное содержание сообщения. Ответ должен быть на русском языке."
        else: # Default to English
            prompt_text = "Summarize the following text to its main idea. If necessary, use additional bullet points to convey the core content of the message. The answer should be in English."

        messages = [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": text_to_summarize}
        ]

        # API request, using GPT-3.5-turbo
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-3.5-turbo", 
            messages=messages,
            max_tokens=500, # summary length limit
            temperature=0.4 # Parameter for controlling creativity (0.0 - less creative, 1.0 - more creative)
        )

        summary_text = chat_completion.choices[0].message.content.strip()
        print(f"[{callback.message.date.strftime('%Y-%m-%d %H:%M:%S')}] Підсумований текст: {summary_text}")

        
        await bot.edit_message_text(
            chat_id=summarizing_message.chat.id,
            message_id=summarizing_message.message_id,
            text=f"📊 **Summary:**\n```\n{summary_text}\n```",
            parse_mode="MarkdownV2"
        )
        
        await callback.message.edit_reply_markup(reply_markup=None)

    except Exception as e:
        print(f"Помилка при підсумовуванні тексту: {e}")
        await bot.edit_message_text(
            chat_id=summarizing_message.chat.id,
            message_id=summarizing_message.message_id,
            text="❌ An error occurred during summarization. Please try again."
        )
    
@dp.message(F.voice | F.video_note) 
async def handle_voice_message(message: types.Message, state: FSMContext):
    """
    Processes incoming voice messages or video clips.
    Uploads a file, recognizes text via OpenAI Whisper, and sends it to the user.
    """
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано голосове/відео повідомлення від {message.from_user.full_name} ({message.from_user.id}).")

    # Lang set check
    user_id = message.from_user.id
    chosen_language = get_user_language(user_id)
    

    if chosen_language is None:
        # If lang = none, show lang choose keys
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_ua")],
            [types.InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
            [types.InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang_pl")],
            [types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
        ])
        await message.answer(
            "Будь ласка, спочатку виберіть мову для взаємодії з ботом. Це допоможе мені краще розпізнавати ваш голос. / Please, choose your language first. This will help me recognize your voice better.",
            reply_markup=keyboard
        )
        
        return

    # Taking lang code for OpenAI
    openai_lang_code = LANGUAGE_MAP.get(chosen_language, "en")# we have "en" as default


    temp_file_path = f"E:/!dump/JettScrible_dump/{message.from_user.id}_{message.date.timestamp()}"
    
    #determine what exactly received: a voice or video note
    file_info_to_download = None
    if message.voice:
        file_info_to_download = message.voice
        temp_file_path += ".ogg"
        print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Розпізнається голосове повідомлення (ID: {file_info_to_download.file_id})")
    elif message.video_note:
        file_info_to_download = message.video_note
        temp_file_path += ".mp4" # Відеокружечки часто в MP4
        print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Розпізнається відеокружечок (ID: {file_info_to_download.file_id})")
        await message.answer("Processing video notes might take a bit longer as I need to extract audio. Please wait...")

    if not file_info_to_download:
        await message.answer("Failed to get file info.")
        return

    processing_message = await message.answer("Working on it... ⏳") 

    try:
         
       # os.makedirs("downloads", exist_ok=True)

        
        file_obj = await bot.get_file(file_info_to_download.file_id)
        await bot.download_file(file_obj.file_path, temp_file_path)
        print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Файл завантажено до: {temp_file_path}")

        with open(temp_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=openai_lang_code 
            )
        recognized_text = transcription.text
        print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Розпізнаний текст: {recognized_text}")
        await state.update_data(last_transcribed_text=recognized_text)
        
        keyboard_options = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="📝 Summarize", callback_data="summarize_text"),
            ]
        ])

        if not recognized_text:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text="Could not recognize speech. Please try again.")
        elif len(recognized_text) <= TELEGRAM_MESSAGE_MAX_LENGTH:
            # If the text fits into one message
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_message.message_id,
                text=f"✅ Text:\n```\n{recognized_text}\n```",
                parse_mode="MarkdownV2",
                reply_markup=keyboard_options # button
            )
        else:
            short_text_preview = recognized_text[:FILE_SEND_THRESHOLD] + "..." if len(recognized_text) > FILE_SEND_THRESHOLD else recognized_text
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_message.message_id,
                text=f"✅ Text \(first {FILE_SEND_THRESHOLD} symbols\):\n```\n{short_text_preview}\n```",
                parse_mode="MarkdownV2",
                reply_markup=keyboard_options # button
            )
            
            transcript_filename = f"transcription_{message.from_user.id}_{message.date.timestamp()}.txt"
            transcript_file_path = os.path.join("E:/!dump/JettScrible_dump/", transcript_filename)
            with open(transcript_file_path, "w", encoding="utf-8") as f:
                f.write(recognized_text)

            await message.answer_document(
                document=FSInputFile(transcript_file_path),
                caption="Full transcription text in file."
            )
            print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Повний текст збережено у файл та відправлено: {transcript_file_path}")

    except Exception as e:
        print(f"Помилка при обробці голосового повідомлення: {e}")
        await bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text="❌ An error occurred during processing. Please try again.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Тимчасовий файл (аудіо) видалено: {temp_file_path}")
        
        if 'transcript_file_path' in locals() and os.path.exists(transcript_file_path):# locals() - checks if variable exists to avoid an error
            os.remove(transcript_file_path)
            print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Тимчасовий файл (текст) видалено: {transcript_file_path}")
            
@dp.message() 
async def handle_any_message(message: types.Message):
    """
    Handles messages different from voice and video notes
    """
    user_id = message.from_user.id
    chosen_language = get_user_language(user_id)
    print(f"[{message.date.strftime('%Y-%m-%d %H:%M:%S')}] Отримано непідтримуване повідомлення типу '{message.content_type}' від {message.from_user.full_name} ({message.from_user.id}).")
    
    if chosen_language == "ua":
       await message.answer("Я розумію лише голосові повідомлення або відеозаписи. Будь ласка, надішліть голосове повідомлення.")
    elif chosen_language == "pl":
       await message.answer(u"Rozumiem tylko wiadomości głosowe lub video notes. Proszę wysłać wiadomość głosową.")
    elif chosen_language == "ru":
       await message.answer("Я понимаю только голосовые сообщения или видеозаметки. Пожалуйста, отправьте голосовое сообщение.")
    else:
        await message.answer("I only understand voice messages or video notes. Please send a voice message.")
        
async def main():
    print("Running bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot has been stoped manually .")
    except Exception as e:
        print(f"Error: {e}")
        
        
        