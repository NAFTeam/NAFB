from naff import Extension, slash_command, InteractionContext, slash_option


class Fun(Extension):
    @slash_command(
        name="how_many", description="How many users have [text] in their name"
    )
    @slash_option("text", "The text to search with", opt_type=3, required=True)
    async def how_many(self, ctx: InteractionContext, text: str):
        count = sum(
            text.strip().lower() in member.display_name.lower()
            for member in ctx.guild.members
        )
        await ctx.send(
            f"{count} member{' has' if count == 1 else 's have'} `{text}` in their name."
        )


def setup(bot):
    Fun(bot)
