# USED FOR TESTING

from ultralytics import YOLO

def main():
    model = YOLO('models/models-med/best.pt')

    results = list(model.predict('input_videos/bball_4.mp4', save=True, stream=True))

    print(results[0])
    print('==========================')
    for box in results[0].boxes:
        print(box)


if __name__ == '__main__':
    main()