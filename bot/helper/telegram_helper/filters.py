from telegram.ext import MessageFilter
from telegram import Message
from bot import AUTHORIZED_CHATS, SUDO_USERS, OWNER_ID, getLogger
from bot.helper.ext_utils.bot_utils import is_magnet, is_url

logger = getLogger(__name__)


class CustomFilters:
    class __OwnerFilter(MessageFilter):
        def filter(self, message: Message):
            return message.from_user.id == OWNER_ID

    owner_filter = __OwnerFilter()

    class __AuthorizedUserFilter(MessageFilter):
        def filter(self, message: Message):
            uid = message.from_user.id
            return uid in AUTHORIZED_CHATS or uid in SUDO_USERS or uid == OWNER_ID

    authorized_user = __AuthorizedUserFilter()

    class __AuthorizedChat(MessageFilter):
        def filter(self, message: Message):
            return message.chat.id in AUTHORIZED_CHATS

    authorized_chat = __AuthorizedChat()

    class __SudoUser(MessageFilter):
        def filter(self, message: Message):
            return message.from_user.id in SUDO_USERS

    sudo_user = __SudoUser()

    class _DetectTorrentsAndMagnets(MessageFilter):
        def filter(self, message: Message):
            
            if message.edit_date:
                logger.info("Edited msg")
                return

            if message.document and '.torrent' in message.document.file_name:
                a = True
            elif message.text:
                if is_magnet(message.text):
                    a = True
                elif is_url(message.text):
                    a = True
                else:
                    return False
            else:
                return False

            if message.chat.id in AUTHORIZED_CHATS:
                b = True
            elif message.chat.type != "channel":
                if message.from_user.id in (AUTHORIZED_CHATS, SUDO_USERS):
                    b =  True
                elif message.from_user.id == OWNER_ID:
                    b = True
                else:
                    return False
            else:
                return False
            return a and b

    detect_torrent_and_magnets = _DetectTorrentsAndMagnets()

    @staticmethod
    def _owner_query(user_id):
        return user_id == OWNER_ID or user_id in SUDO_USERS
