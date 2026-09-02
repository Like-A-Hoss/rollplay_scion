# Dice_Options.py
import nextcord

class RollOptions:
    HERO_LEVEL_CHOICES = ["Origin", "Hero", "Demigod", "God", "God Feat of Scale"]
    SCALE_CHOICES = [str(i) for i in range(7)]
    DIVINITY_DICE_CHOICES = [str(i) for i in range(11)]

    @staticmethod
    def dice_pool():
        return nextcord.SlashOption(
            name="dice_pool",
            description="Number of dice to roll (do NOT subtract divinity dice).",
            required=True,
        )

    @staticmethod
    def enhancement():
        return nextcord.SlashOption(
            name="enhancement",
            description="Enhancement added to the roll (usually 0–3).",
            default=0,
            required=True,
        )

    @staticmethod
    def hero_type():
        return nextcord.SlashOption(
            name="hero_type",
            description="Choose the hero tier or antagonist power level.",
            choices=RollOptions.HERO_LEVEL_CHOICES,
            required=True,
        )

    @staticmethod
    def scale():
        return nextcord.SlashOption(
            name="scale",
            description="Difference in scale for the action.",
            choices=RollOptions.SCALE_CHOICES,
            required=True,
        )

    @staticmethod
    def difficulty():
        return nextcord.SlashOption(
            name="difficulty",
            description="Difficulty of the roll (default 1).",
            required=False,
            default=1,
        )

    @staticmethod
    def divinity_dice():
        return nextcord.SlashOption(
            name="divinity_dice",
            description="Number of dice converted to divinity dice (Demigod/God only).",
            choices=RollOptions.DIVINITY_DICE_CHOICES,
            required=False,
            default=0,
        )

    @staticmethod
    def again():
        return nextcord.SlashOption(
            name="again",
            description="The 'again' threshold for exploding dice (default 10).",
            choices=["8", "9", "10"],
            required=False,
            default=10,
        )
