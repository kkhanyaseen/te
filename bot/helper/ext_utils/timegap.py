import time

from bot import TIME_GAP, TIME_GAP_STORE
from bot.helper.ext_utils.bot_utils import timeformatter

def timegap_check(message):
  if message.from_user.id in TIME_GAP_STORE:
    if int(time.time() - TIME_GAP_STORE[message.from_user.id]) < TIME_GAP:
      wtime = timeformatter((int(TIME_GAP_STORE[message.from_user.id]) + TIME_GAP - int(time.time())) * 1000)
      if message.from_user.username:
          uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.username}</a>'
      else:
          uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
      text = f"{uname} You Have To Wait For {wtime}s. Normal Users have Time Restriction For {TIME_GAP}s"
      message.reply_text(
                text=text,
                parse_mode="html",
                quote=True
            )
      return True 
    else:
      del TIME_GAP_STORE[message.from_user.id]
      return False
  else:
    return False
