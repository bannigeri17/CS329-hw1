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
    "wii": "nintendo",
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

def get_brand(game_name:str) -> str:
    return console_brands[game_name] if console_brands[game_name] != "pc" else None


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

        name, console, genre = videogames.get_random_game_from_genre(console_name=v, genre=g, sales_min=10)
        if not name:
            return f"I don't really have a decent game to recommend for the {v}"
        return f"{name} is a good {genre.lower()} game for the {console}"


class FAV_GAME_GENRE(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if 'fav_game' in vars:
            print(vars['fav_game'])
            if vars['fav_game'] in vg_dict:
                genre = vg_dict['fav_game']
                vars['genre'] = genre
                print("genre: " + genre)
                return "Do you prefer " + genre + "games?"
            return "Do you have a favorite genre?"


# TODO: Update the State enum as needed
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

    ERR = auto()

    QUES1b = auto()
    RECOMMEND = auto()
    # Error handling
    UNKNOWN_ANS = auto()
    WHATEV = auto()


ontology = json.loads(open('gaming_ontology.json').read())

knowledge = KnowledgeBase()
knowledge.load_json(ontology)
df = DialogueFlow(State.START, initial_speaker=DialogueFlow.Speaker.SYSTEM, kb=knowledge,
                  macros={"SYSTEM_FAV": SYSTEM_FAV(),
                          "FAV_GAME_GENRE": FAV_GAME_GENRE()})

df.add_system_transition(State.START, State.INIT_PROMPT, '"Hi, do you play video games?"')
df.add_user_transition(State.INIT_PROMPT, State.QUES1a, "[#ONT(yes)]")
df.add_user_transition(State.INIT_PROMPT, State.QUES1b, "[#ONT(no)]")

df.add_system_transition(State.QUES1a, State.ANS1, '"What do you most often play video games on?"')
df.add_system_transition(State.QUES1b, State.ERR, "I am sorry to hear that. I am afraid we cannot be friends then.")

df.add_user_transition(State.ANS1, State.ATARI, "[$device=#ONT(atari)]")
df.add_user_transition(State.ANS1, State.PLAYSTATION, "[$device={#ONT(playstation),playstation}]")
df.add_user_transition(State.ANS1, State.DS, "[$device={#ONT(ds),ds}]")
df.add_user_transition(State.ANS1, State.GAMEBOY, "[$device={#ONT(gameboy),gameboy}]")
df.add_user_transition(State.ANS1, State.NINTENDO, "[$device=#ONT(nintendo)]")
df.add_user_transition(State.ANS1, State.XBOX, "[$device={#ONT(xbox),xbox}]")
df.add_user_transition(State.ANS1, State.PC, "[$device=#ONT(pc)]")
df.add_user_transition(State.ANS1, State.SEGA, "[$device=#ONT(sega)]")
df.add_user_transition(State.ANS1, State.UNNAMED_CONSOLE, "[$device=[console]]")

df.add_system_transition(State.UNNAMED_CONSOLE, State.ANS1, '"What kind of console do you have?"')
df.add_system_transition(State.DS, State.DS_ANS, '"What kind of DS do you have?"')
df.add_user_transition(State.DS_ANS, State.NINTENDO, '"[$device=#ONT(ds)]"')
df.add_system_transition(State.GAMEBOY, State.GAMEBOY_ANS, '"What kind of Gameboy do you have?"')
df.add_user_transition(State.GAMEBOY_ANS, State.NINTENDO, '"[$device = #ONT(gameboy)]"')

df.add_system_transition(State.ATARI, State.QUES2, '"Is there anything you like about using Atari?"')
df.add_system_transition(State.PLAYSTATION, State.QUES2,
                         '"Is there anything you like about using a Playstation console?"')
df.add_system_transition(State.NINTENDO, State.QUES2, '"Is there anything you like about using a Nintendo device?"')
df.add_system_transition(State.XBOX, State.QUES2, '"Is there anything you like about using an Xbox console?"')
df.add_system_transition(State.PC, State.QUES2, '"Is there anything you like about gaming with a PC?"')
df.add_system_transition(State.SEGA, State.QUES2, '"Is there anything you like about using a Sega device?"')

df.add_user_transition(State.QUES2, State.ANS2, "[#ONT(no)]")
df.add_user_transition(State.QUES2, State.QUES3, "[#ONT(yes)]")
df.add_system_transition(State.ANS2, State.ANS3, "well do you at least have a favorite game "
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

# df.add_user_transition(State.ANS4, State.QUES5, "")


# Error transitions
df.add_system_transition(State.UNKNOWN_ANS, State.WHATEV, "I'm not sure I follow.")
df.set_error_successor(State.WHATEV, State.START)

df.run(debugging=False)
