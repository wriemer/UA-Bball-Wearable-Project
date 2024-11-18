from ultralytics import YOLO
import supervision as sv
import pickle
import os
import numpy as np
import pandas as pd
import cv2
import sys 
sys.path.append('../') # used to import from utils
from utils import get_center_of_bbox, get_bbox_width, get_foot_position

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path) 
        self.tracker = sv.ByteTrack()

    def add_position_to_tracks(self,tracks):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    bbox = track_info['bbox']
                    if object == 'ball':
                        position= get_center_of_bbox(bbox)
                    else:
                        position = get_foot_position(bbox)
                    tracks[object][frame_num][track_id]['position'] = position

    def interpolate_ball_positions(self,ball_positions):
        ball_positions = [x.get(1,{}).get('bbox',[]) for x in ball_positions]
        df_ball_positions = pd.DataFrame(ball_positions,columns=['x1','y1','x2','y2'])

        # Remove Outliers
        avg_movement = df_ball_positions.diff().abs().mean()

        last_valid_frame = None
        consecutive_nans = 0
        for i in range(len(df_ball_positions)):
            if df_ball_positions.iloc[i].isna().all():  # If the current frame is NaN
                consecutive_nans += 1
            else:  # If the current frame is not NaN
                if last_valid_frame is not None and consecutive_nans > 0:
                    movement = np.abs(np.array(df_ball_positions.iloc[i].values) - np.array(last_valid_frame))

                    # Scale the movement by the number of NaN frames in between
                    scaled_movement = movement / (consecutive_nans * 0.25)

                    # If the scaled movement is larger than the allowed threshold, set the frame to NaN
                    for j in range(len(movement)):
                        if scaled_movement[j] > (avg_movement[j] * 1.0):  # orig 1.0, changed to increase tolerance
                            df_ball_positions.iloc[i] = np.nan 
                            print(f"OUTLIER FOUND       {j}     {scaled_movement[j]}     {(avg_movement[j])}")

                else : # Reset the NaN counter and update the last valid frame
                    last_valid_frame = df_ball_positions.iloc[i].values
                    consecutive_nans = 0

        # Process frames in batches
        batch_size = 10
        for i in range(0, len(df_ball_positions), batch_size):
            batch = df_ball_positions.iloc[i:i + batch_size]
            
            if batch.isna().all().all():
                continue

            df_ball_positions.iloc[i:i + batch_size] = batch.interpolate()
            df_ball_positions.iloc[i:i + batch_size] = batch.bfill()

        ball_positions = [
            {1: {"bbox": x}} if not pd.isna(x).all() else {}
            for x in df_ball_positions.to_numpy().tolist()
        ]

        return ball_positions

    def detect_frames(self, frames):
        batch_size=20 
        detections = [] 
        a = 1
        for frame in frames[:-1]:
            print(a)
            a += 1
            detections += self.model.predict(frame, conf=0.1)
        return detections

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):
        
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                tracks = pickle.load(f)
            return tracks

        detections = self.detect_frames(frames)

        tracks={
            "players":[],
            "ball":[]
        }

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v:k for k,v in cls_names.items()}

            # Covert to supervision Detection format
            detection_supervision = sv.Detections.from_ultralytics(detection)

            # Track Objects
            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["ball"].append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv['Player']:
                    tracks["players"][frame_num][track_id] = {"bbox":bbox}
            
            for frame_detection in detection_supervision:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]

                if cls_id == cls_names_inv['Ball']:
                    tracks["ball"][frame_num][1] = {"bbox":bbox}

        if stub_path is not None:
            with open(stub_path,'wb') as f:
                pickle.dump(tracks,f)

        return tracks
    
    # Converts an rgb tuple to a bgr tuple
    def convert_rgb_to_bgr(self, rgb_color):
        return (rgb_color[2], rgb_color[1], rgb_color[0])
    
    def draw_ellipse(self,frame,bbox,color,track_id=None):
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)

        cv2.ellipse(
            frame,
            center=(x_center,y2),
            axes=(int(width), int(0.35*width)),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color = self.convert_rgb_to_bgr(color),
            thickness=2,
            lineType=cv2.LINE_4
        )

        rectangle_width = 40
        rectangle_height=20
        x1_rect = x_center - rectangle_width//2
        x2_rect = x_center + rectangle_width//2
        y1_rect = (y2- rectangle_height//2) +15
        y2_rect = (y2+ rectangle_height//2) +15

        if track_id is not None:
            cv2.rectangle(frame,
                          (int(x1_rect),int(y1_rect) ),
                          (int(x2_rect),int(y2_rect)),
                          color,
                          cv2.FILLED)
            
            x1_text = x1_rect+12
            if track_id > 99:
                x1_text -=10
            
            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_text),int(y1_rect+15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (128,128,128),
                2
            )

        return frame

    def draw_traingle(self,frame,bbox,color):
        y= int(bbox[1])
        x,_ = get_center_of_bbox(bbox)

        triangle_points = np.array([
            [x,y],
            [x-10,y-20],
            [x+10,y-20],
        ])
        cv2.drawContours(frame, [triangle_points],0,color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points],0,(0,0,0), 2)

        return frame
    
    def draw_ball_box(self, frame, bbox, color, thickness):
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        x2 = int(bbox[2])
        y2 = int(bbox[3])

        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        return frame
        

    def draw_team_ball_control(self, tracks, frame,frame_num,team_ball_control):
        # Draw a semi-transparent rectaggle 
        overlay = frame.copy()
        cv2.rectangle(overlay, (1350, 850), (1900,970), (255,255,255), -1 )
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        team_ball_control_till_frame = team_ball_control[:frame_num+1]
        # Get the number of time each team had ball control
        team_1_num_frames = team_ball_control_till_frame[team_ball_control_till_frame==1].shape[0]
        team_2_num_frames = team_ball_control_till_frame[team_ball_control_till_frame==2].shape[0]

        if team_1_num_frames + team_2_num_frames != 0:
            team_1 = team_1_num_frames/(team_1_num_frames+team_2_num_frames)
            team_2 = team_2_num_frames/(team_1_num_frames+team_2_num_frames)
        else:
            team_1 = 0
            team_2 = 0

        #cv2.putText(frame, f"Team 1 Ball Control: {team_1*100:.2f}%",(1400,900), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3)
        #cv2.putText(frame, f"Team 2 Ball Control: {team_2*100:.2f}%",(1400,950), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3)

        cv2.putText(frame, 
                    f"Ball Control: {tracks['team_1_name'] if team_ball_control[frame_num] == 1 else tracks['team_2_name']}",
                    (1400,900), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (0,0,0), 
                    3)

        return frame

    def draw_team_info(self, frame, team, position):
        # Determine the rectangle and text placement based on the position
        if position == 1:  # Top-left corner (team 1)
            rect_start = (20, 20)
            rect_end = (570, 140)
            text_start = (30, 50)
        else:  # Top-right corner (team 2)
            frame_width = frame.shape[1]
            rect_start = (frame_width - 570, 20)
            rect_end = (frame_width - 20, 140)
            text_start = (frame_width - 560, 50)

        # Draw a semi-transparent rectangle
        overlay = frame.copy()
        cv2.rectangle(overlay, rect_start, rect_end, (255, 255, 255), -1)
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Add the team information text
        text = f"{team['data']['fullName']}\n{team['data']['division']['name']} - {team['data']['league']['name']}"
        
        #players = []
        #for i in range(5): # Currently just 5 random players, eventually you'll be bale to choose who's on the court?
        #    players.append(team['data']['roster'][i])
        
        #for player in players:
        #    text = text + f"\n{player['data']['number']} - {player['data']['name']}"
            
        y0, dy = text_start[1], 30  # Starting y position and line spacing
        for i, line in enumerate(text.split('\n')):
            y = y0 + i * dy
            cv2.putText(frame, line, (text_start[0], y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        return frame


    def draw_annotations(self, video_frames, tracks, team_ball_control, team_1, team_2):
        output_video_frames= []
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            if True:
                player_dict = tracks["players"][frame_num]
                ball_dict = tracks["ball"][frame_num]

                # Draw Players
                for track_id, player in player_dict.items():
                    color = player.get("team_color",(0,0,255))
                    frame = self.draw_ellipse(frame, player["bbox"],color, track_id)

                    if player.get('has_ball',False):
                        frame = self.draw_traingle(frame, player["bbox"],(0,0,255))
                        # PROBLEM w/ box being drawna round correct player
                        frame = self.draw_ball_box(frame, player["bbox"], (0,255,0), 2)
                
                # Draw ball 
                for track_id, ball in ball_dict.items():
                    #frame = self.draw_traingle(frame, ball["bbox"],(0,255,0))
                    frame = self.draw_ball_box(frame, ball["bbox"], (0,255,0), 2)


                # Draw Team Ball Control
                frame = self.draw_team_ball_control(tracks, frame, frame_num, team_ball_control)

                # Draw API Information
                frame = self.draw_team_info(frame, team_1, 1)
                frame = self.draw_team_info(frame, team_2, 2)

                output_video_frames.append(frame)
            #except: continue

        return output_video_frames
