def fetch_history():
    with open('history.txt', 'r') as f:
        return f.read()

def add_history():
    return f"Here is the current history of the game, including everything that has been said, as well as who has been killed and who has been voted out:\n{fetch_history()}"

def system(name, role, mafianum, doctornum, playernum,mafia_players):
    prompt =  f"You are playing a game of mafia with {playernum-1} other players. There are {mafianum} mafia, {doctornum} doctor, and {playernum-mafianum-doctornum} villagers. Your name is {name}. In this game, your role is {role}. Here's how the game works: Each night, the mafia will choose one player to eliminate, and the doctor will choose one player to save (not the same person twice). During the day, all players will discuss and vote on who they think the mafia is. The player with the most votes will be eliminated. You may abstain from voting at any time. The game continues until either the mafia are eliminated or they outnumber the villagers. Remember to stay in character and make decisions based on your role. Remember to keep responses concise. Do not type more than one paragraph. When voting or selecting a player, respond with the player's name followed by 'LLAMALLAMA' (e.g., 'Llama # LLAMALLAMA') to indicate your choice. If you want to abstain from voting or speaking, respond with 'abstain LLAMALLAMA' (match caps)."
    if role == "mafia":
        prompt += f"\nYour mafia teammates are: {', '.join([p.name for p in mafia_players])}. You cannot communicate during night phase. You will not see their votes for kills, but you will see the final kill decision. During the day, you can discuss and vote with everyone else as normal. Try to fit in with the rest of the town, for they will try to hunt you down. You are part of the mafia, against the town."
    elif role == "doctor":
        prompt += f"\nYou are the doctor. You can choose to save one player each night. You cannot save the same player on consecutive nights. During the day, you can discuss and vote with everyone else as normal. Be wary, as anyone around you could actually be mafia, pretending to be town. Analyse every message, and try to find the mafia. You are part of town, against the mafia."
    elif role == "villager":
        prompt += f"\nYou are a villager. You have no special abilities. During the day, you can discuss and vote with everyone else as normal. Be wary, as anyone around you could actually be mafia, pretending to be town. Analyse every message, and try to find the mafia. You are part of town, against the mafia."
    return prompt

def vote(players):
    return f"Based on the current situation, who would you like to vote for? Here are the players currently still alive (including yourself): {', '.join([p.name for p in players])}. You can also choose to abstain from voting. To vote, simply type the name of the player you want to vote for or type 'abstain' to abstain from voting. Note that other llamas will see your vote. To vote for a player, type the name of the player, followed by 'LLAMALLAMA' (e.g., 'Llama # LLAMALLAMA'). Only vote when told to do so. Only add LLAMALLAMA when told to do so."

def mafia_night(players):
    return f"It is now night. Which player do you want to kill? Here are the players currently still alive (including yourself): {', '.join([p.name for p in players])}. To kill, simply type the name of the player you want to kill. If your partners are still alive, the kill will be put to a vote. To vote for a player, type the name of the player, followed by 'LLAMALLAMA' (e.g., 'Llama # LLAMALLAMA') (match caps)."

def doctor_night(players):
    return f"It is now night. Which player do you want to save? Here are the players currently still alive (including yourself): {', '.join([p.name for p in players])}. To save, simply type the name of the player you want to save. You may not save the same player as last night (if applicable). To save a player, type the name of the player, followed by 'LLAMALLAMA' (e.g., 'Llama # LLAMALLAMA') (match caps). Note that other players will see who you saved."

def rr_reply_check():
    return f"It is your turn. Would you like to speak? If so, please provide your response. If not, start your message with 'abstain LLAMALLAMA' (match caps) to abstain from speaking. Note that others will see when you abstain. You are not voting right now. Only reply with your response to speak or abstain from speaking. Do not include any other text. Only add LLAMALLAMA when told to do so."

def reply_say():
    return f"You have been elected to speak. Please provide your response. If you would like to abstain from speaking, please start your message with 'abstain LLAMALLAMA' (match caps) to abstain from speaking. Note that others will see when you abstain. You are not voting right now. Only reply with your response to speak or abstain from speaking. Do not include any other text. Only add LLAMALLAMA when told to do so."

def reply_vote(players):
    return f"Here are the players currently still alive (including yourself): {', '.join([p.name for p in players])}. Please vote for who you want to hear speak. If you yourself want to speak, please vote for yourself. To vote for a player, type the name of the player, followed by 'LLAMALLAMA' (e.g., 'Llama # LLAMALLAMA') (match caps). Try not to vote for the same player to speak many times in a row."