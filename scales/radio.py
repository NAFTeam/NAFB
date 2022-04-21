import asyncio
from typing import Optional

from dis_snek import Scale, GuildVoice, listen
from dis_snek.api.events import VoiceStateUpdate
from dis_snek.api.voice.audio import AudioVolume
from dis_snek.client.utils import find
from yt_dlp import YoutubeDL

ytdl = YoutubeDL(
    {
        "format": "bestaudio/best",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",  # noqa: S104
    }
)


class YTDLAudio(AudioVolume):
    """An audio object to play sources supported by YTDLP"""

    def __init__(self, src) -> None:
        super().__init__(src)
        self.entry: Optional[dict] = None

    @classmethod
    async def from_url(cls, url, stream=True) -> "YTDLAudio":
        """Create this object from a YTDL support url."""
        data = await asyncio.to_thread(
            lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)

        new_cls = cls(filename)

        if stream:
            new_cls.ffmpeg_before_args = (
                "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            )

        new_cls.entry = data
        return new_cls


class Radio(Scale):
    async def async_start(self):
        for guild in self.bot.guilds:
            if channel := find(
                lambda c: c.name == "lofi-radio" and len(c.voice_members) != 0,
                guild.channels,
            ):
                asyncio.create_task(self.start_radio(channel))

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

    async def start_radio(self, channel: GuildVoice):
        vc = await channel.connect(deafened=True)
        await vc.play(
            await YTDLAudio.from_url("https://www.youtube.com/watch?v=5qap5aO4i9A")
        )

    async def should_leave(self, channel: GuildVoice):
        await asyncio.sleep(5)
        if len(channel.voice_members) == 1:
            if vc := self.bot.get_bot_voice_state(channel.guild.id):
                await vc.disconnect()


def setup(bot):
    Radio(bot)
