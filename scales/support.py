import textwrap

from dis_snek import (
    message_command,
    Scale,
    MessageContext,
    Button,
    ButtonStyles,
    InteractionContext,
    AutoArchiveDuration,
    slash_command,
    component_callback,
    ComponentContext,
    Modal,
    ParagraphText,
    ModalContext,
)
from dis_snek.models.snek.application_commands import modal_callback

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

    @modal_callback("support_thread_modal")
    async def create_thread(self, ctx: ModalContext):
        await ctx.defer(ephemeral=True)

        channel = await self.bot.fetch_channel(thread_channel_id)
        description = ctx.responses.get("description")
        code = ctx.responses.get("code")
        traceback = ctx.responses.get("traceback")
        additional = ctx.responses.get("additional")

        if code and "```" not in code:
            code = f"```py\n{textwrap.dedent(code)}```"
        if traceback and "```" not in traceback:
            traceback = f"```py\n{textwrap.dedent(traceback)}```"

        thread = await channel.create_public_thread(
            name=f"{ctx.author.display_name}'s Support Thread",
            auto_archive_duration=AutoArchiveDuration.ONE_HOUR,
            reason="Bot Support Thread",
        )
        await thread.send(
            f"Welcome to your support thread {ctx.author.mention} - Someone will help you shortly"
        )
        await thread.send(f"**Provided information:**\n{description}")
        if code:
            await thread.send(f"**Code Sample:**\n{code}")
        if traceback:
            await thread.send(f"**Traceback:**\n{traceback}")
        if additional:
            await thread.send(f"**Additional:**\n{additional}")
        await ctx.send(
            f"Your support thread has been created here: {thread.mention}",
            ephemeral=True,
        )

    @component_callback("create_support_thread")
    async def support_thread_button(self, ctx: ComponentContext):
        await ctx.send_modal(
            Modal(
                "Support Thread Wizard",
                custom_id="support_thread_modal",
                components=[
                    ParagraphText(
                        label="Describe Your Problem",
                        custom_id="description",
                        placeholder="Please provide a summary of your problem",
                        required=True,
                    ),
                    ParagraphText(
                        label="Relevant Code",
                        custom_id="code",
                        placeholder="If you have example code put it here",
                        required=False,
                    ),
                    ParagraphText(
                        label="Traceback",
                        custom_id="traceback",
                        placeholder="If you have a traceback put it here",
                        required=False,
                    ),
                    ParagraphText(
                        label="Additional Information",
                        custom_id="additional",
                        placeholder="Anything else? Put it here",
                        required=False,
                    ),
                ],
            )
        )

    @slash_command(
        "support-thread",
        sub_cmd_name="start",
        sub_cmd_description="Start a support thread",
    )
    async def support_start(self, ctx: InteractionContext):
        await self.support_thread_button(ctx)


def setup(bot):
    Support(bot)
