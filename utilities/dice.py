import random

try:
    from . import scaleByFactor
except ImportError:
    import utilities.scaleByFactor as scaleByFactor

class ScionDice():
    def __init__(self, dice_pool:int, enhancement:int, hero_type:str, scale:int, difficulty:int, divinity_dice:int, tn:int, again:int):
        self.dice_pool = dice_pool
        self.enhancement = enhancement
        self.hero_type = hero_type
        self.scale = scale
        self.difficulty = difficulty
        self.tn = tn
        self.divinity_dice = divinity_dice
        self.again = again
    #Set up the value modifiers
    def set_pool(self, numb:int):
        self.dice_pool = numb
    
    def get_pool(self):
        return self.dice_pool
    
    def set_enhancement(self, numb:int):
        self.enhancement = numb
    
    def get_enhancement(self):
        return self.enhancement

    def set_scale(self, numb:int):
        self.scale = numb

    def get_scale(self):
        return self.scale

    def set_difficulty(self, numb:int):
        self.difficulty = numb

    def get_difficulty(self):
        return self.difficulty

    def roll(self):
        #Rolls the number of dice set and records them to display back
        #set up dice roller
        results:list = []
        for _ in range(self.dice_pool):
            results.append(random.randint(1,10))
        return results
    
    def roll_divinity(self):
        #rolls a number of divinity dice and returns the list of results.
        results:list = []
        for _ in range(self.divinity_dice):
            results.append(random.randint(1,10))
        return results

    def count_successes(self, results:list, divine_results:list =[], exploded_results:list = []):
        # The explode step should run first, so these are the final dice values.
        successes = sum(1 for die in results if die >= self.tn)
        successes += sum(1 for die in divine_results if die >= self.tn)
        successes += sum(1 for die in exploded_results if die >= self.tn)
        if successes >= 1:
            successes += self.enhancement
            if self.scale > 0:
                successes += scaleByFactor.dramatic_scale(self.scale)
        return successes
    
    def count_narrative_successes(self, results:list, divine_results:list = [], exploded_results:list = []):
        # The explode step should run first, so these are the final dice values.
        successes = sum(1 for die in results if die >= self.tn)
        successes += sum(1 for die in divine_results if die >= self.tn)
        successes += sum(1 for die in exploded_results if die >= self.tn)
        if successes >= 1:
            successes += self.enhancement
            if self.scale > 0:
                successes *= scaleByFactor.narrative_scale(self.scale)
        return successes

    def check_botch(self, results:list, exploded_results:list = [], successes:int = 0):
        botch = False
        results.extend(exploded_results)
        if successes >= 1:
            botch = False
        else:
            for die in results:
                if die == 1:
                    botch = True
        return botch

    def check_explode(self, results:list):
        exploded_results = []
        for die in results:
            current_die = die
            while current_die >= self.again:
                current_die = random.randint(1, 10)
                exploded_results.append(current_die)
        return exploded_results
    
    def check_catastrophic_success(self,divine_results:list):
        cs = False
        if any(die >= self.tn for die in divine_results):
            cs = True
        return cs
    
    def check_mortal_fail(self, mortal_dice:list):
        mortal_fail = False
        if any(die < self.tn for die in mortal_dice):
            mortal_fail = True
        return mortal_fail
    

