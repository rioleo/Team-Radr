'''This is an example feature function that is fully functional, but returns the same feature value for every data point.  This feature function can be active in this package; it will not degrade performance significantly.  Use this as a template to create other feature functions.  

Important: 
For your feature function to work, it needs to meet two requirements: 

(1) have a function in it called calculate_feature_value().  This function is passed a game state (and optionally a connection to the database of the other raw datapoints).  It must output a dictionary with feature names and values.  In the simplest case, you just return a dictionary with one key (the feature name) and one value (the feature value).  But you're not limited to one; you can calculate arbitrarily many features in one *feature_function.py file.  It's faster to run fewer files that each calculate more features.

Note: names for features must be unique.  This could be fixed, but it's not worth the effort.  Just make sure you're not stepping on someone else's toes by checking the other *feature_function.py files; make names longer if you need.

(2) the function must be registered in __all__ list for the module.  To register the function, add it's name (filename) to the list __all__ in the file /featureCalculator/__init__.py.  See that file for an example.

To get started writing a new feature function, copy this file, rename it, and make sure it's in the folder "featureCalculator/".  Register it as above, and edit calculate_feature_vector() as desired!
'''

from game import Directions, Actions


def calculate_feature_value(state, agent):  #Do not change this line    
    #For debugging:
    # return {}
    
    #Create dict to be returned
    feature_values = {}
    
    #Set up some useful variables
    position = agent.getPosition(state)
    enemies = agent.getOpponentPositions(state) #None for agents w dist > 5
    walls = state.getWalls()
    food = agent.getFood(state)

    
    #Create features for the distance to the nearest food, as well as for the number of nearby pellets
    closest_pellet_dist = float("inf")
    within_5 = []
    within_3 = []
    for pellet in food.asList():
      this_dist = agent.getMazeDistance(position, pellet)
      if this_dist < closest_pellet_dist:
        closest_pellet_dist = this_dist
      if this_dist < 5:
        within_5.append(pellet)
        if this_dist < 3:
          within_3.append(pellet)
    #feature_values["closest_pellet_dist"] = closest_pellet_dist
    feature_values["closest_pellet_dist"] = 0

     #feature_values["num_pellets_within_5_dist"] = len(within_5)
     #feature_values["num_pellets_within_3_dist"] = len(within_3)
    
    #pellet_distances = []
    #for pellet in food.asList():
      #pellet_distances.append()
    

    #Create a feature for how close you are to your nearest teammate
    closest_friend = float("inf")
    for friend in agent.getTeamPositions(state):
      dist = agent.getMazeDistance(position, friend)
      if dist < closest_friend:
        closest_friend = dist
      feature_values["closest_friend_dist"] = closest_friend
      
    #Create features for whether agent is in friendly or enemy territory
      feature_values["in_friendly_territory"] = agent.isPositionInTeamTerritory(state, position)
      feature_values["in_enemy_territory"] = agent.isPositionInEnemyTerritory(state, position)

    
    return feature_values
        
        
    
    