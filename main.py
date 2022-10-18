import asyncio
import logging
import os

import naff
from dotenv import load_dotenv
from naff import Client, Intents, listen

load_dotenv()

logging.basicConfig()
cls_log = logging.getLogger(naff.const.logger_name)
cls_log.setLevel(logging.DEBUG)


class Bot(Client):
    def __init__(self):
        super().__init__(
            intents=Intents.DEFAULT
            | Intents.GUILD_MEMBERS
            | Intents.GUILD_MESSAGE_CONTENT,
            sync_interactions=True,
            delete_unused_application_cmds=True,
            asyncio_debug=True,
            activity="with sneks",
            fetch_members=True,
        )

    @listen()
    async def on_ready(self):
        print(f"{bot.user} logged in")


bot = Bot()
bot.g_id = 701347683591389185


bot.load_extension("scales.support")
bot.load_extension("scales.githubMessages")
bot.load_extension("scales.tictactoe")
bot.load_extension("scales.admin")
bot.load_extension("naff.ext.debug_extension")
bot.load_extension("scales.publish")
bot.load_extension("scales.guild_logging")
bot.load_extension("scales.fun")
bot.load_extension("scales.pings")
bot.load_extension("scales.dev-playground")


if __name__ == "__main__":

    token = os.getenv("TOKEN")
    asyncio.run(bot.astart(token))
