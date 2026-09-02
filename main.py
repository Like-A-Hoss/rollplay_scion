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
    from .utilities.dice_options import RollOptions as RollOptions
    from .settings import SECRET_KEY as SECRET_KEY
    from .settings import TESTING_SERVER as testingServerID
    from .settings import REACTIVE_DEFENSE_LOG_CHANNEL as reactiveDefenseLogChannel
    from .utilities import scaleByFactor
    from .cogs.player_attack_resolver import resolve_player_attack_state
    from .cogs.rolls import RollsCog
    from .utilities import dice as dice
    from .utilities import embed_message_maker as embed_message_maker
    from .cogs import reactive_defense as reactive_defense
else:
    from utilities.dice_options import RollOptions as RollOptions
    from settings import SECRET_KEY as SECRET_KEY
    from settings import TESTING_SERVER as testingServerID
    from settings import REACTIVE_DEFENSE_LOG_CHANNEL as reactiveDefenseLogChannel
    from utilities import scaleByFactor
    from cogs.player_attack_resolver import resolve_player_attack_state
    from cogs.rolls import RollsCog
    from utilities import dice as dice
    from utilities import embed_message_maker as embed_message_maker
    from cogs import reactive_defense as reactive_defense



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

                
@client.slash_command(name="initiative_roll", description="Rolls a number of dice, adds in the enhancement and scale modifiers and generates slots.")
async def initiative_roll(
    interaction: nextcord.Interaction,
    dice_pool: int,
    enhancement: int,
    hero_type: str = RollOptions.hero_type(),
    scale: int = RollOptions.scale(),
    divinity_dice: int = RollOptions.divinity_dice(),
    again: int = RollOptions.again(),
):
    tn = get_tn(hero_type)

    scion_dice = dice.ScionDice(
        dice_pool=dice_pool-divinity_dice,
        divinity_dice=divinity_dice,
        enhancement=enhancement,
        hero_type=hero_type,
        scale=scale,
        difficulty=0,
        tn=tn,
        again=again,
    )

    results = scion_dice.roll()
    divine_results = scion_dice.roll_divinity()
    exploded_results = scion_dice.check_explode(results)
    divine_exploded_results = scion_dice.check_explode(divine_results)
    exploded_results.extend(divine_exploded_results)
    successes = scion_dice.count_successes(results, divine_results, exploded_results)
    botched = scion_dice.check_botch(results, exploded_results, successes)
    message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)
    
    bonuses = f"Enhancement Bonus: {enhancement}\nScale Bonus: {scaleByFactor.dramatic_scale(scale)}"
    
    embed_response = message_maker.initiative(
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            bonuses=bonuses,
            initiative=successes
        )
    await interaction.response.send_message(embed=embed_response)
    
