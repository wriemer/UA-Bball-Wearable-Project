import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import numpy as np
import cv2
import tempfile
import random
import os
from cv_service import main


#"""
#Requirements:
#    - streamlit==0.87.0
#    - streamlit-drawable-canvas==0.12.0
#    - Pillow==8.3.1
#    - tempfile==1.0.1
#"""

# Load a pretrained YOLO Model
#"""
#cascade_path = "haarcascade_fullbody.xml"
#human_cascade = cv2.CascadeClassifier(cascade_path)
#"""

# Title
st.title("Annotate Uploaded Video")

# Image or Video
#upload_type = st.sidebar.selectbox("Select Upload Type", ("Image", "Video"))
upload_type = "Video"

def add_random_boxes(image, n=3):
    image_np = np.array(image.convert("RGB"))
    draw = ImageDraw.Draw(image)

    for _ in range(n):
        # Randomly select the coordinates of the box
        x1, y1 = random.randint(0, image.width - 50), random.randint(0, image.height - 50)
        x2, y2 = x1 + random.randint(30, 100), y1 + random.randint(30, 100)
        # Draw the box
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

    return image

if upload_type == "Image":
    uploaded_image = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Auto-label option
        if st.sidebar.button("Do another task"):
            st.write("Do another task")
            st.image(image, caption="Do another task", use_column_width=True)

        # Random annotation option
        if st.sidebar.button("Add Random Boxes"):
            random_image = add_random_boxes(image)
            st.image(random_image, caption="Image with Random Boxes", use_column_width=True)

elif upload_type == "Video":
    uploaded_video = st.file_uploader("Upload a Video", type=["mp4", "mov", "avi"])

    if uploaded_video is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())

        # Display the original video
        st.video(tfile.name)
        
        # Annotate video
        if st.button("Annotate Video"):
            with st.spinner("Annotating video..."):
                main(uploaded_video.name)
                output_path = 'output_videos/' + uploaded_video.name
            
            # Display
            st.video(output_path)


