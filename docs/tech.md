---
layout: default
title: Technology
---

[Back](/UA-Bball-Wearable-Project/index)

# Technology

## CV
**Roboflow**  
A platform for annotating, augmenting, and managing datasets for computer vision projects.  
*How we used it:*  
We used Roboflow to annotate our custom basketball dataset and apply augmentations to increase the dataset's size and diversity, improving model performance.

**Ultralytics**  
Provides tools and libraries for YOLO (You Only Look Once), a state-of-the-art object detection model.  
*How we used it:*  
We used the YOLOv8 package from Ultralytics to train our basketball detection model and make real-time detections in video frames.

**OpenCV (cv2)**  
An open-source computer vision library that provides tools for image processing and analysis.  
*How we used it:*  
We used OpenCV to annotate images, preprocess video frames, and integrate the outputs from our YOLO model for player tracking and ball possession detection.

## API
**SQLite**  
A lightweight, serverless database engine for managing structured data.  
*How we used it:*  
We used SQLite to create an embedded database for storing historical basketball statistics and tracking player data over time.

## Web App
**Streamlit**  
An open-source Python library for building interactive and data-driven web applications.  
*How we used it:*  
We used Streamlit to develop our web app for visualizing player statistics, game analytics, and video detections in an intuitive, user-friendly interface.