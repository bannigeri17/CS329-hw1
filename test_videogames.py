# Test class for videogames.py

import videogames as v

if __name__ == '__main__':
    print(v.get_console_game_sales('X360'))
    print(v.get_game_count('X360'))
    print(v.get_sales_for_game('Super Mario Bros'))
    print(v.get_best_selling_game('Wii'))
    print(v.get_console_game_time_range('Wii'))
    print(v.get_random_game_from_genre())