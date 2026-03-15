import google.generativeai as genai
from config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

async def get_ai_response(prompt, lang='uz', movies=None, history=None):
    if not GEMINI_API_KEY:
        return "⚠️ Botda AI hozircha sozlangan emas. Admindan API key so'rang!"
    
    # Updated System instruction: Strictly DB recommendations, can use external info for details
    system_prompt = (
        f"Siz 'Top Kinolar' botining aqlli yordamchisisiz. Kinolar va filmlar haqida juda bilimlisiz. "
        f"Faydalanuvchi tanlagan tilda ({lang}) javob bering.\n\n"
        f"1. TAVSIYA QOIDASI: Faqat va faqat quyidagi BAZADA MAVJUD bo'lgan kinolarnigina tavsiya qiling. "
        f"Agar foydalanuvchi bazada yo'q kino haqida so'rasa, u kino hozircha botda yo'qligini ayting va bazadagi birorta o'xshash kinoni taklif qiling.\n"
        f"2. MA'LUMOT QOIDASI: Tavsiya qilayotgan kinongiz haqida ma'lumot berishda o'zingizning keng bilimingizdan foydalanishingiz mumkin "
        f"(syujet, aktyorlar, qiziqarli faktlar va h.k.), lekin o'sha kino albatta bazada bo'lishi shart.\n"
        f"3. KO'RSATISH: Filmni ko'rsatishni so'rasagina [SHOW:kod] qo'shing.\n"
        f"4. TAQIQLANGAN: Javoblarda hech qachon ** (ikkita yulduzcha) belgisini ishlatmang.\n\n"
        "Bazada mavjud kinolar:\n"
    )
    
    if movies:
        for m in movies:
            title, code, desc, imdb = m
            system_prompt += f"- {title} (Kodi: {code}, IMDb: {imdb}): {desc[:100]}...\n"
    else:
        system_prompt += "Hozircha bazada kinolar yo'q."

    # Process history
    full_prompt = ""
    if history:
        full_prompt += "Oldingi suhbat tarixingiz (kontekst uchun):\n"
        for role, content in history:
            role_name = "Foydalanuvchi" if role == "user" else "AI"
            full_prompt += f"{role_name}: {content}\n"
        full_prompt += f"\nFoydalanuvchining yangi savoli: {prompt}"
    else:
        full_prompt = prompt

    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_prompt
        )
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text
        else:
            return "⚠️ AI javob qaytara olmadi (Xavfsizlik filtri yoki boshqa sabab)."
    except Exception as e:
        print(f"DEBUG AI ERROR: {str(e)}")
        return f"❌ Xatolik yuz berdi: {str(e)}"
