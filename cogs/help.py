import nextcord
from nextcord.ext import commands as commands
from utilities import embed_message_maker as embed_message_maker

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="help", description="Provides information about the bot and its commands.")
    async def help_command(self, interaction: nextcord.Interaction):
        message_maker = embed_message_maker.MessageMaker(hero_type="Origin")
        embed_response = message_maker.help_embed()
        await interaction.response.send_message(embed=embed_response, ephemeral=True)

def setup(bot):
    bot.add_cog(HelpCog(bot))