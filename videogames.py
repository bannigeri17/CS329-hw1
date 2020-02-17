import pandas as pd

df = pd.read_csv('vgsales.csv')

def get_game_count(console_name: str) -> int:
    """
    Get the number of games made for a console
    Example answer from chatbot: 'I know x games that were sold for {console name}.'
    """
    pass

def get_console_game_sales(console_name: str) -> float:
    """
    Get the total global sales of games for a given console
    """
    pass

def get_sales_for_game(game_name: str) -> float:
    """
    Get # of global sales for a game
    """
    pass

def get_best_selling_game(console_name: str) -> (str, float):
    """
    Returns the best selling game for the console and its global sales amount
    """
    pass

def get_console_game_time_range(console_name: str) -> (int, int, int):
    """
    Returns a tuple (a, b, c)
    a: Year when first game was sold for the console
    b: Year when last game was sold
    c: b - a, time range
    """
    pass