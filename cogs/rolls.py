from utilities.scion_rules import get_tn
import nextcord
from nextcord.ext import commands as commands
from utilities.dice_options import RollOptions as RollOptions
from utilities import dice as dice
from utilities import embed_message_maker as embed_message_maker

class RollsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # This cog will handle all basic rolls for the bot, including skill checks.
    # -----------------------------
    # /dramatic_roll
    # -----------------------------
    @nextcord.slash_command(
        name="dramatic_roll",
        description="Rolls a dramatic roll for a character."
    )
    async def dramatic_roll(
        self,
        interaction: nextcord.Interaction,
        dice_pool = RollOptions.dice_pool(),
        enhancement= RollOptions.enhancement(),
        hero_type: str = RollOptions.hero_type(),
        scale: int = RollOptions.scale(),
        difficulty: int = 1,
        divinity_dice: int = RollOptions.divinity_dice(),
        again= RollOptions.again(),
    ):
        try:
            dice_pool = int(dice_pool)
            enhancement = int(enhancement)
            scale = int(scale)
            difficulty = int(difficulty)
            divinity_dice = int(divinity_dice)
            again = int(again)
        except (TypeError, ValueError):
            await interaction.response.send_message("Please provide numeric values for the roll options.", ephemeral=True)
            return

        tn = get_tn(hero_type)

        scion_dice = dice.ScionDice(
            dice_pool=dice_pool - divinity_dice,
            enhancement=enhancement,
            hero_type=hero_type,
            scale=scale,
            difficulty=difficulty,
            tn=tn,
            divinity_dice=divinity_dice,
            again=again,
        )
        results = scion_dice.roll()
        divine_results = scion_dice.roll_divinity()
        exploded_results = scion_dice.check_explode(results)
        divine_exploded_results = scion_dice.check_explode(divine_results)
        exploded_results.extend(divine_exploded_results)
        successes = scion_dice.count_successes(results, divine_results, exploded_results)
        message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)
        botched = scion_dice.check_botch(results, exploded_results, successes)
        successes -= difficulty
        divinity = True if divinity_dice > 0 else False
        mortal_fail = scion_dice.check_mortal_fail(divine_results)
        if botched:
            embed_response = message_maker.botch_dramatic(
                interaction=interaction,
                results=results,
                divine_results=divine_results,
                sux=successes,
                difficulty=difficulty,
                divinity=divinity,
                mortal_fail=mortal_fail,
            )
        elif successes > 0:
            embed_response = message_maker.sucess_dramatic(
                interaction=interaction,
                results=results,
                divine_results=divine_results,
                exploded_results=exploded_results,
                sux=successes,
                enhancement=enhancement,
                scale=scale,
                difficulty=difficulty,
                divinity=divinity,
                cs=scion_dice.check_catastrophic_success(divine_results),
            )
        else:
            embed_response = message_maker.fail_dramatic(
                interaction=interaction,
                results=results,
                divine_results=divine_results,
                exploded_results=exploded_results,
                sux=successes,
                enhancement=enhancement,
                scale=scale,
                difficulty=difficulty,
                divinity=divinity,
                mf=mortal_fail,
            )
    
        await interaction.response.send_message(embed=embed_response)

    # End of dramatic_roll command
    
    # This cog will handle all basic rolls for the bot, including skill checks.
    # -----------------------------
    # /narrative_roll
    # -----------------------------
    @nextcord.slash_command(
        name="narrative_roll",
        description=(
            "Rolls a number of dice, adds in the enhancement and scale "
            "modifiers, then subtracts difficulty."
        ),
    )
    async def narrative_roll(
        self,
        interaction: nextcord.Interaction,
        dice_pool: int = RollOptions.dice_pool(),
        enhancement: int = RollOptions.enhancement(),
        hero_type: str = RollOptions.hero_type(),
        scale: int = RollOptions.scale(),
        difficulty: int = 1,
        divinity_dice: int = RollOptions.divinity_dice(),
        again: int = RollOptions.again(),
    ):
        try:
            dice_pool = int(dice_pool)
            enhancement = int(enhancement)
            scale = int(scale)
            difficulty = int(difficulty)
            divinity_dice = int(divinity_dice)
            again = int(again)
        except (TypeError, ValueError):
            await interaction.response.send_message(
                "Please provide numeric values for the roll options.",
                ephemeral=True,
            )
            return

        tn = get_tn(hero_type)
        scion_dice = dice.ScionDice(
            dice_pool=dice_pool - divinity_dice,
            enhancement=enhancement,
            hero_type=hero_type,
            divinity_dice=divinity_dice,
            scale=scale,
            difficulty=difficulty,
            tn=tn,
            again=again,
        )

        results = scion_dice.roll()
        divine_results = scion_dice.roll_divinity()
        exploded_results = scion_dice.check_explode(results)
        divine_exploded_results = scion_dice.check_explode(divine_results)
        exploded_results.extend(divine_exploded_results)
        successes = scion_dice.count_narrative_successes(
            results,
            divine_results,
            exploded_results,
        )
        botched = scion_dice.check_botch(results, exploded_results, successes)
        successes -= difficulty
        divinity = divinity_dice > 0
        mortal_fail = scion_dice.check_mortal_fail(divine_results)
        message_maker = embed_message_maker.MessageMaker(hero_type=hero_type)

        if botched:
            embed_response = message_maker.botch_dramatic(
                interaction=interaction,
                results=results,
                divine_results=divine_results,
                sux=successes,
                difficulty=difficulty,
                divinity=divinity,
                mortal_fail=mortal_fail,
            )
        elif successes > 0:
            embed_response = message_maker.sucess_narrative(
                interaction=interaction,
                results=results,
                divine_results=divine_results,
                exploded_results=exploded_results,
                sux=successes,
                enhancement=enhancement,
                scale=scale,
                difficulty=difficulty,
                divinity=divinity,
                cs=scion_dice.check_catastrophic_success(divine_results),
            )
        else:
            embed_response = message_maker.fail_narrative(
                interaction=interaction,
                results=results,
                divine_results=divine_results,
                exploded_results=exploded_results,
                sux=successes,
                enhancement=enhancement,
                scale=scale,
                difficulty=difficulty,
                divinity=divinity,
            )

        await interaction.response.send_message(embed=embed_response)


def setup(bot):
    bot.add_cog(RollsCog(bot))
