# This file contains main logic for cv operations

from utils import read_video, save_video
from trackers import Tracker
import numpy as np
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from api import SynergySportsAPI
import os
import collections
    
def main(input_video_path, team_1_name, team_1_color, team_2_name, team_2_color):
    print(team_1_name)
    print(team_1_color)
    print(team_2_name)
    print(team_2_color)

     # Read Video
    video_frames, fps = read_video('input_videos/' + input_video_path)

    # Initialize Tracker
    tracker = Tracker('models/models-med/best.pt')

    tracks = tracker.get_object_tracks(video_frames,
                                       read_from_stub=True,
                                       stub_path='stubs/track_stubs.pkl')
    # Get object positions 
    tracker.add_position_to_tracks(tracks)

    # Interpolate missing ball positions
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    tracks["team_1_name"] = team_1_name
    tracks["team_2_name"] = team_2_name

    # Assign Player Teams
    team_assigner = TeamAssigner()
    #team_assigner.assign_team_color(video_frames[0], tracks['players'][0])
    team_assigner.assign_team_colors(team_1_color, team_2_color)
    
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            try:
                team = team_assigner.get_player_team(video_frames[frame_num],   
                                                    track['bbox'],
                                                    player_id)
                tracks['players'][frame_num][player_id]['team'] = team 
                tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]
            except:
                print('ERROR: ', frame_num)

    
    # Assign Ball Acquisition
    player_assigner = PlayerBallAssigner()
    team_ball_control= []

    #Rolling history of team assignment for the last 10 frames
    rolling_history = collections.deque(maxlen=10)

    possession_tracker= []
    for frame_num, player_track in enumerate(tracks['players']):
        try:
            ball_bbox = tracks['ball'][frame_num][1]['bbox']

            possession_tracker.append(player_assigner.assign_ball_to_player(player_track, ball_bbox))
        except: 
            possession_tracker.append(-1)

    possession_tracker = player_assigner.correct_possession_history(possession_tracker, 3)

    team_ball_control= []
    for frame_num, player_track in enumerate(tracks['players']):
        try:
            if possession_tracker[frame_num] != -1:
                current_team = tracks['players'][frame_num][possession_tracker[frame_num]]['team']
                tracks['players'][frame_num][possession_tracker[frame_num]]['has_ball'] = True
                team_ball_control.append(tracks['players'][frame_num][possession_tracker[frame_num]]['team'])
            else:
                current_team = team_ball_control[-1] if team_ball_control else 3

            #Update rolling history with current frame's assignment
            rolling_history.append(current_team)

            #Find mode team assignment from last 10 frames
            mode_team = collections.Counter(rolling_history).most_common(1)[0][0]
            team_ball_control.append(mode_team)

        except: 
            print('Excepted...')
            rolling_history.append(1)
            team_ball_control.append(1)
            continue
    team_ball_control = np.array(team_ball_control)


    API = SynergySportsAPI.SynergySportsAPI()
    ncaa_teams = API.get_teams(API.ncaa_id)
    for team in ncaa_teams:
        if team['data']['name'] == team_1_name:
            api_team_1 = team
            api_team_1['data']['roster'] = API.get_team_roster(api_team_1["data"]["id"])
        elif team['data']['name'] == team_2_name:
            api_team_2 = team
            api_team_2['data']['roster'] = API.get_team_roster(api_team_2["data"]["id"])
    
    events = API.get_game_events(API.game_id_1)

    # Draw output 
    output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control, api_team_1, api_team_2, events)

    base_name, ext = os.path.splitext(input_video_path)
    output_dir = 'output_videos'
    output_path = os.path.join(output_dir, f"{base_name}{ext}")

    # If the output path exists, save the file with a slightly different name
    count = 1
    while os.path.exists(output_path):
        output_path = os.path.join('output_videos', f"{base_name}_{count}{ext}")
        count += 1

    # Save video
    save_video(output_video_frames, output_path, fps)
    return output_path

if __name__ == '__main__':
    main('duke.mp4', 'Georgia', '#DFE2DC', 'Auburn', '#000000')