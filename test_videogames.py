# Test class for videogames.py

import videogames as v
import json

if __name__ == '__main__':
    print(v.get_console_game_sales('X360'))
    print(v.get_game_count('X360'))
    print(v.get_sales_for_game('Super Mario Bros'))
    print(v.get_best_selling_game('Wii'))
    print(v.get_console_game_time_range('Wii'))
    # for i in range(20):
    #     print(v.get_random_game_from_genre())
    s = json.loads(open('gaming_ontology.json').read())
    print(v.get_game_genre("Mario Kart Wii"))
    print(s)