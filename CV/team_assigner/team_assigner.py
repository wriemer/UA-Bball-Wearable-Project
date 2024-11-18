from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import math
import cv2

class TeamAssigner:
    def __init__(self):
        self.team_colors = {}
        self.player_team_dict = {}
        self.show_test_img = 1
    
    def get_clustering_model(self,image):
        # Reshape the image to 2D array
        image_2d = image.reshape(-1,3)

        # Perform K-means with 3 clusters
        kmeans = KMeans(n_clusters=3, init="k-means++",n_init=10)
        kmeans.fit(image_2d)

        return kmeans

    def shrink_bbox(self, bbox, scale=0.5):
        # bbox is [x_min, y_min, x_max, y_max]
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        # Shrink the width and height by the given scale
        new_width = width * (1 - scale)
        new_height = height * (1 - scale)
        
        # Calculate new center
        center_x = bbox[0] + width / 2
        center_y = bbox[1] + height / 2
        
        # Define new bbox centered on the original center
        x_min = int(center_x - new_width / 2)
        x_max = int(center_x + new_width / 2)
        y_min = int(center_y - new_height / 2)
        y_max = int(center_y + new_height / 2)
        
        return [x_min, y_min, x_max, y_max]

    def get_player_color(self,frame,bbox):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])]

        top_half_image = image[0:int(image.shape[0]/2),:]

        # let's find center of image 
        bbox_adj = self.shrink_bbox(bbox)
        img_adj = frame[int(bbox_adj[1]):int(bbox_adj[3]),int(bbox_adj[0]):int(bbox_adj[2])]
        top_half_image = img_adj[0:int(img_adj.shape[0]/2),:]
        if self.show_test_img <= 0:
            plt.imshow(top_half_image)
            plt.show()
            self.show_test_img += 1

        # Get Clustering model
        kmeans = self.get_clustering_model(top_half_image)

        # Get the cluster labels forr each pixel
        labels = kmeans.labels_

        # Reshape the labels to the image shape
        clustered_image = labels.reshape(top_half_image.shape[0],top_half_image.shape[1])

        # Get the player cluster
        corner_clusters = [clustered_image[0,0],clustered_image[0,-1],clustered_image[-1,0],clustered_image[-1,-1]]
        non_player_cluster = max(set(corner_clusters),key=corner_clusters.count)
        player_cluster = 1 - non_player_cluster

        '''
        USED FOR TESTING
        if self.show_test_img >= 0 and self.show_test_img <= 15:
            plt.imshow(top_half_image)
            plt.show()
            plt.imshow(clustered_image)
            plt.show()
            self.show_test_img += 1
        '''

        player_color = kmeans.cluster_centers_[player_cluster]
        print(f'player_color: {player_color}')

        return player_color

    # auto assign team colors
    def assign_team_color(self, frame, player_detections):
        player_colors = []
        for _, player_detection in player_detections.items():
            bbox = player_detection["bbox"]
            player_color =  self.get_player_color(frame,bbox)
            player_colors.append(player_color)
        
        kmeans = KMeans(n_clusters=2, init="k-means++",n_init=10)
        kmeans.fit(player_colors)

        self.kmeans = kmeans

        self.team_colors[1] = kmeans.cluster_centers_[0]
        self.team_colors[2] = kmeans.cluster_centers_[1]
    

    def hex_to_rgb(self, hex_code):
        hex_code = hex_code.lstrip('#')  # Remove the '#' if it exists
        return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

    # assign using entered colors
    def assign_team_colors(self, team_1_color, team_2_color):
        self.team_colors[1] = self.hex_to_rgb(team_1_color)
        self.team_colors[2] = self.hex_to_rgb(team_2_color)

    # Calculate distance btw 2 colors
    def find_color_distance(self, color1, color2):
        return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))

    # return team w/ closest color to player's jersey
    def find_closest_team_color(self, target, color1, color2):
        dist1 = self.find_color_distance(target, color1)
        dist2 = self.find_color_distance(target, color2)
        return 1 if dist1 < dist2 else 2

    def get_player_team(self,frame,player_bbox,player_id):
        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]

        player_color = self.get_player_color(frame,player_bbox)

        # OLD
        #team_id = self.kmeans.predict(player_color.reshape(1,-1))[0]
        #team_id+=1

        team_id = self.find_closest_team_color(player_color, self.team_colors[1], self.team_colors[2])

        self.player_team_dict[player_id] = team_id

        return team_id