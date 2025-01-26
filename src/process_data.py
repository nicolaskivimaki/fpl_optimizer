import pandas as pd
import logging

def process_player_data(data: dict) -> pd.DataFrame:
    """
    Processes raw FPL data into a cleaned and transformed DataFrame.

    Parameters:
    - data (dict): Raw JSON data from FPL API.

    Returns:
    - players_selected (pd.DataFrame): Cleaned and processed players DataFrame.
    """
    # Map element_type to positions
    position_map = {
        1: 'GK',
        2: 'Defender',
        3: 'Midfielder',
        4: 'Forward'
    }

    # Define price updates
    price_updates = {
        'Mohamed Salah': 13.0,
        'Cole Palmer': 10.8,
        'Bukayo Saka': 10.4,
        'Nicolas Jackson': 7.9,
        'Łukasz Fabiański': 4.0
    }

    # Create DataFrame
    players = pd.DataFrame(data['elements'])

    # Select relevant columns
    selected_columns = [
        'first_name', 'second_name', 'team_code', 'element_type',
        'total_points', 'points_per_game', 'starts', 'now_cost'
    ]
    players_selected = players[selected_columns].copy()

    # Convert 'now_cost' to millions
    players_selected['now_cost'] = players_selected['now_cost'] / 10.0

    # Map positions
    players_selected['element_type'] = players_selected['element_type'].map(position_map)

    # Ensure numeric types
    numeric_cols = ['total_points', 'points_per_game', 'now_cost']
    players_selected[numeric_cols] = players_selected[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # Filter out players with no points per game
    players_selected = players_selected[players_selected['points_per_game'] > 0.0].reset_index(drop=True)

    # Create full name
    players_selected['full_name'] = players_selected['first_name'] + ' ' + players_selected['second_name']

    # Update player prices using vectorized operations
    price_update_df = pd.DataFrame(list(price_updates.items()), columns=['full_name', 'new_now_cost'])
    players_selected = players_selected.merge(price_update_df, on='full_name', how='left')
    players_selected['now_cost'] = players_selected['new_now_cost'].combine_first(players_selected['now_cost'])
    players_selected.drop(columns=['new_now_cost'], inplace=True)

    # Calculate Cost/Points ratio
    players_selected['Cost/Points'] = (players_selected['now_cost'] / players_selected['total_points']).round(2)

    # Reset index to use player indices as IDs
    players_selected.reset_index(inplace=True)  # The current index will serve as player_id
    players_selected.rename(columns={'index': 'player_id'}, inplace=True)

    logging.info(f"Processed {len(players_selected)} players after filtering.")
    return players_selected