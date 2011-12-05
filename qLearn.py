import featureCalculator
from featureCalculator.functions import *
import math
import sys

def state_value(state, agent):
    '''Return the value of a state.  This is the feature values for this state * the learned weights for those values, where * is the dot product operator.'''
    print "\t\t\tEvaluating state value.  Feature weights are: "
    print "\t\t\t"+ str(agent.weights)
    weights = agent.weights
    total_val = 0
    feature_values = state_feature_values(state, agent)
    for f_name in feature_values.keys():
        print "\t\t\tfeature: "+str(f_name)+" has value: "+str(feature_values[f_name])
        f_val = feature_values[f_name]
        total_val += f_val * weights[f_name]
    return total_val
    
def food_proximity(agent, position, food):
    proximity_reward = 0.0
    for pellet in food:
      dist_to_pellet = float(agent.getMazeDistance(position, pellet))
      # print "dist_to_pellet: ", dist_to_pellet
      if dist_to_pellet > 1:
        # print "increasing proximity_reward by: ", float(1 / (dist_to_pellet * dist_to_pellet))
        proximity_reward += float(1 / (dist_to_pellet * dist_to_pellet))
      elif dist_to_pellet == 1:
        proximity_reward += float(0.5)
      else: #this probably isn't necessary but just in case
        proximity_reward += float(1)
    total_pellets_eaten = float(agent.theirStartingFood - len(food))
    # print "total_pellets_eaten: ", total_pellets_eaten
    proximity_reward += total_pellets_eaten
    return proximity_reward
    
def transition_reward(state1, state2, agent):
    '''Calculate the reward for moving from state1 to state2.  For example, if you discover that you've eaten one more pellet in state2 than state1, give some reward for having eaten a pellet.  Probably also give some negative reward if you get eaten.  And give a large reward if you win the game.  Etc.  Agent is passed in so that additional data (such as how many pellets were there at the beginning of this particular game) is available.'''

    #Set up some useful variables
    position = agent.getPosition(state2)
    old_position = agent.getPosition(state1)
    food = agent.getFood(state2).asList()
    old_food = agent.getFood(state1).asList()


    #Reward for being near pellets.  The reward is more the closer to the pellet you are.  To keep from basking in being near without ever eating it, Pacman also gets a reward for pellets he's eaten.  He can have his cake and eat it too!  :D
    new_food_proximity = food_proximity(agent, position, food)
    old_food_proximity = food_proximity(agent, old_position, old_food)
    # print "new_food_proximity: ", new_food_proximity
    # print "old_food_proximity: ", old_food_proximity
    proximity_reward = new_food_proximity - old_food_proximity
    
    #
   # proximity_reward = 0
    #if position in food:
     #	proximity_reward = 1
    
    
    # print "proximity_reward: ", proximity_reward
    #Negative reward for our pellets eaten by the enemy
    # enemy_food_eaten_reward = len(agent.getFoodYouAreDefending(state1).asList()) - len(agent.getFoodYouAreDefending(state2).asList()) #higher val means he's eaten more :(


    #Scale the numbers going towards reward calculation
    total_reward = 0
    total_reward += proximity_reward * 1
    # total_reward += enemy_food_eaten_reward * -1
    #Return the total reward
    # print "transition_reward: ", total_reward
    return total_reward

def state_feature_values(state, agent):
    '''Return the feature values for the current state.'''
    feature_values = {}
    for feature in load_feature_functions():
        some_feature_values = feature(state, agent)
        feature_values.update(some_feature_values) #this is why feature names must be unique
    return feature_values
    
def load_feature_functions():
    '''Return a list of all the calculate_feature_value() functions contained within *.py files in /featureCalculator/functions.'''
    functions = []
    for name in dir(featureCalculator.functions):
        if not "__" in name: #only gather hand-coded, not full dir listing
            func = eval("featureCalculator.functions."+name+".calculate_feature_value")
            functions.append(func)
    return functions