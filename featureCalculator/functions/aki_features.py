# Implements the feature where
# it will store 1/closestEnemyOnMySide
# and distanceToEnemyOnTheirSide
# so as to maximize the distance on their side
# and minimize the distance on my side

from game import Directions, Actions

# state is same as successor, no action involved
def calculate_feature_value(state, agent):  #Do not change this line    

    feature_values = {}
    
    myPos = agent.getPosition(state) 

    amIRed = state.isOnRedTeam(agent.index)
    if amIRed:
      enemies = state.getBlueTeamIndices()
    else:
      enemies = state.getRedTeamIndices()
    minDistance = float("inf")
    if agent.isPositionInTeamTerritory(state, myPos): 
        # I'm defending, so minimize the dis
        feature_values['distanceToEnemyOnEnemySide'] = 0
        #minDistance = float("inf")
        for enemy in enemies:
            # Compute distance to closest enemy
            enemyPos = agent.getOpponentPositions(state)[enemy/2]
            if enemyPos is None: #use estimate 
                maxBelief = 0
                maxPos = (1,1)
                belief = agent.beliefs[enemy]
                for pos in belief:
                    if belief[pos] > maxBelief:
                        maxBelief = belief[pos]
                        maxPos = pos
                enemyPos = maxPos
            
            distanceToEnemy = agent.getMazeDistance(enemyPos, myPos)
            
            # Are they scared?
            #ghostState = agent.getScaredTimer(state) > 0
            
            print distanceToEnemy, distanceToEnemy < minDistance, minDistance, enemyPos
            if distanceToEnemy == 0:
                distanceToEnemy = 0.1
            if distanceToEnemy < minDistance:
                minDistance = distanceToEnemy
        #print "The closest enemy to me on my side is", minDistance
        feature_values['distanceToEnemyOnMySide'] = 1/float(minDistance)
    else: 
        # I'm offending, so maximize the dist to the closest - want to run away!
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
                enemyPos = maxPos
          	

            distanceToEnemy = agent.getMazeDistance(enemyPos, myPos)
            # Am I scared?
            ghostState = agent.getScaredTimer(state) > 0
            #print distanceToEnemy, enemyPos, ghostState
            if distanceToEnemy == 0:
                distanceToEnemy = 0.1
            #print distanceToEnemy
            if distanceToEnemy < minDistance:
            	minDistance = distanceToEnemy
        #print "The closest enemy to me on the other side is", minDistance
        feature_values['distanceToEnemyOnEnemySide'] = minDistance
            
    #print feature_values['distanceToEnemyOnMySide']         
       
    return feature_values
        
        
    
    
