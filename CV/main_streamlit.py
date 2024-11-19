import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import numpy as np
import cv2
import tempfile
import random
import os
from cv_service import main
from api.SynergySportsAPI import SynergySportsAPI
import shutil


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

print("Current Working Directory:", os.getcwd())

# Title
st.title("Annotate Uploaded Video")

api = SynergySportsAPI(config_path='./api/config.json')

# Team Selection and Color Assignment
st.sidebar.header("Team Setup")


leagues_data = api.get_leagues()
leagues = leagues_data['data']

# Extract league names from the nested structure
league_info = [(league['data']['name'], league['data']['id']) for league in leagues]
league_names = [league[0] for league in league_info]  # List of league names
        
selected_league_name = st.sidebar.selectbox(
    "Select a League",
    options=league_names,  # Pass the league names directly here
    format_func=lambda name: name if name else "Select a League"  # This is optional; league names are already strings
)

# Find the league_id corresponding to the selected league name
selected_league_id = next(league[1] for league in league_info if league[0] == selected_league_name)

#st.write(f"Selected League: {selected_league_name} (ID: {selected_league_id})")

if selected_league_name:
    teams = api.get_teams(league_id=selected_league_id)  # Use the league_id to fetch teams
    
    # Extract team names for the dropdown
    team_names = [team['data']['name'] for team in teams]

    if team_names:
        # Dropdown to select Team 1
        selected_team_1 = st.sidebar.selectbox(
            "Select Team 1",
            options=team_names,
            format_func=lambda name: name if name else "Select a Team",
        )
        
        # Color picker for Team 1
        team_1_color = st.sidebar.color_picker("Pick a Color for Team 1")
        
        # Dropdown to select Team 2
        selected_team_2 = st.sidebar.selectbox(
            "Select Team 2",
            options=team_names,
            format_func=lambda name: name if name else "Select a Team",
        )
        
        # Color picker for Team 2
        team_2_color = st.sidebar.color_picker("Pick a Color for Team 2")
        
        # Display selected teams and their colors
        #st.write(f"Selected Teams and Colors:")
        #st.write(f"Team 1: {selected_team_1} - Color: {team_1_color}")
        #st.write(f"Team 2: {selected_team_2} - Color: {team_2_color}")
    else:
        st.sidebar.write("No teams available for this league.")
else:
    st.sidebar.write("Please select a league.")

# Image or Video
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
    input_video_dir = './input_videos'

    if uploaded_video is not None:
        video_path = os.path.join(input_video_dir, uploaded_video.name)
        if not os.path.exists(video_path):
            with open(video_path, "wb") as f:
                shutil.copyfileobj(uploaded_video, f)

        #tfile = tempfile.NamedTemporaryFile(delete=False)
        #tfile.write(uploaded_video.read())

        # Display the original video
        st.video(video_path)
        
        # Annotate video
        if st.button("Annotate Video"):
            with st.spinner("Annotating video..."):
                output_path = main(uploaded_video.name, selected_team_1, team_1_color, selected_team_2, team_2_color)
            
            # Display
            st.video(output_path)


