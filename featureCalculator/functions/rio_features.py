'''This is an example feature function that is fully functional, but returns the same feature value for every data point.  This feature function can be active in this package; it will not degrade performance significantly.  Use this as a template to create other feature functions.  

Important: 
For your feature function to work, it needs to meet two requirements: 

(1) have a function in it called calculate_feature_value().  This function is passed a game state (and optionally a connection to the database of the other raw datapoints).  It must output a dictionary with feature names and values.  In the simplest case, you just return a dictionary with one key (the feature name) and one value (the feature value).  But you're not limited to one; you can calculate arbitrarily many features in one *feature_function.py file.  It's faster to run fewer files that each calculate more features.

Note: names for features must be unique.  This could be fixed, but it's not worth the effort.  Just make sure you're not stepping on someone else's toes by checking the other *feature_function.py files; make names longer if you need.

(2) the function must be registered in __all__ list for the module.  To register the function, add it's name (filename) to the list __all__ in the file /featureCalculator/__init__.py.  See that file for an example.

To get started writing a new feature function, copy this file, rename it, and make sure it's in the folder "featureCalculator/".  Register it as above, and edit calculate_feature_vector() as desired!
'''
import operator
from game import Directions, Actions


def calculate_feature_value(state, agent):  #Do not change this line    
	
	feature_values = {}
    #Set up some useful variables
	position = agent.getPosition(state)
	enemies = agent.getOpponentPositions(state) #None for agents w dist > 5
	walls = state.getWalls()
	food = agent.getFood(state)
    
    ## Defend high density food
	foodIamdefending = agent.getFoodYouAreDefending(state).asList()
	remaining = len(foodIamdefending)
	originalcount = agent.startingFood
	dotmap = {}
	for i in foodIamdefending:
		for j in foodIamdefending:
			dist = agent.getMazeDistance(i,j)
			if dist == 1:
				if j in dotmap:	#print i,j
					dotmap[j] += 1	
				else:
					dotmap[j] = 1
	
	highDensity = position
	
	if dotmap != {}:
		# The point where highest density
		highDensity = max(dotmap.iteritems(), key=operator.itemgetter(1))[0]

  # feature_values["distanceToHighDensity"] = (1 if agent.getMazeDistance(highDensity, position) < 10 else 0)

	return feature_values
        
        
    
    