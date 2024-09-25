import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

def get_players(team_id):
    cursor.execute('SELECT PlayerID, Name, JerseyNumber FROM Player WHERE TeamID = ?', (team_id,))
    players = cursor.fetchall()
    return players

def get_teams():
    cursor.execute('SELECT TeamID, TeamName FROM Team')
    teams = cursor.fetchall()
    return teams

def select_players():
    teams = get_teams()
    print("\nAvailable Teams:")
    print("ID: Team Name")
    for team in teams:
        print(f"{team[0]}: {team[1]}")

    team_id = None
    while team_id is None:
        try:
            input_team_id = int(input(f"Select Team (id number): "))
            valid_team_ids = [team[0] for team in teams]
            if input_team_id not in valid_team_ids:
                print(f"Team with ID {input_team_id} doesn't exist. Please select a valid team.")
            else:
                team_id = input_team_id
        except ValueError:
            print("Invalid input. Please enter a valid team ID (an integer).")

    cursor.execute("SELECT TeamName FROM Team WHERE TeamID = ?", (team_id,))
    team_name = cursor.fetchone()[0]

    players = get_players(team_id)
    print("\nAvailable Players:")
    print("ID: Name (Jersey)")
    for player in players:
        print(f"{player[0]}: {player[1]} ({player[2]})")

    selected_players = []
    while len(selected_players) < 5:
        try:
            jersey_number = int(input(f"Select Player {len(selected_players) + 1} (Jersey Number): "))
            cursor.execute('SELECT PlayerID FROM Player WHERE TeamID = ? AND JerseyNumber = ?', (team_id, jersey_number))
            player = cursor.fetchone()
            if player:
                if player[0] in selected_players:
                    print(f"Player with Jersey Number {jersey_number} is already selected. Please select a different player.")
                else:
                    selected_players.append(player[0])
            else:
                print(f"No player found with Jersey Number {jersey_number} in the selected team.")
        except ValueError:
            print("Invalid input. Please enter a valid Jersey Number.")
        except Exception as e:
            print(e)
    return team_name, selected_players

def get_offensive_data(player_ids):
    stats = []  
    for id in player_ids:
        cursor.execute('''
            SELECT p.Name, p.JerseyNumber, s.PPP, s.TwoFGPercentage, s.ThreeFGPercentage
            FROM Player p
            JOIN OffensiveStats s ON p.PlayerID = s.PlayerID
            WHERE p.PlayerID = ?
        ''', (id,))
        player_stats = cursor.fetchone()
        if player_stats:
            stats.append(player_stats)
    return stats

def get_defensive_data(player_ids):
    stats = []  
    for id in player_ids:
        cursor.execute('''
            SELECT p.Name, p.JerseyNumber, s.PPP, s.TwoFGPercentage, s.ThreeFGPercentage
            FROM Player p
            JOIN DefensiveStats s ON p.PlayerID = s.PlayerID
            WHERE p.PlayerID = ?
        ''', (id,))
        player_stats = cursor.fetchone()
        if player_stats:
            stats.append(player_stats)
    return stats

def print_data(stats):
    for data in stats:
        print(f"Name: {data[0]}, JerseyNumber: {data[1]}, PPP: {data[2]}, TwoFGPercentage: {data[3]}%, ThreeFGPercentage: {data[4]}%")

def main():
    # I'll eventually just make a team class, I am just lazy right now
    team_1, team_1_players = select_players()
    team1_offensive_data = get_offensive_data(team_1_players)
    team1_defensive_data = get_defensive_data(team_1_players)

    team_2, team_2_players = select_players()
    team2_offensive_data = get_offensive_data(team_2_players)
    team2_defensive_data = get_defensive_data(team_2_players)

    possession = True #True = Team1 O and Team 2 D
    while(True):
        if(possession):
            print(f"\n\n{team_1}: Offense")
            print_data(team1_offensive_data)
            print(f"\n{team_2}: Defense")
            print_data(team2_defensive_data)
        else:
            print(f"\n\n{team_1}: Defense")
            print_data(team1_defensive_data)
            print(f"\n{team_2}: Offense")
            print_data(team2_offensive_data)

        user_input = input("\nEnter '1' to change possession, or '2' to quit: ").strip().lower()
        
        if user_input == '2':
            break 
        elif user_input == '1':
            possession = not possession
        else:
            print("Invalid input, try again.")

    conn.close()

if __name__ == "__main__":
    main()
