# ninjaAgents.py
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

#############
# FACTORIES #
#############

NUM_KEYBOARD_AGENTS = 0
class BaselineAgents(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, isRed, first='offense', second='defense', third='offense', rest='offense', **args):
    AgentFactory.__init__(self, isRed)
    self.agents = [first, second, third]
    self.rest = rest

  def getAgent(self, index):
    if len(self.agents) > 0:
      return self.choose(self.agents.pop(0), index)
    else:
      return self.choose(self.rest, index)

  def choose(self, agentStr, index):
    if agentStr == 'keys':
      global NUM_KEYBOARD_AGENTS
      NUM_KEYBOARD_AGENTS += 1
      if NUM_KEYBOARD_AGENTS == 1:
        return keyboardAgents.KeyboardAgent(index)
      elif NUM_KEYBOARD_AGENTS == 2:
        return keyboardAgents.KeyboardAgent2(index)
      else:
        raise Exception('Max of two keyboard agents supported')
    elif agentStr == 'offense':
      return OffensiveReflexAgent(index)
    elif agentStr == 'defense':
      return DefensiveReflexAgent(index)
    else:
      raise Exception("No staff agent identified by " + agentStr)

class AllOffenseAgents(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, **args):
    AgentFactory.__init__(self, **args)

  def getAgent(self, index):
    return OffensiveReflexAgent(index)

