# Note: 1000 tokens ~ 750 words
# Note: def_a_llama will always request to speak.
# Note: List of full history is history.txt

"""Lineup:
GROQ:
1. meta-llama/llama-4-scout-17b-16e-instruct (Working)
2. llama-3.1-8b-instant
3. llama-3.3-70b-versatile
4. meta-llama/llama-4-maverick-17b-128e-instruct
5. definitely a llama
6. player
"""

from groq import Groq
from dotenv import load_dotenv
import os
import random
import prompts_list as pl

load_dotenv()
models = {1: "meta-llama/llama-4-scout-17b-16e-instruct", 2: "llama-3.1-8b-instant", 3: "llama-3.3-70b-versatile", 4: "meta-llama/llama-4-maverick-17b-128e-instruct", 5: "def_a_llama", 6: "user"}

def update_history(text):
    with open('history.txt', 'a') as f:
        f.write(f"{text}\n")

def clear_history():
    with open('history.txt', 'w') as f:
        f.truncate(0)

def get_random_response(start=None,stop=None): # indexed from 0, do start = None to start from beginning, stop = None to read until end
    with open("responses.txt", 'r') as file:
        lines = file.readlines()
        if start is not None:
            lines = lines[start:]
        if stop is not None:
            lines = lines[:stop]
    return random.choice(lines).strip() 

def count_votes(votes):
    vote_count = {}
    for vote in votes:
        vote_count[vote] = vote_count.get(vote, 0) + 1
    if not vote_count:
        return None
    max_count = max(vote_count.values())
    winners = [k for k, v in vote_count.items() if v == max_count]
    return winners if len(winners) > 1 else winners[0] if winners else None


def ask(model, keynum, user, system="", start=None, stop=None): # model = model, user = user prompt, system = system prompt, start and stop for get_random_response()
    if model == models[1] or model == models[2] or model == models[3] or model == models[4]:
        client = Groq(
            api_key=os.environ.get(f"GROQ_API_KEY_{str(keynum)}"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system,
                },
                {
                    "role": "user",
                    "content": pl.add_history() + "\n" + user,
                }
            ],
            model = model,
        )
        return chat_completion.choices[0].message.content

    elif model == "def_a_llama":
        return get_random_response(start, stop)
    
    elif model == "user":
        print(user)
        return input("\n")
    
    else:
        raise ValueError("Invalid model name")
        

class Player:
    def __init__(self, keynum, id, name, model, role, status="alive"):
        self.key = keynum # api_key number used
        self.id = id # 0-9, used for voting
        self.name = name 
        self.model = model
        self.role = role
        self.status = status

