import cv2

# reads video specified by video_path
def read_video(video_path):
    print(4)
    cap = cv2.VideoCapture(video_path)

    # get frame rate of input video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # store list of frames contained in video
    frames = []
    print(5)
    a = 0
    while True:
        a += 1
        print(a)
        # read in video
        ret, frame = cap.read()

        # break loop if video done
        if not ret:
            break

        frames.append(frame)

    return frames, fps

def save_video(ouput_video_frames, output_video_path, fps):
    # set video format
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # specify output video settings
    # last tuple represents (width, height) for video
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (ouput_video_frames[0].shape[1], ouput_video_frames[0].shape[0]))

    # write frames to output
    for frame in ouput_video_frames:
        out.write(frame)

    out.release()