class OffenseDefenseAgents(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, **args):
    AgentFactory.__init__(self, **args)
    self.offense = False

  def getAgent(self, index):
    self.offense = not self.offense
    if self.offense:
      return OffensiveReflexAgent(index)
    else:
      return DefensiveReflexAgent(index)

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  beliefs = [None,None,None,None,None,None]

  def __init__(self, index):
    CaptureAgent.__init__(self, index)
    self.firstTurnComplete = False
    self.startingFood = 0
    self.theirStartingFood = 0
    
    self.legalPositions = None
    self.estimate = util.Counter()
  
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  
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
        ReflexCaptureAgent.beliefs[enemy] = util.Counter()
        for p in self.legalPositions: 
          #sometimes enemy goes first, so enemy might not be in the initial state already.
          #So I'm allowing some variability here. (only the grid nearby init state gets prob)
          if abs(p[0] - enemyInitPos[0]) + abs(p[1] - enemyInitPos[1]) < 3:
            ReflexCaptureAgent.beliefs[enemy][p] = 1.0  
          else:
            ReflexCaptureAgent.beliefs[enemy][p] = 0  
        ReflexCaptureAgent.beliefs[enemy].normalize()

   
    #we are getting P(enemy being this pos | noisyDis) here
    for enemy in enemies:
      enemyInitPos = gameState.getInitialAgentPosition(enemy)
      isGone = True  #if isGone stays True, means enemy is eaten, so start from init. 
      for p in self.legalPositions:
        if ReflexCaptureAgent.beliefs[enemy][p] > 0:
          isGone = False
          break
      
      observedEnemyPos = self.getOpponentPositions(gameState)[enemy/2]
      if observedEnemyPos is not None:
        for p in self.legalPositions: 
          if p == observedEnemyPos:
            ReflexCaptureAgent.beliefs[enemy][p] = 1             
          else:
            ReflexCaptureAgent.beliefs[enemy][p] = 0 
      elif isGone == True: #so this enemy is eaten. Let's reset the belief. 
        initPos = gameState.getInitialAgentPosition(enemy)
        ReflexCaptureAgent.beliefs[enemy][initPos] = 1.0
        for p in self.legalPositions: 
          if abs(p[0] - enemyInitPos[0]) + abs(p[1] - enemyInitPos[1]) < 3:
            ReflexCaptureAgent.beliefs[enemy][p] = 1.0  
          else:
            ReflexCaptureAgent.beliefs[enemy][p] = 0  
        ReflexCaptureAgent.beliefs[enemy].normalize()
      else:  # this is the normal case. 
        noisyDis = gameState.getAgentDistance(enemy)
        selfPos = self.getPosition(gameState)
      
        self.estimate[enemy] = util.Counter()
        
        for pos in self.legalPositions:
          trueDis = abs(pos[0] - selfPos[0]) + abs(pos[1] - selfPos[1])
          self.estimate[enemy][pos] = gameState.getDistanceProb(trueDis, noisyDis)

        self.estimate[enemy].normalize()
 
        for pos in self.legalPositions:
          ReflexCaptureAgent.beliefs[enemy][pos] *= self.estimate[enemy][pos]
          
        ReflexCaptureAgent.beliefs[enemy].normalize() 
    
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
            newBeliefs[newPos] += ReflexCaptureAgent.beliefs[enemy][p] * newPosDist[newPos] 
        
        newBeliefs.normalize()
        ReflexCaptureAgent.beliefs[enemy] = newBeliefs  
      
        """
        if amIRed and enemy == 1:
          print ""
          print "enemy number ", enemy, " my index ", self.index
          for pos in ReflexCaptureAgent.beliefs[enemy]:
            if ReflexCaptureAgent.beliefs[enemy][pos] > 0:
              print pos, ": ", ReflexCaptureAgent.beliefs[enemy][pos]
        """ 
         
    #comment out this if you don't want to show the coloring display for each enemy.       
    self.displayDistributionsOverPositions(ReflexCaptureAgent.beliefs)
  
  def chooseAction(self, gameState):
    self.guessEnemyPos(gameState)
  
    if not self.firstTurnComplete:
      self.firstTurnComplete = True
      self.startingFood = len(self.getFoodYouAreDefending(gameState).asList())
      self.theirStartingFood = len(self.getFood(gameState).asList())
    
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return random.choice(bestActions)

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

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}
  
  """
  Features (not the best features) which have learned weight values stored.
  """
  def getMutationFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    position = self.getPosition(gameState)

    distances = 0.0
    for tpos in self.getTeamPositions(successor):
      distances = distances + abs(tpos[0] - position[0])
    features['xRelativeToFriends'] = distances
    
    enemyX = 0.0
    for epos in self.getOpponentPositions(successor):
      if epos is not None:
        enemyX = enemyX + epos[0]
    features['avgEnemyX'] = distances
    
    foodLeft = len(self.getFoodYouAreDefending(successor).asList())
    features['percentOurFoodLeft'] = foodLeft / self.startingFood
    
    foodLeft = len(self.getFood(successor).asList())
    features['percentTheirFoodLeft'] = foodLeft / self.theirStartingFood
    
    features['IAmAScaredGhost'] = 1.0 if self.isPacman(successor) and self.getScaredTimer(successor) > 0 else 0.0
    
    features['enemyPacmanNearMe'] = 0.0
    minOppDist = 10000
    minOppPos = (0, 0)
    for ep in self.getOpponentPositions(successor):
      # For a feature later on
      if ep is not None and self.getMazeDistance(ep, position) < minOppDist:
        minOppDist = self.getMazeDistance(ep, position)
        minOppPos = ep
      if ep is not None and self.getMazeDistance(ep, position) <= 1 and self.isPositionInTeamTerritory(successor, ep):
        features['enemyPacmanNearMe'] = 1.0
        
    features['numSameFriends'] = 0
    for friend in self.getTeam(successor):
      if successor.getAgentState(self.index).isPacman is self.isPacman(successor):
        features['numSameFriends'] = features['numSameFriends'] + 1

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDiffDistance = min([1000] + [self.getMazeDistance(position, food) - self.getMazeDistance(minOppPos, food) for food in foodList if minOppDist < 1000])
      features['blockableFood'] = 1.0 if minDiffDistance < 1.0 else 0.0

    return features

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = self.getMutationFeatures(gameState, action)
    successor = self.getSuccessor(gameState, action)
    
    features['successorScore'] = self.getScore(successor)
    
    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    features['numFood'] = len(foodList)
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    
    #Capsule feature start
    amIRed = successor.isOnRedTeam(self.index)
    if amIRed:
        capsulePos = successor.getBlueCapsules()
    else:
        capsulePos = successor.getRedCapsules()
    if capsulePos:
        selfPos = self.getPosition(successor)
        #print capsulePos[1]
        distanceToCapsule = self.getMazeDistance(capsulePos[0], selfPos)
        #distanceToCapsule = abs(capsulePos[0][0]-selfPos[0])+abs(capsulePos[0][1]-selfPos[1])    
        #print distanceToCapsule
        features['distanceToCapsule'] = distanceToCapsule
    else:
        features['distanceToCapsule'] = 0
    
    #print features['distanceToCapsule']
    #Capsule feature ends
    
    return features

  def getWeights(self, gameState, action):
    weights = regularMutation.aggressiveDWeightsDict
    weights['successorScore'] = 1.5
    # Always eat nearby food
    weights['numFood'] = -1000
    # Favor reaching new food the most
    weights['distanceToFood'] = -5
    weights['distanceToCapsule'] = -10 
    return weights

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = self.getMutationFeatures(gameState, action)
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1
    
    foodList = self.getFoodYouAreDefending(successor).asList()
    distance = 0
    for food in foodList:
      distance = distance + self.getMazeDistance(myPos, food)
    features['totalDistancesToFood'] = distance

    return features

  def getWeights(self, gameState, action):
    weights = regularMutation.goalieDWeightsDict
    weights['numInvaders'] = -100
    weights['onDefense'] = 100
    weights['invaderDistance'] = -1.5
    weights['totalDistancesToFood'] = -0.1
    weights['stop'] = -1
    weights['reverse'] = -1
    return weights


