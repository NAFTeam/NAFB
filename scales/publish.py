from naff.models import Extension, listen, GuildNews, Message


class Publish(Extension):
    @listen()
    async def on_message_create(self, event):
        message: Message = event.message
        if isinstance(message.channel, GuildNews):
            try:
                await message.publish()
            except Exception:
                print("publish failed")
                pass
            else:
                await message.add_reaction("📣")


def setup(bot):
    Publish(bot)
