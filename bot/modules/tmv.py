import requests
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import unquote

from pyrogram import enums
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot import LOGGER, dispatcher
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker

#listener_dict = {}

def makeKeyboard(user_id):
    buttons = ButtonMaker()
    #print("movie_list : " ,movie_list)
    for key,value in enumerate(movie_list):
        buttons.sbutton(value,f"mv {user_id} {key}")
    buttons.sbutton("Cancel", f"mv {user_id} cancel")

    return buttons.build_menu(1)
  
def tamilmv():
    mainUrl = 'https://www.1tamilmv.cafe/'
    mainlink = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'Connection':'Keep-alive',
        'sec-ch-ua-platform': '"Windows"',
    }
    
    global movie_dict 
    movie_dict = {}
    global real_dict
    real_dict  = {}
    web = requests.request("GET",mainUrl,headers=headers)
    soup = BeautifulSoup(web.text,'lxml')
    linker = []
    magre = []
    badtitles = []
    realtitles = []
    global movie_list
    movie_list = []

    num = 0
    
    temps = soup.find_all('div',{'class' : 'ipsType_break ipsContained'})

    for i in range(21):
        title = temps[i].findAll('a')[0].text
        badtitles.append(title)
        links = temps[i].find('a')['href']
        content = str(links)
        linker.append(content)
        
    for element in badtitles:
        realtitles.append(element.strip())
        movie_dict[element.strip()] = None
    #print(badtitles)
    movie_list = list(movie_dict)
        
    for url in linker:

        html = requests.request("GET",url)
        soup = BeautifulSoup(html.text,'lxml')
        pattern=re.compile(r"magnet:\?xt=urn:[a-z0-9]+:[a-zA-Z0-9]{40}")
        bigtitle = soup.find_all('a')
        alltitles = []
        filelink = []
        mag = []
        for i in soup.find_all('a', href=True):
            if i['href'].startswith('magnet'):
                mag.append(i['href'])
                
        for a in soup.findAll('a', {"data-fileext": "torrent", 'href': True}):
            filelink.append(a['href'])
            alltitles.append(a.text)


        for p in range(0,len(filelink)):
#             #print(f"*{alltitles[p]}* -->\n🧲 `{mag[p]}`\n🗒️->[Torrent file]({filelink[p]})")
            try:
              real_dict.setdefault(movie_list[num],[])
              real_dict[movie_list[num]].append({"Title": alltitles[p], "TorrentFile": filelink[p]})
              #real_dict[movie_list[num]].append((f"*{alltitles[p]}* -->\n🧲 `{mag[p]}`\n🗒️->[Torrent file]({filelink[p]})"))
            except:
              pass
            
        num = num + 1
        
def select_mv(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    #print("data : ", data)
    msg = query.message
    data = data.split(" ")
    uid = int(data[1])
    data = data[2]
    global movie_list
    global real_dict
    '''
    try:
        task_info = listener_dict[task_id]
    except:
        return editMessage("This is an old task", msg)
    
    uid = task_info[0]
    u_name = task_info[1]
    '''
    
    if user_id != uid and not CustomFilters._owner_query(user_id):
        return query.answer(text="This task is not for you!", show_alert=True)
    #print("data1 : ", data)
    #print("Movie Dict : " , movie_list)
    #sendMessage(f"<b>Here's your Movie links 🎥</b>", query.bot, msg)
    if data == "cancel":
        query.answer()
        editMessage('🥰', msg)
    for key , value in enumerate(movie_list):
        if data == f"{key}":
            if movie_list[int(data)] in real_dict.keys():
                for file_data in real_dict[movie_list[int(data)]]:
                    LOGGER.info(f"{file_data}")
                    title = file_data["Title"]
                    torrent_file_url = file_data["TorrentFile"]
                    
                    # Download the torrent file
                    response = requests.get(torrent_file_url)
                    file_name = f"{title}.torrent"
                    query.bot.send_document(chat_id=msg.chat_id, document=response.content, filename=file_name, caption=title + "\n\n #KristyX")
                    
            else:
                sendMessage(f"<b>Torrent Files Not Available</b>", query.bot, msg)

def list_tmv(update, context):
    msg_id = update.message.message_id
    user_id = update.message.from_user.id 
    u_name = update.message.from_user.first_name
    
    lm = sendMessage("<b>Please wait for 10 seconds...🤖</b>", context.bot, update.message)
    tamilmv()
    deleteMessage(context.bot, lm)
    #listener_dict[msg_id] = [user_id, u_name]
    sendMarkup("Select a Movie from the list 🙂 : ", context.bot, update.message, reply_markup=makeKeyboard(user_id))
         
  

list_tmv_handler = CommandHandler(BotCommands.TMVCommand, list_tmv,
                                       filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user), run_async=True)
quality_handler = CallbackQueryHandler(select_mv, pattern="mv", run_async=True)

dispatcher.add_handler(list_tmv_handler)
dispatcher.add_handler(quality_handler)
