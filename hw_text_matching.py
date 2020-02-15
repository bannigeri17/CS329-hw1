from typing import Dict, Any, List

from emora_stdm import KnowledgeBase, DialogueFlow, Macro, Ngrams
from enum import Enum, auto
import json, csv

vg_dict = {}
with open("vgsales.csv", newline='') as csvfile:
    file_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in file_reader:
        key = row[1].lower()
        vg_dict[key] = row[2:]

class FAV_GAME(Macro):

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):

        if 'device' in vars:
            return our_favorite[vars['device']]

# TODO: Update the State enum as needed
class State(Enum):
    START = 0
    INIT_PROMPT = auto()
    QUES1 = auto()  # What do you most often play video games on?
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

    QUES1b = auto()  #
    ANS1b = auto()

    QUES2 = auto()
    ANS2 = auto()

    ERR = auto()


# TODO: create the ontology as needed

#with open("gaming_ontology.json") as json_file:
#    ontology = json.load(json_file)
#ontology = json.load('gaming_ontology.json')

ontology = {
  "ontology":{
    "brands":
    [
      "atari",
      "playstation",
      "nintendo",
      "xbox",
      "pc",
      "sega"
    ],
    "atari": [
      "2600"
    ],
    "playstation":[
      "ps2",
      "ps3",
      "ps4",
      "psp"
    ],
    "nintendo":[
      "switch",
      "nes",
      "snes",
      "ds",
      "n64",
      "wii",
      "gameboy"
    ],
    "xbox":[
      "360",
      "one"
    ],
    "pc":[
      "laptop",
      "computer",
      "desktop"
    ],
    "sega": [
      "genesis",
      "dreamcast"
    ],
    "gameboy":[
      "color",
      "advance",

    ],
    "ds":[
      "3ds",
      "2ds",
      "dsi",
      "ds"
    ],
    "genesis": [
      "genesis",
      "megadrive"
    ]
  }
}

knowledge = KnowledgeBase()
knowledge.load_json(ontology)
df = DialogueFlow(State.START, initial_speaker=DialogueFlow.Speaker.SYSTEM, kb=knowledge)

df.add_system_transition(State.START, State.INIT_PROMPT, '"Hi, do you play video games?"')
df.add_user_transition(State.INIT_PROMPT, State.QUES1, "{yes,yeah}")

df.add_system_transition(State.QUES1, State.ANS1, '"What do you most often play video games on?"')
df.add_user_transition(State.ANS1, State.ATARI, "[$device={#ONT(atari),atari}]")
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
df.add_user_transition(State.GAMEBOY_ANS, State.NINTENDO, '"[$device = #ONT(ds)]"')

df.add_system_transition(State.ATARI, State.QUES1b, '"Is there anything you like about using Atari?"')
df.add_system_transition(State.PLAYSTATION, State.QUES1b, '"Is there anything you like about using a Playstation console?"')
df.add_system_transition(State.NINTENDO, State.QUES1b, '"Is there anything you like about using a Nintendo device?"')
df.add_system_transition(State.XBOX, State.QUES1b, '"Is there anything you like about using Xbox?"')
df.add_system_transition(State.PC, State.QUES1b, '"Is there anything you like about gaming with a PC?"')
df.add_system_transition(State.SEGA, State.QUES1b, '"Is there anything you like about Sega?"')

df.add_user_transition(State.QUES1b, State.ANS1b, '-{no,not really, nah}')
df.add_user_transition(State.QUES1b, State.QUES2, '{no,not really, no}')

df.add_system_transition(State.QUES2,State.ANS2, "What's your favorite game to play on your $device , mine is #FAV_GAME")

df.set_error_successor(State.INIT_PROMPT, State.ERR)
# TODO: create your own dialogue manager


df.run(debugging=False)
