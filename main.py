import aiohttp
import asyncio
import time
import random
import re

async def check_cookie(session, cookie, proxy=None, proxy_auth=None):
    try:
        async with session.post("https://auth.roblox.com/v2/logout", cookies={'.ROBLOSECURITY': cookie}, proxy=proxy, proxy_auth=proxy_auth) as response:
            if 'X-CSRF-TOKEN' in response.headers:
                return cookie, True
    except Exception as e:
        print(f"Error checking cookie with proxy {proxy}: {e}")
    return cookie, False

async def cookie_checker(cookies, proxies=None):
    valid_cookies = []
    invalid_count = 0

    async with aiohttp.ClientSession() as session:
        tasks = []
        for cookie in cookies:
            if proxies:
                proxy, proxy_auth = random.choice(proxies)
            else:
                proxy, proxy_auth = None, None
            tasks.append(check_cookie(session, cookie, proxy, proxy_auth))
        
        results = await asyncio.gather(*tasks)
        for cookie, is_valid in results:
            if is_valid:
                valid_cookies.append(cookie)
            else:
                invalid_count += 1

    return valid_cookies, invalid_count

def load_cookies(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

def save_cookies(file_path, cookies):
    with open(file_path, "w") as file:
        for cookie in cookies:
            file.write(cookie + '\n')

def load_proxies(file_path):
    proxies = []
    proxy_pattern = re.compile(r'^(?:(?P<user>[^:]+):(?P<pass>[^@]+)@)?(?P<host>[^:]+):(?P<port>\d+)$')

    with open(file_path, "r") as file:
        for line in file:
            match = proxy_pattern.match(line.strip())
            if match:
                user = match.group('user')
                password = match.group('pass')
                host = match.group('host')
                port = match.group('port')
                proxy = f"http://{host}:{port}"
                proxy_auth = aiohttp.BasicAuth(user, password) if user and password else None
                proxies.append((proxy, proxy_auth))
            else:
                print(f"Skipping malformed proxy line: {line.strip()}")

    return proxies

def main():
    input_file = 'cookies.txt'
    output_file = 'cookiew.txt'
    proxy_file = 'proxies.txt'

    cookies = load_cookies(input_file)
    total_cookies = len(cookies)

    use_proxy = input("Do you want to verify cookies with a proxy? (yes/no): ").strip().lower() == 'yes'
    proxies = []

    if use_proxy:
        proxies = load_proxies(proxy_file)
        if not proxies:
            print("No proxies loaded. Please check your proxies.txt file.")
            return
        print(f"Loaded {len(proxies)} proxies.")

    start_time = time.time()
    valid_cookies, invalid_count = asyncio.run(cookie_checker(cookies, proxies if use_proxy else None))
    elapsed_time = time.time() - start_time

    save_cookies(output_file, valid_cookies)

    valid_count = len(valid_cookies)
    print(f"Valid Cookies: {valid_count} | Invalid Cookies: {invalid_count} | Cookies Checked: {valid_count + invalid_count}/{total_cookies} in {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()
