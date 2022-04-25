from dis_snek import (
    Scale,
    listen,
    Embed,
    BrandColors,
    Message,
    TimestampStyles,
    Role,
    Timestamp,
)
from dis_snek.api.events import MemberUpdate, MemberAdd, MemberRemove, BaseEvent
from dis_snek.ext.debug_scale import strf_delta


class Logging(Scale):
    ...

    @staticmethod
    def base_embed(event: BaseEvent) -> Embed:
        title = event.resolved_name.replace("on_", "").replace("_", " ").title()
        embed = Embed(title=title, color=BrandColors.BLURPLE)

        return embed

    async def send_embed(self, embed: Embed) -> Message:
        channel = await self.bot.fetch_channel(968256006645751808)
        return await channel.send(embeds=embed)

    @listen()
    async def on_member_update(self, event: MemberUpdate):
        before = event.before
        after = event.after

        if (
            before.display_name == after.display_name and before.roles == after.roles
        ) or (after is None or before is None):
            # filter events
            return None

        emb = self.base_embed(event)
        emb.set_thumbnail(url=after.display_avatar.url)
        emb.set_author(name=after.tag, icon_url=after.display_avatar.url)

        if before.display_name != after.display_name:
            emb.add_field(name="Old Display Name", value=before.display_name)
            emb.add_field(name="New Display Name", value=after.display_name)

        if before.roles != after.roles:
            new_roles: list[Role] = []
            removed_roles: list[Role] = []

            # search for removed roles
            for role in before.roles:
                if role not in after.roles:
                    removed_roles.append(role)

            # search for added roles
            for role in after.roles:
                if role not in before.roles:
                    new_roles.append(role)

            if new_roles:
                emb.add_field(
                    name="New Roles", value="\n".join(r.name for r in new_roles)
                )
            if removed_roles:
                emb.add_field(
                    name="Removed Roles", value="\n".join(r.name for r in removed_roles)
                )

        await self.send_embed(emb)

    @listen()
    async def on_member_add(self, event: MemberAdd):
        emb = self.base_embed(event)
        emb.color = BrandColors.GREEN
        emb.set_author(name=event.member.tag, icon_url=event.member.display_avatar.url)
        emb.add_field(name="📅 Account Creation", value=event.member.created_at)
        emb.add_field(
            name="🕐 Account Age",
            value=event.member.created_at.format(TimestampStyles.RelativeTime),
        )
        emb.set_thumbnail(event.member.display_avatar.url)
        await self.send_embed(emb)

    @listen()
    async def on_member_remove(self, event: MemberRemove):
        emb = self.base_embed(event)
        emb.color = BrandColors.RED
        emb.set_thumbnail(url=event.member.display_avatar.url)
        emb.set_author(name=event.member.tag, icon_url=event.member.display_avatar.url)

        emb.add_field(name="📅 Account Creation", value=event.member.created_at)
        emb.add_field(
            name="⏰ Left After",
            value=strf_delta(Timestamp.utcnow() - event.member.joined_at),
        )
        await self.send_embed(emb)


def setup(bot):
    Logging(bot)
