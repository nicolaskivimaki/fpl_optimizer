import pandas as pd
from typing import List, Optional, Dict
import logging

def display_team(
    team: Dict[str, List[int]],
    all_players: pd.DataFrame,
    bench_gk_weight: float,
    bench_weight: float
):
    """
    Displays the selected team with detailed information.

    Parameters:
    - team (Dict[str, List[int]]): Dictionary containing 'starters' and 'bench' player IDs.
    - all_players (pd.DataFrame): DataFrame containing all player data.
    - bench_gk_weight (float): Weight applied to bench goalkeepers.
    - bench_weight (float): Weight applied to other bench players.
    """
    if not team:
        logging.error("No team to display.")
        return

    starters = team.get('starters', [])
    bench = team.get('bench', [])

    # Calculate costs
    cost_st = all_players.loc[starters, 'now_cost'].sum()
    cost_be = all_players.loc[bench, 'now_cost'].sum()

    logging.info(f"Starters cost: £{cost_st:.1f}m")
    logging.info(f"Bench cost: £{cost_be:.1f}m")

    # Calculate points
    points_st = all_players.loc[starters, 'total_points'].sum()

    bench_players = all_players.loc[bench]
    bench_gk_points = bench_players[bench_players['element_type'] == 'GK']['total_points'].sum() * bench_gk_weight
    bench_other_points = bench_players[bench_players['element_type'] != 'GK']['total_points'].sum() * bench_weight
    points_be = bench_gk_points + bench_other_points

    logging.info(f"Starters total points: {points_st}")
    logging.info(f"Bench total points: {points_be}")

    # Calculate team statistics
    best_total_points = points_st + points_be
    best_comb_cost = cost_st + cost_be
    best_cpp = best_comb_cost / best_total_points if best_total_points != 0 else float('inf')

    logging.info(f"Total points: {best_total_points}")
    logging.info(f"Total cost: £{best_comb_cost:.1f}m")
    logging.info(f"Cost/point: {best_cpp:.2f}m\n")

    # Define the order of positions
    position_order = ['GK', 'Defender', 'Midfielder', 'Forward']

    # Function to print players in a group
    def print_team_group(group_name: str, player_ids: List[int], all_players: pd.DataFrame):
        print(f"\n{group_name}:")
        for position in position_order:
            print(f"\nPosition: {position}")
            for player_id in player_ids:
                player = all_players.loc[player_id]
                if player['element_type'] == position:
                    # Determine the weight used for bench players
                    if group_name == "BENCH" and player['element_type'] == 'GK':
                        weight = bench_gk_weight
                    elif group_name == "BENCH":
                        weight = bench_weight
                    else:
                        weight = 1  # Starters are not weighted
                    adjusted_points = player['total_points'] * weight
                    print(
                        f"Player: {player['first_name']} {player['second_name']} - {player['element_type']} - "
                        f"Team Code: {player['team_code']} - Total points: {player['total_points']} - "
                        f"Cost: £{player['now_cost']}m - Adjusted Points: {adjusted_points:.1f}"
                    )

    # Print Starters and Bench
    print_team_group("STARTERS", starters, all_players)
    print_team_group("BENCH", bench, all_players)