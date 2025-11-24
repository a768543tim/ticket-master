import logging
import asyncio
import telegram
import traceback

logging.getLogger('telegram').setLevel(logging.CRITICAL)
logging.getLogger('telegram.bot').setLevel(logging.CRITICAL)
# ==================================================================================================================================================================
# https://api.telegram.org/botToken/getUpdates

class Telegram_Notify(object):

    def __init__(self):
        super(Telegram_Notify, self).__init__()
        self.bot_token_dict = {
                               "Stable": "1697912885:AAGYkloTCw0Kfm_KteBHDxjyg0YUq1PvXLE",
                               "MessageAss": "7562690964:AAHMIrGsvgFNNoPkSbagczbIGdeLHAmjOi0",
                              }
        self.chat_id_dict = {
                             "TimKuo": "1075765570",
                             "Test_Chat": "-760599970",
                             "Stable": "-1002221160891",
                             "CDET_Alert": "-4685035867",
                             "CDET_Annou": "-4701825632",
                            }
        self.user_id_dict = {
                             "TimKuo": "1075765570",
                             "Allen": "5288197386",
                             "Gavin": "852055634",
                             "Derrick": "999620195",
                             "Celia": "1358850325"
                            }
        self.user_name_dict = {
                               "TimKuo": "a768543_timkuo",
                               "Allen": "allenkuo0613",
                               "Gavin": "gavinchen04",
                               "Derrick": "adcwe",
                               "Celia": "wei933"
                              }

    async def sendMessage(self, message, chat_name, bot_name="MessageAss"):
        try:
            bot_token = self.bot_token_dict[bot_name]
            chat_id = self.chat_id_dict[chat_name]
            bot = telegram.Bot(token=bot_token)
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
        except:
            pass
            # traceback.print_exc()

    async def sendPhoto(self, photo_url, chat_name, bot_name="MessageAss"):
        try:
            bot_token = self.bot_token_dict[bot_name]
            chat_id = self.chat_id_dict[chat_name]
            bot = telegram.Bot(token=bot_token)
            with open(photo_url, "rb") as photo:
                await bot.sendPhoto(chat_id=chat_id, photo=photo)
        except:
            traceback.print_exc()

    async def sendFile(self, document_url, chat_name, bot_name="MessageAss"):
        try:
            bot_token = self.bot_token_dict[bot_name]
            chat_id = self.chat_id_dict[chat_name]
            bot = telegram.Bot(token=bot_token)
            with open(document_url, "rb") as document:
                bot.sendDocument(chat_id, document=document)
        except:
            traceback.print_exc()

    async def echoMessage(self, message, user_list, chat_name, bot_name="MessageAss"):
        try:
            bot_token = self.bot_token_dict[bot_name]
            chat_id = self.chat_id_dict[chat_name]
            mention_msg = ""
            for user in user_list:
                user_id = self.user_id_dict[user]
                user_name = self.user_name_dict[user]
                mention = "["+user_name+"](tg://user?id="+str(user_id)+")"
                mention_msg += mention + " "
            tag_message = f"{message}\n{mention_msg}"
            # print(tag_message)
            bot = telegram.Bot(token=bot_token)
            await bot.sendMessage(chat_id=chat_id, text=tag_message, parse_mode="Markdown")
        except:
            pass

tg_notify = Telegram_Notify()


async def main():
    await tg_notify.sendMessage("🚀 Test message from async bot!", chat_name="TimKuo")


if __name__ == "__main__":
    asyncio.run(main())
