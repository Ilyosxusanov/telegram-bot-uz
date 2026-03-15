from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.translations import texts

def movie_keyboard(download_link, lang='uz'):
    builder = InlineKeyboardBuilder()
    if download_link and download_link.startswith("http"):
        text = "🎬 Filmni yuklab olish" if lang == 'uz' else ("🎬 Скачать фильм" if lang == 'ru' else "🎬 Download Movie")
        builder.row(types.InlineKeyboardButton(text=text, url=download_link))
    return builder.as_markup()

def search_results_keyboard(movies):
    builder = InlineKeyboardBuilder()
    for movie in movies:
        builder.row(types.InlineKeyboardButton(
            text=f"🎥 {movie[1]} ({movie[5]})", callback_data=f"movie_{movie[5]}")
        )
    builder.adjust(1)
    return builder.as_markup()

def sub_keyboard(channel_link, lang='uz'):
    t = texts[lang]
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=t['join_btn'], url=channel_link))
    builder.row(types.InlineKeyboardButton(text=t['cont_btn'], callback_data="check_sub"))
    return builder.as_markup()

def lang_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="setlang_uz"),
        types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru"),
        types.InlineKeyboardButton(text="🇺🇸 English", callback_data="setlang_en")
    )
    return builder.as_markup()

def main_menu_keyboard(lang='uz'):
    t = texts[lang]
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=t['most_searched'], callback_data="cat_most"))
    builder.row(types.InlineKeyboardButton(text=t['top_imdb'], callback_data="cat_imdb"))
    builder.row(types.InlineKeyboardButton(text=t['by_code'], callback_data="cat_code")) # Added back
    builder.row(types.InlineKeyboardButton(text=t['ai_search'], callback_data="ai_chat"))
    builder.adjust(2, 1, 1)
    return builder.as_markup()
