import csv
import json
from enum import Enum, auto
from typing import Dict, Any, List

from emora_stdm import KnowledgeBase, DialogueFlow, Macro, Ngrams

import videogames

# a dictionary mapping a game title to various data points about it, i.e. platform, release year and genre
vg_dict = {}
# a dictionary using vgsales.csv to map platforms to an arbitrary favorite game from that platform
sys_favs = {}
# dictionary similarly arbitrarily mapping a given genre to system's "favorite" game from that genre
genre_favs = {}
# genre = None

already_recommended = {}

console_dict = {  # mapping the names we match for in our program to their equivalent encoding in vgsales.csv
    'gameboy': 'gb',
    '360': 'x360',
    'laptop': 'pc',
    'computer': 'pc',
    'desktop': 'pc',
    'playstation': 'ps',
    'advance': 'gba',
    'xbox': 'xb',
    'one': 'xone',
    'genesis': 'gen',
    'dreamcast': 'dc'
}

console_brands = {
    "2600":"atari",
    "ps2":"playstation",
    "ps3":"playstation",
    "ps4":"playstation",
    "psp":"playstation",
    "switch":"nintendo",
    "nes":"nintendo",
    "snes":"nintendo",
    "ds":"nintendo",
    "n64":"nintendo",
    "wii":"nintendo",
    "advance":"nintendo",
    "gameboy":"nintendo",
    "3ds":"nintendo",
    "color":"nintendo",
    "2ds":"nintendo",
    "dsi":"nintendo",
    "360":"xbox",
    "one":"xbox",
    "genesis":"sega",
    "dreamcast":"sega",
    "megadrive":"sega",
    "computer":"pc",
    "laptop":"pc",
    "desktop":"pc"
}

console_recs = {
    #kind of arbitrary logic here, mostly just recommend switch unless a more recent console within that brand exists
    "2600":"switch",
    "ps2":"ps4",
    "ps3":"ps4",
    "ps4":"psp",
    "psp":"ps4",
    "switch":"pc",
    "nes":"switch",
    "snes":"switch",
    "ds":"switch",
    "n64":"switch",
    "wii":"switch",
    "advance":"switch",
    "gameboy":"switch",
    "3ds":"switch",
    "color":"switch",
    "2ds":"switch",
    "dsi":"switch",
    "360":"one",
    "one":"pc",
    "genesis":"switch",
    "dreamcast":"switch",
    "megadrive":"switch",
    "computer":"switch",
    "laptop":"switch",
    "desktop":"switch"
}

def get_brand(console_name:str) -> str:
    return console_brands[console_name] if console_brands[console_name] != "pc" else None

with open("vgsales.csv", newline='') as csvfile:
    file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in file_reader:
        key = row[1].lower()
        vg_dict[key] = row[2:]
        if row[2].lower() not in sys_favs:
            sys_key = row[2].lower()
            sys_favs[sys_key] = row[1].lower()
        if row[4].lower() not in genre_favs:
            gen_key = row[4].lower()
            genre_favs[gen_key] = row[1].lower()


# print(sys_favs)
print('')