@client.slash_command(name="attack_antagonist", description="For use when attacking an antagonist.")
async def attack_antagonist(
    interaction: nextcord.Interaction,
    dice_pool: int = RollOptions.dice_pool(),
    enhancement: int = RollOptions.enhancement(),
    defense: int = nextcord.SlashOption(
        name="defense",
        description="The defense value of the antagonist being attacked.",
        required=True
    ),
    hero_type: str = RollOptions.hero_type(),
    scale: int = RollOptions.scale(),
    divinity_dice: int = RollOptions.divinity_dice(),
    again: int = RollOptions.again(),
):
    tn = get_tn(hero_type)

    scion_dice = dice.ScionDice(
        dice_pool=dice_pool-divinity_dice,
        divinity_dice=divinity_dice,
        enhancement=enhancement,
        hero_type=hero_type,
        scale=scale,
        difficulty=defense,
        tn=tn,
        again=again,
    )
    results = scion_dice.roll()
    divine_results = scion_dice.roll_divinity()
    exploded_results = scion_dice.check_explode(results)
    divine_exploded_results = scion_dice.check_explode(divine_results)
    exploded_results.extend(divine_exploded_results)
    successes = scion_dice.count_successes(results, divine_results, exploded_results)
    botched = scion_dice.check_botch(results, exploded_results, successes)
    successes -= defense
    message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)
    divinity = True if divinity_dice > 0 else False
    catastrophic_success = scion_dice.check_catastrophic_success(divine_results) if divinity else False
    mortal_fail = scion_dice.check_mortal_fail(divine_results) if divinity else False
    if successes > 0:
        embed_response = message_maker.attack(
            interaction=interaction,
            results=results,
            divine_results=divine_results,
            exploded_results=exploded_results,
            sux=successes,
            success="success",
            bonuses=f"Enhancement Bonus: +{enhancement}\nScale Bonus: +{scaleByFactor.dramatic_scale(scale)}extra successes",
            defense=defense,
            divinity=divinity,
            divine_modifier=catastrophic_success,
        )
    else:
        if botched:
            embed_response = message_maker.attack(
                interaction=interaction,
                results=results,
                divine_results=divine_results,
                exploded_results=exploded_results,
                sux=successes,
                success="botch",
                bonuses="No bonuses applied",
                defense=defense,
                divinity=divinity,
                divine_modifier=mortal_fail,
            )
        else:
            embed_response = message_maker.attack(
                interaction=interaction,
                results=results,
                divine_results=divine_results,
                exploded_results = exploded_results,
                sux=successes,
                success="failure",
                bonuses=f"Enhancement Bonus: +{enhancement}\nScale Bonus: +{scaleByFactor.dramatic_scale(scale)}extra successes",
                defense=defense,
                divinity=divinity,
                divine_modifier=mortal_fail,
            )
    await interaction.response.send_message(embed=embed_response)


@client.slash_command(name="attack_player", description="For use when attacking a player.")
async def attack_player(
    interaction: nextcord.Interaction,
    antagonist_name: str,
    character_name: str,
    player: nextcord.Member,
    attacker_dice_pool: int = RollOptions.dice_pool(),
    enhancement: int = RollOptions.enhancement(),
    rollaway_cost: int = nextcord.SlashOption(
        name="rollaway_cost",
        description="Enter the roll away cost (attacker Composure or Defense)",
        required=True,
    ),
    attacker_hero_type: str = RollOptions.hero_type(),
    attack_type: str = nextcord.SlashOption(
        name="attack_type",
        description="Choose the attack type",
        choices=["Melee", "Ranged"],
    ),
    scale: int = RollOptions.scale(),
    divinity_dice: int = RollOptions.divinity_dice(),
    again: int = RollOptions.again(),
):
    tn = get_tn(attacker_hero_type)
    attack_params = {
        "dice_pool": attacker_dice_pool,
        "enhancement": enhancement,
        "hero_type": attacker_hero_type,
        "scale": scale,
        "difficulty": 0,
        "tn": tn,
        "again": again,
        "divinity_dice": divinity_dice,
    }

    state_id = await reactive_defense.start_defense(
        interaction,
        antagonist_name,
        character_name,
        player,
        attack_params,
        attack_type,
        rollaway_cost,
    )
    await _send_debug_channel_message(
        f"[attack_player] created reactive defense state: {state_id}"
    )


@client.slash_command(
    name="attack_player_resolve",
    description="Resolve a queued attack on a player after defender finalizes their defense.",
    guild_ids=[int(testingServerID)],
)
async def attack_player_resolve(
    interaction: nextcord.Interaction,
    state_id: str = nextcord.SlashOption(
        name="state_id",
        description="Reactive defense state id to resolve",
        required=True,
    ),
):
    _, message = await resolve_player_attack_state(client, interaction, state_id)
    await interaction.response.send_message(message, ephemeral=True)
    

@client.slash_command(name="help", description="Provides information about the bot and its commands.")
async def hep_command(interaction):
    message_maker = embed_message_maker.MessageMaker(hero_type="Origin")
    embed_response = message_maker.help_embed()
    
    await interaction.response.send_message(embed=embed_response, ephemeral=True)

client.add_cog(RollsCog(client))

client.run(SECRET_KEY)