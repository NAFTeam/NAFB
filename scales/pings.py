import attrs
from naff import Extension, slash_command, InteractionContext


@attrs.define()
class PingObject:
    id: int = attrs.field()
    description: str = attrs.field()
    added_message: str | None = attrs.field(default=None)
    removed_message: str | None = attrs.field(default=None)


class Pings(Extension):
    def __init__(self, bot):
        self.ping_roles: dict[str, PingObject] = {
            "lib-news": PingObject(
                923682774915883028, "Get notified about library news"
            ),
            "guild-news": PingObject(
                981173285880475658, "Get notified about guild news"
            ),
            "polls": PingObject(
                929787105134133269, "Get notified when a poll is posted"
            ),
        }

        for name, data in self.ping_roles.items():
            cmd = self.ping.subcommand(name, sub_cmd_description=data.description)(
                self.template_cmd
            )
            self.bot.add_interaction(cmd)

    @slash_command(name="ping", description="Get notifications about guild events")
    async def ping(self, ctx: InteractionContext):
        ...

    async def template_cmd(self, ctx: InteractionContext):
        ping = ctx.invoke_target.split()[-1]
        data = self.ping_roles[ping]

        if ctx.author.has_role(data.id):
            await ctx.author.remove_role(data.id, "User requested to remove role")
            return await ctx.send(
                data.removed_message or f"{ping} role has been removed", ephemeral=True
            )
        else:
            await ctx.author.add_role(data.id, "User requested to add role")
            return await ctx.send(
                data.added_message or f"{ping} role has been added", ephemeral=True
            )


def setup(bot):
    Pings(bot)
