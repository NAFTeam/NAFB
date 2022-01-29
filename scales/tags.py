import datetime

import aioredis as aioredis
import attr
import orjson as orjson
from dis_snek import MISSING
from dis_snek.models import (
    Scale,
    slash_command,
    OptionTypes,
    InteractionContext,
    slash_option,
    AutocompleteContext,
    Snowflake_Type,
    to_snowflake,
)
from thefuzz import fuzz, process


def deserialize_datetime(date):
    if isinstance(date, str):
        return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
    return date


@attr.s(auto_attribs=True, on_setattr=[attr.setters.convert, attr.setters.validate])
class Tag:
    name: str = attr.ib(converter=lambda x: x.lower())
    content: str
    author_id: Snowflake_Type = attr.ib(converter=to_snowflake)
    creation: datetime = attr.ib(
        factory=datetime.datetime.now, converter=deserialize_datetime
    )


class Tags(Scale):
    def __init__(self, bot):
        self.tags = {}
        self.redis: aioredis.Redis = MISSING
        self.bot.loop.create_task(self.connect())

    async def connect(self):
        self.redis = await aioredis.from_url(
            "redis://localhost/6", decode_responses=True
        )
        try:
            await self.redis.ping()
        except:
            await self.bot.stop()
        await self.cache()

    async def cache(self):
        keys = await self.redis.keys("*")
        for key in keys:
            await self.get_tag(key)
        print(f"Cached {len(self.tags)} tags")

    async def get_tag(self, tag_name: str) -> Tag:
        if tag_name in self.tags:
            return self.tags[tag_name]
        else:
            tag_data = await self.redis.get(tag_name)
            if tag_data:
                self.tags[tag_name] = Tag(**orjson.loads(tag_data))
                return self.tags[tag_name]
        return None

    async def put_tag(self, tag: Tag):
        self.tags[tag.name] = tag
        await self.redis.set(tag.name, orjson.dumps(tag.__dict__))

    async def delete_tag(self, tag: Tag):
        self.tags.pop(tag.name, None)
        await self.redis.delete(tag.name)

    @slash_command("tag", "Send a requested tag to this channel")
    @slash_option(
        "tag_name",
        "The name of the tag you want to send",
        OptionTypes.STRING,
        required=True,
    )
    async def tag(self, ctx: InteractionContext, tag_name: str):
        tag = await self.get_tag(tag_name.lower().replace("_", " "))
        if tag:
            return await ctx.send(tag.content.encode("utf-8").decode("unicode_escape"))
        else:
            return await ctx.send(f"No tag exists called `{tag_name}`")

    @slash_command("create_tag", "Create a tag")
    @slash_option(
        "name",
        "The name of the tag you want to create",
        OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        "content",
        "The name of the tag you want to create",
        OptionTypes.STRING,
        required=True,
    )
    async def create_tag(self, ctx: InteractionContext, name: str, content: str):
        if name.lower() in self.tags.keys():
            return await ctx.send(f"`{name}` already exists")
        else:
            tag = Tag(name, content, ctx.author.id)
            await self.put_tag(tag)
            await ctx.send(f"Created `{tag.name}`")

    @slash_command("delete_tag", "Delete a tag")
    @slash_option(
        "name",
        "The name of the tag you want to delete",
        OptionTypes.STRING,
        required=True,
    )
    async def del_tag(self, ctx: InteractionContext, name: str):
        tag = await self.get_tag(name)
        if tag:
            if tag.author_id == ctx.author.id or ctx.author.has_role(
                870318611737247764
            ):
                await self.delete_tag(tag)
                return await ctx.send(f"Deleted `{tag.name}`")
            else:
                return await ctx.send(
                    "Only the creator of the tag, or a contributor may delete it"
                )
        return await ctx.send(f"No tag called `{tag.name}`")

    @tag.autocomplete("tag_name")
    @del_tag.autocomplete("name")
    async def tag_autocomplete(self, ctx: AutocompleteContext, **kwargs):
        tags = self.tags.keys()
        output = []
        if tags:
            if ctx.input_text:
                print(ctx.input_text)
                result = process.extract(
                    ctx.input_text, tags, scorer=fuzz.partial_token_sort_ratio
                )
                output = [t[0] for t in result if t[1] > 50]
            else:
                output = list(tags)[:25]
            return await ctx.send(output)

        await ctx.send([])


def setup(bot):
    Tags(bot)
