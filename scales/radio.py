import asyncio

from naff import Extension, listen, GuildVoice
from naff.api.events import VoiceStateUpdate
from naff_link.client import Client as LinkClient


class Radio(Extension):
    @listen()
    async def on_startup(self):
        self.naff_link = await LinkClient.initialize(self.bot)
        await self.naff_link.connect_to("lavalink", 2333, "youshallnotpass")

    @listen()
    async def on_voice_state_update(self, event: VoiceStateUpdate):
        channel_id = event.before.channel.id if event.before else event.after.channel.id
        channel = self.bot.get_channel(channel_id)
        member = event.before.member if event.before else event.after.member

        if member.id != self.bot.user.id:
            if channel.name == "lofi-radio":
                vc = self.bot.get_bot_voice_state(channel.guild.id)
                if not vc and event.after is not None:
                    return await self.start_radio(channel)
                else:
                    asyncio.create_task(self.should_leave(channel))

    @listen()
    async def on_stats_update(self, event):
        self.latest_stats = event.stats

    @listen()
    async def on_player_update(self, event):
        self.player_state = event.state

    async def start_radio(self, channel: GuildVoice):
        vc = await self.naff_link.voice_connect(channel, channel.guild)
        await vc.play("https://www.youtube.com/watch?v=jfKfPfyJRdk")

    async def should_leave(self, channel: GuildVoice):
        await asyncio.sleep(5)
        if len(channel.voice_members) == 1:
            if vc := self.bot.get_bot_voice_state(channel.guild.id):
                await vc.disconnect()


def setup(bot):
    Radio(bot)
