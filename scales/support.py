from dis_snek.models.application_commands import slash_command
from dis_snek.models.command import message_command
from dis_snek.models.context import MessageContext, InteractionContext
from dis_snek.models.discord_objects.components import Button
from dis_snek.models.enums import ButtonStyles, AutoArchiveDuration, ChannelTypes
from dis_snek.models.listener import listen
from dis_snek.models.scale import Scale

thread_channel_id = 901576539941007400


class Support(Scale):
    @message_command()
    async def init(self, ctx: MessageContext):
        if ctx.author.id == 174918559539920897:
            await ctx.message.delete()
            await ctx.send(
                "To get some support with this library, please press the button below.",
                components=[
                    Button(
                        style=ButtonStyles.BLURPLE,
                        label="Create Support Thread",
                        custom_id="create_support_thread",
                        emoji="❔",
                    )
                ],
            )

    async def create_thread(self, ctx: InteractionContext):
        channel = await self.bot.get_channel(thread_channel_id)

        thread = await channel.create_thread_without_message(
            name=f"{ctx.author.display_name}'s Support Thread",
            auto_archive_duration=AutoArchiveDuration.ONE_HOUR,
            reason="Bot Support Thread",
            thread_type=ChannelTypes.GUILD_PUBLIC_THREAD,
        )
        await thread.send(
            f"Hi {ctx.author.mention}. Welcome to your support thread! Please explain your issue here "
            f"(with tracebacks where appropriate), and someone will help you shortly."
        )
        await ctx.send(
            f"Your support thread has been created here: {thread.mention}",
            ephemeral=True,
        )

    @listen()
    async def on_button(self, b):
        ctx = b.context
        if ctx.custom_id == "create_support_thread":
            await ctx.defer(ephemeral=True)
            await self.create_thread(ctx)

    @slash_command(
        "support-thread",
        sub_cmd_name="start",
        sub_cmd_description="Start a support thread",
    )
    async def support_start(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)
        await self.create_thread(ctx)


def setup(bot):
    Support(bot)
