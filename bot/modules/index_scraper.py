import requests
import base64 
import json
import urllib
from telegram.ext import CommandHandler

from bot import dispatcher, app
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage
from bot.helper.telegram_helper.bot_commands import BotCommands

next_page = False
next_page_token = "" 
 
def index(update, context):
    user_id_ = update.message.from_user.id 
    pre_send = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    if len(pre_send) > 1:
        txt = pre_send[1]
    elif reply_to is not None:
        txt = reply_to.text
    else:
        txt = ""
    link = txt     
    if 'baashaxcloud' in link:
        msg = sendMessage(f'Running Scrape ...', context.bot, update.message)
        index_link = link
        
        e = main(url=index_link, username='BaashaX', password='DriveX')
        for e1 in e:
            eur = f'{e1}'
            sendMessage(eur, context.bot, update.message)
        editMessage('Index Scrape Done', msg)
    elif 'sony-tamizh' in link:
        msg = sendMessage(f'Running Scrape ...', context.bot, update.message)
        index_link = link
        
        e = main(url=index_link, username='Romeo*', password='VideoM')
        for e1 in e:
            eur = f'{e1}'
            sendMessage(eur, context.bot, update.message)
        editMessage('Index Scrape Done', msg)
    elif 'workers' in link:
        msg = sendMessage(f'Running Scrape ...', context.bot, update.message)
        index_link = link
        
        e = main(url=index_link, username='', password='')
        for e1 in e:
            eur = f'{e1}'
            sendMessage(eur, context.bot, update.message)
        editMessage('Index Scrape Done', msg)
    else:
        sendMessage('Send A Valid Index Links', context.bot, update.message)  
  
def authorization_token(username, password):
	 user_pass = f"{username}:{password}"
	 token ="Basic "+ base64.b64encode(user_pass.encode()).decode()
	 return token

	 	 
def decrypt(string): 
     return base64.b64decode(string[::-1][24:-20]).decode('utf-8')  

  
def func(payload_input, url, username, password): 
    global next_page 
    global next_page_token
    
    url = url + "/" if  url[-1] != '/' else url
         
    try: headers = {"authorization":authorization_token(username,password)}
    except: return "username/password combination is wrong"
 
    encrypted_response = requests.post(url, data=payload_input, headers=headers)
    if encrypted_response.status_code == 401: return "username/password combination is wrong"
   
    try: decrypted_response = json.loads(decrypt(encrypted_response.text))
    except: return "something went wrong. check index link/username/password field again"
       
    page_token = decrypted_response["nextPageToken"] 
    if page_token == None: 
        next_page = False 
    else: 
        next_page = True 
        next_page_token = page_token 
   
     
    result = []
   
    if list(decrypted_response.get("data").keys())[0] == "error": pass
    else :
      file_length = len(decrypted_response["data"]["files"])
      for i, _ in enumerate(range(file_length)):
	        files_type   = decrypted_response["data"]["files"][i]["mimeType"] 
	        files_name   = decrypted_response["data"]["files"][i]["name"] 
	     
	        if files_type == "application/vnd.google-apps.folder": pass
	        else:
	            direct_download_link = url + urllib.parse.quote(files_name)
	            ex = f"{direct_download_link}"
	            #app.send_message(text = ex,context.bot, update.message)
    
  
	            results= f"{direct_download_link}"
	            result.append(results)
	           
	            
	            
      return result
	        
	
def main(url, username="none", password="none"):
	x = 0
	payload = {"page_token":next_page_token, "page_index": x}	
	print(f"Index Link: {url}\n\n")
	a = func(payload, url, username, password)
	return a 
	while next_page == True:
		payload = {"page_token":next_page_token, "page_index": x}
		print(func(payload, url, username, password))
		x += 1
                         
index_handler = CommandHandler(BotCommands.IndexCommand, index, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
                         
dispatcher.add_handler(index_handler)
