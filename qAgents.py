# baselineAgents.py
# -----------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
from captureAgents import AgentFactory
import distanceCalculator
import random, time, util
from game import Directions
import keyboardAgents
import game
from util import nearestPoint
import regularMutation
import qLearn

#############
# FACTORIES #
#############
      
class qLearnAgents(AgentFactory):
  '''Returns three q-learning agents.'''
  def __init__(self, isRed, alpha=0.1, epsilon=0.9):
    AgentFactory.__init__(self, isRed)
    self.alpha = alpha
    self.epsilon = epsilon
  
  def getAgent(self, index):
    return qLearningAgent(index, self.alpha, self.epsilon)

##########
# Agents #
##########

class qLearningAgent(CaptureAgent):
  '''A q-learning agent.  Note that this agent has no decay (gamma) term; its future gains are not discounted.  (This could be easily changed, just not sure if that makes sense or not.)  The features learned are those specified in the *feature_function.py files in featureCalculator/functions.  The reward function for transitions (to speed up learning by essentially pruning the exploration space) is specified in qLearn.py.'''
  
  def __init__(self, index, alpha, epsilon):
    CaptureAgent.__init__(self, index)
    self.weights = util.Counter()
    self.alpha = alpha #learning rate--higher means learn in larger steps
    self.epsilon = epsilon #exploration rate--higher means explore more
    self.firstTurnComplete = False
    self.startingFood = 0
    self.theirStartingFood = 0
  
  def chooseAction(self, gameState):
    '''The exposed interface for this agent for picking an action.'''

    #Store food info at the beginning of the game:
    if not self.firstTurnComplete:
      self.firstTurnComplete = True
      self.startingFood = len(self.getFoodYouAreDefending(gameState).asList())
      self.theirStartingFood = len(self.getFood(gameState).asList())
    else:
      #Update learned weights based on latest transition (after first turn)
      self.update(self.previous_game_state, gameState)  
      
    #Pick the best action to take
    actionChosen = self.pickAction(gameState)
    
    #Before we return our decision, record where we are now and what we
    #decided so we can learn in the future whether it was a good call
    self.previous_game_state = gameState
    
    print "action chosen: ", actionChosen
    #Return the action chosen
    return actionChosen
    
  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor
    
  def getPolicy(self, state):
    '''Get the best action to take in this state.  If there are no legal actions, return None.'''
    print "In getPolicy.  "
    
    
    #Return None if there are no legal actions:
    if not len(self.getLegalActions(state)) > 0:
      return None
    
    #Calculate the best action(s)
    chosen_action = None
    max_val = None
    best_actions = []
    for action in self.getLegalActions(state):
      #Set what the state would look like if we took this action:
      successor_state = self.getSuccessor(state, action)
      #Evaluate how good that state would be PLUS THE MOTHERFUCKING REWARD THAT HE WOULD GET FOR GOING THERE
      print "\t\t\t(Calculating state value for successor state that comes after action: "+str(action)+")"
      successor_val = qLearn.state_value(successor_state, self)
      transition_reward = qLearn.transition_reward(state, successor_state, self)
      val = transition_reward + successor_val
      print "\t\tIf action is: "+str(action)
      print "\t\tthen transition reward will be: "+str(transition_reward)
      print "\t\tand new state value will be: "+str(successor_val)
      print "\t\tfor a total worth of: "+str(val)
      
      if val == max_val:
        best_actions.append(action)
      elif val > max_val:
        best_actions = [action]
        max_val = val
        
    #Choose a random action from the best actions
    chosen_action = random.choice(best_actions)
    return chosen_action
    
  def pickAction(self, state):
    '''Get the best action to take in the current state.  With probability epsilon, take a random action; otherwise we take the best policy action.  If there are no legal actions (the case at the terminal state), we choose None.'''
    legalActions = self.getLegalActions(state)
    action = None
    if len(legalActions) is 0:
        return None
    if util.flipCoin(self.epsilon):
        action = random.choice(legalActions)
    else:
        action = self.getPolicy(state)
    return action

  def update(self, last_state, state):
    '''Updates/learns feature weights based on a transition from one state to another.  We learn from the transition from the previous state to this one, now that we can see what happened after our last decision and how it turned out.'''
    
    #Calculate the correction term:
    current_state_value = qLearn.state_value(state, self)
    previous_state_value = qLearn.state_value(self.previous_game_state, self)
    reward = qLearn.transition_reward(self.previous_game_state, state, self)
    correction = (reward + current_state_value) - previous_state_value
    print "current state value: \t", current_state_value
    print "previous state value: \t", previous_state_value
    print "correction: \t\t", correction
    #Calculate the feature values for the current state:
    feature_values = qLearn.state_feature_values(state, self)
    #What if we calculated for previous state and took the difference?
    feature_values_old = qLearn.state_feature_values(self.previous_game_state, self)
    
    #Update learned weights:
    for f_name in feature_values.keys():
      f_val = feature_values[f_name]
      f_val_old = feature_values_old[f_name]
      f_val_delta = f_val - f_val_old
      self.weights[f_name] += self.alpha * correction * f_val_delta
    