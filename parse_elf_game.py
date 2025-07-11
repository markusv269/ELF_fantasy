import pandas as pd

url = "https://raw.githubusercontent.com/armstjc/european-league-of-football-data-repository/main/game_stats/player/2025_elf_player_stats.csv"
elf_stats = pd.read_csv(url)

def get_game_stats(game_id):
    """
    Parses the ELF game data from a CSV file.
    Args:
        game_id (str): The Game ID, e.g. "hdmb2507"
    Returns:
        pd.DataFrame: The game data as a DataFrame
    """
    # Filter the DataFrame for the specific game_id
    game_data = elf_stats[elf_stats['game_id'] == game_id]
    if game_data.empty:
        raise ValueError(f"No data found for game_id: {game_id}")
    return game_data.reset_index(drop=True)