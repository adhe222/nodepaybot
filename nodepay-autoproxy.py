import asyncio
import aiohttp
import time
import uuid
from curl_cffi import requests
from loguru import logger
from fake_useragent import UserAgent
from termcolor import colored
import sys

PING_INTERVAL = 60
RETRIES = 60

DOMAIN_API = {
    "SESSION": "http://api.nodepay.ai/api/auth/session",
    "PING": "https://nw.nodepay.org/api/network/ping"
}

CONNECTION_STATES = {
    "CONNECTED": 1,
    "DISCONNECTED": 2,
    "NONE_CONNECTION": 3
}

status_connect = CONNECTION_STATES["NONE_CONNECTION"]
browser_id = None
account_info = {}
last_ping_time = {}

proxy_success_count = {}

def uuidv4():
    return str(uuid.uuid4())

def valid_resp(resp):
    if not resp or "code" not in resp or resp["code"] < 0:
        raise ValueError("Invalid response")
    return resp

async def render_profile_info(proxy, token):
    global browser_id, account_info

    try:
        np_session_info = load_session_info(proxy)

        if not np_session_info:
            browser_id = uuidv4()
            response = await call_api(DOMAIN_API["SESSION"], {}, proxy, token)
            valid_resp(response)
            account_info = response["data"]
            if account_info.get("uid"):
                save_session_info(proxy, account_info)
                await start_ping(proxy, token)
            else:
                handle_logout(proxy)
        else:
            account_info = np_session_info
            await start_ping(proxy, token)
    except Exception as e:
        logger.error(f"Error in render_profile_info for proxy {proxy}: {e}")
        error_message = str(e)
        if any(phrase in error_message for phrase in [
            "sent 1011 (internal error) keepalive ping timeout; no close frame received",
            "500 Internal Server Error"
        ]):
            logger.info(f"Removing error proxy from the list: {proxy}")
            remove_proxy_from_list(proxy)
            return None
        else:
            logger.error(f"Connection error: {e}")
            return proxy

async def call_api(url, data, proxy, token):
    user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
    random_user_agent = user_agent.random
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.post(url, json=data, headers=headers, impersonate="safari15_5", proxies={
                                "http": proxy, "https": proxy}, timeout=30)

        response.raise_for_status()
        return valid_resp(response.json())
    except Exception as e:
        logger.error(f"Error during API call: {e}")
        raise ValueError(f"Failed API call to {url}")

async def start_ping(proxy, token):
    try:
        while True:
            await ping(proxy, token)
            await asyncio.sleep(PING_INTERVAL)
    except asyncio.CancelledError:
        logger.info(f"Ping task for proxy {proxy} was cancelled")
    except Exception as e:
        logger.error(f"Error in start_ping for proxy {proxy}: {e}")

async def ping(proxy, token):
    global last_ping_time, RETRIES, status_connect

    current_time = time.time()

    if proxy in last_ping_time and (current_time - last_ping_time[proxy]) < PING_INTERVAL:
        logger.info(f"Skipping ping for proxy { proxy}, not enough time elapsed")
        return

    last_ping_time[proxy] = current_time

    try:
        data = {
            "id": account_info.get("uid"),
            "browser_id": browser_id,
            "timestamp": int(time.time()),
            "version": "2.2.7"
        }

        response = await call_api(DOMAIN_API["PING"], data, proxy, token)
        if response["code"] == 0:
            logger.info(f"Ping successful : {response} with id : {account_info.get('uid')}")
            RETRIES = 0
            status_connect = CONNECTION_STATES["CONNECTED"]

            if proxy not in proxy_success_count:
                proxy_success_count[proxy] = 0
            proxy_success_count[proxy] += 1

            if proxy_success_count[proxy] >= 3:
                logger.info(f"Proxy {proxy} has reached the maximum number of successful connections (3). It will not be used anymore.")
                remove_proxy_from_list(proxy)
                return

        else:
            handle_ping_fail(proxy, response)
    except Exception as e:
        logger.error(f"Ping failed : {e}")
        handle_ping_fail(proxy, None)

