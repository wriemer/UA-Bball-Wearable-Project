import sys 
sys.path.append('../')
from utils import get_center_of_bbox, measure_distance, get_bbox_width, get_bbox_height

class PlayerBallAssigner():
    def __init__(self):
        self.max_player_ball_distance = 450
        self.previous_possessor = -1
    
    def assign_ball_to_player(self,players,ball_bbox):
        DEPTH_SCALING_STRENGTH = 0.75 # Controls how much of an effect depth scaling has (e^(strength * deviation))
        PREVIOUS_POSSESSOR_BIAS = 0.7 # Controls the amount the prvious possessor is favored. Lower values = more favored

        average_player_height = 190  # Average player height in cm (brought down a bit due to posture) | this could be replaced by querying the actual players heights?
        average_ball_height = 24    # Average basketball size in cm (Made sliughtly bigger due to boundry boxes increasing size)
        expected_ratio = average_player_height / average_ball_height
        
        ball_position = get_center_of_bbox(ball_bbox)
        ball_size = max(get_bbox_width(ball_bbox), get_bbox_height(ball_bbox))

        miniumum_distance = 99999
        assigned_player=-1
        for player_id, player in players.items():
            player_bbox = player['bbox']

            distance = measure_distance(get_center_of_bbox(player_bbox),ball_position)

            player_height = get_bbox_height(player_bbox)
            size_ratio = player_height / ball_size
            deviation = abs(size_ratio - expected_ratio)
            scaling_factor = 2.718 ** (DEPTH_SCALING_STRENGTH * deviation)

            weighted_distance = distance * scaling_factor

            if player_id == self.previous_possessor:
                weighted_distance = weighted_distance * PREVIOUS_POSSESSOR_BIAS

            if distance < self.max_player_ball_distance:
                if weighted_distance < miniumum_distance:
                    miniumum_distance = weighted_distance
                    assigned_player = player_id

        self.previous_possessor = assigned_player
        return assigned_player
    
    def correct_possession_history(self, possession_history, tolerance=3):
        corrected = []
        current = possession_history[0]
        new = -1
        new_score = 0
        
        for player in possession_history:
            if player == current:
                while new_score > 0:
                    corrected.append(current)
                    new_score -= 1
                corrected.append(player)
            elif player == new:
                new_score += 1
                if new_score > tolerance:
                    current = new
                    while new_score > 0:
                        corrected.append(current)
                        new_score -= 1
            else:
                while new_score > 0:
                    corrected.append(current)
                    new_score -= 1
                new = player
                new_score = 1

        while new_score > 0:
            corrected.append(current)
            new_score -= 1
        
        return corrected