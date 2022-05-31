import asyncio
import logging
from pathlib import Path

import naff
from naff import Client, Intents, listen, slash_command, InteractionContext

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
            debug_scope=870046872864165888,
            fetch_members=True,
        )

    @listen()
    async def on_ready(self):
        print(f"{bot.user} logged in")

    @slash_command(
        name="news_ping",
        description="Get mentioned whenever news is posted",
        scopes=[701347683591389185],
    )
    async def news_ping(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)
        ping_id = 923682774915883028
        if ctx.author.has_role(ping_id):
            await ctx.author.remove_role(ping_id, "User requested to remove role")
            return await ctx.send("The news ping role has been removed", ephemeral=True)
        else:
            await ctx.author.add_role(ping_id, "User requested to add role")
            return await ctx.send("The news ping role has been added", ephemeral=True)

    @slash_command(
        name="poll_ping",
        description="Get mentioned whenever polls are posted",
        scopes=[701347683591389185],
    )
    async def poll_ping(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)
        ping_id = 929787105134133269
        if ctx.author.has_role(ping_id):
            await ctx.author.remove_role(ping_id, "User requested to remove role")
            return await ctx.send("The poll ping role has been removed", ephemeral=True)
        else:
            await ctx.author.add_role(ping_id, "User requested to add role")
            return await ctx.send("The poll ping role has been added", ephemeral=True)

    @slash_command(
        name="satisfactory_ping",
        description="Get mentioned for satisfactory related content",
        scopes=[701347683591389185],
    )
    async def satisfactory_ping(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)
        ping_id = 968418694285905930
        if ctx.author.has_role(ping_id):
            await ctx.author.remove_role(ping_id, "User requested to remove role")
            return await ctx.send(
                "The Satisfactory ping role has been removed", ephemeral=True
            )
        else:
            await ctx.author.add_role(ping_id, "User requested to add role")
            return await ctx.send(
                "The Satisfactory ping role has been added", ephemeral=True
            )


bot = Bot()
bot.g_id = 701347683591389185


bot.load_extension("scales.support")
bot.load_extension("scales.githubMessages")
bot.load_extension("scales.tictactoe")
bot.load_extension("scales.admin")
bot.load_extension("naff.ext.debug_extension")
bot.load_extension("scales.tags")
bot.load_extension("scales.publish")
bot.load_extension("scales.guild_logging")
bot.load_extension("scales.fun")
bot.load_extension("scales.radio")
bot.load_extension("scales.pings")

asyncio.run(bot.astart((Path(__file__).parent / "token.txt").read_text().strip()))