class Game:
    def __init__(self, user, messages_per_round = 30, player_num = 10, mafia_num = 2, doctor_num = 1, defallamachance = 0.0057, pause = True): # default to 5% chance of 1 def_a_llama
        """
        NOTES: 
        defallamachance is chance that any one non-user player is definitely a llama. 
        formula (defallamachance = d, % chance of 1 def_a llama = p, number of players = n):
        p = 1 - (1-d)^(n-1)
        d = 1-(1-p)^(1/(n-1))
        def_a_llama does not work well above 10 players (can only vote, mention llamas 0-9)"""

        self.user = user # User is player?
        self.messages_per_round = messages_per_round
        self.player_num = player_num
        self.mafia_num = mafia_num
        self.doctor_num = doctor_num
        self.defallamachance = defallamachance
        self.players = []
        self.alive_players = []
        self.mafia_players = []
        self.doctor_players = []
        self.villager_players = []
        self.night_num = 0
        self.messages_this_day = 0
        self.pause = pause # Whether you want to wait for user between each statement
        
    def setup_players(self):
        roles = ["mafia"] * self.mafia_num + ["doctor"] * self.doctor_num + ["villager"] * (self.player_num - self.mafia_num - self.doctor_num)
        random.shuffle(roles)
        
        # Pick a random position for the user player
        user_position = random.randint(0, self.player_num - 1) if self.user else None
        
        for i in range(self.player_num):
            if i == user_position:
                model = "user"
            else:
                # Check for def_a_llama first
                if random.random() < self.defallamachance:
                    model = "def_a_llama"
                else:
                    # Choose from other models (1, 2, 3, 4) with equal chance
                    other_models = [1, 2, 3, 4]
                    chosen_key = random.choice(other_models)
                    model = models.get(chosen_key)
            
            self.players.append(Player(random.randint(1,4), i, f"Llama {i}", model, roles[i]))
            if roles[i] == "mafia":
                self.mafia_players.append(self.players[-1])
            if roles[i] == "doctor":
                self.doctor_players.append(self.players[-1])
            else:
                self.villager_players.append(self.players[-1])
        self.alive_players = self.players.copy()


    def check_win(self):
        mafia_alive = sum(1 for p in self.alive_players if p.role == "mafia")
        doctor_alive = sum(1 for p in self.alive_players if p.role == "doctor")
        villager_alive = sum(1 for p in self.alive_players if p.role == "villager")
        
        if mafia_alive == 0:
            return "All mafia eliminated. Town win!"
        elif mafia_alive >= doctor_alive + villager_alive:
            return "Mafia outnumber the town. Mafia win!"
        else:
            return False


    def update_alive(self):
        self.alive_players = [p for p in self.players if p.status == "alive"]


    def mafia_kill(self):
        kill_votes = []
        for p in self.mafia_players:
            if p.status == "alive":
                vote = ask(p.model, p.key, pl.mafia_night(self.alive_players), pl.system(p.name, p.role, self.mafia_num, self.doctor_num, self.player_num, self.mafia_players),None,11)
                # Match votes against alive player names/ids (e.g. "Llama 9 LLAMALLAMA")
                matched = False
                for ap in self.alive_players:
                    if f"{ap.name} LLAMALLAMA" in vote or f"{ap.id} LLAMALLAMA" in vote:
                        kill_votes.append(ap.id)
                        matched = True
                        break
                if not matched and "abstain LLAMALLAMA" in vote:
                    kill_votes.append("abstain")
        return random.choice(count_votes(kill_votes)) if type(count_votes(kill_votes)) is list else count_votes(kill_votes)
        
        
    def doctor_save(self,past = []): # past should be in order
        saves = []
        for p in self.doctor_players:
            if p.status == "alive":
                vote = ask(p.model, p.key, pl.doctor_night(self.alive_players), pl.system(p.name, p.role, self.mafia_num, self.doctor_num, self.player_num, self.mafia_players),None,11)
                matched = False
                for ap in self.alive_players:
                    if f"{ap.name} LLAMALLAMA" in vote or f"{ap.id} LLAMALLAMA" in vote:
                        saves.append(ap.id)
                        matched = True
                        break
                if not matched and "abstain LLAMALLAMA" in vote:
                    saves.append("abstain")
        return [s for s in saves if s not in past and s != "abstain"]
        
        
    def discussion(self):
        random.shuffle(self.alive_players)
        for _ in range(2):
            for p in self.alive_players:
                input("Press Enter") if self.pause else None
                response = ask(p.model, p.key, pl.rr_reply_check(), pl.system(p.name, p.role, self.mafia_num, self.doctor_num, self.player_num, self.mafia_players),11)
                if "abstain LLAMALLAMA" in response:
                    update_history(f"{p.name} abstained from speaking.")
                    print(f"{"You" if p.model == "user" else p.name} abstained from speaking.\n")
                else:
                    update_history(f"{p.name}: {response}")
                    print(f"{"You" if p.model == "user" else p.name}: {response}\n")
                    self.messages_this_day += 1
        
        # Voting phase: continue until message quota reached
        player_by_id = {p.id: p for p in self.alive_players}
        while self.messages_this_day < self.messages_per_round:
            speaker_votes = []
            for p in self.alive_players:
                response = ask(p.model, p.key, pl.reply_vote(self.alive_players), pl.system(p.name, p.role, self.mafia_num, self.doctor_num, self.player_num, self.mafia_players), start=None, stop=11)
                matched = False
                for ap in self.alive_players:
                    if f"{ap.name} LLAMALLAMA" in response or f"{ap.id} LLAMALLAMA" in response:
                        speaker_votes.append(ap.id)
                        matched = True
                        break
                if not matched and "abstain LLAMALLAMA" in response:
                    speaker_votes.append("abstain")
            chosen_id = random.choice(count_votes(speaker_votes)) if type(count_votes(speaker_votes)) is list else count_votes(speaker_votes)
            if chosen_id != "abstain":
                print(f"{"You were" if player_by_id[chosen_id].model == "user" else player_by_id[chosen_id].name + " was"} chosen to speak next.\n")
                chosen_player = player_by_id[chosen_id]
                response = ask(chosen_player.model, chosen_player.key, pl.reply_say(), pl.system(chosen_player.name, chosen_player.role, self.mafia_num, self.doctor_num, self.player_num, self.mafia_players), 11)
                if "abstain LLAMALLAMA" in response:
                    update_history(f"{chosen_player.name} abstained from speaking.")
                    print(f"\n{"You" if chosen_player.model == "user" else chosen_player.name} abstained from speaking.\n")
                    input("Press Enter") if self.pause else None
                else:
                    update_history(f"{chosen_player.name}: {response}")
                    print(f"\n{"You" if chosen_player.model == "user" else chosen_player.name}: {response}\n")
                    input("Press Enter") if self.pause else None
                    self.messages_this_day += 1


    def vote_round(self): 
        votes = []
        random.shuffle(self.alive_players)
        for p in self.alive_players: 
            response = ask(p.model, p.key, pl.vote(self.alive_players), pl.system(p.name, p.role, self.mafia_num, self.doctor_num, self.player_num, self.mafia_players), start=None, stop=11)
            matched = False
            for ap in self.alive_players:
                if f"{ap.name} LLAMALLAMA" in response or f"{ap.id} LLAMALLAMA" in response:
                    votes.append(ap.id)
                    print(f"{"You" if p.model == "user" else p.name} voted for {response.replace(' LLAMALLAMA','')}.")
                    update_history(f"{p.name} voted for {response.replace(' LLAMALLAMA','')}.")
                    matched = True
                    break
            if not matched and "abstain LLAMALLAMA" in response:
                print(f"{"You" if p.model == "user" else p.name} abstained from voting.")
                update_history(f"{p.name} abstianed from voting.")
                votes.append("abstain")
        chosen_vote = random.choice(count_votes(votes)) if type(count_votes(votes)) is list else count_votes(votes)
        if chosen_vote != "abstain":
            voted_player = [p for p in self.alive_players if p.id == chosen_vote][0]
            voted_player.status = "dead"
            update_history(f"{voted_player.name} was voted out by the town. They were {"not" if voted_player.role != "mafia" else ""} mafia.")
            print(f"{"You were" if voted_player.model == "user" else voted_player.name + " was"} voted out by the town. They were {"not" if voted_player.role != "mafia" else ""} mafia.\n")


    def run_game(self):
        print("At pauses, press Enter to continue")
        input("Press Enter")
        clear_history()
        self.setup_players()
        players_by_id = {p.id: p for p in self.players}

        for p in self.players:
            print(f"Player {p.id}: {p.name}, Role: {p.role}, Model: {p.model}") # debug
            if p.model == "user":
                print(pl.system(p.name, p.role, self.mafia_num, self.doctor_num, self.player_num, self.mafia_players)) # show system prompt to user

        while not self.check_win():
            self.night_num += 1
            self.messages_this_day = 0
            past_saves = []
            update_history(f"Night {self.night_num} begins.")
            print(f"Night {self.night_num} begins.")
            input("Press Enter") if self.pause else None
            
            kill = self.mafia_kill()
            saves = self.doctor_save(past_saves)
            if kill is None or kill == "abstain":
                update_history("No kill tonight.")
                print("No kill tonight.")
                input("Press Enter") if self.pause else None
            elif kill in saves:
                update_history(f"No kills tonight. The doctor(s) saved someone.")
                print(f"No kills tonight. The doctor(s) saved someone.")
                input("Press Enter") if self.pause else None
            else:
                update_history(f"Llama {kill} was killed by the mafia.")
                print(f"Llama {kill} was killed by the mafia.")
                players_by_id[kill].status = "dead"
                input("Press Enter") if self.pause else None
            if saves:
                update_history(f"Doctor(s) attempted to save Llama(s) {', '.join(str(s) for s in saves)}.")
                print(f"Doctor(s) attempted to save Llama(s) {', '.join(str(s) for s in saves)}.")
                input("Press Enter") if self.pause else None
            past_saves = saves
            self.update_alive()

            update_history(f"Day {self.night_num} begins.")
            print(f"Day {self.night_num} begins.")

            self.discussion()
            input("Press Enter") if self.pause else None
            self.vote_round()
            input("Press Enter") if self.pause else None
            self.update_alive()
        
        print(self.check_win())

game = Game(False, 25, 10, 1, 1, .1, True)
game.run_game()