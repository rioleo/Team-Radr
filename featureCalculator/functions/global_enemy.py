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
    enemy_positions = agent.getOpponentPositions(state) #None for agents w dist > 5
    friend_positions = agent.getTeamPositions(state)
    walls = state.getWalls()
    food = agent.getFood(state)
    
    #Get the other agents on my team and enemies
    if state.isOnRedTeam(agent.index):
      friends_indices = state.getRedTeamIndices()
      enemy_indices = state.getBlueTeamIndices()
    else:
      friends_indices = state.getBlueTeamIndices()
      enemy_indices = state.getRedTeamIndices()

    enemy_locations = []
    for enemy_index in enemy_indices:
      enemyPos = agent.getOpponentPositions(state)[enemy_index/2]
      if enemyPos is None: #use estimate 
          maxBelief = 0
          maxPos = (1,1)
          belief = agent.beliefs[enemy_index]
          for pos in belief:
              if belief[pos] > maxBelief:
                  maxBelief = belief[pos]
                  maxPos = pos
          enemyPos = maxPos
      enemy_locations.append(enemyPos)
    
    #At this point we have enemy_locations.  
    enemy_positions_in_enemy_territory = []
    enemy_positions_in_friendly_territory = []
    for enemy_location in enemy_locations:
      if agent.isPositionInTeamTerritory(state, enemy_location):
        enemy_positions_in_friendly_territory.append(enemy_location)
      else:
        enemy_positions_in_enemy_territory.append(enemy_location)
    #At this point we have enemy locations split up by whether they're in friendly territory or enemy
  
    proximity_to_enemies_in_enemy_territory = 0.0
    for agent_index in friends_indices:
      position = state.getAgentState(agent_index).getPosition()
      proximity = 0.0
      for enemy_location in enemy_positions_in_enemy_territory:
        dist_to_enemy = agent.getMazeDistance(position, enemy_location)
        proximity += float(1/ float(dist_to_enemy * dist_to_enemy +1))
      proximity_to_enemies_in_enemy_territory += proximity
    #At this point proximity_to_enemies_in_enemy_territory represents how close we are to enemies who are (themselves) in enemy territory, where higher values mean we're closer to them.
      
    proximity_to_enemies_in_friendly_territory = 0.0
    for agent_index in friends_indices:
      position = state.getAgentState(agent_index).getPosition()
      proximity = 0.0
      for enemy_location in enemy_positions_in_friendly_territory:
        dist_to_enemy = agent.getMazeDistance(position, enemy_location)
        proximity += float(1/ float(dist_to_enemy * dist_to_enemy +1))
      proximity_to_enemies_in_friendly_territory += proximity    
    #At this point proximity_to_enemies_in_friendly_territory represents how close we are to enemies who are (themselves) in friendly territory, where higher values mean we're closer to them.
    
    #Create features for these:
    feature_values["close_to_enemies_in_enemy_territory"] = proximity_to_enemies_in_enemy_territory
    feature_values["close_to_enemies_in_friendly_territory"] = proximity_to_enemies_in_friendly_territory
    
    #Create a feature for number of invaders (which will be weighted high enough to push us over the edge of liking being near them to actually eating them)
    enemies = [state.getAgentState(i) for i in agent.getOpponents(state)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    feature_values["numInvaders"] = len(invaders)
    
    
    return feature_values
