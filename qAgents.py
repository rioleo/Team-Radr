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
  
  beliefs = [None,None,None,None,None,None]
  
  def __init__(self, index, alpha, epsilon):
    CaptureAgent.__init__(self, index)
    self.weights = util.Counter()
    self.alpha = alpha #learning rate--higher means learn in larger steps
    self.epsilon = epsilon #exploration rate--higher means explore more
    self.firstTurnComplete = False
    self.startingFood = 0
    self.theirStartingFood = 0
    
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
  

  
  def chooseAction(self, gameState):
    '''The exposed interface for this agent for picking an action.'''

    self.guessEnemyPos(gameState)

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
    