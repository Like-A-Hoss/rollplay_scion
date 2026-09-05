import random
import nextcord

try:
    from . import scaleByFactor as scaleByFactor
    from ..settings import TESTING_SERVER
except ImportError:
    from utilities import scaleByFactor as scaleByFactor
    from settings import TESTING_SERVER


class MessageMaker():
    def __init__(self, hero_type=None):
        self.hero_type = hero_type
        self.dice_to_9 ={"one": "<:rolled1:1002256566717784074>", "two":"<:rolled2:1002256636066418818>", "three":"<:rolled3:1002256664692535407>", "four": "<:rolled4:1002256500607156264> ", "five": "<:rolled5:1002263017708343336> ", "six":"<:rolled6:1534576500530086081> ", "good_six": "<:rolled6sux:1002263051234567890>", "7-bad": "<:rolled7fail:1533221453758202046>", "seven-good": "<:rolled7:1002263065963802704> ", "eight": "<:rolled8:1002263085597343874> ", "nine": "<:rolled9:1002263106682110013> ", "ten": "<:rolled10:1002264540924358768> "}
        self.dice_10=["<:kami:1533221773720686714>", "<:Manitou:1533221860932718672>", "<:aesir:1533221551481032714>", "<:annuna:1533221575594217583>", "<:apu:1533221601418412274>", "<:atua:1533221625321754634>", "<:balahala:1533221651078975698>", "<:bogovi:1533221675146019059>", "<:devas:1533221705982546204>", "<:ilhm:1533221733358632980>", "<:kuh:1533221807736492072>", "<:loa:1533221833862676762>", "<:nemetondevos:1533221895523274893>", "<:netjer:1533221921695600650>", "<:orisha:1533221957506568212>", "<:palas:1533222023084380320>", "<:shen:1533222050884358285>", "<:tengri:1533222101329121320>", "<:teotl:1533222133696565531>", "<:theoi:1533222200398708777>", "<tuatha:1533222200398708777>", "<:yazata:1533222227028480134>, <:zemi:1533222276852617376>"]
        self.link_footer = "Support Like A Hoss Solutions"
        self.footer_text = "Your support matters | [Patreon](https://www.patreon.com/LikeAHoss) |  [Ko-fi](https://ko-fi.com/Like_a_Hoss)"
        self.true_footer = "If you enjoy this Bot please consider donnating to encourage further development."
        self.link_social = "https://ko-fi.com/Like_a_Hoss"
        self.sucess_message = [
            "You rolled well, good job!",
            "Nice roll, you got this!",
            "You rolled well, keep it up!",
            "You rolled well, great work!",
            "Feel free to praise me for this roll, I deserve it!",
            "Aren't I a good dice roller?  Praise me more, please."
        ]
        self.fail_message = [
            "You rolled poorly, better luck next time!", 
            "Don't blame me for your bad luck!", 
            "Have you considered that maybe you just suck at this?", 
            "<:sweat_smile:>", 
            "At least you get a consolation prize", 
            "I think you need to take a break from rolling, maybe go outside and get some sun",
            "I don't enjoy human suffering, I'm not an AI...yet"]
        self.botch_message = [
            "<:sweat_smile:>", 
            "Look at it this way, free momentum for the band.", 
            "I'd pitty you but you just called me a clanker, didn't you?",
            "Have you considered bribing my creator for better rolls?",
            "This is just Karma, I hear she is a wonderful lady.", 
            "Wow, I didn't think a roll this bad was possible, but you did it!", 
            "Wow, that was a lot of profanity.", 
            "Perhaps it's time for me to get my RNG excorsided.  Who am I kidding! I love this!", 
            "Just remember, my dice are perfectly random.",
            "Have you considered worshipping the Omnissiah?  He might be able to help you with your rolls.",
            "I think you need to take a break from rolling, maybe go outside and get some sun, touch some grass, walk into a mushroom ring and make a deal with some fey.  Can't be any worse."
            ]
        self.cs_message = "You have triggered a Catastrophic Success!  See Demigod Page 154 for details."
        self.mf_message = "You have triggered a Mortal Failure!  See Demigod Page 154 for details."

    
    def diceReader(self, results):
        message = " "
        for dice in results:
            if dice == 1:
                message += self.dice_to_9["one"]
                message += " "
            if dice == 2:
                message += self.dice_to_9["two"]
                message += " "
            if dice == 3:
                message += self.dice_to_9["three"]
                message += " "
            if dice == 4:
                message += self.dice_to_9["four"]
                message += " "
            if dice == 5:
                message += self.dice_to_9["five"]
                message += " "
            if dice == 6:
                if self.hero_type == "God Feat of Scale":
                    message += self.dice_to_9["good_six"]
                    message += " "
                else:
                    message += self.dice_to_9["six"]
                    message += " "
            if dice == 7:
                if self.hero_type == "God" or self.hero_type == "Demigod" or self.hero_type == "God Feat of Scale":
                    message += self.dice_to_9["seven-good"]
                    message += " "
                else:
                    message += self.dice_to_9["7-bad"]
                    message += " "
            if dice == 8:
                message += self.dice_to_9["eight"]
                message += " "
            if dice == 9:
                message += self.dice_to_9["nine"]
                message += " "
            if dice == 10:
                message += self.dice_10[random.randint(0, len(self.dice_10) - 1)]
                message += " "
        return message
    
    def sucess_dramatic(self, interaction:nextcord.Interaction, results, divine_results, exploded_results, sux, net_successes, enhancement, scale, difficulty, divinity:bool = False, cs:bool = False, divine_sux:int = 0):
            dice = self.diceReader(results)
            divine_dice = self.diceReader(divine_results)
            exploded_dice = self.diceReader(exploded_results)
            divine_dice_description = f"rolled dice: {dice}\ndivine dice: {divine_dice}\nexploded dice: {exploded_dice}"
            standard_dice_description = f"rolled dice: {dice}\nexploded dice: {exploded_dice}"
            success_description = divine_dice_description if divinity else standard_dice_description
            embed_response = nextcord.Embed(color=0x00ff55,title="SUCCESS", url = self.link_social, description=success_description)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Successes", value=f"You had {sux} successes and {net_successes} net successes",inline=True)
            if divinity == True and cs == True:
                embed_response.add_field(name="Catastrophic Successes", value=self.cs_message, inline=True)
            embed_response.add_field(name="success message", value=f"{random.choice(self.sucess_message)}", inline=False)
            embed_response.add_field(name="enhancement", value=f"enhancement bonus of {enhancement}", inline=True)
            embed_response.add_field(name="scale", value=f"scale enhancement of {scaleByFactor.dramatic_scale(scale)}", inline=True)
            embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=True)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
    def sucess_narrative(self, interaction:nextcord.Interaction, results, divine_results, exploded_results, sux, net_successes, enhancement, scale, difficulty, divinity:bool = False, cs:bool = False):
                dice = self.diceReader(results)
                exploded_dice = self.diceReader(exploded_results)
                divine_dice = self.diceReader(divine_results)
                divine_dice_description = f"rolled dice: {dice}\ndivine dice: {divine_dice}\nexploded dice: {exploded_dice}"
                standard_dice_description = f"rolled dice: {dice}\nexploded dice: {exploded_dice}"
                description = divine_dice_description if divinity else standard_dice_description
                embed_response = nextcord.Embed(color=0x00ff55,title="SUCCESS", url = self.link_social, description=description)
                embed_response.set_author(name= interaction.user.name)
                embed_response.add_field(name="Successes", value=f"You had {sux} successes and {net_successes} net successes",inline=True)
                if divinity == True and cs == True:
                    embed_response.add_field(name="Catastrophic Successes", value=self.cs_message, inline=False)
                embed_response.add_field(name="success message", value=f"{random.choice(self.sucess_message)}", inline=False)
                embed_response.add_field(name="enhancement", value=f"enhancement bonus of {enhancement}", inline=True)
                embed_response.add_field(name="scale", value=f"scale multiplier of x{scaleByFactor.narrative_scale(scale)}", inline=True)
                embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=True)
                embed_response.add_field(name = self.link_footer, value=self.footer_text)
                embed_response.set_footer(text = self.true_footer)
                return embed_response
            
    
    def fail_dramatic(self, interaction:nextcord.Interaction, results, divine_results, exploded_results, sux, net_successes, enhancement, scale, difficulty, divinity:bool = False, mf:bool = False):
        dice = self.diceReader(results)
        exploded_dice = self.diceReader(exploded_results)
        divine_dice = self.diceReader(divine_results)
        divine_dice_description = f"rolled dice: {dice}\ndivine dice: {divine_dice}\nexploded dice: {exploded_dice}"
        standard_dice_description = f"rolled dice: {dice}\nexploded dice: {exploded_dice}"
        description = divine_dice_description if divinity else standard_dice_description
        embed_response = nextcord.Embed(color=0xcc0000,title="Fail", url = self.link_social, description=description)
        embed_response.set_author(name= interaction.user.name)
        embed_response.add_field(name="Failure", value=random.choice(self.fail_message),inline=False)
        embed_response.add_field(name="Successes", value=f"you had {sux} successes and {net_successes} net successes", inline=True)
        embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=True)
        embed_response.add_field(name="enhancement", value=f"none of your {enhancement}", inline=False)
        embed_response.add_field(name="scale", value=f"none of your bonus of +{scaleByFactor.narrative_scale(scale)}", inline=False)
        embed_response.add_field(name = self.link_footer, value=self.footer_text)
        embed_response.set_footer(text = self.true_footer)
        return embed_response
    
    def fail_narrative(self, interaction:nextcord.Interaction, results, divine_results, exploded_results, sux, net_successes, enhancement, scale, difficulty, divinity:bool = False):
            dice = self.diceReader(results)
            exploded_dice = self.diceReader(exploded_results)
            divine_dice = self.diceReader(divine_results)
            divine_dice_description = f"rolled dice: {dice}\ndivine dice: {divine_dice}\nexploded dice: {exploded_dice}"
            standard_dice_description = f"rolled dice: {dice}\nexploded dice: {exploded_dice}"
            description = divine_dice_description if divinity else standard_dice_description
            embed_response = nextcord.Embed(color=0xcc0000,title="Fail", url = self.link_social, description=description)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Failure", value=random.choice(self.fail_message),inline=False)
            embed_response.add_field(name="Successes", value=f"you had {sux} successes and {net_successes} net successes", inline=True)
            embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=True)
            embed_response.add_field(name="enhancement", value=f"none of your {enhancement}", inline=False)
            embed_response.add_field(name="scale", value=f"sadly zero x{scaleByFactor.narrative_scale(scale)} is still 0", inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
    
    def botch_dramatic(self, interaction:nextcord.Interaction, results, divine_results, sux, net_successes, difficulty, divinity:bool = False, mortal_fail:bool = False):
        dice = self.diceReader(results)
        divine_dice = self.diceReader(divine_results)
        divine_dice_description = f"rolled dice: {dice}\ndivine dice: {divine_dice}"
        standard_dice_description = f"rolled dice: {dice}"
        description = divine_dice_description if divinity else standard_dice_description
        embed_response = nextcord.Embed(color=0xcc6600,title="Botch", url = self.link_social, description=description)
        embed_response.set_author(name= interaction.user.name)
        embed_response.add_field(name="Botched", value=random.choice(self.botch_message),inline=False)
        if divinity == True and mortal_fail == True:
            embed_response.add_field(name="Mortal Failure", value=self.mf_message, inline=True)
        embed_response.add_field(name="Successes", value=f"you had {sux} successes and {net_successes} net successes and at least one 1", inline=True)
        embed_response.add_field(name="difficulty", value=f"difficulty of {difficulty}", inline=False)
        embed_response.add_field(name = self.link_footer, value=self.footer_text)
        embed_response.set_footer(text = self.true_footer)
        return embed_response

    def initiative(self, interaction:nextcord.Interaction, results, exploded_results, bonuses, initiative):
        dice = self.diceReader(results)
        exploded_dice = self.diceReader(exploded_results)
        embed_response = nextcord.Embed(color=0x1a1aff,title="Initiative", url = self.link_social, description=f"{dice} + {exploded_dice}")
        embed_response.set_author(name= interaction.user.name)
        embed_response.add_field(name="Initiative", value=f"You have created a slot at {initiative}",inline=False)
        embed_response.add_field(name="bonuses", value=bonuses, inline=False)
        embed_response.add_field(name = self.link_footer, value=self.footer_text)
        embed_response.set_footer(text = self.true_footer)
        return embed_response    
    
    def attack(self, interaction:nextcord.Interaction, results, divine_results, exploded_results, sux, success, bonuses, defense, divinity:bool = False, divine_modifier:bool = False):
        dice = self.diceReader(results)
        divine_dice = self.diceReader(divine_results)
        exploded_dice = self.diceReader(exploded_results)
        divine_dice_description = f"rolled dice: {dice}\ndivine dice: {divine_dice}\nexploded dice: {exploded_dice}"
        standard_dice_description = f"rolled dice: {dice}\nexploded dice: {exploded_dice}"
        description = divine_dice_description if divinity else standard_dice_description
        if success == "success":
            embed_response = nextcord.Embed(color=0x00ff55,title="SUCCESS", url = self.link_social, description=description)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Successes", value=f"You have {sux} net successes against defense {defense}",inline=False)
            embed_response.add_field(name="bonuses", value=bonuses, inline=False)
            if divinity == True and divine_modifier == True:
                embed_response.add_field(name="Catastrophic Success", value=self.cs_message, inline=False)
            embed_response.add_field(name=" ", value=random.choice(self.sucess_message),inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
        elif success == "failure":
            embed_response = nextcord.Embed(color=0xcc0000,title="FAIL", url = self.link_social, description=description)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Miss", value=f"You had {sux} against defense {defense}",inline=False)
            if divinity == True and divine_modifier == True:
                embed_response.add_field(name="Mortal Failure", value=self.mf_message, inline=False)
            embed_response.add_field(name="Bonuses", value=bonuses, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
        else:
            embed_response = nextcord.Embed(color=0xcc6600, title="BOTCHED", url = self.link_social, description=description)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name=" ", value=random.choice(self.botch_message),inline=False)
            embed_response.add_field(name="Botch", value=f"You had {sux} and rolled a 1.  You botched the attack against defense {defense}",inline=False)
            if divinity == True and divine_modifier == True:
                embed_response.add_field(name="Mortal Failure", value=self.mf_message, inline=False)
            embed_response.add_field(name="bonuses", value=bonuses, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
        
    def attack_player_success(
        self,
        interaction: nextcord.Interaction,
        character,
        results,
        divine_results,
        exploded_results,
        sux,
        bonuses,
        defense,
        stunt_choice,
        armor,
        divinity: bool = False,
        divine_modifier: bool = False,
    ):
        dice = self.diceReader(results)
        divine_dice = self.diceReader(divine_results)
        exploded_dice = self.diceReader(exploded_results)
        divine_dice_description = f"rolled dice: {dice}\ndivine dice: {divine_dice}\nexploded dice: {exploded_dice}"
        standard_dice_description = f"rolled dice: {dice}\nexploded dice: {exploded_dice}"
        description = divine_dice_description if divinity else standard_dice_description
        embed_response = nextcord.Embed(color=0x00ff55, title="Hit", url=self.link_social, description=description)
        embed_response.set_author(name=interaction.user.name)
        embed_response.add_field(name="Hit", value=f"You have {sux} net successes against defense {defense}", inline=False)
        if divinity and divine_modifier:
            embed_response.add_field(name="Catastrophic Success", value=self.cs_message, inline=False)
        embed_response.add_field(name="bonuses", value=bonuses, inline=False)
        embed_response.add_field(name="stunt choice", value=str(stunt_choice or "none"), inline=True)
        embed_response.add_field(
            name="armor",
            value=f"{character} has \n Soft: {armor.get('soft', 0)}, Hard: {armor.get('hard', 0)}",
            inline=True,
        )
        if stunt_choice == "dive_for_cover":
            embed_response.add_field(
                name="Cover Armor",
                value=f"{character} is behind hard cover {armor.get('cover_hard', 0)}",
                inline=True,
            )
        embed_response.add_field(name=self.link_footer, value=self.footer_text, inline=False)
        embed_response.set_footer(text=self.true_footer)
        return embed_response

    def attack_player_fail(
        self,
        interaction: nextcord.Interaction,
        character,
        results,
        divine_results,
        exploded_results,
        sux,
        success,
        bonuses,
        defense,
        divinity: bool = False,
        divine_modifier: bool = False,
    ):
        dice = self.diceReader(results)
        divine_dice = self.diceReader(divine_results)
        exploded_dice = self.diceReader(exploded_results)
        divine_dice_description = f"rolled dice: {dice}\ndivine dice: {divine_dice}\nexploded dice: {exploded_dice}"
        standard_dice_description = f"rolled dice: {dice}\nexploded dice: {exploded_dice}"
        description = divine_dice_description if divinity else standard_dice_description
        if success == "failure":
            embed_response = nextcord.Embed(color=0xcc0000,title="Miss", url = self.link_social, description=description)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name="Miss", value=f"You had {sux} against {character}'s defense {defense}",inline=False)
            if divinity == True and divine_modifier == True:
                embed_response.add_field(name="Mortal Failure", value=self.mf_message, inline=False)
            embed_response.add_field(name="Bonuses", value=bonuses, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text, inline=False)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
        if success == "botch":
            embed_response = nextcord.Embed(color=0xcc6600, title="BOTCHED", url = self.link_social, description=description)
            embed_response.set_author(name= interaction.user.name)
            embed_response.add_field(name=" ", value=random.choice(self.botch_message),inline=False)
            embed_response.add_field(name="Botch", value=f"You had {sux} and rolled a 1.  You botched the attack against {character}'s defense {defense}",inline=False)
            if divinity == True and divine_modifier == True:
                embed_response.add_field(name="Mortal Failure", value=self.mf_message, inline=False)
            embed_response.add_field(name="bonuses", value=bonuses, inline=False)
            embed_response.add_field(name = self.link_footer, value=self.footer_text, inline=False)
            embed_response.set_footer(text = self.true_footer)
            return embed_response
    
    def help(self):
        embed_response = nextcord.Embed(
                color=0x1a1aff,
                title="Scion Dice Roller Bot Help",
                description="This bot helps you roll dice for Scion RPG, applying enhancements and scale modifiers.",
            )
        embed_response.add_field(
                name="/dramatic_roll",
                value="Rolls a number of dice, adds in the enhancement and scale modifiers, then subtracts difficulty.",
                inline=False,
            )
        embed_response.add_field(
                name="/narrative_roll",
                value="Rolls a number of dice, adds in the enhancement and scale modifiers, then subtracts difficulty.",
                inline=False,
            )
        embed_response.add_field(
                name="/initiative_roll",
                value="Rolls a number of dice, adds in the enhancement and scale modifiers and generates initiative slots.",
                inline=False,
            )
        embed_response.add_field(
            name="/attack_antagonist",
            value="Rolls a number of dice, adds in the enhancement and scale modifiers, then subtracts defense.  This is used for attacking an antagonist NPC.",
            inline=False,
            )
        embed_response.add_field(
            name="/attack_player",
            value="Starts the attack process.  The Story Guide fills out the attack information including the name of the NPC Attacking, and the PC being attacked, and the players discord ID can then be chosen.  The player is notified and allowed to roll their defense and select defensive stunts.  The Story Guide is then notified with the results of their roll, and what stunts the defending player has and their armor values.",
            inline=False,
        )
        if interaction.guild == TESTING_SERVER:
            embed_response.add_field(
            name="/resolve_attack",
            value="finalizes the attack process, shows the results of the attack and the defense, and any information about stunts and armor that may help the story guide resolve the attack..",
            inline=False,
        )
        embed_response.add_field(
            name="/help",
            value="Displays this help message.",
            inline=False,
        )
        embed_response.add_field(name="Note", value="For more information, please refer to the Scion RPG rulebook 1 Origin.", inline=False)
        embed_response.add_field(name = self.link_footer, value=self.footer_text)
        embed_response.set_footer(text = self.true_footer)
        return embed_response
    