import cv2

#Function to read in video
def read_video(video_path):
    cap=cv2.VideoCapture(video_path)
    frames = []
    #While video has more frames, read in each individual frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

#Function to save 
def save_video(output_video_frames, output_video_path):
    #Define output format and write in video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, 24, (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))

    for frame in output_video_frames:
        out.write(frame)
    out.release()