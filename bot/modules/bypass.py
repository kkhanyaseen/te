import re
import time
import requests
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from re import match as rematch

from telegram import Message
from telegram.ext import CommandHandler
from bot import LOGGER, dispatcher, PAID_SERVICE, PAID_USERS, OWNER_ID
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage, deleteMessage
from PyBypass import bypass

def bypasser(update, context):
    user_id_ = update.message.from_user.id
    if PAID_SERVICE is True:
        if not (user_id_ in PAID_USERS) and user_id_ != OWNER_ID:
            sendMessage(f"Buy Paid Service to Use this Scrape Feature.", context.bot, update.message)
            return
    message:Message = update.effective_message
    link = None
    if message.reply_to_message: link = message.reply_to_message.text
    else:
        link = message.text.split(' ', 1)
        if len(link) == 2:
            link = link[1]
        else:
            help_msg = "<b>Send link after command:</b>"
            help_msg += f"\n<code>/{BotCommands.ScrapeCommand[0]}" + " {link}" + "</code>"
            help_msg += "\n<b>By Replying to Message (Including Link):</b>"
            help_msg += f"\n<code>/{BotCommands.ScrapeCommand[0]}" + " {message}" + "</code>"
            return sendMessage(help_msg, context.bot, update.message)
    try: link = rematch(r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", link)[0]
    except TypeError: return sendMessage('Not a Valid Link.', context.bot, update)
    links = []
    if "dulink.in" in link:
        msg = sendMessage(f'Please wait a minute....\n\nBypassing Your Dulink', context.bot, update.message)
        links = bypass_du(link)
        deleteMessage(context.bot, msg)
        sendMessage(f"<b><u>Given Link:</u></b> <code>{link}</code>\n\n<b><u>Bypassed Link:</u></b> <code>{links}</code>", context.bot, update.message)
    elif "shareus.in" in link:
        msg = sendMessage(f'Please wait a minute....\n\nBypassing Your Shareus', context.bot, update.message)
        links = shareus(link)
        deleteMessage(context.bot, msg)
        sendMessage(f"<b><u>Given Link:</u></b> <code>{link}</code>\n\n<b><u>Bypassed Link:</u></b> <code>{links}</code>", context.bot, update.message)
    elif "tnlink" in link:
        msg = sendMessage(f'Please wait a minute....\n\nBypassing Your TNlink Link', context.bot, update.message)
        links = tnlink(link)
        deleteMessage(context.bot, msg)
        sendMessage(f"<b><u>Given Link:</u></b> <code>{link}</code>\n\n<b><u>Bypassed Link:</u></b> <code>{links}</code>", context.bot, update.message)
    elif "xpshort" in link:
        msg = sendMessage(f'Please wait a minute....\n\nBypassing Your XPShort Link', context.bot, update.message)
        links = xpshort(link)
        deleteMessage(context.bot, msg)
        sendMessage(f"<b><u>Given Link:</u></b> <code>{link}</code>\n\n<b><u>Bypassed Link:</u></b> <code>{links}</code>", context.bot, update.message)
    elif "gplinks" in link:
        msg = sendMessage(f'Please wait a minute....\n\nBypassing Your GPlinks Link', context.bot, update.message)
        links = gplinks(link)
        deleteMessage(context.bot, msg)
        sendMessage(f"<b><u>Given Link:</u></b> <code>{link}</code>\n\n<b><u>Bypassed Link:</u></b> <code>{links}</code>", context.bot, update.message)
    else:
        msg = sendMessage(f'Please wait a minute....\n\nBypassing Your Link on PyBpass Lib', context.bot, update.message)
        links = pybypass(link)
        deleteMessage(context.bot, msg)
        sendMessage(f"<b><u>Given Link:</u></b> <code>{link}</code>\n\n<b><u>Bypassed Link:</u></b> <code>{links}</code>", context.bot, update.message)
        
def bypass_du(url):
    client = cloudscraper.create_scraper(allow_brotli=False)
   
    DOMAIN = "https://cac.teckypress.in/"

    url = url[:-1] if url[-1] == '/' else url

    code = url.split("/")[-1]
    
    
    final_url = f"{DOMAIN}/{code}"
    
    ref = "https://teckypress.in/"
    
    h = {"referer": ref}

    resp = client.get(final_url, headers=h)
    soup = BeautifulSoup(resp.content, "html.parser")
    
    inputs = soup.find_all("input")
    
    data = { input.get('name'): input.get('value') for input in inputs }

    h = { "x-requested-with": "XMLHttpRequest" }
    
    
    r = client.post(f"{DOMAIN}/links/go", data=data, headers=h)
    try:
        return r.json()['url']
    except: return "Something went wrong :("
    
def shareus(url):
    token = url.split("=")[-1]
    bypassed_url = "https://us-central1-my-apps-server.cloudfunctions.net/r?shortid="+ token
    response = requests.get(bypassed_url).text
    return response

def tnlink(url):
    client = requests.session()
    
    
    DOMAIN = "https://gadgets.usanewstoday.club"

    url = url[:-1] if url[-1] == '/' else url

    code = url.split("/")[-1]
    
    final_url = f"{DOMAIN}/{code}"
    
    ref = "https://usanewstoday.club/"
    
    h = {"referer": ref}
  
    resp = client.get(final_url,headers=h)
    
    soup = BeautifulSoup(resp.content, "html.parser")
    
    inputs = soup.find_all("input")
   
    data = { input.get('name'): input.get('value') for input in inputs }

    h = { "x-requested-with": "XMLHttpRequest" }
    
    time.sleep(8)
    r = client.post(f"{DOMAIN}/links/go", data=data, headers=h)
    try:
        return r.json()['url']
    except: return "Something went wrong :("
    
def gplinks(url: str):
 
 url = url[:-1] if url[-1] == '/' else url
 token = url.split("/")[-1]
    
 domain ="https://gplinks.co/"
 referer = "https://mynewsmedia.co/"

    
 client = requests.Session()
 vid = client.get(url, allow_redirects= False).headers["Location"].split("=")[-1]
 url = f"{url}/?{vid}"

 response = client.get(url, allow_redirects=False)
 soup = BeautifulSoup(response.content, "html.parser")
    
    
 inputs = soup.find(id="go-link").find_all(name="input")
 data = { input.get('name'): input.get('value') for input in inputs }
    

 time.sleep(5)
 headers={"x-requested-with": "XMLHttpRequest"}
 bypassed_url = client.post(domain+"links/go", data=data, headers=headers).json()["url"]
 return bypassed_url

def xpshort(url):     
    client = requests.session()
    
    
    DOMAIN = "https://push.bdnewsx.com"

    url = url[:-1] if url[-1] == '/' else url

    code = url.split("/")[-1]
    
    final_url = f"{DOMAIN}/{code}"
    
    ref = "https://techrfour.com/"
    
    h = {"referer": ref}
  
    resp = client.get(final_url,headers=h)
    
    soup = BeautifulSoup(resp.content, "html.parser")
    
    inputs = soup.find_all("input")
   
    data = { input.get('name'): input.get('value') for input in inputs }

    h = { "x-requested-with": "XMLHttpRequest" }
    
    time.sleep(8)
    r = client.post(f"{DOMAIN}/links/go", data=data, headers=h)
    try:
        return r.json()['url']
    except: return "Something went wrong :("

def pybypass(url):
    """ PyBypass is Based on https://github.com/sanjit-sinha/PyBypass"""
    try:
        return bypass(url)
    except: return "Something went wrong on PyBypass"
    
srp_handler = CommandHandler(BotCommands.BypassCommand, bypasser,filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)

dispatcher.add_handler(srp_handler)
