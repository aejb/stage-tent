from os import name
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

client = discord.Client(intents=discord.Intents.default())
slash = SlashCommand(client, sync_commands=True)

GUILD_ID = 844651116918603786
STAGE_CATEGORY = 846898034956173343
ARCHIVE_CATEGORY = 846898101935800350
STAGE_HOST = 845194457128370206
STAGE_OBSERVER = 845194557985783808

def gettoken():
    token_file = open("token.txt", "r")
    token_string = token_file.read()
    token_token = token_string.split("\n")
    bot_token = str(token_token[0])
    return bot_token

token = gettoken()

@slash.subcommand(base="session", name="create",
    description="Create a new Stage session",
    guild_ids=[GUILD_ID],
    options=[
        create_option(
            name="name",
            description="The name of the stage to be created",
            option_type=3,
            required=True
        )
    ])
async def _session_create(ctx, name: str):
    if name in [item.name for item in ctx.guild.stage_channels]:
        await ctx.send(content=f"A stage called {name} already exists. Please choose another name.")
    else:
        category = discord.utils.get(ctx.guild.channels, id=STAGE_CATEGORY)
        host = discord.utils.get(ctx.guild.roles, id=STAGE_HOST)
        observer = discord.utils.get(ctx.guild.roles, id=STAGE_OBSERVER)
        creator = ctx.author
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            host: discord.PermissionOverwrite(view_channel=True, manage_channels=True, manage_permissions=True),
            observer: discord.PermissionOverwrite(view_channel=True, manage_channels=True, manage_permissions=True),
            creator: discord.PermissionOverwrite(view_channel=True, manage_channels=True, manage_permissions=True)
        }
        stage = await ctx.guild.create_stage_channel(name, category=category, overwrites=overwrites)
        text = await ctx.guild.create_text_channel(f"{name}-text", category=category, overwrites=overwrites)
        await ctx.send(content=f"Stage {stage.mention} and channel {text.mention} created.")
        print(f"{stage} created by {creator}")

@slash.subcommand(base="session", name="start",
    description="Start a public stage",
    guild_ids=[GUILD_ID],
    options=[
        create_option(
            name="channel",
            description="The stage you want to open",
            option_type=7,
            required=True
        )
    ])
async def _session_start(ctx, channel: discord.StageChannel):
    stage_host = discord.utils.get(ctx.guild.roles, id=STAGE_HOST)
    stage_observer = discord.utils.get(ctx.guild.roles, id=STAGE_OBSERVER)
    if channel.overwrites_for(ctx.author).manage_permissions or stage_host in ctx.author.roles or stage_observer in ctx.author.roles:
        text = discord.utils.get(ctx.guild.text_channels, name=f"{channel.name}-text")
        if text:
            overwrite = discord.PermissionOverwrite(view_channel=True)
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await text.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(content=f"{channel.mention} and {text.mention} have been opened!")
            print(f"{channel} opened by {ctx.author}")
        else:
            await ctx.send(content=f"Error: Text channel for {channel.mention} not found. The text channel should be named `#{channel.name}-text`.", hidden=True)
    else:
        await ctx.send(content=f"Error: You do not have the required permissions to open {channel.mention}. You need Manage Permissions.", hidden=True)

@slash.subcommand(base="session", name="stop",
    description="Stop a public stage",
    guild_ids=[GUILD_ID],
    options=[
        create_option(
            name="channel",
            description="The stage you want to close",
            option_type=7,
            required=True
        )
    ])
async def _session_stop(ctx, channel: discord.StageChannel):
    stage_host = discord.utils.get(ctx.guild.roles, id=STAGE_HOST)
    stage_observer = discord.utils.get(ctx.guild.roles, id=STAGE_OBSERVER)
    archive_category = discord.utils.get(ctx.guild.channels, id=ARCHIVE_CATEGORY)
    if channel.overwrites_for(ctx.author).manage_permissions or stage_host in ctx.author.roles or stage_observer in ctx.author.roles:
        text = discord.utils.get(ctx.guild.text_channels, name=f"{channel.name}-text")
        if text:
            overwrite = discord.PermissionOverwrite(view_channel=False)
            await text.edit(category=archive_category)
            await channel.edit(category=archive_category)
            ## These may be redundant with Sync
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await channel.set_permissions(stage_host, overwrite=discord.PermissionOverwrite())
            await channel.set_permissions(stage_observer, overwrite=discord.PermissionOverwrite())
            await text.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await text.set_permissions(stage_host, overwrite=discord.PermissionOverwrite())
            await text.set_permissions(stage_observer, overwrite=discord.PermissionOverwrite())
            ## Sync
            await channel.edit(sync_permissions=True)
            await text.edit(sync_permissions=True)
            await ctx.send(content=f"{channel.mention} and {text.mention} have been closed!")
            print(f"{channel} closed by {ctx.author}")
        else:
            await ctx.send(content=f"Error: Text channel for {channel.mention} not found. The text channel should be named `#{channel.name}-text`.", hidden=True)
    else:
        await ctx.send(content=f"Error: You do not have the required permissions to open {channel.mention}. You need Manage Permissions.", hidden=True)

client.run(token)