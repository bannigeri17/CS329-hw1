from emora_stdm import KnowledgeBase, DialogueFlow
from enum import Enum, auto
import json


# TODO: Update the State enum as needed
class State(Enum):
    START = 0
    INIT_PROMPT = auto()
    QUES1 = auto() #What do you most often play video games on?
    ANS1 = auto()

    #console brands/device types
    ATARI = auto()
    PLAYSTATION = auto()
    NINTENDO = auto()
    XBOX = auto()
    PC = auto()
    SEGA = auto()

    #edge cases for further specifying types of devices
    GAMEBOY = auto()
    DS = auto()
    GENESIS = auto()

    QUES2 = auto()

    ERR = auto()


# TODO: create the ontology as needed
ontology = {
    "ontology": {

        }
}


knowledge = KnowledgeBase()
knowledge.load_json(ontology)
df = DialogueFlow(State.START, initial_speaker=DialogueFlow.Speaker.SYSTEM, kb=knowledge)

df.add_system_transition(State.START, State.INIT_PROMPT, '"Hi, do you play video games?"')
df.add_user_transition(State.INIT_PROMPT,State.QUES1,"{yes,yeah}")
df.add_system_transition(State.QUES1,State.ANS1,'"What do you most often play video games on?"')
df.add_user_transition(State.ANS1,State.ATARI,'$device={#ONT(atari),atari}')
df.add_user_transition(State.ANS1,State.PLAYSTATION,'$device=#ONT(playstation)')
df.add_user_transition(State.ANS1,State.DS,'$device={#ONT(ds),ds}')
df.add_user_transition(State.ANS1,State.NINTENDO,'$device=#ONT(nintendo)')
df.set_error_successor(State.INIT_PROMPT, State.ERR)
# TODO: create your own dialogue manager


df.run(debugging=False)