import pulp
import pandas as pd
from typing import List, Optional, Dict
import logging

def find_optimal_full_team(
    all_players: pd.DataFrame,
    total_budget: float = 100.0,
    bench_gk_weight: float = 0.2,
    bench_weight: float = 0.3,
    team_limit: int = 3,
    position_requirements: Dict[str, int] = None
) -> Dict[str, List[int]]:
    """
    Finds the optimal full team (starters + bench) using linear programming.

    Parameters:
    - all_players (pd.DataFrame): DataFrame containing all player data.
    - total_budget (float): Total allowed budget.
    - bench_gk_weight (float): Weight for bench goalkeepers.
    - bench_weight (float): Weight for other bench players.
    - team_limit (int): Maximum number of players allowed per team.
    - position_requirements (Dict[str, int], optional): Number of starters per position.

    Returns:
    - team (Dict[str, List[int]]): Dictionary containing 'starters' and 'bench' player IDs.
    """
    if position_requirements is None:
        position_requirements = {
            'GK': 1,
            'Defender': 3,
            'Midfielder': 4,
            'Forward': 3
        }

    # Initialize problem
    prob = pulp.LpProblem("FPL_Full_Team_Optimization", pulp.LpMaximize)

    # Decision variables for starters and bench
    starters_vars = pulp.LpVariable.dicts("Starter", all_players['player_id'], 0, 1, pulp.LpBinary)
    bench_vars = pulp.LpVariable.dicts("Bench", all_players['player_id'], 0, 1, pulp.LpBinary)

    # Objective: Maximize total points (starters + weighted bench)
    prob += pulp.lpSum([
        all_players.loc[player_id, 'total_points'] * starters_vars[player_id] +
        all_players.loc[player_id, 'total_points'] * bench_weight * bench_vars[player_id]
        for player_id in all_players['player_id']
    ]) + pulp.lpSum([
        all_players.loc[player_id, 'total_points'] * (bench_gk_weight - bench_weight) * bench_vars[player_id]
        for player_id in all_players['player_id'] if all_players.loc[player_id, 'element_type'] == 'GK'
    ]), "Total_Points"

    # Total budget constraint
    prob += pulp.lpSum([
        all_players.loc[player_id, 'now_cost'] * starters_vars[player_id] +
        all_players.loc[player_id, 'now_cost'] * bench_vars[player_id]
        for player_id in all_players['player_id']
    ]) <= total_budget, "Total_Cost"

    # Team constraints
    teams = all_players['team_code'].unique()
    for team in teams:
        team_players = all_players[all_players['team_code'] == team]['player_id']
        prob += pulp.lpSum([
            starters_vars[player_id] + bench_vars[player_id] for player_id in team_players
        ]) <= team_limit, f"Team_Limit_{team}"

    # Position constraints for starters
    for position, required_count in position_requirements.items():
        position_players = all_players[all_players['element_type'] == position]['player_id']
        prob += pulp.lpSum([
            starters_vars[player_id] for player_id in position_players
        ]) == required_count, f"Starter_Position_{position}"

    # Total number of starters and bench players
    prob += pulp.lpSum([starters_vars[player_id] for player_id in all_players['player_id']]) == sum(position_requirements.values()), "Total_Starters"
    prob += pulp.lpSum([bench_vars[player_id] for player_id in all_players['player_id']]) == 4, "Total_Bench_Players"  # Typically 7 bench spots

    # Ensure that a player cannot be both a starter and a bench player
    for player_id in all_players['player_id']:
        prob += starters_vars[player_id] + bench_vars[player_id] <= 1, f"Starter_Bench_Exclusive_{player_id}"

    # Solve the problem
    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)

    # Check if an optimal solution was found
    if pulp.LpStatus[prob.status] != 'Optimal':
        logging.warning("No optimal solution found for the full team.")
        return {}

    # Extract selected players
    starters = [player_id for player_id in all_players['player_id'] if pulp.value(starters_vars[player_id]) == 1]
    bench = [player_id for player_id in all_players['player_id'] if pulp.value(bench_vars[player_id]) == 1]

    return {'starters': starters, 'bench': bench}