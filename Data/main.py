from fastapi import FastAPI
import csv

app = FastAPI()


def load_athlete_data():
    data = []

    def process_row(row, school):
        player_data = row[None]
        return {
            "name": player_data[0],
            "jersey": player_data[1],
            "team": player_data[2],
            "data": {
                "rank": row["sep="],
                "points": player_data[3],
                "fg_made": player_data[4],
                "fg_miss": player_data[5],
                "fg_att": player_data[6],
                "fg_percentage": player_data[7],
                "efg_percentage": player_data[8],
                "two_fg_made": player_data[9],
                "two_fg_miss": player_data[10],
                "two_fg_att": player_data[11],
                "two_fg_percentage": player_data[12],
                "three_fg_made": player_data[13],
                "three_fg_miss": player_data[14],
                "three_fg_att": player_data[15],
                "three_fg_percentage": player_data[16],
                "free_throw_percentage": player_data[17],
                "score_percentage": player_data[18],
                "sf_percentage": player_data[19],
                "+1": player_data[20],
            },
            "school": school,
        }

    with open("./data/UA_23-24_Stats.csv", mode="r") as file:
        csv_reader = csv.DictReader(file, delimiter=",")
        for row in csv_reader:
            if None not in row or len(row[None]) < 20:
                continue
            data.append(process_row(row, "UA"))

    with open("./data/UTK_23-24_Stats.csv", mode="r") as file:
        csv_reader = csv.DictReader(file, delimiter=",")
        for row in csv_reader:
            if None not in row or len(row[None]) < 20:
                continue
            data.append(process_row(row, "UTK"))

    return data


ATHLETES = load_athlete_data()


@app.get("/athletes")
def get_all_athletes():
    return ATHLETES


@app.get("/athletes/school/{school}")
def get_athletes_by_school(school: str):
    school_athletes = [
        athlete for athlete in ATHLETES if athlete["school"].lower() == school.lower()
    ]
    if school_athletes:
        return school_athletes
    return {"error": "No athletes found for this school"}


@app.get("/athlete/jersey/{jersey_number}")
def get_athlete_by_jersey(jersey_number: int):
    for athlete in ATHLETES:
        if int(athlete["jersey_number"]) == jersey_number:
            return athlete
    return {"error": "Athlete not found"}


@app.get("/athletes/points/{pts_threshold}")
def get_athletes_by_points_threshold(pts_threshold: float):
    players_above_threshold = [
        athlete
        for athlete in ATHLETES
        if float(athlete["data"]["points"]) >= pts_threshold
    ]
    if players_above_threshold:
        return players_above_threshold
    return {"error": "No athletes found with points above threshold"}
