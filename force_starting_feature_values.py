from database import db


#Initialize weights with hand-set values
weights = {}
# weights["in_enemy_territory"] = 1  #Positive to say being in enemy territory is good
# weights["in_friendly_territory"] = -1  #Negative to say being in friendly territory is bad
# weights["closest_pellet_dist"] = 5  #Positive to say being near pellets is good (feature is as an inverse)
# weights["closest_friend_dist"] = -1 #Negative to say being near friends is bad (feature is as an inverse)
# weights["num_pellets_within_5_dist"] = 0.1
# weights["closest_friend_is_closer_than_2"] = -10 #Negative to say having a friend too close is bad
weights["percent_food_eaten"] = 100  #Positive to say more food eaten is good
weights["two_agents_share_same_closest_pellet"] = -5 #Negative because it is bad for agents to go for the same goal
# weights["closest_friend_is_too_close"] = -9000 #Negative to say having a friend too close is bad
# weights["there_is_a_friend_at_0_away"] = -100 #Negative to say having a friend too close is bad
# weights["there_is_a_friend_at_1_away"] = -100 #Negative to say having a friend too close is bad
weights["min_dist_to_closest_pellet"] = -2 #Negative because higher distance is worse (being farther from pellets in general)
weights["avg_dist_to_closest_pellet"] = -2
weights["min_dist_to_closest_friend"] = -2 #Negative because being near a friend is bad (feature is inverse)
weights["percent_agents_in_friendly_territory"] = -1 #Negative because agents being in friendly territory is kinda bad



#Save out weights to db
collection = db.getCollection("pacman_weights")
collection.update({}, {"$set": {"the_weights": weights}})
db.kthxbye(collection)

