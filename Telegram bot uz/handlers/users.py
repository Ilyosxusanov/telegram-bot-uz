from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from database.db import add_user, get_movie_by_code, get_movies_by_title, set_user_lang, get_user_lang, get_top_imdb, get_most_searched, get_movies_by_category, get_all_movies
from keyboards.inline import movie_keyboard, search_results_keyboard, lang_keyboard, main_menu_keyboard, sub_keyboard, category_movies_keyboard
from utils.translations import texts
from utils.states import AIStates
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        texts['uz']['select_lang'] + "\n" + texts['ru']['select_lang'] + "\n" + texts['en']['select_lang'],
        reply_markup=lang_keyboard()
    )

@router.callback_query(F.data.startswith("setlang_"))
async def set_lang_callback(callback: types.CallbackQuery, bot: Bot):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    set_user_lang(user_id, lang)
    
    from config import CHANNEL_LINK
    from utils.check_sub import is_subscribed
    
    if await is_subscribed(bot, user_id):
        await callback.message.edit_text(
            texts[lang]['welcome'],
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        await callback.message.edit_text(
            texts[lang]['welcome'],
            reply_markup=sub_keyboard(CHANNEL_LINK, lang)
        )

@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: types.CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    from utils.check_sub import is_subscribed
    
    if await is_subscribed(bot, user_id):
        await callback.message.edit_text(
            texts[lang]['sub_success'] + "\n\n" + texts[lang]['welcome'],
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        await callback.answer(texts[lang]['sub_required'], show_alert=True)

@router.callback_query(F.data.startswith("cat_"))
async def category_callback(callback: types.CallbackQuery, bot: Bot):
    cat = callback.data.split("_")[1]
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    
    if cat == "code":
        await callback.message.answer(texts[lang]['enter_code'])
    elif cat == "imdb":
        movies = get_top_imdb(10)
        await callback.message.answer(texts[lang]['top_imdb'], reply_markup=search_results_keyboard(movies))
    elif cat == "most":
        movies = get_most_searched(10)
        await callback.message.answer(texts[lang]['most_searched'], reply_markup=search_results_keyboard(movies))

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✍️ Adminga yozish", callback_data="contact_admin"))
    await message.answer(
        "Savol va takliflaringiz bo'lsa, adminga murojaat qilishingiz mumkin:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == "contact_admin")
async def contact_admin_callback(callback: types.CallbackQuery):
    await callback.message.answer("Xabaringizni yozib qoldiring. Men uni adminga yetkazaman! 👇")
    # Bu yerda oddiy xabar kutish rejimini state orqali qilsa ham bo'ladi, 
    # lekin hozircha keyingi xabarni admin'ga yuborish mantiqini soddalashtiramiz.

@router.message(Command("donat"))
async def cmd_donat(message: types.Message):
    await message.answer(
        "Bot rivoji uchun hissa qo'shmoqchi bo'lsangiz:\n\n"
        "💳 Karta: `9860600408859723`",
        parse_mode="Markdown"
    )

@router.message(Command("top"))
async def cmd_top(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    movies = get_top_imdb(10)
    await message.answer(texts[lang]['top_imdb'], reply_markup=search_results_keyboard(movies))

@router.message(Command("move", "movies"))
async def cmd_movies(message: types.Message):
    movies = get_movies_by_category('movies')
    if not movies:
        return await message.answer("Hozircha kinolar mavjud emas.")
    await message.answer("🎬 **Barcha Kinolar:**", reply_markup=category_movies_keyboard(movies), parse_mode="Markdown")

@router.message(Command("seryallar", "seryal"))
async def cmd_series(message: types.Message):
    movies = get_movies_by_category('series')
    if not movies:
        return await message.answer("Hozircha seryallar mavjud emas.")
    await message.answer("📺 **Barcha Seryallar:**", reply_markup=category_movies_keyboard(movies), parse_mode="Markdown")

@router.message(Command("anime"))
async def cmd_anime(message: types.Message):
    movies = get_movies_by_category('anime')
    if not movies:
        return await message.answer("Hozircha animelar mavjud emas.")
    await message.answer("🎎 **Barcha Animelar:**", reply_markup=category_movies_keyboard(movies), parse_mode="Markdown")

@router.message(Command("multifilmlar", "multfilm"))
async def cmd_cartoons(message: types.Message):
    movies = get_movies_by_category('cartoons')
    if not movies:
        return await message.answer("Hozircha multfilmlar mavjud emas.")
    await message.answer("🧸 **Barcha Multfilmlar:**", reply_markup=category_movies_keyboard(movies), parse_mode="Markdown")

@router.message(Command("ai"))
async def cmd_ai(message: types.Message, state: FSMContext):
    from config import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        return await message.answer("⚠️ Botda AI hozircha sozlangan emas. Admindan API key so'rang!")
    
    lang = get_user_lang(message.from_user.id)
    await state.set_state(AIStates.chatting)
    await message.answer(
        texts[lang]['ai_welcome'],
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "ai_chat")
async def ai_chat_callback(callback: types.CallbackQuery, state: FSMContext):
    from config import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        return await callback.answer("⚠️ AI hozircha sozlangan emas.", show_alert=True)
    
    lang = get_user_lang(callback.from_user.id)
    await state.set_state(AIStates.chatting)
    await callback.message.answer(
        texts[lang]['ai_welcome'],
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("stop"))
async def cmd_stop(message: types.Message, state: FSMContext):
    await state.clear()
    lang = get_user_lang(message.from_user.id)
    await message.answer("Amallar to'xtatildi. ✅", reply_markup=main_menu_keyboard(lang))

@router.message(AIStates.chatting)
async def process_ai_message(message: types.Message):
    if message.text:
        from utils.ai import get_ai_response
        from database.db import get_all_movies, add_chat_msg, get_chat_history
        import re
        
        user_id = message.from_user.id
        lang = get_user_lang(user_id)
        movies = get_all_movies()
        
        # Save user message to history
        add_chat_msg(user_id, "user", message.text)
        
        # Load last 10 messages for history
        history = get_chat_history(user_id, limit=10)
        
        wait_msg = await message.answer("🤔 O'ylayapman...")
        response = await get_ai_response(message.text, lang=lang, movies=movies, history=history)
        
        # Parse for [SHOW:code]
        show_match = re.search(r'\[SHOW:(\d+)\]', response)
        clean_response = re.sub(r'\[SHOW:\d+\]', '', response).strip()
        
        # Strip ** formatting fail-safe
        clean_response = clean_response.replace("**", "")
        
        await wait_msg.edit_text(clean_response)
        
        # Save AI response to history
        add_chat_msg(user_id, "assistant", clean_response)
        
        if show_match:
            movie_code = show_match.group(1)
            movie = get_movie_by_code(movie_code)
            if movie:
                await show_movie_details(message, movie, lang)

async def show_movie_details(event: types.Message | types.CallbackQuery, movie, lang):
    bot = event.bot
    user_id = event.from_user.id if isinstance(event, types.Message) else event.from_user.id
    chat_id = event.chat.id if isinstance(event, types.Message) else event.message.chat.id
    
    title, desc, img, link, code, imdb, views = movie[1], movie[2], movie[3], movie[4], movie[5], movie[6], movie[7]
    
    # Clean up title/desc
    display_title = title.replace("**", "")
    display_desc = desc.replace("**", "")
    
    caption = (
        f"🎬 **Nomi:** {display_title}\n"
        f"🔢 **Kodi:** `{code}`\n"
        f"👁️ **Ko'rishlar:** {views}\n"
        f"⭐ **IMDb:** {imdb}\n\n"
        f"📝 **Tavsif:** {display_desc}"
    )
    
    await bot.send_chat_action(chat_id, "upload_document")
    
    try:
        # Basic validation for img
        if not img or img in [".", "#", " "]:
             return await bot.send_message(chat_id, caption, reply_markup=movie_keyboard(link, lang), parse_mode="Markdown")

        if not img.startswith("http"):
            try:
                await bot.send_video(
                    chat_id=chat_id,
                    video=img,
                    caption=caption,
                    reply_markup=movie_keyboard(link, lang),
                    parse_mode="Markdown"
                )
            except Exception:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=img,
                    caption=caption,
                    reply_markup=movie_keyboard(link, lang),
                    parse_mode="Markdown"
                )
        else:
            await bot.send_photo(
                chat_id=chat_id,
                photo=img,
                caption=caption,
                reply_markup=movie_keyboard(link, lang),
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Error sending media: {e}")
        try:
            await bot.send_message(chat_id, caption, reply_markup=movie_keyboard(link, lang), parse_mode="Markdown")
        except:
            pass

@router.callback_query(F.data.startswith("movie_"))
async def movie_callback(callback: types.CallbackQuery):
    code = callback.data.split("_")[1]
    movie = get_movie_by_code(code)
    lang = get_user_lang(callback.from_user.id)
    
    if movie:
        await show_movie_details(callback, movie, lang)
    else:
        await callback.answer(texts[lang]['not_found'], show_alert=True)
    await callback.answer()

@router.message(F.text)
async def process_search(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    from utils.check_sub import is_subscribed
    from config import CHANNEL_LINK
    
    if not await is_subscribed(bot, user_id):
        return await message.answer(
            texts[lang]['sub_required'],
            reply_markup=sub_keyboard(CHANNEL_LINK, lang)
        )

    text = message.text
    # Kod bo'yicha qidirish
    if text.isdigit():
        movie = get_movie_by_code(text)
        if movie:
            await show_movie_details(message, movie, lang)
        else:
            await message.answer(texts[lang]['not_found'])
    else:
        # Nomi bo'yicha qidirish
        movies = get_movies_by_title(text)
        if movies:
            await message.answer(
                texts[lang]['search_res'].format(text),
                reply_markup=search_results_keyboard(movies)
            )
        else:
            # Agar kino topilmasa va bu kimsandir murojati bo'lishi mumkin bo'lsa
            from config import ADMIN_IDS
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            
            kb = InlineKeyboardBuilder()
            profile_url = f"tg://user?id={user_id}"
            kb.row(types.InlineKeyboardButton(text="👤 Profilni ochish", url=profile_url))
            kb.row(types.InlineKeyboardButton(text="✍️ Javob berish", callback_data=f"reply_to_{user_id}"))
            
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin_id, 
                        f"📩 **Yangi murojaat!**\n\n"
                        f"👤 **Kimdan:** {message.from_user.full_name}\n"
                        f"🆔 **ID:** `{user_id}`\n"
                        f"💬 **Xabar:** {text}",
                        parse_mode="Markdown",
                        reply_markup=kb.as_markup()
                    )
                except Exception as e:
                    print(f"Error notifying admin {admin_id}: {e}")
            await message.answer("Xabaringiz adminga yetkazildi! ✅")
