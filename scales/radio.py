import asyncio

from naff import Extension, listen, GuildVoice
from naff.api.events import VoiceStateUpdate
from naff_link import NaffLink


class Radio(Extension):
    def __init__(self, _):
        self.bot.load_extension("naff_link")
        self.naff_link: NaffLink = self.bot.naff_link

    @listen()
    async def on_startup(self):
        self.naff_link.add_node("localhost", 2333, "youshallnotpass", "eu")

    @listen()
    async def on_voice_state_update(self, event: VoiceStateUpdate):

        channel_id = event.before.channel.id if event.before else event.after.channel.id
        latest_channel = self.bot.get_channel(channel_id)
        member = event.before.member if event.before else event.after.member

        if member.id == self.bot.user.id:
            return

        if latest_channel.name == "lofi-radio":
            vc_player = self.naff_link.get_player(latest_channel.guild)
            if (not vc_player or not vc_player.is_connected) and event.after:
                return await self.start_radio(latest_channel)
            else:
                asyncio.create_task(self.should_leave(latest_channel))

    async def start_radio(self, channel: GuildVoice):
        await self.naff_link.ready.wait()
        vc_player = await self.naff_link.connect_to_vc(channel.guild, channel)

        results = await self.naff_link.get_tracks(
            "https://www.youtube.com/watch?v=jfKfPfyJRdk"
        )
        await vc_player.play(results.tracks[0])

    async def should_leave(self, channel: GuildVoice):
        await asyncio.sleep(5)
        if len(channel.voice_members) == 1:
            if channel.voice_members[0].id == self.bot.user.id:
                await self.naff_link.disconnect(channel.guild)

    @listen()
    async def on_queue_end_event(self, event):
        await self.start_radio(event.player.channel)


def setup(bot):
    Radio(bot)
