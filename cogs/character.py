import nextcord
from nextcord.ext import commands as commands
from datetime import datetime, timezone

from utilities.json_reader import read_character
from utilities.json_writer import write_character, delete_character


class CharacterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------------
    # /character_enter
    # -----------------------------
    @nextcord.slash_command(
        name="character_enter",
        description="Manually enter a new character."
    )
    async def character_enter(
        self,
        interaction: nextcord.Interaction,
        character_name: str
    ):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)

        data = {
            #header information
            "guild": guild_id,
            "user": user_id,
            "character": character_name,
            "created": datetime.now(timezone.utc).isoformat(),

            # Core attributes and skills
            "attributes": {},
            "skills": {},
            "callings": "",
            "pantheon": "",
            "hero_type": "",
            "legend": 0,

            # Paths
            "origin_path": {},
            "role_path": {},
            "pantheon_path": {}
        }

        write_character(guild_id, user_id, character_name, data)

        await interaction.response.send_message(
            f"Character **{character_name}** created successfully."
        )

    # -----------------------------
    # /character_view
    # -----------------------------
    @nextcord.slash_command(
        name="character_view",
        description="View one of your characters."
    )
    async def character_view(
        self,
        interaction: nextcord.Interaction,
        character_name: str
    ):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)

        data = read_character(guild_id, user_id, character_name)

        if not data:
            await interaction.response.send_message(
                f"No character named **{character_name}** found."
            )
            return

        embed = nextcord.Embed(
            title=f"{data['character']} (Hero Level {data['hero_type']})",
            description=f"Pantheon: {data['pantheon']}\nLegend: {data['legend']}\nCallings: {data['callings']}",
            color=nextcord.Color.blue()
        )

        embed.add_field(
            name="Attributes",
            value="\n".join([f"{k}: {v}" for k, v in data["attributes"].items()]) or "None",
            inline=False
        )

        embed.add_field(
            name="Skills",
            value="\n".join([f"{k}: {v}" for k, v in data["skills"].items()]) or "None",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    # -----------------------------
    # /character_delete
    # -----------------------------
    @nextcord.slash_command(
        name="character_delete",
        description="Delete one of your characters."
    )
    async def character_delete(
        self,
        interaction: nextcord.Interaction,
        character_name: str
    ):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)

        delete_character(guild_id, user_id, character_name)

        await interaction.response.send_message(
            f"Character **{character_name}** deleted."
        )


def setup(bot):
    bot.add_cog(CharacterCog(bot))
