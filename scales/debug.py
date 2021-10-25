import platform

from dis_snek.const import __version__, __py_version__
from dis_snek.models import slash_command, InteractionContext, Embed
from dis_snek.models.enums import Intents
from dis_snek.models.scale import Scale
from dis_snek.utils.cache import TTLCache


class DebugScale(Scale):
    # def __init__(self, bot):
    #     self.add_scale_check(self.check)
    #
    # @staticmethod
    # async def check(ctx):
    #     return ctx.author.id == 174918559539920897

    @slash_command(
        "debug",
        sub_cmd_name="info",
        sub_cmd_description="Get basic information about the bot",
    )
    async def debug_info(self, ctx: InteractionContext):
        e = Embed("Dis-Snek Debug Information")
        e.add_field("Operating System", platform.platform())

        e.add_field("Version Info", f"Dis-Snek@{__version__} | Py@{__py_version__}")

        privileged_intents = [
            i.name for i in self.bot.intents if i in Intents.PRIVILEGED
        ]
        if privileged_intents:
            e.add_field("Privileged Intents", " | ".join(privileged_intents))

        e.add_field("Loaded Scales", ", ".join(self.bot.scales))

        e.add_field("Guilds", str(len(self.bot.guilds)))

        e.set_footer(self.bot.user.username, icon_url=self.bot.user.avatar.url)
        await ctx.send(embeds=[e])

    @debug_info.subcommand(
        "cache", sub_cmd_description="Get information about the current cache state"
    )
    async def cache_info(self, ctx: InteractionContext):
        e = Embed("Dis-Snek Cache Information", "")
        caches = [
            "channel_cache",
            "dm_channels",
            "guild_cache",
            "member_cache",
            "message_cache",
            "role_cache",
            "user_cache",
        ]

        for cache in caches:
            val = getattr(self.bot.cache, cache)
            if isinstance(val, TTLCache):
                e.description += f"\n`{cache}`: {len(val)} / {val.hard_limit}({val.soft_limit}) ttl:`{val.ttl}`s"
            else:
                e.description += f"\n`{cache}`: {len(val)} / ∞ (no_expire)"

        e.set_footer(self.bot.user.username, icon_url=self.bot.user.avatar.url)
        await ctx.send(embeds=[e])


def setup(bot):
    DebugScale(bot)
