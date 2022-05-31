import aiohttp
from naff.client.errors import CommandCheckFailure
from naff.models import (
    Extension,
    prefixed_command,
    PrefixedContext,
    check,
    Context,
)


def is_owner():
    """
    Is the author the owner of the bot.

    parameters:
        coro: the function to check
    """

    async def check(ctx: Context) -> bool:
        return ctx.author.id == 174918559539920897

    return check


class Admin(Extension):
    @prefixed_command()
    @check(is_owner())
    async def set_avatar(self, ctx: PrefixedContext):
        if not ctx.message.attachments:
            return await ctx.send(
                "There was no image to use! Try using that command again with an image"
            )
        async with aiohttp.ClientSession() as session:
            async with session.get(ctx.message.attachments[0].url) as r:
                if r.status == 200:
                    data = await r.read()
                    await self.bot.user.edit(avatar=data)
                    return await ctx.send("Set avatar, how do i look? 😏")
        await ctx.send("Failed to set avatar 😔")

    @set_avatar.error
    async def avatar_error(self, error, ctx):
        if isinstance(error, CommandCheckFailure):
            await ctx.send("You do not have permission to use this command!")


def setup(bot):
    Admin(bot)
