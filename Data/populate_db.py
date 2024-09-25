import sqlite3
import pandas as pd
import os

def initialize_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Create tables (if they don't exist)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Team (
        TeamID INTEGER PRIMARY KEY AUTOINCREMENT,
        TeamName TEXT NOT NULL UNIQUE,
        CoachName TEXT,
        Conference TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Player (
        PlayerID INTEGER PRIMARY KEY AUTOINCREMENT,
        TeamID INTEGER NOT NULL,
        Name TEXT NOT NULL,
        Position TEXT,
        JerseyNumber INTEGER NOT NULL,
        FOREIGN KEY (TeamID) REFERENCES Team(TeamID) ON DELETE CASCADE,
        UNIQUE(TeamID, JerseyNumber)
    );
    ''')


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OffensiveStats (
        StatID INTEGER PRIMARY KEY AUTOINCREMENT,
        PlayerID INTEGER NOT NULL,
        GamesPlayed INTEGER,
        Possessions REAL,
        PercentTime REAL,
        Points INTEGER,
        PPP REAL,
        FGAttempts INTEGER,
        FGMade INTEGER,
        FGMissed INTEGER,
        FGPercentage REAL,
        EFGPercentage REAL,
        TurnoverPercentage REAL,
        FreeThrowPercentage REAL,
        FTA_FGA REAL,
        PercentShootingFoul REAL,
        ScoringPercentage REAL,
        TwoFGAttempts INTEGER,
        TwoFGMade INTEGER,
        TwoFGMissed INTEGER,
        TwoFGPercentage REAL,
        ThreeFGAttempts INTEGER,
        ThreeFGMade INTEGER,
        ThreeFGMissed INTEGER,
        ThreeFGPercentage REAL,
        ThreePA_FGA REAL,
        FOREIGN KEY (PlayerID) REFERENCES Player(PlayerID) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DefensiveStats (
        StatID INTEGER PRIMARY KEY AUTOINCREMENT,
        PlayerID INTEGER NOT NULL,
        GamesPlayed INTEGER,
        Possessions REAL,
        PercentTime REAL,
        Points INTEGER,
        PPP REAL,
        FGAttempts INTEGER,
        FGMade INTEGER,
        FGMissed INTEGER,
        FGPercentage REAL,
        EFGPercentage REAL,
        TurnoverPercentage REAL,
        FreeThrowPercentage REAL,
        FTA_FGA REAL,
        PercentShootingFoul REAL,
        ScoringPercentage REAL,
        TwoFGAttempts INTEGER,
        TwoFGMade INTEGER,
        TwoFGMissed INTEGER,
        TwoFGPercentage REAL,
        ThreeFGAttempts INTEGER,
        ThreeFGMade INTEGER,
        ThreeFGMissed INTEGER,
        ThreeFGPercentage REAL,
        ThreePA_FGA REAL,
        FOREIGN KEY (PlayerID) REFERENCES Player(PlayerID) ON DELETE CASCADE
    );
    ''')
    conn.commit()
    cursor.close()
    conn.close()


def populate_table(folder_path, type):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)

            try:
                df = pd.read_csv(file_path, skiprows=1, sep=',')
                print(f"Processing {filename}")

                required_columns = ["Player","GP","Poss","%Time","Pts",
                                    "PPP","FG Att","FG Made","FG Miss",
                                    "FG%","eFG%","TO%","%FT","FTA/FGA",
                                    "%SF","Score%","2 FG Att","2 FG Made",
                                    "2 FG Miss","2 FG%","3FG Att","3 FG Made",
                                    "3 FG Miss","3 FG%","3PA/FGA"]
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    print(f"Missing columns in {filename}: {missing_columns}. Skipping this file.")
                    continue

                # Get the team id
                team_name = df['Team'].iloc[0]
                cursor.execute("INSERT OR IGNORE INTO Team (TeamName) VALUES (?)", (team_name,))
                cursor.execute("SELECT TeamID FROM Team WHERE TeamName = ?", (team_name,))
                team_id = cursor.fetchone()[0]

                stats_data = []
                for index, row in df.iterrows():
                    row = row.fillna(value={'Player': None, 'Position': None, 'Jersey #': None})
                    cursor.execute('''
                    SELECT PlayerID FROM Player WHERE TeamID = ? AND JerseyNumber = ?
                    ''', (team_id, row['Jersey #']))
                    result = cursor.fetchone()
                    
                    if result:
                        player_id = result[0]
                    else:
                        cursor.execute('''
                        INSERT INTO Player (TeamID, Name, Position, JerseyNumber)
                        VALUES (?, ?, ?, ?)
                        ''', (team_id, row['Player'], None, row['Jersey #']))
                        player_id = cursor.lastrowid

                    stats_data.append((
                        player_id,
                        row['GP'],
                        row['Poss'],
                        row['%Time'],
                        row['Pts'],
                        row['PPP'],
                        row['FG Att'],
                        row['FG Made'],
                        row['FG Miss'],
                        row['FG%'],
                        row['eFG%'],
                        row['TO%'],
                        row['%FT'],
                        row['FTA/FGA'],
                        row['%SF'],
                        row['Score%'],
                        row['2 FG Att'],
                        row['2 FG Made'],
                        row['2 FG Miss'],
                        row['2 FG%'],
                        row['3FG Att'],
                        row['3 FG Made'],
                        row['3 FG Miss'],
                        row['3 FG%'],
                        row['3PA/FGA']
                    ))
                if type == "offensive":
                    cursor.executemany('''
                    INSERT INTO OffensiveStats (
                        PlayerID, GamesPlayed, Possessions, PercentTime, Points, PPP, 
                        FGAttempts, FGMade, FGMissed, FGPercentage, EFGPercentage, 
                        TurnoverPercentage, FreeThrowPercentage, FTA_FGA, PercentShootingFoul, ScoringPercentage, 
                        TwoFGAttempts, TwoFGMade, TwoFGMissed, TwoFGPercentage, 
                        ThreeFGAttempts, ThreeFGMade, ThreeFGMissed, ThreeFGPercentage, ThreePA_FGA
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', stats_data)
                else:
                    cursor.executemany('''
                    INSERT INTO DefensiveStats (
                        PlayerID, GamesPlayed, Possessions, PercentTime, Points, PPP, 
                        FGAttempts, FGMade, FGMissed, FGPercentage, EFGPercentage, 
                        TurnoverPercentage, FreeThrowPercentage, FTA_FGA, PercentShootingFoul, ScoringPercentage, 
                        TwoFGAttempts, TwoFGMade, TwoFGMissed, TwoFGPercentage, 
                        ThreeFGAttempts, ThreeFGMade, ThreeFGMissed, ThreeFGPercentage, ThreePA_FGA
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', stats_data)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    conn.commit()
    cursor.close()
    conn.close()

def main():
    initialize_db()
    populate_table("csv/offensive", "offensive")
    populate_table("csv/defensive", "defensive")

if __name__ == '__main__':
    main()