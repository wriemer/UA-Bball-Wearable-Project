import cv2
import random
import os

VIDEO_TITLE = "duke_basketball" # Set this to .mp4 name (Without .mp4)
FRAME_COUNT = 50 # Set to desired amount of frames

def extract_random_frames(video_path, num_frames=FRAME_COUNT):
    # Open the video file
    video = cv2.VideoCapture(video_path)
    
    # Get total number of frames
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Generate random frame numbers
    frame_indices = random.sample(range(total_frames), num_frames)
    frame_indices.sort()  # Sorting to make frame extraction efficient
    
    # Create a folder for frames based on the VIDEO_TITLE
    output_folder = f'frame_dump/{VIDEO_TITLE}'
    os.makedirs(output_folder, exist_ok=True)
    
    frames = []
    
    for i, frame_idx in enumerate(frame_indices):
        # Set the video to the selected frame
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        
        # Read the frame
        ret, frame = video.read()
        if ret:
            frames.append(frame)
            # Save the frame as an image in the created folder
            cv2.imwrite(f'{output_folder}/random_frame_{i+1}.jpg', frame)
    
    # Release the video capture object
    video.release()

# Example usage
video_path = f'videos/{VIDEO_TITLE}.mp4'  # Uses the VIDEO_TITLE to open the correct video file
extract_random_frames(video_path)
