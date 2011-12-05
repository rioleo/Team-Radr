'''This is an example feature function that is fully functional, but returns the same feature value for every data point.  This feature function can be active in this package; it will not degrade performance significantly.  Use this as a template to create other feature functions.  

Important: 
For your feature function to work, it needs to meet two requirements: 

(1) have a function in it called calculate_feature_value().  This function is passed a game state (and optionally a connection to the database of the other raw datapoints).  It must output a dictionary with feature names and values.  In the simplest case, you just return a dictionary with one key (the feature name) and one value (the feature value).  But you're not limited to one; you can calculate arbitrarily many features in one *feature_function.py file.  It's faster to run fewer files that each calculate more features.

Note: names for features must be unique.  This could be fixed, but it's not worth the effort.  Just make sure you're not stepping on someone else's toes by checking the other *feature_function.py files; make names longer if you need.

(2) the function must be registered in __all__ list for the module.  To register the function, add it's name (filename) to the list __all__ in the file /featureCalculator/__init__.py.  See that file for an example.

To get started writing a new feature function, copy this file, rename it, and make sure it's in the folder "featureCalculator/".  Register it as above, and edit calculate_feature_vector() as desired!
'''

from game import Directions, Actions
from sets import Set


def calculate_feature_value(state, agent):  #Do not change this line    
    #Create dict to be returned
    feature_values = {}
    #Set up some useful variables
    position = agent.getPosition(state)
    enemies = agent.getOpponentPositions(state) #None for agents w dist > 5
    walls = state.getWalls()
    food = agent.getFood(state)
    
    #Create features for the distance to the nearest food, as well as for the number of nearby pellets.  Note the closest_pellet calculation is used below to figure out if two agents are going after the same goal.
    closest_pellet_dist = float("inf")
    within_5 = []
    within_3 = []
    for pellet in food.asList():
      this_dist = agent.getMazeDistance(position, pellet)
      if this_dist < closest_pellet_dist:
        closest_pellet_dist = this_dist
        closest_pellet = pellet
      if this_dist < 5:
        within_5.append(pellet)
        if this_dist < 3:
          within_3.append(pellet)
    feature_values["closest_pellet_dist"] = 1/float(closest_pellet_dist+1)
    # feature_values["num_pellets_within_5_dist"] = len(within_5)
    # feature_values["num_pellets_within_3_dist"] = len(within_3)
    
    #How much food has been eaten?
    starting_food_count = agent.theirStartingFood
    current_food_count = float(len(food.asList()))
    feature_values["percent_food_eaten"] = (starting_food_count - current_food_count) / starting_food_count
    
    

    #Figure out where the closest friend is  
    closest_friend_dist = 1000
    distances = []
    for friend in agent.getTeamPositions(state):
      dist = agent.getMazeDistance(position, friend)
      print "friend", friend, "at position", position, dist
      #distances.append(dist)
      # print "distance to friend: ", str(dist)
      # print "my position: ", position
      # print "friend position: ", friend
      if dist < closest_friend_dist and dist != 0:
        closest_friend_dist = dist
    # print "closest friend found at "+str(closest_friend_dist)+" away."
    #Remove the one 0 from distances list that represents yourself!  important.  took forever to find out.  :p
    
    #closest_friend_dist = min(distances)
    print closest_friend_dist
    feature_values["closest_friend_dist"] = 1/(float(closest_friend_dist+1)*float(closest_friend_dist+1))
     
    #Create features for whether agent is in friendly or enemy territory
    if agent.isPositionInTeamTerritory(state, position):
      feature_values["in_enemy_territory"] = 0
      feature_values["in_friendly_territory"] = 1
    else:
      feature_values["in_enemy_territory"] = 1
      feature_values["in_friendly_territory"] = 0
      
    #Is the closest pellet to this agent the same as the closest to another teammate? (are we going for the same thing?)
    #For each agent, calculate the closest pellet to it.  Then if two pellets are the same, return shared_goal True
    closest_pellets = Set()
    for agent_position in agent.getTeamPositions(state):
      closest_pellet_dist = float("inf")
      closest_pellet = None
      for pellet in food.asList():
        distance_to_pellet = agent.getMazeDistance(agent_position, pellet)
        if distance_to_pellet <= closest_pellet_dist:
          closest_pellet_dist = distance_to_pellet
          closest_pellet = pellet
      closest_pellets.add(closest_pellet)
    #Now closest_pellets holds the pellets closest to each agent.
    if len(closest_pellets) < len(agent.getTeamPositions(state)):
      feature_values["two_agents_share_same_closest_pellet"] = 1
    else:
      feature_values["two_agents_share_same_closest_pellet"] = 0


    return feature_values
        
        
    
#Miscellaneous crap:
# if closest_friend_dist < 2:
#   feature_values["closest_friend_is_closer_than_2"] = 1
# else:
#   feature_values["closest_friend_is_closer_than_2"] = 0
  

# #Make some features about closest friend:
# if 0 in distances:
#   feature_values["there_is_a_friend_at_0_away"] = 1
#   # print "BALLS. friends are at 0 away."
#   # print "distances: "+str(distances)
# else:
#   feature_values["there_is_a_friend_at_0_away"] = 0
#   # print "HOLY_FUCK there isn't a friend at 0 away"
# if 1 in distances:
#   feature_values["there_is_a_friend_at_1_away"] = 1
# else:
#   feature_values["there_is_a_friend_at_1_away"] = 0

  
# if closest_friend_dist < 1:
#   feature_values["closest_friend_is_too_close"] = 1
# else:
#   feature_values["closest_friend_is_too_close"] = 0

    