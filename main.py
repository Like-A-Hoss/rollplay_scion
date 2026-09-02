try:
    import audioop  # type: ignore
except ModuleNotFoundError:
    import audioop_lts as audioop  # type: ignore

import os
import sys
import traceback

import nextcord
from nextcord.ext import commands

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if __package__:
    from .settings import SECRET_KEY as SECRET_KEY
    from .settings import TESTING_SERVER as testingServerID
    from .settings import REACTIVE_DEFENSE_LOG_CHANNEL as reactiveDefenseLogChannel
    from .cogs.rolls import RollsCog
    from .cogs.combat import CombatCog
    from .utilities import embed_message_maker as embed_message_maker
else:
    from settings import SECRET_KEY as SECRET_KEY
    from settings import TESTING_SERVER as testingServerID
    from settings import REACTIVE_DEFENSE_LOG_CHANNEL as reactiveDefenseLogChannel
    from cogs.rolls import RollsCog
    from cogs.combat import CombatCog
    from utilities import embed_message_maker as embed_message_maker



intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True



client = commands.Bot(intents=intents)
# SlashOption constants
HERO_LEVEL_CHOICES = ["Origin", "Hero", "Demigod", "God", "God Feat of Scale"]
SCALE_CHOICES = [0, 1, 2, 3, 4, 5, 6]
HERO_TYPE_DESCRIPTION = "Choose the hero type, or antagonist power level"
DIVINITY_DICE_OPTIONS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]





async def _send_debug_channel_message(message: str):
    if not reactiveDefenseLogChannel:
        return
    try:
        channel_id = int(reactiveDefenseLogChannel)
    except (TypeError, ValueError):
        return

    channel = client.get_channel(channel_id)
    if channel is None:
        try:
            channel = await client.fetch_channel(channel_id)
        except Exception:
            return

    try:
        await channel.send(message[:1900])
    except Exception:
        return

@client.event
async def on_ready():
    print("Hello Papa!\n")

    try:
        guild_id = int(testingServerID)
    except (TypeError, ValueError):
        print(f"Invalid TESTING_SERVER value: {testingServerID}")
        return
    if guild_id is None:
        print("TESTING_SERVER environment variable is not set.")
    print (f"Using guild ID: {guild_id}")
    
    guild = client.get_guild(guild_id)
    if guild is None:
        print(f"Could not find guild with ID {guild_id}")
        print("Guilds currently available to this bot:")
        for available_guild in client.guilds:
            print(f"- {available_guild.id}: {available_guild.name}")
        return

    channel = next((c for c in guild.text_channels if c.name == "general"), None)
    if channel is None:
        channel = guild.system_channel

    if channel is not None:
        await channel.send("Hello Papa!\n")

    try:
        await client.sync_application_commands(guild_id=guild_id)
        print(f"Synced slash commands to guild: {guild.name} ({guild.id})")
        await _send_debug_channel_message(
            f"[startup] Synced slash commands to guild: {guild.name} ({guild.id})"
        )
    except Exception as exc:
        print(f"Failed to sync slash commands for guild {guild.name} ({guild.id}): {exc}")
        await _send_debug_channel_message(
            "\n".join(
                [
                    "[startup_error] command sync failed",
                    f"guild={guild.name} ({guild.id})",
                    f"error={exc}",
                ]
            )
        )


@client.event
async def on_application_command_error(interaction: nextcord.Interaction, error: Exception):
    command_name = "unknown"
    try:
        command_name = interaction.application_command.qualified_name
    except Exception:
        pass

    trace = traceback.format_exc()
    await _send_debug_channel_message(
        "\n".join(
            [
                "[slash_error]",
                f"command={command_name}",
                f"user={interaction.user}",
                f"error={error}",
                f"trace={trace[:1400]}",
            ]
        )
    )

    try:
        if not interaction.response.is_done():
            await interaction.response.send_message("Something went wrong while processing this command.", ephemeral=True)
    except Exception:
        pass

                
@client.slash_command(name="help", description="Provides information about the bot and its commands.")
async def hep_command(interaction):
    message_maker = embed_message_maker.MessageMaker(hero_type="Origin")
    embed_response = message_maker.help_embed()
    
    await interaction.response.send_message(embed=embed_response, ephemeral=True)

client.add_cog(RollsCog(client))
client.add_cog(CombatCog(client))

client.run(SECRET_KEY)