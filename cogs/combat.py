from utilities.scion_rules import get_tn
import nextcord
from nextcord.ext import commands as commands
from utilities.dice_options import RollOptions as RollOptions
from utilities import dice as dice
from utilities import embed_message_maker as embed_message_maker
from utilities import scaleByFactor as scaleByFactor

try:
    from . import reactive_defense
    from .player_attack_resolver import resolve_player_attack_state
    from ..settings import REACTIVE_DEFENSE_LOG_CHANNEL, TESTING_SERVER
except ImportError:
    from cogs import reactive_defense
    from cogs.player_attack_resolver import resolve_player_attack_state
    from settings import REACTIVE_DEFENSE_LOG_CHANNEL, TESTING_SERVER


class CombatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # This cog will handle all combat rolls for the bot, including inniative, attacks on antagonists and attacks on players.
    
    # -----------------------------
    # initiative_roll
    # -----------------------------
    @nextcord.slash_command(
        name="initiative_roll",
        description=(
            "Rolls a number of dice, adds in the enhancement and scale "
            "modifiers and generates slots."
        ),
    )
    async def initiative_roll(
        self,
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
            dice_pool=dice_pool - divinity_dice,
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
        exploded_results.extend(scion_dice.check_explode(divine_results))
        successes = scion_dice.count_successes(
            results,
            divine_results,
            exploded_results,
        )
        message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)
        embed_response = message_maker.initiative(
            interaction=interaction,
            results=results,
            exploded_results=exploded_results,
            bonuses=(
                f"Enhancement Bonus: {enhancement}\n"
                f"Scale Bonus: {scaleByFactor.dramatic_scale(scale)}"
            ),
            initiative=successes,
        )
        await interaction.response.send_message(embed=embed_response)

    # -----------------------------
    # attack_antagonist
    # -----------------------------
    @nextcord.slash_command(
        name="attack_antagonist",
        description="For use when attacking an antagonist.",
    )
    async def attack_antagonist(
        self,
        interaction: nextcord.Interaction,
        dice_pool: int = RollOptions.dice_pool(),
        enhancement: int = RollOptions.enhancement(),
        defense: int = nextcord.SlashOption(
            name="defense",
            description="The defense value of the antagonist being attacked.",
            required=True,
        ),
        hero_type: str = RollOptions.hero_type(),
        scale: int = RollOptions.scale(),
        divinity_dice: int = RollOptions.divinity_dice(),
        again: int = RollOptions.again(),
    ):
        tn = get_tn(hero_type)
        scion_dice = dice.ScionDice(
            dice_pool=dice_pool - divinity_dice,
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
        exploded_results.extend(scion_dice.check_explode(divine_results))
        successes = scion_dice.count_successes(
            results,
            divine_results,
            exploded_results,
        )
        botched = scion_dice.check_botch(results, exploded_results, successes)
        successes -= defense
        message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)
        divinity = divinity_dice > 0
        catastrophic_success = (
            scion_dice.check_catastrophic_success(divine_results)
            if divinity
            else False
        )
        mortal_fail = scion_dice.check_mortal_fail(divine_results) if divinity else False

        if successes > 0:
            embed_response = message_maker.attack(
                interaction=interaction,
                results=results,
                divine_results=divine_results,
                exploded_results=exploded_results,
                sux=successes,
                success="success",
                bonuses=(
                    f"Enhancement Bonus: +{enhancement}\n"
                    f"Scale Bonus: +{scaleByFactor.dramatic_scale(scale)}extra successes"
                ),
                defense=defense,
                divinity=divinity,
                divine_modifier=catastrophic_success,
            )
        elif botched:
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
                exploded_results=exploded_results,
                sux=successes,
                success="failure",
                bonuses=(
                    f"Enhancement Bonus: +{enhancement}\n"
                    f"Scale Bonus: +{scaleByFactor.dramatic_scale(scale)}extra successes"
                ),
                defense=defense,
                divinity=divinity,
                divine_modifier=mortal_fail,
            )

        await interaction.response.send_message(embed=embed_response)

    # -----------------------------
    # attack_player
    # -----------------------------
    @nextcord.slash_command(
        name="attack_player",
        description="For use when attacking a player.",
    )
    async def attack_player(
        self,
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
        attack_params = {
            "dice_pool": attacker_dice_pool,
            "enhancement": enhancement,
            "hero_type": attacker_hero_type,
            "scale": scale,
            "difficulty": 0,
            "tn": get_tn(attacker_hero_type),
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
        await self._send_debug_channel_message(
            f"[attack_player] created reactive defense state: {state_id}"
        )

    # -----------------------------
    # attack_player_resolve
    # -----------------------------
    @nextcord.slash_command(
        name="attack_player_resolve",
        description="Resolve a queued attack on a player after defender finalizes their defense.",
        guild_ids=[int(TESTING_SERVER)],
    )
    async def attack_player_resolve(
        self,
        interaction: nextcord.Interaction,
        state_id: str = nextcord.SlashOption(
            name="state_id",
            description="Reactive defense state id to resolve",
            required=True,
        ),
    ):
        _, message = await resolve_player_attack_state(
            self.bot,
            interaction,
            state_id,
        )
        await interaction.response.send_message(message, ephemeral=True)

    async def _send_debug_channel_message(self, message: str):
        if not REACTIVE_DEFENSE_LOG_CHANNEL:
            return
        try:
            channel_id = int(REACTIVE_DEFENSE_LOG_CHANNEL)
        except (TypeError, ValueError):
            return

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception:
                return

        try:
            await channel.send(message[:1900])
        except Exception:
            return


def setup(bot):
    bot.add_cog(CombatCog(bot))
    