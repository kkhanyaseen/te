import requests, json
from re import split as re_split
from time import sleep, time
from datetime import timedelta, datetime
from threading import Thread
from telegram.ext import CommandHandler, CallbackQueryHandler

from bot import *
from bot.helper.ext_utils.bot_utils import get_user_task, check_duration, is_jc_link
from bot.helper.ext_utils.timegap import timegap_check
from bot.helper.mirror_utils.download_utils.aria2_download import add_aria2c_download
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, delete_all_messages, update_all_messages, auto_delete_upload_message, auto_delete_message, sendLinksLog, editMessage
from bot.helper.telegram_helper.button_build import ButtonMaker
from .listener import MirrorLeechListener

listener_dict = {}

META_URL = "https://prod.media.jio.com/apis/common/v3/metamore/get/"
def get_metadata(VideoID):
  response = requests.get(url = META_URL + VideoID, headers = {'os': 'Android'})
  return json.loads(response.text)

def _jcdl(bot, message, isZip=False, extract=False, isQbit=False, isLeech=False):
    if BOT_PM:
      try:
        msg1 = f'Added your Requested Link to Downloads'
        send = bot.sendMessage(message.from_user.id, text=msg1, )
        send.delete()
      except Exception as e:
        LOGGER.warning(e)
        bot_d = bot.get_me()
        b_uname = bot_d.username
        uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
        buttons = ButtonMaker()
        buttons.buildbutton("Start Me", f"http://t.me/{b_uname}")
        buttons.buildbutton("Updates Channel", "http://t.me/BaashaXclouD")
        reply_markup = buttons.build_menu(2)
        message = sendMarkup(f"Hey Bro {uname}👋,\n\n<b>I Found That You Haven't Started Me In PM Yet 😶</b>\n\nFrom Now on i Will links in PM Only 😇", bot, message, reply_markup=reply_markup)     
        return
    try:
        user = bot.get_chat_member(f"{FSUB_CHANNEL_ID}", message.from_user.id)
        LOGGER.error(user.status)
        if user.status not in ('member','creator','administrator'):
            buttons = ButtonMaker()
            buttons.buildbutton("Join Updates Channel", "https://t.me/BaashaXclouD")
            reply_markup = buttons.build_menu(1)
            sendMarkup(f"<b>⚠️You Have Not Joined My Updates Channel</b>\n\n<b>Join Immediately to use the Bot.</b>", bot, message, reply_markup)
            return
    except:
        pass

    total_task = len(download_dict)
    user_id = message.from_user.id
    if message.from_user.username:
        uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.username}</a>'
    else: 
        uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
	
    edate = DURATION_DICT.get(user_id, "")
    if user_id != OWNER_ID and user_id not in SUDO_USERS:
        expiration_date = datetime.strptime(edate, "%Y-%m-%d")
        current_date = datetime.now()
        expiry_days = (expiration_date - current_date).days
        if expiry_days == 0:
            bot.restrict_chat_member(chat_id=message.chat_id, user_id=user_id, permissions=ChatPermissions(False))
            return sendMessage(f"<b>{uname} is Restrict for send Message in This Group. Due to Paid End.</b>", bot, message)
        if expiry_days < 0:
            bot.kick_chat_member(chat_id=message.chat_id, user_id=user_id, until_date=None)
            return sendMessage(f"<b>{uname} is Kicked in This Group. Due to Paid Not Renewed.</b>", bot, message)

    if user_id != OWNER_ID and user_id not in SUDO_USERS:
            if TOTAL_TASKS_LIMIT == total_task:
                return sendMessage(f"<b>Bot Total Task Limit : {TOTAL_TASKS_LIMIT}\nTasks Processing : {total_task}\n#TotalLimitExceeded\n\nTo avoid Overload</b>", bot ,message)
            if USER_TASKS_LIMIT == get_user_task(user_id):
                return sendMessage(f"<b>User Total Limit : {USER_TASKS_LIMIT}\nYour Tasks : {get_user_task(user_id)}\n#UserLimitExceeded\n\nTo avoid Overload</b>", bot ,message)
    mesg = message.text.split('\n')
    message_args = mesg[0].split(maxsplit=1)
    name_args = mesg[0].split('|', maxsplit=1)
    is_gdtot = False
    is_unified = False
    index = 1
    ratio = None
    seed_time = None
    select = False
    seed = False
    multi = 0
    uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    uid= f"<a>{message.from_user.id}</a>"
    msg_id = message.message_id

    if len(message_args) > 1:
        args = mesg[0].split(maxsplit=3)
        for x in args:
            x = x.strip()
            if x == 's':
               select = True
               index += 1
            elif x == 'd':
                seed = True
                index += 1
            elif x.startswith('d:'):
                seed = True
                index += 1
                dargs = x.split(':')
                ratio = dargs[1] if dargs[1] else None
                if len(dargs) == 3:
                    seed_time = dargs[2] if dargs[2] else None
            elif x.isdigit():
                multi = int(x)
                mi = index
        if multi == 0:
            message_args = mesg[0].split(maxsplit=index)
            if len(message_args) > index:
                link = message_args[index].strip()
                if link.startswith(("|", "pswd:")):
                    link = ''
            else:
                link = ''
        else:
            link = ''
    else:
        link = ''

    if len(name_args) > 1:
        name = name_args[1]
        name = name.split(' pswd:')[0]
        name = name.strip()
    else:
        name = ''

    link = re_split(r"pswd:|\|", link)[0]
    link = link.strip()

    pswd_arg = mesg[0].split(' pswd: ')
    if len(pswd_arg) > 1:
        pswd = pswd_arg[1]
    else:
        pswd = None

    if message.from_user.username:
        tag = f"@{message.from_user.username}"
    else:
        tag = message.from_user.mention_html(message.from_user.first_name)

    reply_to = message.reply_to_message
    if reply_to is not None:
        Thread(target=auto_delete_upload_message, args=(bot, message, reply_to)).start()
        file_ = reply_to.document or reply_to.video or reply_to.audio or reply_to.photo or None
        if not reply_to.from_user.is_bot:
            if reply_to.from_user.username:
                tag = f"@{reply_to.from_user.username}"
            else:
                tag = reply_to.from_user.mention_html(reply_to.from_user.first_name)
            
    listener = MirrorLeechListener(bot, message, isZip, extract, isQbit, isLeech, pswd, tag, select, seed, link)

    if is_jc_link(link):
        bxq = sendMessage("<b>Processing Your Jio Cinema Link...</b>", bot, message)
        link = link.split("id=", 1)
        link = link[1]
        metadata = get_metadata(link)
        metadata['thumb'] = metadata['thumb'].strip('jio_vod').strip('/index.txt')
        link = f'{JC_KEY}'+metadata['thumb']
        sendMessage(f'{msg_id}', bot, message)
        buttons = ButtonMaker()
        buttons.sbutton("130p(112)", f"qu {msg_id} 130p(112)")
        buttons.sbutton("130p(132)", f"qu {msg_id} 130p(132)")
        buttons.sbutton("240p(248)", f"qu {msg_id} 240p(248)")
        buttons.sbutton("240p(300)", f"qu {msg_id} 240p(300)")
        buttons.sbutton("240p(464)", f"qu {msg_id} 240p(464)")
        buttons.sbutton("360p(696)", f"qu {msg_id} 360p(696)")
        buttons.sbutton("480p(896)", f"qu {msg_id} 480p(896)")
        buttons.sbutton("720p(1328)", f"qu {msg_id} 720p(1328)")
        buttons.sbutton("720p(2492)", f"qu {msg_id} 720p(2492)")
        buttons.sbutton("1080p(4192)", f"qu {msg_id} 1080p(4192)")
        buttons.sbutton("1080p(6192)", f"qu {msg_id} 1080p(6192)")
        buttons.sbutton("1080p(8192)", f"qu {msg_id} 1080p(8192)")
        buttons.sbutton("1080p(12192)", f"qu {msg_id} 1080p(12192)")
        reply_markup = buttons.build_menu(2)
        BxP = f'Select Quality You Want👇'
        mname = metadata["name"].replace(' ' ,'.')
        name = f'{mname}.{metadata["year"]}.{metadata["language"]}.'
        listener_dict[msg_id] = [listener, user_id, link, name, select, ratio, seed_time]
        sendMarkup(BxP, bot, message, reply_markup)
    else:
        sendMessage(f'Send Valid Link', bot, message)
          
