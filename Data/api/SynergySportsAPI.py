import requests
import json
import os

class SynergySportsAPI:
    """
    Init and config methods
    """
    def __init__(self, config_path='./Data/api/config.json'):
        self.auth_url = "https://auth.synergysportstech.com/connect/token"
        self.base_url = "https://basketball.synergysportstech.com/external/api"
        self.config_path = config_path
        self.access_token = self._get_access_token()

        self.ncaa_id = None
        self.alabama_id = None
        self.auburn_id = None
        
        self._load_config()
        

    def _load_config(self):
        # Load secrets
        with open(self.config_path) as config_file:
            config = json.load(config_file)
            self.ncaa_id = config['other']['ncaa_mens_id']
            self.alabama_id = config['other']['alabama_id']
            self.auburn_id = config['other']['ncaa_men_team_ids']['auburn']
        return config['client_id'], config['client_secret']

    def _get_access_token(self):
        # Get access token for API authentication
        client_id, client_secret = self._load_config()
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'api.basketball.external'
        }
        
        response = requests.post(self.auth_url, data=data)
        return response.json().get('access_token')

    def _get_headers(self):
        # Return headers with Bearer token for authentication
        return {
            'Authorization': f'Bearer {self.access_token}'
        }

    """
    Custom functions
    """
    def get_leagues(self, league_id=None):
        url = f"{self.base_url}/leagues"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_teams(self, league_id=None, team_id=None):
        league_id = league_id or self.ncaa_id
        team_id = team_id or self.alabama_id

        url = f"{self.base_url}/leagues/{league_id}/teams"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        return response.json()['data']
    
    def get_team_roster(self, team_id=None):
        team_id = team_id or self.alabama_id
        
        print("Team ID: ", team_id)

        url = f"{self.base_url}/teams/{team_id}/players"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        res = response.json()
        
        return res
    
    def search_games(self, league_id=None, team_id=None, season_id=None, status=None, min_date=None, max_date=None):
        """
        Search for games with optional filters for league, team, season, status, and date range.
        """
        url = f"{self.base_url}/games"
        params = {
            "leagueId": league_id,
            "teamId": team_id,
            "seasonId": season_id,
            "status": status,
            "minDate": min_date,
            "maxDate": max_date,
            "take": 10  # Limit to 10 games for example purposes, adjust as needed
        }
        
        # Filter out None values from params
        params = {key: value for key, value in params.items() if value is not None}
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()


    def refresh_access_token(self):
        # Refresh the access token manually if needed
        self.access_token = self._get_access_token()


    def format_print(self, response):
        print(json.dumps(response, indent=4))

# Example usage
if __name__ == '__main__':
    api = SynergySportsAPI()
    
    leagues = api.get_leagues()
    
    api.format_print(leagues['data'][0])

    
    teams = api.get_teams()
    
    print(type(teams))
    api.format_print(teams[0])
    

    auburn_roster = api.get_team_roster(api.auburn_id)
    
    api.format_print(auburn_roster)


    # rand_game = api.auburn_game
    
    # game = api.get_game(rand_game)
    
    # print(game)
    
    