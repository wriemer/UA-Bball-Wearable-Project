# This file will contain main logic for cv operations

from utils import read_video, save_video
from trackers import Tracker

def main():
    #Read in video
    video_frames = read_video('input_videos/film_aau.mp4')

    #Initialize Tracker, takes in trained model
    tracker = Tracker('models/best.pt')

    tracks = tracker.get_object_tracks(video_frames)

    #Save video
    save_video(video_frames, 'output_videos/output.avi')
    

if __name__ == '__main__':
    main()