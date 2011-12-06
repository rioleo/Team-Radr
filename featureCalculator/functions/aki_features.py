'''This is an example feature function that is fully functional, but returns the same feature value for every data point.  This feature function can be active in this package; it will not degrade performance significantly.  Use this as a template to create other feature functions.  

Important: 
For your feature function to work, it needs to meet two requirements: 

(1) have a function in it called calculate_feature_value().  This function is passed a game state (and optionally a connection to the database of the other raw datapoints).  It must output a dictionary with feature names and values.  In the simplest case, you just return a dictionary with one key (the feature name) and one value (the feature value).  But you're not limited to one; you can calculate arbitrarily many features in one *feature_function.py file.  It's faster to run fewer files that each calculate more features.

Note: names for features must be unique.  This could be fixed, but it's not worth the effort.  Just make sure you're not stepping on someone else's toes by checking the other *feature_function.py files; make names longer if you need.

(2) the function must be registered in __all__ list for the module.  To register the function, add it's name (filename) to the list __all__ in the file /featureCalculator/__init__.py.  See that file for an example.

To get started writing a new feature function, copy this file, rename it, and make sure it's in the folder "featureCalculator/".  Register it as above, and edit calculate_feature_vector() as desired!
'''

from game import Directions, Actions

# state is same as successor, no action involved
def calculate_feature_value(state, agent):  #Do not change this line    

    #return {}
    
    feature_values = {}
    
    myPos = agent.getPosition(state) 
    ## was using this before.. #state.getAgentState(agent.index).getPosition()
    
    amIRed = state.isOnRedTeam(agent.index)
    if amIRed:
      enemies = state.getBlueTeamIndices()
    else:
      enemies = state.getRedTeamIndices()
    
    ##Get Enemy-side Capsule feature start
    if amIRed:
        capsulePos = state.getBlueCapsules()
    else:
        capsulePos = state.getRedCapsules()
    if capsulePos:
        #print capsulePos[1]
        distanceToCapsule = agent.getMazeDistance(capsulePos[0], myPos)
        #distanceToCapsule = abs(capsulePos[0][0]-selfPos[0])+abs(capsulePos[0][1]-selfPos[1])    
        #print distanceToCapsule
        # feature_values['distanceToCapsule'] = distanceToCapsule
    else:
        # feature_values['distanceToCapsule'] = 0
    ##Capsule feature ends
    
    """
    ##capture / escape feature
    if agent.isPositionInTeamTerritory(state, myPos): 
        #I'm defending, so minimize the dis
        feature_values['distanceToEnemyOnEnemySide'] = 0 
        
        for enemy in enemies:
            # Compute distance to observed enemy
            enemyPos = agent.getOpponentPositions(state)[enemy/2]
            if enemyPos is None: #use estimate 
                maxBelief = 0
                maxPos = (1,1)
                belief = agent.beliefs[enemy]
                for pos in belief:
                    if belief[pos] > maxBelief:
                        maxBelief = belief[pos]
                        maxPos = pos
                enemyPos = pos
            
            distanceToEnemy = agent.getMazeDistance(enemyPos, myPos)
            if distanceToEnemy == 0:
                distanceToEnemy = 0.1
            feature_values['distanceToEnemyOnMySide'] = 1/distanceToEnemy
    else: 
        #I'm offencing, so minimize the dis
        feature_values['distanceToEnemyOnMySide'] = 0
        
        for enemy in enemies:
            # Compute distance to observed enemy
            enemyPos = agent.getOpponentPositions(state)[enemy/2]
            if enemyPos is None: #use estimate 
                maxBelief = 0
                maxPos = (1,1)
                belief = agent.beliefs[enemy]
                for pos in belief:
                    if belief[pos] > maxBelief:
                        maxBelief = belief[pos]
                        maxPos = pos
                enemyPos = pos
            
            distanceToEnemy = agent.getMazeDistance(enemyPos, myPos)
            if distanceToEnemy == 0:
                distanceToEnemy = 0.1
            feature_values['distanceToEnemyOnEnemySide'] = 1/distanceToEnemy
            
    print feature_values['distanceToEnemyOnMySide']         
    """        
            
    """            
                            #calculate maze distance to observed enemy.
        #Note: observedEnemyPos is the position of PREVIOUS time period. 
        #Assuming enemy is coming closer to me, I subtract 1 from mazeDis
        mazeDisToEnemy = self.getMazeDistance(myPos, observedEnemyPos) - 1
      
        if mazeDisToEnemy == 0:
          features['mazeDisToEnemy'] += -100
        elif mazeDisToEnemy == 1:
          features['mazeDisToEnemy'] += -5
        elif mazeDisToEnemy == 2:
          features['mazeDisToEnemy'] += -2  
        else:
          features['mazeDisToEnemy'] += -1
        
        ## Num of legal actions feature. If enemy is near, it's quite important 
        # so that agent doesn't go into cal-de-sac
        features['numLegalActions'] = len(successor.getLegalActions(self.index)) * 3
    
    """
    
    return feature_values
        
        
    
    