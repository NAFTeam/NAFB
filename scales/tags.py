import datetime
import logging

import aioredis as aioredis
import attr
import orjson as orjson
from naff import (
    MISSING,
    ModalContext,
    Modal,
    ShortText,
    ParagraphText,
    Embed,
    Timestamp,
    BrandColors,
)
from naff.client.utils import optional
from naff.models import (
    Extension,
    slash_command,
    OptionTypes,
    InteractionContext,
    slash_option,
    AutocompleteContext,
    Snowflake_Type,
    to_snowflake,
)
from naff.models.naff.application_commands import modal_callback
from thefuzz import fuzz, process

log = logging.getLogger("rebecca")


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
    modified: datetime.datetime | None = attr.ib(
        default=None, converter=optional(deserialize_datetime)
    )
    modifier_id: Snowflake_Type = attr.ib(
        default=None, converter=optional(to_snowflake)
    )


class Tags(Extension):
    def __init__(self, bot):
        self.tags = {}
        self.redis: aioredis.Redis = MISSING

    async def async_start(self):
        await self.connect()

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
        log.info(f"Cached {len(self.tags)} tags")

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

    @modal_callback("create_tag", "edit_tag")
    async def tag_modal_rcv(self, ctx: ModalContext):
        name = ctx.responses.get("name")
        content = ctx.responses.get("content")
        edit_mode = ctx.custom_id == "edit_tag"
        tag = None

        if not edit_mode and name.lower() in self.tags.keys():
            return await ctx.send(f"`{name}` already exists")
        else:
            if edit_mode:
                tag = await self.get_tag(name.lower())
                tag.modifier_id = ctx.author.id
                tag.modified = datetime.datetime.now()
                tag.content = content
            if not tag:
                tag = Tag(name, content, ctx.author.id)

            await self.put_tag(tag)
            await ctx.send(f"{'Edited' if edit_mode else 'Created'} `{tag.name}`")

    @slash_command(name="tag", description="Send a requested tag to this channel")
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

    @slash_command(name="create_tag", description="Create a tag")
    async def create_tag(self, ctx: InteractionContext):
        modal = Modal(
            title="Tag Wizard",
            components=[
                ShortText(
                    label="Tag Name",
                    placeholder="The name for this tag",
                    custom_id="name",
                ),
                ParagraphText(
                    label="Tag Content",
                    placeholder="What should this tag say",
                    custom_id="content",
                ),
            ],
            custom_id="create_tag",
        )
        await ctx.send_modal(modal)

    @slash_command(name="delete_tag", description="Delete a tag")
    @slash_option(
        "name",
        "The name of the tag you want to delete",
        OptionTypes.STRING,
        required=True,
    )
    async def del_tag(self, ctx: InteractionContext, name: str):
        tag = await self.get_tag(name.lower().replace("_", " "))
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
        return await ctx.send(f"No tag called `{name}`")

    @slash_command(
        name="tag_details", description="Get the details about a specified tag"
    )
    @slash_option(
        "name",
        "The name of the tag you want to delete",
        OptionTypes.STRING,
        required=True,
    )
    async def tag_details(self, ctx: InteractionContext, name: str):
        tag = await self.get_tag(name.lower().replace("_", " "))
        if tag:
            author = await ctx.guild.fetch_member(tag.author_id)
            embed = Embed(
                title="Tag Content",
                description=f"{tag.content}",
                color=BrandColors.BLURPLE,
            )
            embed.add_field("Created At", Timestamp.fromdatetime(tag.creation))
            if tag.modifier_id is not None:
                mod_user = await ctx.guild.fetch_member(tag.modifier_id)
                embed.add_field("Last Modified", Timestamp.fromdatetime(tag.modified))
                embed.add_field("Last Modifier", mod_user.tag)
            embed.set_author(author.tag, icon_url=author.display_avatar.url)

            return await ctx.send(embeds=embed)
        return await ctx.send(f"No tag called `{name}`")

    @slash_command(name="edit_tag", description="Edit an existing tag.")
    @slash_option(
        "name",
        "The name of the tag you want to edit",
        OptionTypes.STRING,
        required=True,
    )
    async def edit_tag(self, ctx: InteractionContext, name: str):
        tag = await self.get_tag(name.lower().replace("_", " "))
        if tag:
            modal = Modal(
                title="Tag Wizard",
                components=[
                    ShortText(
                        label="Tag Name",
                        value=tag.name,
                        custom_id="name",
                    ),
                    ParagraphText(
                        label="Tag Content",
                        placeholder="What should this tag say",
                        value=tag.content,
                        custom_id="content",
                    ),
                ],
                custom_id="edit_tag",
            )
            return await ctx.send_modal(modal)
        return await ctx.send(f"No tag called `{name}`")

    @tag.autocomplete("tag_name")
    @del_tag.autocomplete("name")
    @tag_details.autocomplete("name")
    @edit_tag.autocomplete("name")
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
    t = Tags(bot)