def handle_ping_fail(proxy, response):
    global RETRIES, status_connect

    RETRIES += 1
    if response and response.get("code") == 403:
        handle_logout(proxy)
    elif RETRIES < 2:
        status_connect = CONNECTION_STATES["DISCONNECTED"]
    else:
        status_connect = CONNECTION_STATES["DISCONNECTED"]

def handle_logout(proxy):
    global status_connect, account_info

    status_connect = CONNECTION_STATES["NONE_CONNECTION"]
    account_info = {}
    save_status(proxy, None)
    logger.info(f"Logged out and cleared session info for proxy {proxy}")

async def load_proxies_from_url(api_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                response.raise_for_status()
                proxies = await response.text()
                proxy_list = proxies.splitlines()
                return proxy_list
    except Exception as e:
        logger.error(f"Failed to load proxies from URL: {e}")
        raise SystemExit("Exiting due to failure in loading proxies")

def load_tokens(token_file):
    try:
        with open(token_file, 'r') as file:
            tokens = file.read().splitlines()
        return tokens
    except Exception as e:
        logger.error(f"Failed to load tokens: {e}")
        raise SystemExit("Exiting due to failure in loading tokens")

def save_status(proxy, status):
    pass

def save_session_info(proxy, data):
    data_to_save = {
        "uid": data.get("uid"),
        "browser_id": browser_id
    }
    pass

def load_session_info(proxy):
    return {}

def is_valid_proxy(proxy):
    return True

def remove_proxy_from_list(proxy):
    global all_proxies
    if proxy in all_proxies:
        all_proxies.remove(proxy)
        logger.info(f"Proxy {proxy} removed from the active list due to exceeding the connection limit.")

async def render_for_token(token, all_proxies):
    active_proxies = [proxy for proxy in all_proxies if is_valid_proxy(proxy)][:100]
    tasks = {asyncio.create_task(render_profile_info(proxy, token)): proxy for proxy in active_proxies}

    done, pending = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
    for task in done:
        failed_proxy = tasks[task]
        if task.result() is None:
            logger.info(f"Removing and replacing failed proxy: {failed_proxy}")
            active_proxies.remove(failed_proxy)
            if all_proxies:
                new_proxy = all_proxies.pop(0)
                if is_valid_proxy(new_proxy):
                    active_proxies.append(new_proxy)
                    new_task = asyncio.create_task(render_profile_info(new_proxy, token))
                    tasks[new_task] = new_proxy
    tasks.pop(task)

    for proxy in set(active_proxies) - set(tasks.values()):
        new_task = asyncio.create_task(render_profile_info(proxy, token))
        tasks[new_task] = proxy

    await asyncio.sleep(3)

async def update_proxies_periodically(proxy_url, update_interval=300):
    global all_proxies
    while True:
        try:
            logger.info("Fetching updated proxy list...")
            all_proxies = await load_proxies_from_url(proxy_url)
            logger.info(f"Updated proxy list: {len(all_proxies)} proxies loaded.")
        except Exception as e:
            logger.error(f"Error updating proxies: {e}")

        await asyncio.sleep(update_interval)

async def loading_animation():
    while True:
        for i in range(3):
            sys.stdout.write(colored("\rMohon bersabar...! Masih mencari proxy yang work...! " + "." * (i + 1), 'yellow'))
            sys.stdout.flush()
            await asyncio.sleep(1)

async def banner():
    banner_text = colored("""
    KONTLIJO
    """, 'cyan', attrs=['bold'])
    sys.stdout.write(banner_text)
    sys.stdout.flush()
    await asyncio.sleep(1)

async def main():
    await banner()  # Display the banner
    proxy_url = 'https://files.ramanode.top/airdrop/grass/server_1.txt'
    all_proxies = await load_proxies_from_url(proxy_url)
    all_tokens = load_tokens('token_list.txt')

    if not all_tokens:
        print("No tokens found in token_list.txt. Exiting the program.")
        exit()

    asyncio.create_task(update_proxies_periodically(proxy_url, update_interval=300))

    loading_task = asyncio.create_task(loading_animation())

    tasks = []

    for token in all_tokens:
        tasks.append(asyncio.create_task(render_for_token(token, all_proxies)))

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    print("\nAlright, we here! Running the script with tokens from token_list.txt.")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program terminated by user.")