class SYSTEM_FAV(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if 'device' in vars:
            if vars['device'] in sys_favs:
                return "? My favorite is " + sys_favs[vars['device']] + "!"
            elif console_dict[vars['device']] in sys_favs:
                return "? My favorite is " + console_dict[vars['device']] + "!"
            return "? I don't really have a favorite for that device."


class RECOMMEND_GAME(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        v = None
        g = None
        if 'device' in vars:
            v = vars['device']
        if 'genre' in vars:
            g = vars['genre']

        name = None
        i = 0

        while (name in already_recommended or name is None) and i<100:
            name, console, genre = videogames.get_random_game_from_genre(console_name=v, genre=g, sales_min=10)
            i += 1
            already_recommended.add(name)
            vars['recommendation'] = name
        if not name:
            return f"I don't really have a decent game to recommend for the {v}"
        return f"{name} is a good {genre.lower()} game for the {console}"

class GAME_DETAILS(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        d = vars['device']
        if 'recommendation' in vars:
            r = vars['recommendation']
            sales_df = videogames.get_sales_for_game(r)
            sales_total = sales_df.get_value(0,'Global_Sales')
            rel_year = videogames.get_game_release_year(r)
            return f"{r} has been sold for the {d} since {rel_year}, and has produced a global revenue of ${sales_total} million!\n Do you want a new recommendation or a console recommendation?"

class CONSOLE_RECOMMEND(Macro):

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if 'device' in vars:
            new_d = console_recs(vars['device'])
            vars['device'] = new_d
            return f"I recommend the {new_d}!\nWhat's your favorite game to play on the {new_d}?"


class PLATFORM_BRAND(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if 'device' in vars:
            vars['brand'] = get_brand(vars['device'])
            if vars['brand'] is not None:
                return f"{vars['device']} is a {vars['brand']} device!"

class FAV_GAME_GENRE(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if 'fav_game' in vars:
            #print(vars['fav_game'])
            if vars['fav_game'] in vg_dict:
                genre = vg_dict['fav_game']
                vars['genre'] = genre
                #print("genre: " + genre)
                return "Do you prefer " + genre + "games?"


class State(Enum):
    START = 0
    INIT_PROMPT = auto()
    QUES1a = auto()  # What do you most often play video games on?
    ANS1 = auto()

    # console brands/device types
    ATARI = auto()
    PLAYSTATION = auto()
    NINTENDO = auto()
    XBOX = auto()
    PC = auto()
    SEGA = auto()
    UNNAMED_CONSOLE = auto()

    # edge cases for further specifying types of devices
    GAMEBOY = auto()
    DS = auto()
    GENESIS = auto()  # not sure if we need to handle any cases here
    DS_ANS = auto()
    GAMEBOY_ANS = auto()
    XBOX_ANS = auto()
    ATARI_ANS = auto()

    QUES2 = auto()  # Is there anything you like about using a $brand device?
    ANS2 = auto()

    QUES3 = auto()  # What's your favorite game to play on your $device?
    ANS3 = auto()

    QUES3b = auto()  # do you have a favorite genre of video games?
    ANS3b = auto()

    QUES3c = auto()
    ANS3c = auto()

    QUES4 = auto()  # Do you prefer $genre games?
    ANS4 = auto()

    QUES5 = auto()  # What do you like about $genre games?
    ANS5 = auto()

    QUES6 = auto() # What

    ERR = auto()

    QUES1b = auto()
    QUES1c = auto()
    RECOMMEND = auto()
    # Error handling
    UNKNOWN_ANS = auto()
    WHATEV = auto()
    UNKNOWN_CONSOLE = auto()
    LOOPBACK = auto()


ontology = json.loads(open('gaming_ontology.json').read())

knowledge = KnowledgeBase()
knowledge.load_json(ontology)
df = DialogueFlow(State.START, initial_speaker=DialogueFlow.Speaker.SYSTEM, kb=knowledge,
                  macros={"SYSTEM_FAV": SYSTEM_FAV(),
                          "FAV_GAME_GENRE": FAV_GAME_GENRE(),
                          "RECOMMEND_GAME":RECOMMEND_GAME(),
                          "PLATFORM_BRAND":PLATFORM_BRAND()})

# First Question
df.add_system_transition(State.START, State.INIT_PROMPT, '"Hi, do you play video games?"')

# Three possible answers from user
df.add_user_transition(State.INIT_PROMPT, State.QUES1a, "[#ONT(yes)]")
df.add_user_transition(State.INIT_PROMPT, State.QUES1b, "[#ONT(no)]")
df.set_error_successor(State.INIT_PROMPT, State.QUES1c)

# Question 1: System can handle in 3 possible ways
df.add_system_transition(State.QUES1a, State.ANS1, '"What do you most often play video games on?"')
df.add_system_transition(State.QUES1b, State.LOOPBACK, '"I am sorry to hear that. '
                                                       'I am afraid we cannot be friends then."')
df.add_system_transition(State.QUES1c, State.INIT_PROMPT, '"Sorry. I didn\'t catch that, '
                                                          'can you rephrase your answer?"')

# Device
df.add_user_transition(State.ANS1, State.QUES2, "$device=[{gameboy,wii}]")
#"[$device={#ONT(playstation), #ONT(sega), #ONT(ds), #ONT(gameboy), #ONT(nintendo), #ONT(xbox), #ONT(pc)}]"
df.add_user_transition(State.ANS1, State.ATARI, "[{#ONT(atari)}]")

df.set_error_successor(State.ANS1, State.UNKNOWN_CONSOLE)
df.add_system_transition(State.UNKNOWN_CONSOLE, State.ANS1, '"Sorry. I don\'t know that one. '
                                                            'Give me the name of one of your game consoles"')

df.add_system_transition(State.ATARI, State.ATARI_ANS, '"What model Atari do you have?"')
df.add_user_transition(State.ATARI_ANS, State.QUES2, '[$device=#ONT(atari)]')
df.set_error_successor(State.ATARI_ANS, State.UNKNOWN_CONSOLE)


# Question 3
df.add_system_transition(State.QUES2, State.ANS2, '"#PLATFORM_BRAND Is there anything you like about using device ?"')

df.add_user_transition(State.ANS2, State.QUES3b, "[#ONT(no)]")
df.add_user_transition(State.ANS2, State.QUES3, "[#ONT(yes)]")

df.add_system_transition(State.QUES3b, State.ANS3, "well do you at least have a favorite game "
                                                 "to play on your $device #SYSTEM_FAV")
df.add_system_transition(State.QUES3, State.ANS3, "whats your favorite game to play on your $device #SYSTEM_FAV")

# TODO: FIGURE OUT HOW TO ASSIGN VARIABLE DIRECTLY TO INPUT TEXT, OR HOW TO RECEIVE THE GAME INPUT
df.add_user_transition(State.ANS3, State.QUES4, "$fav_game=[-{#ONT(no)}]")
df.add_user_transition(State.ANS3, State.QUES3b, "[#ONT(no)]")

df.add_system_transition(State.QUES3b, State.ANS3b, '"Do you have a favorite genre of video game?"')

df.add_user_transition(State.ANS3b, State.RECOMMEND, "[#ONT(no)]")
df.add_user_transition(State.ANS3b, State.QUES3c, "[#ONT(yes)]")
df.add_user_transition(State.ANS3b, State.ANS3c, "$genre=[-{#ONT(no), #ONT(yes)}]")
df.add_system_transition(State.QUES3c, State.QUES3b, 'Great, please tell me')

df.add_system_transition(State.ANS3c, State.QUES4, "#RECOMMEND_GAME")
df.add_system_transition(State.QUES4, State.ANS4, "#FAV_GAME_GENRE")

df.add_user_transition(State.ANS4, State.QUES5, "")

df.add_system_transition(State.QUES6, State.ANS6, 'Do you want to learn more about $recommendation , a different recommendation or a console recommendation?')

df.add_user_transition(State.ANS6, State.QUES6b, '[more]')
df.add_user_transition(State.ANS6, State.QUES6c, '[different,game]')
df.add_user_transition(State.ANS6, State.QUES6d, '[console]')

df.add_system_transition(State.QUES6b,State.ANS6,'#GAME_DETAILS')
df.add_system_transition(State.QUES6c,State.ANS6,'#RECOMMEND_GAME')
df.add_system_transition(State.QUES6d,State.ANS3,'#RECOMMEND_CONSOLE')

df.add_system_transition(State.QUES7,State.ANS7, '"Do you like $recommendation ?"')
df.add_user_transition(State.ANS7, State.QUES8, "#ONT(yes)")
df.add_user_transition(State.ANS7, State.QUES6, '#ONT(no)')

df.add_system_transition(State.QUES8,State.ANS8, "What do you like about $recommendation ?")

df.add_user_transition(State.ANS8, State.END, "/.*/")

df.add_user_transition(State.LOOPBACK, State.START, "/.*/")
# Error transitions
df.add_system_transition(State.UNKNOWN_ANS, State.WHATEV, "I'm not sure I follow.")
df.set_error_successor(State.WHATEV, State.START)

df.run(debugging=False)
