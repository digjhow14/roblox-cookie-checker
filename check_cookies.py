import aiohttp
import asyncio
import time

async def check_cookie(session, cookie):
    try:
        async with session.post("https://auth.roblox.com/v2/logout", cookies={'.ROBLOSECURITY': cookie}) as response:
            if 'X-CSRF-TOKEN' in response.headers:
                return cookie, True
    except:
        pass
    return cookie, False

async def cookie_checker(cookies):
    valid_cookies = []
    invalid_count = 0
    async with aiohttp.ClientSession() as session:
        tasks = [check_cookie(session, cookie) for cookie in cookies]
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

def main():
    input_file = 'cookies.txt'
    output_file = 'cookiew.txt'

    cookies = load_cookies(input_file)
    total_cookies = len(cookies)

    start_time = time.time()
    valid_cookies, invalid_count = asyncio.run(cookie_checker(cookies))
    elapsed_time = time.time() - start_time

    save_cookies(output_file, valid_cookies)

    valid_count = len(valid_cookies)
    print(f"Valid Cookies: {valid_count} | Invalid Cookies: {invalid_count} | Cookies Checked: {valid_count + invalid_count}/{total_cookies} in {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()
  
