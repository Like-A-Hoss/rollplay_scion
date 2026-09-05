class MomentumTracker:
    def __init__(self):
        self.momentum = 0

    def add_momentum(self, amount: int):
        self.momentum += amount

    def remove_momentum(self, amount: int):
        self.momentum -= amount
        if self.momentum < 0:
            self.momentum = 0

    def get_momentum(self) -> int:
        return self.momentum
    
    def reset_momentum(self, player_count: int):
        # Reset momentum based on the number of players in the game
        self.momentum = player_count
        