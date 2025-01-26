from fetch_data import fetch_fpl_player_data
from process_data import process_player_data
from find_optimal_team import find_optimal_full_team
from display_team import display_team

def main():

    players_data = fetch_fpl_player_data()
    #print(players_data)

    processed_players_data = process_player_data(players_data)
    print(processed_players_data)

    # Define position requirements for starters
    position_requirements = {
        'GK': 1,
        'Defender': 3,
        'Midfielder': 4,
        'Forward': 3
    }

    # Define total budget
    total_budget = 100.0  # £100m

    # Find optimal team
    team = find_optimal_full_team(
        all_players=processed_players_data,
        total_budget=total_budget,
        bench_gk_weight=0.1,
        bench_weight=0.2,
        team_limit=3,
        position_requirements=position_requirements
    )

    # Display the team
    display_team(
        team=team,
        all_players=processed_players_data,
        bench_gk_weight=0.2,
        bench_weight=0.3
    )

if __name__ == "__main__":
    main()