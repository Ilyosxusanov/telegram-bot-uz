import asyncio
import aiohttp
import string

async def test_token(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    return True
    except Exception:
        pass
    return False

async def main():
    base_token = "8634062491:AAEGM76eppFLNVyloW5-h5pY5Yk_4f-E8-U"
    chars = string.ascii_letters + string.digits + "_-"
    
    print(f"Testing suffixes for {base_token}...")
    
    tasks = []
    for char in chars:
        tasks.append(test_token(base_token + char))
    
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        if result:
            correct_token = base_token + chars[i]
            print(f"CORRECT_TOKEN_FOUND: {correct_token}")
            return
    
    print("No 1-char suffix found. Testing 2-char suffixes...")
    # Optional: logic for 2-char if needed
    for c1 in chars:
        tasks = []
        for c2 in chars:
            tasks.append(test_token(base_token + c1 + c2))
        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results):
            if result:
                correct_token = base_token + c1 + chars[i]
                print(f"CORRECT_TOKEN_FOUND: {correct_token}")
                return

if __name__ == "__main__":
    asyncio.run(main())
