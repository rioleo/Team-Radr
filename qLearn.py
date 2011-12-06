import featureCalculator
from featureCalculator.functions import *
import math
import sys

def state_value(state, agent):
    '''Return the value of a state.  This is the feature values for this state * the learned weights for those values, where * is the dot product operator.'''
    debug = False
    if debug:
      print "\t\t\tEvaluating state value.  Printing feature weights and values."
    # print "\t\t\t"+ str(agent.weights)
    weights = agent.weights
    total_val = 0
    feature_values = state_feature_values(state, agent)
    for f_name in feature_values.keys():
        f_val = feature_values[f_name]
        total_val += f_val * weights[f_name]
        # print "\t\t\tfeature: "+str(f_name)+" has value: "+str(feature_values[f_name])+" with weight: "+str(weights[f_name])
        if debug:
          print "\t\t\t\tFeature: \t\t"+str(f_name)
          print "\t\t\t\tAnd weight:\t\t"+str(weights[f_name])
          print "\t\t\t\tWith value:\t\t"+str(f_val)
          print "\t\t\t\tUpdates value:\t"+str(f_val*weights[f_name])
    if debug:
      print "\t\t\tFor a total value: "+str(total_val)

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
    proximity_reward += total_pellets_eaten #Heavily bias towards pellets eaten as opposed to nearby
    return proximity_reward
    
def pellets_eaten_at_state(state, agent):
    food_present = agent.getFood(state).asList()
    starting_food = agent.theirStartingFood
    return float(starting_food - len(food_present))
    
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
    proximity_reward_delta = new_food_proximity - old_food_proximity
    #Calculate separately the total # pellets eaten:
    pellets_that_were_eaten = pellets_eaten_at_state(state1, agent)
    pellets_that_are_now_eaten = pellets_eaten_at_state(state2, agent)
    new_pellets_eaten = pellets_that_are_now_eaten - pellets_that_were_eaten

    # #Calculate whether this agent was just eaten (which we'll say can never be good; though this isn't necessarily always the case, it is the large majority of the time)--NOTE THIS ISN'T ACTUALLY CORRECT BECAUSE PACMAN COULD HAVE JUST WILLINGLY GONE BACK TO HIS OWN SIDE AND TURNED BACK INTO A GHOST
    # agent_just_got_eaten = (agent.isPacman(state1) and agent.isGhost(state2))
    # if agent_just_got_eaten:
    #   eaten_penalty = 1
    # else:
    #   eaten_penalty = 0

    #Scale the numbers going towards reward calculation
    total_reward = 0
    total_reward += proximity_reward_delta * 1
    total_reward += new_pellets_eaten
    # total_reward -= eaten_penalty * 2

    # return 0 #For debugging
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