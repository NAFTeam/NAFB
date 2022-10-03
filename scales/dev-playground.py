import asyncio

from naff import (
    Extension,
    InteractionContext,
    slash_command,
    GuildCategory,
    slash_option,
    SlashCommandChoice,
    ChannelTypes,
    OptionTypes,
    MessageableMixin,
    Guild,
)
from naff.client.errors import HTTPException

CHANNEL_TYPE_CHOICES = [
    SlashCommandChoice(c.name, int(c))
    for c in ChannelTypes
    if c not in (1, 3, 4, 10, 11, 12)
]


class DevPlayground(Extension):
    @property
    def test_category(self) -> GuildCategory:
        return self.bot.get_channel(1026435541903884369)

    @property
    def dev_guild(self) -> Guild:
        return self.bot.get_guild(701347683591389185)

    @slash_command("dev", scopes=[701347683591389185])
    async def dev_playground(self, ctx: InteractionContext):
        await ctx.send("Hello, world!")

    @dev_playground.subcommand(
        "create_test_channel", sub_cmd_description="Create a temporary testing channel"
    )
    @slash_option(
        "type",
        "The type of channel to create",
        opt_type=OptionTypes.INTEGER,
        choices=CHANNEL_TYPE_CHOICES,
        required=True,
    )
    async def create_text_channel(self, ctx: InteractionContext, type: int):
        await ctx.defer()
        channel_type = ChannelTypes(type)
        channel = await self.test_category.create_channel(
            channel_type, f"test-{ctx.author.id}"
        )
        await ctx.send(
            f"`{str(channel_type).split('.')[-1]}::`{channel.mention} has been created for you"
        )
        if isinstance(channel, MessageableMixin):
            try:
                await channel.send(ctx.author.mention)
            except HTTPException:
                pass

    @dev_playground.subcommand(
        "complete_testing", sub_cmd_description="Delete all of your tesitng channels"
    )
    async def complete_testing(self, ctx: InteractionContext):
        await ctx.defer()
        channels = [c for c in self.dev_guild.channels if str(ctx.author.id) in c.name]
        msg = await ctx.send(f"Deleting `{len(channels)}` testing channels")

        await asyncio.gather(*[c.delete() for c in channels])

        await msg.edit(f"Deleted `{len(channels)}` testing channels")


def setup(bot):
    DevPlayground(bot)
