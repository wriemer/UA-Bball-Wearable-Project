import math
import requests
import json
import os

import SynergySportsAPI

# Example usage and testing of the SynergySportsAPI class

def main():
    API = SynergySportsAPI.SynergySportsAPI()
    
    ncaa_teams = API.get_teams(API.ncaa_id)
    
    print('TEST TEAM')
    for team in ncaa_teams:
        if team['data']['name'] == 'Georgia':
            API.format_print(team)
        elif team['data']['name'] == 'Auburn':
            API.format_print(team)
    
    
    auburn_roster = API.get_team_roster(API.auburn_id)
    rand_player = auburn_roster['data'][0]

    print('TEST PLAYER')
    API.format_print(rand_player)
    
    
    events = API.get_game_events(API.game_id_1)
    first_event = events['data'][0]
    
    print('TEST EVENTS')
    API.format_print(first_event)

if __name__ == '__main__':
    main()