def select_format(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    msg = query.message
    data = data.split(" ")
    task_id = int(data[1])
    sendMessage(f'{task_id}', bot, message)
    auth = ''
    try:
        task_info = listener_dict[task_id]
    except:
        return editMessage("This is an old task", msg)
    uid = task_info[1]
    link = task_info[2]
    listener = task_info[0]
    name = task_info[3]
    select = task_info[4]
    ratio = task_info[5]
    seed_time = task_info[6]
    if user_id != uid and not CustomFilters._owner_query(user_id):
        return query.answer(text="This task is not for you!", show_alert=True)
    elif data[2] == "130p(112)":
        link = link + "_112.mp4"
        quality = "130p"
    elif data[2] == "130p(132)":
        link = link + "_132.mp4"
        quality = "130p"
    elif data[2] == "240p(248)":
        link = link + "_248.mp4"
        quality = "240p"
    elif data[2] == "240p(300)":
        link = link + "_300.mp4"
        quality = "240p"
    elif data[2] == "240p(464)":
        link = link + "_464.mp4"
        quality = "240p"
    elif data[2] == "360p(696)":
        link = link + "_696.mp4"
        quality = "360p"
    elif data[2] == "480p(896)":
        link = link + "_896.mp4"
        quality = "480p"
    elif data[2] == "720p(1328)":
        link = link + "_1328.mp4"
        quality = "720p"
    elif data[2] == "720p(2492)":
        link = link + "_2492.mp4"
        quality = "720p"
    elif data[2] == "1080p(4192)":
        link = link + "_4192.mp4"
        quality = "1080p"
    elif data[2] == "1080p(6192)":
        link = link + "_6192.mp4"
        quality = "1080p"
    elif data[2] == "1080p(8192)":
        link = link + "_8192.mp4"
        quality = "1080p"
    elif data[2] == "1080p(12192)":
        link = link + "_12192.mp4"
        quality = "1080p"
    else:
        pass
    name = name + quality + ".JC-WEBDL.H.264-BaashaX.mp4"
    Thread(target=add_aria2c_download, args=(link, f'{DOWNLOAD_DIR}{listener.uid}', listener, name,
                                                     auth, ratio, seed_time)).start()
    query.message.delete()
    del listener_dict[task_id]

def jcxdl(update, context):
    _jcdl(context.bot, update.message)      
		
jcdl_handler = CommandHandler(BotCommands.JCDLCommand, jcxdl,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)		
quality_handler = CallbackQueryHandler(select_format, pattern="qu", run_async=True)
        
dispatcher.add_handler(quality_handler)
dispatcher.add_handler(jcdl_handler)      
