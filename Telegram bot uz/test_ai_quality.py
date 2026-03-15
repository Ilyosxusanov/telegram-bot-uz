import asyncio
import sys
from utils.ai import get_ai_response
from database.db import get_all_movies

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def test():
    movies = get_all_movies()
    query = "Menga Spiderman kinosini ko'rsat"
    print(f"Query: {query}")
    response = await get_ai_response(query, lang='uz', movies=movies)
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test())
