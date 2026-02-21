import asyncio
import aiohttp
import random
import string

NAMES = 5
LENGTH = 5
FILE = "valid.txt"
BIRTHDAY = "1999-04-20"
CONCURRENT_REQUESTS = 10  # adjust (5–20 is safe)

class bcolors:
    OKBLUE = '\033[94m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

found = 0
lock = asyncio.Lock()

def make_username(length):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

async def check_username(session, username):
    url = f"https://auth.roblox.com/v1/usernames/validate?request.username={username}&request.birthday={BIRTHDAY}"
    async with session.get(url, timeout=5) as resp:
        data = await resp.json()
        return data.get("code")

async def worker(session):
    global found
    while found < NAMES:
        username = make_username(LENGTH)
        try:
            code = await check_username(session, username)

            async with lock:
                if found >= NAMES:
                    return

                if code == 0:
                    found += 1
                    print(f"{bcolors.OKBLUE}[{found}/{NAMES}] [+] Found: {username}{bcolors.ENDC}")
                    with open(FILE, "a+") as f:
                        f.write(username + "\n")
                else:
                    print(f"{bcolors.FAIL}[-] Taken: {username}{bcolors.ENDC}")

        except Exception as e:
            print("Error:", e)

async def main():
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [worker(session) for _ in range(CONCURRENT_REQUESTS)]
        await asyncio.gather(*tasks)

    print(f"{bcolors.OKBLUE}[!] Finished{bcolors.ENDC}")

asyncio.run(main())
