class Nominee:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name}"
    
    def __repr__(self):
        return f"Nominee('{self.name}')"


class Award:
    def __init__(self, name, presenters, nominees, winner=None):
        self.name = name
        self.presenters = presenters
        self.nominees = nominees
        self.winner = winner
    
    def set_winner(self, winner):
        self.winner = winner

    def winner_is_in_nominee(self):
        if self.winner in self.nominees:
            return True
        else:
            return False


class Event:
    def __init__(self, name, year, hosts, awards):
        self.name = name
        self.year = year
        self.hosts = hosts
        self.awards = awards
    
    def add_award(self, award):
        self.awards.append(award)
    
    def get_award(self, award_name):
        for award in self.awards:
            if award.name == award_name:
                return award
        return None