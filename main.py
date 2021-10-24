import logging
import random

import dis_snek.const
from dis_snek.client import Snake
from dis_snek.models.color import Color
from dis_snek.models.command import message_command
from dis_snek.models.discord_objects.channel import GuildText
from dis_snek.models.discord_objects.components import ActionRow, Button
from dis_snek.models.context import (
    InteractionContext,
    ComponentContext,
    Context,
    MessageContext,
)
from dis_snek.models.discord_objects.embed import Embed
from dis_snek.models.application_commands import (
    SlashCommandOption,
    slash_command,
    context_menu,
    slash_option,
)
from dis_snek.models.enums import (
    Intents,
    CommandTypes,
    ButtonStyles,
    AutoArchiveDuration,
    ChannelTypes,
)
from dis_snek.models.events import Button as ButtonEvent
from dis_snek.models.listener import listen

logging.basicConfig()
cls_log = logging.getLogger(dis_snek.const.logger_name)
cls_log.setLevel(logging.INFO)


class Bot(Snake):
    def __init__(self):
        super().__init__(
            intents=Intents.ALL,
            sync_interactions=True,
            asyncio_debug=True,
            activity="Powered by sneks",
        )

    @listen()
    async def on_ready(self):
        print(f"{bot.user} logged in")

    @slash_command(name="info", description="Information about sneks")
    async def info(self, ctx: InteractionContext):
        emb = Embed(
            description="Dis-snek is an API Wrapper for discord, written in Python. This wrapper is in early development, as such this server acts as a place to contribute and give feedback as the wrapper matures"
        )
        emb.add_field(
            "Links:",
            value="-[GitHub](https://github.com/LordOfPolls/dis_snek)\n-[Trello](https://trello.com/b/LVjnmYKt/dev-board)",
        )
        emb.set_thumbnail(
            url="https://cdn.discordapp.com/icons/870046872864165888/c665942b7f58cc2d2720fd276ae1729e.png?size=1024"
        )
        emb.color = 16426522
        await ctx.send(embeds=emb)


bot = Bot()
bot.g_id = 701347683591389185


bot.grow_scale("scales.support")
bot.grow_scale("scales.githubMessages")
bot.grow_scale("scales.tictactoe")
bot.grow_scale("scales.admin")

bot.start("Mzc5MzQzMzIyNTQ1NzgyNzg0.WgiY_w.1Y22HfdmBB_ctZHnHrlgGtd_nZo")
