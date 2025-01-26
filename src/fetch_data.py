import requests
import logging

def fetch_fpl_player_data():
    api_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(api_url)
    try:
        players_data = response.json()
        logging.info(f"Succesfully fetched player data. Available data keys: {list(players_data.keys())}")
        return players_data
    except Exception as e:
        logging.info("Failed to fetch player data. Status code: {response.status_code}")
        exit(1)
    

#fetched_data = fetch_fpl_player_data()
#print(fetched_data)
