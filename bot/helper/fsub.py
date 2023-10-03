from asyncio import sleep
from datetime import datetime, timedelta, timezone
from time import time
from re import match as re_match

from pyrogram.errors import (FloodWait, PeerIdInvalid, RPCError,
                             UserNotParticipant)
from pyrogram.types import ChatPermissions
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot import DATABASE_URL, LOGGER
from bot.helper.ext_utils.db_handler import DbManger
from bot.helper.telegram_helper.message_utils import forcesub

async def forcesub(message, ids, button=None):
    join_button = {}
    _msg = ''
    for channel_id in ids.split():
        if channel_id.startswith('-100'):
            channel_id = int(channel_id)
        elif channel_id.startswith('@'):
            channel_id = channel_id.replace('@', '')
        else:
            continue
        try:
            chat = await message._client.get_chat(channel_id)
        except PeerIdInvalid as e:
            LOGGER.error(f"{e.NAME}: {e.MESSAGE} for {channel_id}")
            continue
        try:
            await chat.get_member(message.from_user.id)
        except UserNotParticipant:
            if username := chat.username:
                invite_link = f"https://t.me/{username}"
            else:
                invite_link = chat.invite_link
            join_button[chat.title] = invite_link
        except RPCError as e:
            LOGGER.error(f"{e.NAME}: {e.MESSAGE} for {channel_id}")
        except Exception as e:
            LOGGER.error(f'{e} for {channel_id}')
    if join_button:
        if button is None:
            button = ButtonMaker()
        _msg = f"You need to join our channel to use me."
        for key, value in join_button.items():
            button.ubutton(f'{key}', value, 'footer')
    return _msg, button

    msg = []
    if filtered := await message_filter(message):
        msg.append(filtered)
    button = None
    if message.chat.type != message.chat.type.PRIVATE:
            if ids := FSUB_IDS
                _msg, button = await forcesub(message, ids, button)
                if _msg:
                    msg.append(_msg)
    return msg, button
