---
layout: default
title: Sprint Log
---

[Back](/UA-Bball-Wearable-Project/index)

# Our Approach

Initially, we were going to make a pair of smart glasses that identifies players
and team pocessions and displays relevant live and historical statistics to the
glasses. We then pivoted to making a CV model that canidentify teams and
pocessions and a web app surrounding this. The web app allows users to upload
videos and annotate the videos and display relevant live and historical
statistics. The stats are from the SynergySports API and a local database we
created. We also created a wrapper for the SynergySports API to demonstrate the
potential of the API.

# Work Log for Each Sprint

## Sprint 1

The goal for sprint 1 was to get a basic computer vision model up and running.
We wanted to be able to detect players in a video and track their movement.
Also, we began collecting historical data and setting up a database to store it.

- **Embedded Database for Historical Stats**
  - Created a SQLite database to store historical stats
- **Basic CV Functionality**
  - Simple possession identification

## Sprint 2

In sprint 2, we found out we were not getting any glasses. So, we pivoted to a
web app that would allow users to upload videos and get the same functionality
as if they were wearing the glasses. We also wanted to improve the accuracy of
our computer vision model.

- **Created a custom dataset to train our model**
  - Annotated over 750 pictures
- **Used our new dataset to train a more accurate model**
  - Tried various sizes to optimize the speed-to-accuracy ratio
- **Converted the computer vision service to process a single frame at a time**
  - More accurately simulates a live feed
- **Developed a web app due to lack of hardware**
  - Demonstrates the computer vision functionality

## Sprint 3

For Sprint 3, we focused on improving the accuracy of our model and adding more
functionality to the web app. We also created a wrapper for the Synergy API to
demonstrate the potential of the API. Addionally, we focused on documenting and
setting up the project to be easily handed off to future teams.

- **Improved color detection**
  - Used to assign players to teams
- **Added more functionality to the front end of the web app**
  - Team name and color assignment
- **Created a wrapper for the Synergy API**
  - Demonstrates the potential of the API
- **New algorithm for assigning possession**
  - Scales boundary boxes based on depth
- **Post possession smoothing**
  - Corrects short bursts of misdetections
