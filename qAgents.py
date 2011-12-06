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
from database import db #you will have troubles if pymongo isn't installed!  :p
import sys

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
  
  beliefs = [None,None,None,None,None,None]
  
  def __init__(self, index, alpha, epsilon):
    CaptureAgent.__init__(self, index)
    self.weights = util.Counter()
    self.alpha = alpha #learning rate--higher means learn in larger steps
    self.epsilon = epsilon #exploration rate--higher means explore more
    self.firstTurnComplete = False
    self.startingFood = 0
    self.theirStartingFood = 0
    self.debug = False
    
    #used for estimating the enemy pos
    self.legalPositions = None
    self.estimate = util.Counter()
  
  
  def guessEnemyPos(self, gameState):
    #get enemy indices
    amIRed = gameState.isOnRedTeam(self.index)
    if amIRed:
      enemies = gameState.getBlueTeamIndices()
    else:
      enemies = gameState.getRedTeamIndices()
  
    #initialize legalPos and beliefs for each opponent
    if self.legalPositions is None:
      self.legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] > 0]
      
      for enemy in enemies:
        enemyInitPos = gameState.getInitialAgentPosition(enemy)
        qLearningAgent.beliefs[enemy] = util.Counter()
        for p in self.legalPositions: 
          #sometimes enemy goes first, so enemy might not be in the initial state already.
          #So I'm allowing some variability here. (only the grid nearby init state gets prob)
          if abs(p[0] - enemyInitPos[0]) + abs(p[1] - enemyInitPos[1]) < 3:
            qLearningAgent.beliefs[enemy][p] = 1.0  
          else:
            qLearningAgent.beliefs[enemy][p] = 0  
        qLearningAgent.beliefs[enemy].normalize()

   
    #we are getting P(enemy being this pos | noisyDis) here
    for enemy in enemies:
      enemyInitPos = gameState.getInitialAgentPosition(enemy)
      isGone = True  #if isGone stays True, means enemy is eaten, so start from init. 
      for p in self.legalPositions:
        if qLearningAgent.beliefs[enemy][p] > 0:
          isGone = False
          break
      
      observedEnemyPos = self.getOpponentPositions(gameState)[enemy/2]
      if observedEnemyPos is not None:   # enemy is near you! Don't estimate, just look at it. 
        for p in self.legalPositions: 
          if p == observedEnemyPos:
            qLearningAgent.beliefs[enemy][p] = 1             
          else:
            qLearningAgent.beliefs[enemy][p] = 0 
      elif isGone == True: #so this enemy is eaten. Let's reset the belief. 
        initPos = gameState.getInitialAgentPosition(enemy)
        qLearningAgent.beliefs[enemy][initPos] = 1.0
        for p in self.legalPositions: 
          if abs(p[0] - enemyInitPos[0]) + abs(p[1] - enemyInitPos[1]) < 3:
            qLearningAgent.beliefs[enemy][p] = 1.0  
          else:
            qLearningAgent.beliefs[enemy][p] = 0  
        qLearningAgent.beliefs[enemy].normalize()
      else:  # this is the normal case. 
        noisyDis = gameState.getAgentDistance(enemy)
        selfPos = self.getPosition(gameState)
      
        self.estimate[enemy] = util.Counter()
        
        for pos in self.legalPositions:
          trueDis = abs(pos[0] - selfPos[0]) + abs(pos[1] - selfPos[1])
          self.estimate[enemy][pos] = gameState.getDistanceProb(trueDis, noisyDis)

        self.estimate[enemy].normalize()
 
        for pos in self.legalPositions:
          qLearningAgent.beliefs[enemy][pos] *= self.estimate[enemy][pos]
          
        qLearningAgent.beliefs[enemy].normalize() 
    
        #if enemy is staying the place forever, code until here is enough.
        # above corresponds to the part1 of assignment2. below is part2.
        #Now, update the beliefs for next step based on the movement distribution. 
        newBeliefs = util.Counter()
        for p in self.legalPositions: 
          newBeliefs[p] = 0.0 
      
        for p in self.legalPositions:
          possibleLegalActions = ["East", "North", "West", "South", "Stop"]
        
          if gameState.hasWall(p[0]+1, p[1]):
            possibleLegalActions.remove("East")
          if gameState.hasWall(p[0], p[1]+1):
            possibleLegalActions.remove("North")
          if gameState.hasWall(p[0]-1, p[1]):
            possibleLegalActions.remove("West")
          if gameState.hasWall(p[0], p[1]-1):
            possibleLegalActions.remove("South")
        
          prob = 1.0 / len(possibleLegalActions) 
        
          newPosDist = util.Counter()

          if not gameState.hasWall(p[0]+1, p[1]):
            newPosDist[(p[0]+1, p[1])] = prob
          if not gameState.hasWall(p[0], p[1]+1):
            newPosDist[(p[0], p[1]+1)] = prob
          if not gameState.hasWall(p[0]-1, p[1]):
            newPosDist[(p[0]-1, p[1])] = prob
          if not gameState.hasWall(p[0], p[1]-1):
            newPosDist[(p[0], p[1]-1)] = prob
            
          newPosDist[(p[0], p[1])] = prob #agent might be stopping there. 

          #print newPosDist
        
          for newPos in newPosDist:
            newBeliefs[newPos] += qLearningAgent.beliefs[enemy][p] * newPosDist[newPos] 
        
        newBeliefs.normalize()
        qLearningAgent.beliefs[enemy] = newBeliefs  
      
        """
        if amIRed and enemy == 1:
          print ""
          print "enemy number ", enemy, " my index ", self.index
          for pos in qLearningAgent.beliefs[enemy]:
            if qLearningAgent.beliefs[enemy][pos] > 0:
              print pos, ": ", qLearningAgent.beliefs[enemy][pos]
        """ 
         
    #comment out this if you don't want to show the coloring display for each enemy.       
    self.displayDistributionsOverPositions(qLearningAgent.beliefs)
  
  def load_weights_from_db(self):
    collection = db.getCollection("pacman_weights") #Change this name to something different if you want to have your own persistence for personal debugging... but DO NOT COMMIT THE CHANGE OF THIS LINE!
    loaded = collection.find_one() #there is only one object in the database
    if loaded is None:
      print "Couldn't load the weights from the database.  Going to go ahead and assume that the db was wiped, and set some fresh 0 weights in there."
      weights = {}
      collection.save({"the_weights": weights})
      loaded_weights = collection.find_one()["the_weights"]
    else:
      loaded_weights = loaded["the_weights"]
    db.kthxbye(collection)
    #Because MongoDB can't store the Counter, but rather stores it as a dict, we re-create a counter (so we get nice 0 default values) from the dict by iteratively populating.  Kinda slow, but meh.
    weights_counter = util.Counter()
    for key in loaded_weights:
      weights_counter[key] = loaded_weights[key]
    return weights_counter
      
  def save_weights_to_db(self):
    collection = db.getCollection("pacman_weights")
    collection.update({}, {"$set": {"the_weights": self.weights}})
    db.kthxbye(collection)
  
  def chooseAction(self, gameState):
    '''The exposed interface for this agent for picking an action.'''
    
    self.guessEnemyPos(gameState)
    
    #Re-load the learned weights that were saved.      
    # self.weights = self.load_weights_from_db()
      
    #Store food info at the beginning of the game:
    if not self.firstTurnComplete:
      self.firstTurnComplete = True
      self.startingFood = len(self.getFoodYouAreDefending(gameState).asList())
      self.theirStartingFood = len(self.getFood(gameState).asList())
      self.startingFoodToEat = len(self.getFood(gameState).asList())
      self.weights["agent1_dist_to_closest_pellet"] = -1
      self.weights["agent2_dist_to_closest_pellet"] = -1
      self.weights["agent3_dist_to_closest_pellet"] = -1
      
      # self.weights = {'min_dist_to_closest_pellet':1, 'min_dist_to_closest_friend':1, 'percent_agents_in_friendly_territory':1, 'percent_food_eaten':1, 'avg_dist_to_closest_pellet':1, 'previous_state_val_maxed_over_actions':1,'two_agents_share_same_closest_pellet':1}
    else:
      #Update learned weights based on latest transition (after first turn)
      self.update(self.previous_game_state, gameState)
      
    #Pick the best action to take
    actionChosen = self.pickAction(gameState)
    
    #Before we return our decision, record where we are now and what we
    #decided so we can learn in the future whether it was a good call
    self.previous_game_state = gameState
    
    if self.debug: 
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
    
    if self.debug:
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
      #Evaluate how good that state would be 
      if self.debug:
        print "\n\n\t\t(Calculating state value for successor state that comes after action: "+str(action)+")"
      successor_val = qLearn.state_value(successor_state, self)
      transition_reward = qLearn.transition_reward(state, successor_state, self)
      val = transition_reward + successor_val #IS THIS WARRANTED?  OR SHOULD IT JUST BE THE TRANSITION_REWARD?
      if self.debug:
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
    #Store the max value so we don't have to recompute it later:
    self.previous_state_val_maxed_over_actions = max_val
    
    return chosen_action
    
  def pickAction(self, state):
    '''Get the best action to take in the current state.  With probability epsilon, take a random action; otherwise we take the best policy action.  If there are no legal actions (the case at the terminal state), we choose None.'''
    legalActions = self.getLegalActions(state)
    if len(legalActions) is 0:
        return None
        
    #Calculate the best action
    action = self.getPolicy(state) #important: during calculation the best action_state pair's val is cached

    #With probability epsilon, choose a random action
    if util.flipCoin(self.epsilon):
        action = random.choice(legalActions)

    return action

  def update(self, last_state, state):
    '''Updates/learns feature weights based on a transition from one state to another.  We learn from the transition from the previous state to this one, now that we can see what happened after our last decision and how it turned out.'''
    
    #Calculate the correction term:
    current_state_value = qLearn.state_value(state, self)
    # previous_state_value = qLearn.state_value(self.previous_game_state, self)
    # if self.previous_state_val_maxed_over_actions:
    #   current_state_expected_value = self.previous_state_val_maxed_over_actions
    # else:
    #   print "(No cached previous_state_val_maxed_over_actions exists, because this is the first turn... calculating fresh.)"
    #   current_state_expected_value = qLearn.state_value(self.getSuccessor(self.previous_game_state, self.getPolicy(self.previous_game_state)), self)
    
    current_state_expected_value = self.previous_state_val_maxed_over_actions
    
    reward = qLearn.transition_reward(self.previous_game_state, state, self)
    correction = (reward + current_state_value) - current_state_expected_value
    
    if self.index == 1:
      print "\nprinting update for agent 1:"
      print "reward:\t", reward
      print "current_state_value: \t", current_state_value
      print "current_state_expected_value: \t", current_state_expected_value
      print "correction: \t\t", correction
      
    #Calculate the feature values for the current state:
    feature_values = qLearn.state_feature_values(state, self)
    #What if we calculated for previous state and took the difference?
    feature_values_old = qLearn.state_feature_values(self.previous_game_state, self)
    
    #Update learned weights:
    # for f_name in feature_values.keys():
    #   f_val = feature_values[f_name]
    #   f_val_old = feature_values_old[f_name]
    #   f_val_delta = f_val - f_val_old
    #   #Theoretically correct: --note, not really. see below.
    #   self.weights[f_name] += self.alpha * correction * f_val
    #   #Desperate hack, which at least sets the signs correctly on the feature weights:
    #   # self.weights[f_name] += self.alpha * correction * f_val_delta
    
    print "Updating weights"
    print "\tOld weights:"
    for key in self.weights:
      print "\t\t"+str(key)+"\t"+str(self.weights[key])
    for f_name in feature_values_old.keys():
      f_val_old = feature_values_old[f_name]
      #Actually correct:
      self.weights[f_name] += self.alpha * correction * f_val_old
    print "\tNew weights:"
    for key in self.weights:
      print "\t\t"+str(key)+"\t"+str(self.weights[key])
      
    # self.save_weights_to_db()
    