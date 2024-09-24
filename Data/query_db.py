import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()


def get_players():
    cursor.execute('SELECT PlayerID, Name, JerseyNumber FROM Player')
    players = cursor.fetchall()
    return players

def select_players():
    players = get_players()
    print("Available Players:")
    print("ID: Name (Jersey)")
    for player in players:
        print(f"{player[0]}: {player[1]} ({player[2]})")

    selected_players = []
    while len(selected_players) < 5:
        try:
            jersey_number = int(input(f"Select Player {len(selected_players) + 1} (Jersey Number): "))
            cursor.execute('SELECT PlayerID FROM Player WHERE JerseyNumber = ?', (jersey_number,))
            player = cursor.fetchone()
            selected_players.append(player[0])
        except ValueError:
            print("Invalid input. Please enter a valid PlayerID.")
        except Exception as e:
            print(e)
    return selected_players

def get_player_data(player_ids):
    stats = []  
    for id in player_ids:
        cursor.execute('''
            SELECT p.Name, p.JerseyNumber, s.PPP, s.TwoFGPercentage, s.ThreeFGPercentage
            FROM Player p
            JOIN Stats s ON p.PlayerID = s.PlayerID
            WHERE p.PlayerID = ?
        ''', (id,))
        player_stats = cursor.fetchone()
        if player_stats:
            stats.append(player_stats)
            
    return stats

def main():
    selected_players = select_players()
    player_data = get_player_data(selected_players)
    print("\nPlayer Data:")
    for data in player_data:
        print(f"Name: {data[0]}, JerseyNumber: {data[1]}, PPP: {data[2]}, TwoFGPercentage: {data[3]}%, ThreeFGPercentage: {data[4]}%")
    
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
