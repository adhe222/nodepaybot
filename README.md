# Nodepay Automate with Proxies | Bypass Version!
Automate farming Nodepay Network using proxies. Please use the bypass version. I found Nodepay's real IP host to make farming easier without being blocked by Cloudflare protection. 
- This bot support multiple accounts. Run ```run-multi-bypass.py```
- Place multiple tokens in ```token_list.txt```
### Tools and components required
1. Nodepay Account | Register: [https://app.nodepay.ai/register](https://app.nodepay.ai/register?ref=ZUCBuJaIoBXLE6J)
2. Proxies Static Residental | [FREE 10 PREMIUM PROXIES](https://www.webshare.io/?referral_code=p7k7whpdu2jg) | Good Premium Proxies (paid): [922proxy](https://www.922proxy.com/register?inviter_code=d03d4fed), [proxy-cheap](https://app.proxy-cheap.com/r/JysUiH), [infatica](https://dashboard.infatica.io/aff.php?aff=544)
3. VPS (OPTIONAL) and Python3
# Setup Tutorial
- Open [Nodepay](https://app.nodepay.ai/register?ref=ZUCBuJaIoBXLE6J) and login to dashboard
- Press F12 or CTRL + SHIFT + I
- Select Console
- At the console, type ```allow pasting``` and press enter
![0001](https://github.com/im-hanzou/getgrass_bot/blob/main/pasting.JPG)
- Then type ``localStorage.getItem('np_token')`` and press enter
![0002](https://github.com/im-hanzou/getgrass_bot/blob/main/nodepaytoken.png)
- The text that appears is your nodepay token and copy the text
### Component installation
- Install Python For Windows: [Python](https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe)
- For Unix:
```bash
apt install python3 python3-pip -y
```
- Installing requirements: 
```bash
python -m pip install -r requirements.txt
```
### Run the Bot
- clone repo
```bash
git clone https://github.com/adhe222/nodepaybot.git
```
- Replace the proxies example in ```local_proxies.txt``` to your own proxies, please use only 3 proxies with proxies http only.
#### Run command
- Run for autoproxy server:
```bash
python nodepay-autoproxy.py
```
>Press Enter, or
- Run for multi bypassed server with manual proxies:
  
```bash
python run-multi-bypass.py
```
# Operating status
If the following log appears, it means it is running successfully.
```bash
2024-07-30 04:37:18.263 | INFO     | __main__:ping:110 - Ping successful: {'success': True, 'code': 0, 'msg': 'Success', 'data': {'ip_score': 88}}
2024-07-30 04:37:48.621 | INFO     | __main__:ping:110 - Ping successful: {'success': True, 'code': 0, 'msg': 'Success', 'data': {'ip_score': 90}}
2024-07-30 04:38:18.968 | INFO     | __main__:ping:110 - Ping successful: {'success': True, 'code': 0, 'msg': 'Success', 'data': {'ip_score': 94}}
2024-07-30 04:38:59.338 | INFO     | __main__:ping:110 - Ping successful: {'success': True, 'code': 0, 'msg': 'Success', 'data': {'ip_score': 98}}
```
# Notes
- Run this bot, and it will update your referrer code to my invite code if you don't have one.
- One account only can connect with 3 Proxies.
- Feel free to enjoy and recode or create new bots using the Nodepay API with direct IP that I found.
- You can just run this bot at your own risk, I'm not responsible for any loss or damage caused by this bot. This bot is for educational purposes only.
