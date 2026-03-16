from aiogram import Router, types, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from database.db import add_movie, get_stats, get_all_movies, get_movie_by_code, update_movie
from utils.states import AdminStates, AddMovieStates, EditMovieStates
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

def cancel_kb():
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_wizard"))
    return kb.as_markup()

@router.message(Command("stats"), F.from_user.id.in_(ADMIN_IDS))
async def stats_cmd(message: types.Message):
    u_count, m_count = get_stats()
    await message.answer(
        f"📊 Bot Statistikasi:\n\n"
        f"👥 Foydalanuvchilar: {u_count}\n"
        f"🎬 Kinolar: {m_count}"
    )

# Faqat admin ishlata oladi
@router.message(Command("add"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_add_movie_wizard(message: types.Message, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎬 Kinolar", callback_data="addcat_movies"),
           types.InlineKeyboardButton(text="📺 Seryallar", callback_data="addcat_series"))
    kb.row(types.InlineKeyboardButton(text="🎎 Anime", callback_data="addcat_anime"),
           types.InlineKeyboardButton(text="🧸 Multfilmlar", callback_data="addcat_cartoons"))
    kb.row(types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_wizard"))
    
    await state.set_state(AddMovieStates.category)
    await message.answer("Qaysi bo'limga qo'shamiz?", reply_markup=kb.as_markup())

@router.callback_query(F.data == "cancel_wizard")
async def cancel_wizard_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Amal bekor qilindi.")
    await callback.answer()

@router.callback_query(AddMovieStates.category, F.data.startswith("addcat_"), F.from_user.id.in_(ADMIN_IDS))
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.split("_")[1]
    cat_names = {"movies": "🎬 Kino", "series": "📺 Seryal", "anime": "🎎 Anime", "cartoons": "🧸 Multfilm"}
    await state.update_data(category=cat)
    await state.set_state(AddMovieStates.title)
    await callback.message.edit_text(f"Tanlandi: {cat_names[cat]}\n\n1. Nomi qanday?", reply_markup=cancel_kb())
    await callback.answer()

@router.message(AddMovieStates.title, F.from_user.id.in_(ADMIN_IDS))
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.replace("**", ""))
    await state.set_state(AddMovieStates.media)
    await message.answer("2. Video yoki Rasm yuboring:", reply_markup=cancel_kb())

@router.message(AddMovieStates.media, F.from_user.id.in_(ADMIN_IDS))
async def process_media(message: types.Message, state: FSMContext):
    media_url = None
    
    if message.photo:
        media_url = message.photo[-1].file_id
    elif message.video:
        media_url = message.video.file_id
    elif message.animation:
        media_url = message.animation.file_id
    elif message.text and message.text.startswith("http"):
        media_url = message.text
    else:
        return await message.answer("⚠️ Iltimos, video, rasm yoki link yuboring:", reply_markup=cancel_kb())
    
    await state.update_data(photo=media_url)
    await state.set_state(AddMovieStates.imdb)
    await message.answer("3. IMDb reytingi (masalan 8.5):", reply_markup=cancel_kb())

@router.message(AddMovieStates.imdb, F.from_user.id.in_(ADMIN_IDS))
async def process_imdb(message: types.Message, state: FSMContext):
    try:
        rating = float(message.text)
    except:
        return await message.answer("⚠️ Faqat raqam kiriting (masalan 8.5):", reply_markup=cancel_kb())
        
    await state.update_data(imdb=rating)
    await state.set_state(AddMovieStates.code)
    await message.answer("4. Kino kodini kiriting (boshqa kinolar bilan o'xshash bo'lmasin):", reply_markup=cancel_kb())

@router.message(AddMovieStates.code, F.from_user.id.in_(ADMIN_IDS))
async def process_code(message: types.Message, state: FSMContext):
    code = message.text
    data = await state.get_data()
    
    # Defaults
    link = "#"
    desc = "Kino ma'lumotlari"
    
    success = add_movie(data['title'], desc, data['photo'], link, code, data['imdb'], data['category'])
    if success:
        await message.answer(
            f"✅ **Muvaffaqiyatli qo'shildi!**\n\n"
            f"🎬 Nomi: {data['title']}\n"
            f"🔢 Kodi: `{code}`\n"
            f"⭐ IMDb: {data['imdb']}"
        )
    else:
        await message.answer(f"❌ Xatolik: `{code}` kodli ma'lumot allaqachon mavjud! Boshqa kod kiriting:")
        return # Qayta kiritishni kutamiz
    
    await state.clear()

@router.callback_query(F.data.startswith("reply_to_"), F.from_user.id.in_(ADMIN_IDS))
async def reply_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.split("_")[-1]
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminStates.waiting_for_reply)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_reply"))
    
    await callback.message.answer(
        f"✍️ ID: `{user_id}` bo'lgan foydalanuvchiga javobingizni yozing:",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_reply")
async def cancel_reply_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Javob berish bekor qilindi.")
    await callback.answer()

@router.message(AdminStates.waiting_for_reply, F.from_user.id.in_(ADMIN_IDS))
async def process_admin_reply(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    
    try:
        if message.text:
            await bot.send_message(target_user_id, f"✉️ **Admin javobi:**\n\n{message.text}", parse_mode="Markdown")
        elif message.photo:
            await bot.send_photo(target_user_id, message.photo[-1].file_id, caption=f"✉️ **Admin javobi:**\n\n{message.caption or ''}", parse_mode="Markdown")
        
        await message.answer("✅ Javobingiz foydalanuvchiga yuborildi!")
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")
        await state.clear()

# --- TAHRIRLASH (EDIT) QISMI ---

@router.message(Command("edit"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_edit_movie(message: types.Message, state: FSMContext):
    await state.set_state(EditMovieStates.waiting_for_code)
    await message.answer("📝 **Kino tahrirlash**\n\nKino kodini yuboring:", reply_markup=cancel_kb())

@router.message(EditMovieStates.waiting_for_code, F.from_user.id.in_(ADMIN_IDS))
async def process_edit_code(message: types.Message, state: FSMContext):
    code = message.text
    movie = get_movie_by_code(code)
    if not movie:
        return await message.answer("❌ Bunday kodli kino topilmadi. Qayta urinib ko'ring:", reply_markup=cancel_kb())
    
    await state.update_data(edit_code=code)
    await state.set_state(EditMovieStates.choosing_field)
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎬 Nomi", callback_data="editfield_title"))
    kb.row(types.InlineKeyboardButton(text="🖼️ Media (Video/Rasm)", callback_data="editfield_image_url"))
    kb.row(types.InlineKeyboardButton(text="📝 Tavsif", callback_data="editfield_description"))
    kb.row(types.InlineKeyboardButton(text="🔗 Yuklab olish linki", callback_data="editfield_download_link"))
    kb.row(types.InlineKeyboardButton(text="⭐ IMDb", callback_data="editfield_imdb_rating"))
    kb.row(types.InlineKeyboardButton(text="✅ Tugatish", callback_data="cancel_wizard"))
    
    await message.answer(
        f"📋 **Kino ma'lumotlari:**\n\n"
        f"🎬 Nomi: {movie[1]}\n"
        f"🔢 Kodi: {movie[5]}\n\n"
        f"O'zgartirmoqchi bo'lgan bo'limni tanlang:",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.startswith("editfield_"), F.from_user.id.in_(ADMIN_IDS))
async def edit_field_callback(callback: types.CallbackQuery, state: FSMContext):
    field = callback.data.split("_", 1)[1]
    await state.update_data(edit_field=field)
    await state.set_state(EditMovieStates.updating_value)
    
    field_names = {
        "title": "yangi Nomini",
        "image_url": "yangi Media (Video yoki Rasm)ni",
        "description": "yangi Tavsifni",
        "download_link": "yangi Yuklab olish linkini",
        "imdb_rating": "yangi IMDb reytingini"
    }
    
    await callback.message.answer(f"📥 Iltimos, {field_names.get(field)} yuboring:", reply_markup=cancel_kb())
    await callback.answer()

@router.message(EditMovieStates.updating_value, F.from_user.id.in_(ADMIN_IDS))
async def process_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    code = data['edit_code']
    field = data['edit_field']
    
    new_value = None
    if field == "image_url":
        if message.photo:
            new_value = message.photo[-1].file_id
        elif message.video:
            new_value = message.video.file_id
        elif message.animation:
            new_value = message.animation.file_id
        elif message.text and message.text.startswith("http"):
            new_value = message.text
        else:
            return await message.answer("⚠️ Iltimos, media yuboring!")
    elif field == "imdb_rating":
        try:
            new_value = float(message.text)
        except:
            return await message.answer("⚠️ Iltimos, IMDb reytingini raqamda yuboring (masalan: 8.5)!")
    else:
        new_value = message.text.replace("**", "")
        
    update_data = {field: new_value}
    success = update_movie(code, **update_data)
    
    if success:
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="🏠 Menu", callback_data="cancel_wizard"))
        kb.row(types.InlineKeyboardButton(text="✏️ Yana tahrirlash", callback_data=f"edit_again_{code}"))
        await message.answer("✅ Ma'lumot muvaffaqiyatli yangilandi!", reply_markup=kb.as_markup())
    else:
        await message.answer("❌ Yangilashda xatolik yuz berdi.")
    
    await state.set_state(EditMovieStates.choosing_field)

@router.callback_query(F.data.startswith("edit_again_"), F.from_user.id.in_(ADMIN_IDS))
async def edit_again_callback(callback: types.CallbackQuery, state: FSMContext):
    # Bu handler process_edit_code dagi keyboardni qayta chiqaradi
    code = callback.data.split("_")[-1]
    movie = get_movie_by_code(code)
    
    await state.update_data(edit_code=code)
    await state.set_state(EditMovieStates.choosing_field)
    
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎬 Nomi", callback_data="editfield_title"))
    kb.row(types.InlineKeyboardButton(text="🖼️ Media", callback_data="editfield_image_url"))
    kb.row(types.InlineKeyboardButton(text="📝 Tavsif", callback_data="editfield_description"))
    kb.row(types.InlineKeyboardButton(text="🔗 Link", callback_data="editfield_download_link"))
    kb.row(types.InlineKeyboardButton(text="⭐ IMDb", callback_data="editfield_imdb_rating"))
    kb.row(types.InlineKeyboardButton(text="✅ Tugatish", callback_data="cancel_wizard"))
    
    await callback.message.edit_text(
        f"📋 **Kino ma'lumotlari:**\n\n"
        f"🎬 Nomi: {movie[1]}\n"
        f"🔢 Kodi: {movie[5]}\n\n"
        f"Yana nimani o'zgartiramiz?",
        reply_markup=kb.as_markup()
    )
    await callback.answer()
